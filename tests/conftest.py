from pathlib import Path

import pytest

PYPROJECT = """
[project]
name = "demo-service"
description = "A demo web service"
requires-python = ">=3.11"
dependencies = ["fastapi>=0.100"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.4"]

[project.scripts]
demo-service = "demo.cli:main"
"""

MODULE = '''
"""Demo module: handles requests."""


class Handler:
    """Routes requests."""

    def handle(self, request):
        """Process one request."""
        return request


def undocumented_helper(x):
    return x
'''

DOCKERFILE = """
FROM python:3.11-slim AS base
WORKDIR /app
ENV DEMO_MODE=production
ARG BUILD_REF
EXPOSE 8000
COPY . .
CMD ["demo-service"]
"""

COMPOSE = """
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEMO_MODE=production
      - DEMO_TOKEN=secret-value
    depends_on:
      - db
  db:
    image: postgres:16
    volumes:
      - data:/var/lib/postgresql/data
volumes:
  data:
"""

SCRIPT = """#!/usr/bin/env bash
# Deploys the demo service to the target host.

deploy() {
  echo deploying
}
"""


@pytest.fixture
def fixture_repo(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "demo.py").write_text(MODULE, encoding="utf-8")
    (tmp_path / "Dockerfile").write_text(DOCKERFILE, encoding="utf-8")
    (tmp_path / "docker-compose.yml").write_text(COMPOSE, encoding="utf-8")
    (tmp_path / "deploy.sh").write_text(SCRIPT, encoding="utf-8")
    return tmp_path
