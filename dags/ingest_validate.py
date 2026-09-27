"""Issue #97: the ``ingest_validate`` DAG lands both data sources into MinIO bronze.

Four tasks, one pod each, running the ``tfm-lakehouse/ingest`` image
(infra/ingest/Dockerfile) because Airflow's own Python (3.13) cannot run
``tfm_lakehouse`` (3.14). The code, the JSON Schema and the data are not in the
image: they are mounted from the repository checkout with hostPath, which is
only valid because k3s is a single node on the same machine as the checkout
(decision D2 in the issue document). Tasks pass data to each other through
``data/bronze_runs/<run_id>/`` and print a ``TASK_SUMMARY`` line in their log;
XCom is not used.

Order (decision D7): the API enrichment needs the ORCID iDs the synthetic CVNs
declare, and the synthetic generator needs the ORCID subset.

Credentials: AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY come from the existing
``minio-root-credentials`` Secret (issue #91) by ``secretKeyRef`` on the pod
spec, the only place they work in this setup (issue #93's finding). Nothing
secret is in this file.
"""

from __future__ import annotations

import os

import pendulum
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import DAG, Param
from kubernetes.client import models as k8s

NAMESPACE = "tfm-lakehouse"
INGEST_IMAGE = "tfm-lakehouse/ingest:py3.14"
# Path of the repository checkout on the machine that runs k3s. Override with
# TFM_REPO_ROOT (set on the dag-processor/scheduler pods, e.g. via a Helm
# values env entry) on a checkout other than this development machine's;
# issue #102 found this had to be hand-edited otherwise (see
# docs/development/tfm_lakehouse_workflow.md, Canonical Prerequisites).
REPO_ROOT = os.environ.get("TFM_REPO_ROOT", "/mnt/e/Carlos/unii/tfg/repo/TFG-open-cvn-schema")
TASKS_MODULE = "python -m tfm_lakehouse.bronze.tasks"
RUN_ID_ARG = "--run-id '{{ run_id }}'"

VOLUMES = [
    k8s.V1Volume(name="src", host_path=k8s.V1HostPathVolumeSource(path=f"{REPO_ROOT}/src", type="Directory")),
    k8s.V1Volume(name="schemas", host_path=k8s.V1HostPathVolumeSource(path=f"{REPO_ROOT}/schemas", type="Directory")),
    k8s.V1Volume(name="data", host_path=k8s.V1HostPathVolumeSource(path=f"{REPO_ROOT}/data", type="DirectoryOrCreate")),
]
VOLUME_MOUNTS = [
    k8s.V1VolumeMount(name="src", mount_path="/repo/src", read_only=True),
    k8s.V1VolumeMount(name="schemas", mount_path="/repo/schemas", read_only=True),
    k8s.V1VolumeMount(name="data", mount_path="/repo/data"),
]


def _secret_env(name: str, key: str) -> k8s.V1EnvVar:
    return k8s.V1EnvVar(
        name=name,
        value_from=k8s.V1EnvVarSource(secret_key_ref=k8s.V1SecretKeySelector(name="minio-root-credentials", key=key)),
    )


ENV_VARS = [
    _secret_env("AWS_ACCESS_KEY_ID", "root-user"),
    _secret_env("AWS_SECRET_ACCESS_KEY", "root-password"),
    k8s.V1EnvVar(name="TFM_DATA_DIR", value="/repo/data"),
]


def _ingest_task(task_id: str, command: str, *, timeout_minutes: int, retries: int) -> KubernetesPodOperator:
    """One DAG task: a pod running one ``tfm_lakehouse.bronze.tasks`` command.

    The command goes through ``bash -c`` so optional flags rendered from
    params can expand to nothing.
    """
    return KubernetesPodOperator(
        task_id=task_id,
        namespace=NAMESPACE,
        name=task_id.replace("_", "-"),
        image=INGEST_IMAGE,
        image_pull_policy="IfNotPresent",
        cmds=["/bin/bash", "-c"],
        arguments=[f"exec {TASKS_MODULE} {command}"],
        env_vars=ENV_VARS,
        volumes=VOLUMES,
        volume_mounts=VOLUME_MOUNTS,
        security_context=k8s.V1PodSecurityContext(run_as_user=1000, run_as_group=1000),
        container_resources=k8s.V1ResourceRequirements(
            requests={"cpu": "250m", "memory": "512Mi"}, limits={"memory": "3Gi"}
        ),
        startup_timeout_seconds=300,
        get_logs=True,
        on_finish_action="delete_pod",
        retries=retries,
        execution_timeout=pendulum.duration(minutes=timeout_minutes),
    )


with DAG(
    dag_id="ingest_validate",
    description="Lands the ORCID bulk subset, ORCID API records and synthetic CVNs into MinIO bronze (issue #97)",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 9, 19, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": pendulum.duration(minutes=1)},
    params={
        "count": Param(1000, type="integer", minimum=1, description="Synthetic CVN documents to generate"),
        "seed": Param(42, type="integer", description="Seed of the synthetic generator and of the API sample"),
        "orcid_link_ratio": Param(0.7, type="number", minimum=0, maximum=1, description="Share of CVNs carrying their ORCID iD"),
        "enrichment_sample_size": Param(200, type="integer", minimum=1, description="ORCID iDs to look up in the API"),
        "bulk_max_records": Param(20000, type="integer", minimum=0, description="ORCID bulk records to land; 0 lands all (~40 GB)"),
        "rejection_threshold": Param(0.05, type="number", minimum=0, maximum=1, description="Highest tolerated share of rejected records"),
        "force_refetch": Param(False, type="boolean", description="Extract the ORCID subset again (about 81 minutes)"),
        "force_bulk_landing": Param(False, type="boolean", description="Land the ORCID bulk snapshot even if already landed"),
    },
    tags=["tfm", "issue-97", "ingestion", "bronze"],
    doc_md=__doc__,
) as dag:
    fetch_orcid_bulk_subset = _ingest_task(
        "fetch_orcid_bulk_subset",
        "orcid-bulk-subset {{ '--force-refetch' if params.force_refetch else '' }}",
        timeout_minutes=180,
        retries=0,
    )
    generate_synthetic_cvn = _ingest_task(
        "generate_synthetic_cvn",
        f"synthetic-cvn {RUN_ID_ARG} --count {{{{ params.count }}}} --seed {{{{ params.seed }}}}"
        " --orcid-link-ratio {{ params.orcid_link_ratio }}",
        timeout_minutes=60,
        retries=1,
    )
    fetch_orcid_api_enrichment = _ingest_task(
        "fetch_orcid_api_enrichment",
        f"orcid-api-enrichment {RUN_ID_ARG} --sample-size {{{{ params.enrichment_sample_size }}}} --seed {{{{ params.seed }}}}",
        timeout_minutes=30,
        retries=1,
    )
    validate_and_land_bronze = _ingest_task(
        "validate_and_land_bronze",
        f"land-bronze {RUN_ID_ARG} --bulk-max-records {{{{ params.bulk_max_records }}}}"
        " --rejection-threshold {{ params.rejection_threshold }}"
        " {{ '--force-bulk-landing' if params.force_bulk_landing else '' }}",
        timeout_minutes=180,
        retries=1,
    )

    fetch_orcid_bulk_subset >> generate_synthetic_cvn >> fetch_orcid_api_enrichment >> validate_and_land_bronze
