"""Issue #98: manual-trigger DAG that runs the bronze -> silver Spark job.

Provisional: issue #99 absorbs this task into its ``transform_publish`` DAG. It
follows the issue #93 pattern: the ``KubernetesPodOperator`` pod IS the Spark
driver (``--deploy-mode client``), so it runs ``spark-submit`` as its command
through the image's own ``/opt/entrypoint.sh`` (which registers the arbitrary
uid in ``/etc/passwd``; going around it fails, issue #93's Task 8).

The image is the silver one (infra/spark-conf/Dockerfile.silver): Python 3.10
plus pydantic, jsonschema and requests, because the job reuses the repository's
own code. That code (``src/``) and the JSON Schema (``schemas/``) are mounted
from the checkout with hostPath on the driver pod and, through
``spark.kubernetes.executor.volumes.hostPath.*``, on every executor (they run
the validation UDFs). This is only valid because k3s is a single node on the
machine that holds the checkout (issue #97, decision D2).

``spark.kubernetes.container.image`` is overridden on the command line because
``iceberg-catalog.conf`` names the issue #93 image, which lacks those libraries.
Credentials come from the existing ``minio-root-credentials`` Secret by
``secretKeyRef`` on this pod (the driver) and, via ``iceberg-catalog.conf``, on
the executors; nothing secret is in this file.
"""

from __future__ import annotations

import pendulum
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import DAG, Param
from kubernetes.client import models as k8s

NAMESPACE = "tfm-lakehouse"
SILVER_IMAGE = "tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-silver"
# Path of the repository checkout on the machine that runs k3s.
REPO_ROOT = "/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema"
JOB = "/repo/src/tfm_lakehouse/spark_jobs/bronze_to_silver.py"
SUMMARY_FILE = "/repo/data/silver_runs/{{ run_id | replace(':', '_') | replace('+', '_') }}/summary.json"


def _executor_hostpath(name: str) -> str:
    return (
        f"--conf spark.kubernetes.executor.volumes.hostPath.{name}.mount.path=/repo/{name} "
        f"--conf spark.kubernetes.executor.volumes.hostPath.{name}.mount.readOnly=true "
        f"--conf spark.kubernetes.executor.volumes.hostPath.{name}.options.path={REPO_ROOT}/{name}"
    )


SPARK_SUBMIT_COMMAND = " ".join(
    [
        "exec /opt/entrypoint.sh /opt/spark/bin/spark-submit",
        "--master k8s://https://kubernetes.default.svc:443",
        "--deploy-mode client",
        "--name issue98-bronze-to-silver",
        "--properties-file /opt/spark/conf/iceberg-catalog.conf",
        f"--conf spark.kubernetes.namespace={NAMESPACE}",
        f"--conf spark.kubernetes.container.image={SILVER_IMAGE}",
        "--conf spark.driver.bindAddress=0.0.0.0",
        "--conf spark.driver.host=$POD_IP",
        "--driver-memory 1g",
        "--conf spark.executor.instances={{ params.executors }}",
        "--conf spark.executor.cores=1",
        "--conf spark.executor.memory={{ params.executor_memory }}",
        "--conf spark.executor.memoryOverhead={{ params.executor_memory_overhead }}",
        "--conf spark.executorEnv.PYTHONPATH=/repo/src",
        _executor_hostpath("src"),
        _executor_hostpath("schemas"),
        JOB,
        "--shuffle-partitions {{ params.shuffle_partitions }}",
        "--rejection-threshold {{ params.rejection_threshold }}",
        "--org-threshold {{ params.org_threshold }}",
        f"--summary-file {SUMMARY_FILE}",
        "{{ ('--manifest /repo/data/bronze_runs/' ~ params.ground_truth_run_id ~ '/synthetic_cvn/manifest.jsonl') if params.ground_truth_run_id else '' }}",
    ]
)


def _secret_env(name: str, key: str) -> k8s.V1EnvVar:
    return k8s.V1EnvVar(
        name=name,
        value_from=k8s.V1EnvVarSource(secret_key_ref=k8s.V1SecretKeySelector(name="minio-root-credentials", key=key)),
    )


with DAG(
    dag_id="issue98_bronze_to_silver",
    description="Rebuilds the silver Iceberg tables from bronze: validation, normalization, entity resolution (issue #98)",
    schedule=None,
    start_date=pendulum.datetime(2026, 9, 19, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    params={
        "executors": Param(2, type="integer", minimum=1, description="Spark executor pods"),
        "executor_memory": Param("1g", type="string", description="Executor JVM heap"),
        "executor_memory_overhead": Param("1g", type="string", description="Executor off-heap memory; holds the Python workers that parse the XML"),
        "shuffle_partitions": Param(16, type="integer", minimum=1, description="spark.sql.shuffle.partitions"),
        "rejection_threshold": Param(0.05, type="number", minimum=0, maximum=1, description="Highest tolerated share of rejected records per source"),
        "ground_truth_run_id": Param("", type="string", description="Run id under data/bronze_runs/ whose synthetic manifest evaluates the resolution; empty skips the evaluation"),
        "org_threshold": Param(1.0, type="number", minimum=0, maximum=1, description="Organization similarity needed by the name/affiliation rule; 1.0 = equal names"),
    },
    tags=["tfm", "issue-98", "spark", "silver"],
    doc_md=__doc__,
) as dag:
    bronze_to_silver = KubernetesPodOperator(
        task_id="bronze_to_silver",
        namespace=NAMESPACE,
        name="issue98-bronze-to-silver",
        image=SILVER_IMAGE,
        image_pull_policy="IfNotPresent",
        service_account_name="spark",
        cmds=["/bin/bash", "-c"],
        arguments=[SPARK_SUBMIT_COMMAND],
        env_vars=[
            k8s.V1EnvVar(
                name="POD_IP",
                value_from=k8s.V1EnvVarSource(field_ref=k8s.V1ObjectFieldSelector(field_path="status.podIP")),
            ),
            k8s.V1EnvVar(name="PYTHONPATH", value="/repo/src"),
            _secret_env("AWS_ACCESS_KEY_ID", "root-user"),
            _secret_env("AWS_SECRET_ACCESS_KEY", "root-password"),
        ],
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
        execution_timeout=pendulum.duration(minutes=60),
    )
