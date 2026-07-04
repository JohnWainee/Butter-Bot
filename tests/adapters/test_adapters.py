from pathlib import Path

from butter_bot.adapters import detect_adapters, extract_all
from butter_bot.core import scan_repo


def facts_by_ecosystem(fixture_repo: Path) -> dict:
    scan = scan_repo(fixture_repo)
    return {facts.ecosystem: facts for facts in extract_all(scan)}


def test_all_wave1_adapters_detected(fixture_repo: Path):
    scan = scan_repo(fixture_repo)
    ecosystems = {adapter.ecosystem for adapter in detect_adapters(scan)}
    assert ecosystems == {"python", "shell", "dockerfile", "compose"}


def test_python_manifest_facts(fixture_repo: Path):
    manifest = facts_by_ecosystem(fixture_repo)["python"].manifests["pyproject.toml"]
    assert manifest["name"] == "demo-service"
    assert manifest["scripts"] == {"demo-service": "demo.cli:main"}
    assert "dev" in manifest["optional_dependencies"]


def test_python_structure_and_docstrings(fixture_repo: Path):
    facts = facts_by_ecosystem(fixture_repo)["python"]
    module = facts.structure["modules"]["src/demo.py"]
    assert module["doc"] == "Demo module: handles requests."
    assert module["classes"][0]["name"] == "Handler"
    assert module["functions"][0]["name"] == "undocumented_helper"
    coverage = facts.doc_conventions
    assert coverage["documented"] >= 2
    assert coverage["undocumented"] >= 1


def test_dockerfile_facts(fixture_repo: Path):
    manifest = facts_by_ecosystem(fixture_repo)["dockerfile"].manifests["Dockerfile"]
    assert manifest["base_images"] == ["python:3.11-slim"]
    assert manifest["exposed_ports"] == ["8000"]
    assert manifest["env_keys"] == ["DEMO_MODE"]
    assert manifest["build_args"] == ["BUILD_REF"]
    assert manifest["workdir"] == "/app"


def test_compose_facts_record_env_keys_not_values(fixture_repo: Path):
    manifest = facts_by_ecosystem(fixture_repo)["compose"].manifests["docker-compose.yml"]
    web = manifest["services"]["web"]
    assert web["env_keys"] == ["DEMO_MODE", "DEMO_TOKEN"]
    assert "secret-value" not in str(manifest)
    assert web["depends_on"] == ["db"]
    assert manifest["services"]["db"]["image"] == "postgres:16"


def test_shell_facts(fixture_repo: Path):
    structure = facts_by_ecosystem(fixture_repo)["shell"].structure
    script = structure["scripts"]["deploy.sh"]
    assert script["header"] == "Deploys the demo service to the target host."
    assert script["functions"] == ["deploy"]
