FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY src ./src

RUN uv sync --locked --no-dev

EXPOSE 8000

CMD ["uv", "run", "src/app/main.py"]
