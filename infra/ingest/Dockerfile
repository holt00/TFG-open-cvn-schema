# Ingestion image for the issue #97 `ingest_validate` DAG. Build context is the
# repo root (see .dockerignore, which keeps data/ out of the context):
#   docker build -f infra/ingest/Dockerfile -t tfm-lakehouse/ingest:py3.14 .
#
# Holds only Python 3.14 and the project's runtime dependencies, pinned by
# uv.lock. The code (src/), the JSON Schema (schemas/), and the data (data/)
# are NOT baked in: the DAG mounts them from the repository checkout with
# hostPath, so editing code needs no rebuild and no `k3s ctr images import`
# (issue #97, decision D2).

FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/repo/src \
    HOME=/tmp

RUN pip install --no-cache-dir uv==0.9.30

WORKDIR /build
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project && rm -rf /build /root/.cache

WORKDIR /repo
USER 1000:1000
