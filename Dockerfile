FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
RUN apt install unzip
# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Prepend venv bin so uv run (and any scripts) use the right env
ENV PATH="/app/.venv/bin:$PATH"

# Expose the ports your app needs
EXPOSE 8000 3000

# Run your app (replace `my_app` with your uv script name)
CMD ["uv", "run", "reflex", "run"]