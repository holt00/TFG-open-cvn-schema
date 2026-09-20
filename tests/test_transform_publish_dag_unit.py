"""Structure of the ``transform_publish`` DAG file (issue #99), checked statically.

Airflow is not installed on the host and the DAG runs in the cluster, so these tests read
the file with ``ast``: the chain, the task ids, the jobs it launches, and that no secret
is written in it. Importing the file for real (and rendering its commands) is done in
the cluster, in the issue's Task 6 and Task 8.
"""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DAG_FILE = ROOT / "dags" / "transform_publish.py"
SOURCE = DAG_FILE.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)

TASKS = ["bronze_to_silver", "silver_to_gold", "publish_gold_to_postgres"]


def _string_constants() -> list[str]:
    return [node.value for node in ast.walk(TREE) if isinstance(node, ast.Constant) and isinstance(node.value, str)]


def test_the_dag_declares_the_three_tasks_in_a_chain():
    assignments = {
        target.id: node.value
        for node in ast.walk(TREE)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    for task in TASKS:
        call = assignments[task]
        assert isinstance(call, ast.Call) and call.args[0].value == task  # the variable and the task id agree

    chain = [node for node in ast.walk(TREE) if isinstance(node, ast.BinOp) and isinstance(node.op, ast.RShift)]
    rendered = {ast.unparse(node) for node in chain}
    assert "bronze_to_silver >> silver_to_gold >> publish_gold_to_postgres" in rendered


def test_the_dag_id_is_transform_publish_and_it_is_not_scheduled_yet():
    dag_call = next(
        node for node in ast.walk(TREE) if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "DAG"
    )
    keywords = {kw.arg: kw.value for kw in dag_call.keywords}

    assert keywords["dag_id"].value == "transform_publish"
    assert keywords["schedule"].value is None  # manual trigger first (decision D8)
    assert keywords["max_active_runs"].value == 1


@pytest.mark.parametrize("job", ["bronze_to_silver.py", "silver_to_gold.py", "publish_gold_to_postgres.py"])
def test_every_launched_job_exists(job):
    assert job in _string_constants()
    assert (ROOT / "src" / "tfm_lakehouse" / "spark_jobs" / job).is_file()


def test_the_jobs_directory_matches_the_repo_mount():
    assert re.search(r'JOBS = "/repo/src/tfm_lakehouse/spark_jobs"', SOURCE)


def test_only_the_publish_task_receives_the_postgres_password_and_only_by_secret_reference():
    postgres_calls = [
        node for node in ast.walk(TREE)
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "_spark_driver_task"
    ]
    with_postgres = {call.args[0].value for call in postgres_calls if any(kw.arg == "postgres" and kw.value.value for kw in call.keywords)}
    assert with_postgres == {"publish_gold_to_postgres"}
    assert '_secret_env("PG_PASSWORD", "postgresql-gold-credentials", "password")' in SOURCE


def test_no_credential_is_written_in_the_file():
    lowered = SOURCE.lower()
    assert "password=" not in lowered and "secret_key=" not in lowered and "access_key=" not in lowered
    assert not re.search(r"jdbc:postgresql://[^\s\"']*:[^\s\"'@]*@", SOURCE)  # no user:password@ in a URL


def test_the_image_is_the_gold_image_and_is_overridden_on_the_command_line():
    assert 'SPARK_IMAGE = "tfm-lakehouse/spark-py:3.5.9-iceberg1.11.0-gold"' in SOURCE
    assert "--conf spark.kubernetes.container.image={SPARK_IMAGE}" in SOURCE


def test_pods_are_deleted_when_they_finish_and_run_as_the_spark_service_account():
    assert 'on_finish_action="delete_pod"' in SOURCE
    assert 'service_account_name="spark"' in SOURCE


def test_the_dag_keeps_every_parameter_of_the_provisional_issue_98_dag():
    # transform_publish absorbs issue98_bronze_to_silver, so its parameters must survive.
    for parameter in [
        "executors", "executor_memory", "executor_memory_overhead", "shuffle_partitions",
        "rejection_threshold", "ground_truth_run_id", "org_threshold",
    ]:
        assert f'"{parameter}": Param(' in SOURCE
