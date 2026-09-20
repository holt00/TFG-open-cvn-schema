"""Issue #99: the ``transform_publish`` DAG, bronze -> silver -> gold -> PostgreSQL.

Three tasks in a chain, each a Spark job run the way issues #93 and #98 established:
the ``KubernetesPodOperator`` pod IS the Spark driver (``--deploy-mode client``) and
runs ``spark-submit`` as its command through the image's own ``/opt/entrypoint.sh``
(which registers the arbitrary uid in ``/etc/passwd``; going around it fails).

    bronze_to_silver >> silver_to_gold >> publish_gold_to_postgres

* ``bronze_to_silver`` (issue #98): validation, normalization and entity resolution
  into the ``lakehouse.silver`` Iceberg tables. It absorbs the provisional
  ``issue98_bronze_to_silver`` DAG.
* ``silver_to_gold`` (issue #99): the research indicators into ``lakehouse.gold``.
* ``publish_gold_to_postgres`` (issue #99): stages the gold tables into the dedicated
  PostgreSQL and swaps them in atomically, so Superset (issue #100) never sees a
  missing or half-loaded table.

One image runs all three: the gold one (infra/spark-conf/Dockerfile.gold), that is the
silver image (Python 3.10 with pydantic, jsonschema, requests) plus the PostgreSQL JDBC
driver. The code (``src/``) and the JSON Schema (``schemas/``) are mounted from the
checkout with hostPath on the driver pod and, through
``spark.kubernetes.executor.volumes.hostPath.*``, on every executor. This is only valid
because k3s is a single node on the machine that holds the checkout (issue #97, D2).
``spark.kubernetes.container.image`` is overridden on the command line because
``iceberg-catalog.conf`` names the issue #93 image.

Credentials come from Secrets by ``secretKeyRef``, never from this file: MinIO's
``minio-root-credentials`` on the driver (and, through ``iceberg-catalog.conf``, on the
executors), and ``postgresql-gold-credentials`` as ``PG_PASSWORD`` on the publish
driver only. The PostgreSQL password reaches the executors that write over JDBC inside
the write's options, so they need no environment variable of their own.
"""

from __future__ import annotations

import pendulum
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import DAG, Param
from kubernetes.client import models as k8s

NAMESPACE = "tfm-lakehouse"
SPARK_IMAGE = "tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold"
# Path of the repository checkout on the machine that runs k3s.
REPO_ROOT = "/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema"
JOBS = "/repo/src/tfm_lakehouse/spark_jobs"
RUN_DIR = "{{ run_id | replace(':', '_') | replace('+', '_') }}"


def _executor_hostpath(name: str) -> str:
    return (
        f"--conf spark.kubernetes.executor.volumes.hostPath.{name}.mount.path=/repo/{name} "
        f"--conf spark.kubernetes.executor.volumes.hostPath.{name}.mount.readOnly=true "
        f"--conf spark.kubernetes.executor.volumes.hostPath.{name}.options.path={REPO_ROOT}/{name}"
    )


def spark_submit_command(name: str, job: str, job_args: list[str], *, executors: str, executor_memory: str, overhead: str) -> str:
    """Return the shell command a driver pod runs: ``spark-submit`` in client mode."""
    return " ".join(
        [
            "exec /opt/entrypoint.sh /opt/spark/bin/spark-submit",
            "--master k8s://https://kubernetes.default.svc:443",
            "--deploy-mode client",
            f"--name {name}",
            "--properties-file /opt/spark/conf/iceberg-catalog.conf",
            f"--conf spark.kubernetes.namespace={NAMESPACE}",
            f"--conf spark.kubernetes.container.image={SPARK_IMAGE}",
            "--conf spark.driver.bindAddress=0.0.0.0",
            "--conf spark.driver.host=$POD_IP",
            "--driver-memory 1g",
            f"--conf spark.executor.instances={executors}",
            "--conf spark.executor.cores=1",
            f"--conf spark.executor.memory={executor_memory}",
            f"--conf spark.executor.memoryOverhead={overhead}",
            "--conf spark.executorEnv.PYTHONPATH=/repo/src",
            _executor_hostpath("src"),
            _executor_hostpath("schemas"),
            f"{JOBS}/{job}",
            *job_args,
        ]
    )


BRONZE_TO_SILVER_COMMAND = spark_submit_command(
    "transform-publish-bronze-to-silver",
    "bronze_to_silver.py",
    [
        "--shuffle-partitions {{ params.shuffle_partitions }}",
        "--rejection-threshold {{ params.rejection_threshold }}",
        "--org-threshold {{ params.org_threshold }}",
        f"--summary-file /repo/data/silver_runs/{RUN_DIR}/summary.json",
        "{{ ('--manifest /repo/data/bronze_runs/' ~ params.ground_truth_run_id ~ '/synthetic_cvn/manifest.jsonl') if params.ground_truth_run_id else '' }}",
    ],
    executors="{{ params.executors }}",
    executor_memory="{{ params.executor_memory }}",
    overhead="{{ params.executor_memory_overhead }}",
)

SILVER_TO_GOLD_COMMAND = spark_submit_command(
    "transform-publish-silver-to-gold",
    "silver_to_gold.py",
    [
        "--run-id '{{ run_id }}'",
        "--shuffle-partitions {{ params.gold_shuffle_partitions }}",
        "--max-entities-per-doi {{ params.max_entities_per_doi }}",
        "{{ ('--max-year ' ~ params.max_year) if params.max_year else '' }}",
        f"--summary-file /repo/data/gold_runs/{RUN_DIR}/silver_to_gold_summary.json",
    ],
    executors="{{ params.gold_executors }}",
    executor_memory="{{ params.gold_executor_memory }}",
    overhead="512m",
)

PUBLISH_COMMAND = spark_submit_command(
    "transform-publish-publish-gold",
    "publish_gold_to_postgres.py",
    [f"--summary-file /repo/data/gold_runs/{RUN_DIR}/publish_summary.json"],
    executors="{{ params.gold_executors }}",
    executor_memory="{{ params.gold_executor_memory }}",
    overhead="512m",
)


def _secret_env(name: str, secret: str, key: str) -> k8s.V1EnvVar:
    return k8s.V1EnvVar(
        name=name,
        value_from=k8s.V1EnvVarSource(secret_key_ref=k8s.V1SecretKeySelector(name=secret, key=key)),
    )


def _spark_driver_task(task_id: str, command: str, *, postgres: bool = False, minutes: int = 30) -> KubernetesPodOperator:
    env_vars = [
        k8s.V1EnvVar(
            name="POD_IP",
            value_from=k8s.V1EnvVarSource(field_ref=k8s.V1ObjectFieldSelector(field_path="status.podIP")),
        ),
        k8s.V1EnvVar(name="PYTHONPATH", value="/repo/src"),
        _secret_env("AWS_ACCESS_KEY_ID", "minio-root-credentials", "root-user"),
        _secret_env("AWS_SECRET_ACCESS_KEY", "minio-root-credentials", "root-password"),
    ]
    if postgres:
        env_vars.append(_secret_env("PG_PASSWORD", "postgresql-gold-credentials", "password"))
    return KubernetesPodOperator(
        task_id=task_id,
        namespace=NAMESPACE,
        name=f"transform-publish-{task_id.replace('_', '-')}",
        image=SPARK_IMAGE,
        image_pull_policy="IfNotPresent",
        service_account_name="spark",
        cmds=["/bin/bash", "-c"],
        arguments=[command],
        env_vars=env_vars,
        volumes=[
            k8s.V1Volume(name="src", host_path=k8s.V1HostPathVolumeSource(path=f"{REPO_ROOT}/src", type="Directory")),
            k8s.V1Volume(name="schemas", host_path=k8s.V1HostPathVolumeSource(path=f"{REPO_ROOT}/schemas", type="Directory")),
            k8s.V1Volume(name="data", host_path=k8s.V1HostPathVolumeSource(path=f"{REPO_ROOT}/data", type="DirectoryOrCreate")),
        ],
        volume_mounts=[
            k8s.V1VolumeMount(name="src", mount_path="/repo/src", read_only=True),
            k8s.V1VolumeMount(name="schemas", mount_path="/repo/schemas", read_only=True),
            k8s.V1VolumeMount(name="data", mount_path="/repo/data"),
        ],
        container_resources=k8s.V1ResourceRequirements(requests={"cpu": "500m", "memory": "1Gi"}, limits={"memory": "2Gi"}),
        startup_timeout_seconds=300,
        get_logs=True,
        on_finish_action="delete_pod",
        execution_timeout=pendulum.duration(minutes=minutes),
    )


with DAG(
    dag_id="transform_publish",
    description="Bronze -> silver -> gold -> PostgreSQL: validation, entity resolution, indicators, atomic publish (issues #98, #99)",
    schedule=None,
    start_date=pendulum.datetime(2026, 9, 20, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    params={
        "executors": Param(2, type="integer", minimum=1, description="bronze_to_silver: Spark executor pods"),
        "executor_memory": Param("1g", type="string", description="bronze_to_silver: executor JVM heap"),
        "executor_memory_overhead": Param("1g", type="string", description="bronze_to_silver: executor off-heap memory; holds the Python workers that parse the XML"),
        "shuffle_partitions": Param(16, type="integer", minimum=1, description="bronze_to_silver: spark.sql.shuffle.partitions"),
        "rejection_threshold": Param(0.05, type="number", minimum=0, maximum=1, description="Highest tolerated share of rejected records per source"),
        "ground_truth_run_id": Param("", type="string", description="Run id under data/bronze_runs/ whose synthetic manifest evaluates the resolution; empty skips the evaluation"),
        "org_threshold": Param(1.0, type="number", minimum=0, maximum=1, description="Organization similarity needed by the name/affiliation rule; 1.0 = equal names"),
        "gold_executors": Param(2, type="integer", minimum=1, description="silver_to_gold and publish: Spark executor pods"),
        "gold_executor_memory": Param("1g", type="string", description="silver_to_gold and publish: executor JVM heap"),
        "gold_shuffle_partitions": Param(16, type="integer", minimum=1, description="silver_to_gold: spark.sql.shuffle.partitions"),
        "max_year": Param(0, type="integer", minimum=0, description="Highest accepted publication year; 0 = the current year plus one"),
        "max_entities_per_doi": Param(200, type="integer", minimum=2, description="A DOI reported by more entities is left out of the collaboration pairs"),
    },
    tags=["tfm", "issue-99", "spark", "silver", "gold"],
    doc_md=__doc__,
) as dag:
    bronze_to_silver = _spark_driver_task("bronze_to_silver", BRONZE_TO_SILVER_COMMAND, minutes=60)
    silver_to_gold = _spark_driver_task("silver_to_gold", SILVER_TO_GOLD_COMMAND)
    publish_gold_to_postgres = _spark_driver_task("publish_gold_to_postgres", PUBLISH_COMMAND, postgres=True)

    bronze_to_silver >> silver_to_gold >> publish_gold_to_postgres
