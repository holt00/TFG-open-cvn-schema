"""Issue #93 end-to-end proof: Airflow triggers spark-submit in Kubernetes
client deploy mode against the Iceberg Hadoop catalog on MinIO configured
in issue #92 (infra/spark-conf/iceberg-catalog.conf).

The KubernetesPodOperator's own pod runs the custom Spark image
(infra/spark-conf/Dockerfile) and IS the Spark driver in client mode, so
spark-submit is invoked directly as this pod's command. The command is
routed through the image's own /opt/entrypoint.sh (its $1 is neither
"driver" nor "executor", so it falls into that script's pass-through
branch) rather than replacing it outright: entrypoint.sh is what patches
/etc/passwd for the arbitrary spark_uid before anything else runs, which a
full override was found to skip (see the issue document's Task 8 findings
-- Ivy's local-repo init and Hadoop's UserGroupInformation both fail
without that patched entry). The outer bash -c is only there to expand
$POD_IP (Kubernetes Downward API) into spark.driver.host, since executors
must reach this pod's driver directly over the flat pod network (no
Service involved in client mode, unlike cluster mode).

AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY are injected here directly from the
existing minio-root-credentials Secret (issue #91), rather than via the
spark.kubernetes.driver.secretKeyRef.* properties in iceberg-catalog.conf:
those properties only take effect when spark-submit itself builds a driver
pod spec, which happens only in cluster deploy mode. In client mode the
driver is just this pod, so its env has to be set on this pod's own spec
(found the hard way in issue #93's Task 8 -- the executor-side
secretKeyRef properties in that file are unaffected and still apply, since
Spark always creates executor pods itself regardless of driver deploy
mode).
"""

from __future__ import annotations

import pendulum
from airflow.models.dag import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s

NAMESPACE = "tfm-lakehouse"
SPARK_IMAGE = "tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0"

SPARK_SUBMIT_COMMAND = " ".join(
    [
        "exec /opt/entrypoint.sh /opt/spark/bin/spark-submit",
        "--master k8s://https://kubernetes.default.svc:443",
        "--deploy-mode client",
        "--name issue93-iceberg-smoke-test",
        "--properties-file /opt/spark/conf/iceberg-catalog.conf",
        f"--conf spark.kubernetes.namespace={NAMESPACE}",
        "--conf spark.driver.bindAddress=0.0.0.0",
        "--conf spark.driver.host=$POD_IP",
        "local:///opt/spark/jobs/iceberg_smoke_test.py",
    ]
)

with DAG(
    dag_id="issue93_spark_iceberg_smoke_test",
    schedule=None,
    start_date=pendulum.datetime(2026, 9, 16, tz="UTC"),
    catchup=False,
    tags=["tfm", "issue-93", "spark", "iceberg"],
) as dag:
    spark_submit = KubernetesPodOperator(
        task_id="spark_submit_iceberg_smoke_test",
        namespace=NAMESPACE,
        name="issue93-spark-submit-launcher",
        image=SPARK_IMAGE,
        image_pull_policy="IfNotPresent",
        service_account_name="spark",
        cmds=["/bin/bash", "-c"],
        arguments=[SPARK_SUBMIT_COMMAND],
        env_vars=[
            k8s.V1EnvVar(
                name="POD_IP",
                value_from=k8s.V1EnvVarSource(
                    field_ref=k8s.V1ObjectFieldSelector(field_path="status.podIP")
                ),
            ),
            k8s.V1EnvVar(
                name="AWS_ACCESS_KEY_ID",
                value_from=k8s.V1EnvVarSource(
                    secret_key_ref=k8s.V1SecretKeySelector(
                        name="minio-root-credentials", key="root-user"
                    )
                ),
            ),
            k8s.V1EnvVar(
                name="AWS_SECRET_ACCESS_KEY",
                value_from=k8s.V1EnvVarSource(
                    secret_key_ref=k8s.V1SecretKeySelector(
                        name="minio-root-credentials", key="root-password"
                    )
                ),
            ),
        ],
        get_logs=True,
        # Kept around after this issue's first run for Task 8's manual pod
        # inspection; revisit for #97/#99's real DAGs which should clean up.
        on_finish_action="keep_pod",
    )
