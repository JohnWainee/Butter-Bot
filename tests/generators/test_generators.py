from pathlib import Path

from butter_bot.adapters import extract_all
from butter_bot.core import scan_repo
from butter_bot.generators import build_architecture_plan, build_runbook_plan


def plans(fixture_repo: Path):
    facts = extract_all(scan_repo(fixture_repo))
    return build_runbook_plan(facts), build_architecture_plan(facts)


def test_runbook_sections_present(fixture_repo: Path):
    runbook, _ = plans(fixture_repo)
    names = [s.name for s in runbook.sections]
    assert names == ["build", "run", "configuration", "verify"]


def test_runbook_build_section_content(fixture_repo: Path):
    runbook, _ = plans(fixture_repo)
    build = next(s for s in runbook.sections if s.name == "build")
    assert 'pip install -e ".[dev]"' in build.generated
    assert "docker build" in build.generated
    assert "Source files:" in build.generated


def test_runbook_configuration_lists_keys_only(fixture_repo: Path):
    runbook, _ = plans(fixture_repo)
    config = next(s for s in runbook.sections if s.name == "configuration")
    assert "`DEMO_TOKEN`" in config.generated
    assert "secret-value" not in config.generated


def test_runbook_facts_hash_is_stable(fixture_repo: Path):
    first, _ = plans(fixture_repo)
    second, _ = plans(fixture_repo)
    assert [s.facts_hash for s in first.sections] == [s.facts_hash for s in second.sections]


def test_architecture_sections(fixture_repo: Path):
    _, architecture = plans(fixture_repo)
    names = [s.name for s in architecture.sections]
    assert names == ["modules", "entry-points", "doc-coverage"]
    modules = architecture.sections[0]
    assert "`src/demo.py`" in modules.generated
    assert "Demo module: handles requests." in modules.generated
