"""Architecture overview generator: modules, entry points, doc coverage."""

from butter_bot.adapters import AdapterFacts
from butter_bot.core import digest_facts

from .models import DocPlan, SectionPlan


def build_architecture_plan(facts_list: list[AdapterFacts]) -> DocPlan:
    """Assemble an architecture overview plan from adapter facts."""
    by_ecosystem = {facts.ecosystem: facts for facts in facts_list}
    sections = [
        _modules_section(by_ecosystem),
        _entry_points_section(by_ecosystem),
        _doc_coverage_section(facts_list),
    ]
    return DocPlan(
        doc_type="architecture",
        title="Architecture",
        target_path="docs/architecture.md",
        sections=[s for s in sections if s is not None],
    )


def _modules_section(by_ecosystem: dict[str, AdapterFacts]) -> SectionPlan | None:
    python = by_ecosystem.get("python")
    if not python:
        return None
    modules = python.structure.get("modules", {})
    if not modules:
        return None
    facts = {"modules": {path: module["doc"] for path, module in modules.items()}}
    lines = ["## Modules", "", "| Module | Summary |", "| --- | --- |"]
    for path, module in sorted(modules.items()):
        summary = module["doc"] or "(no docstring)"
        lines.append(f"| `{path}` | {summary} |")
    lines.append("")
    return SectionPlan(
        name="modules",
        facts=facts,
        facts_hash=digest_facts(facts),
        generated="\n".join(lines),
        brief=(
            "Add a short data-flow paragraph above the table: "
            "name the entry point and describe how data moves between modules."
        ),
    )


def _entry_points_section(by_ecosystem: dict[str, AdapterFacts]) -> SectionPlan | None:
    python = by_ecosystem.get("python")
    if not python:
        return None
    scripts: dict[str, str] = {}
    for manifest in python.manifests.values():
        scripts.update(manifest.get("scripts", {}))
    if not scripts:
        return None
    facts = {"scripts": scripts}
    lines = ["## Entry points", ""]
    lines.extend(f"- `{name}` runs `{target}`" for name, target in sorted(scripts.items()))
    lines.append("")
    return SectionPlan(
        name="entry-points",
        facts=facts,
        facts_hash=digest_facts(facts),
        generated="\n".join(lines),
        brief=None,
    )


def _doc_coverage_section(facts_list: list[AdapterFacts]) -> SectionPlan | None:
    rows: list[tuple[str, str, int, int]] = []
    for facts in facts_list:
        conventions = facts.doc_conventions
        if "documented" in conventions:
            rows.append(
                (
                    facts.ecosystem,
                    conventions.get("convention", ""),
                    conventions["documented"],
                    conventions["undocumented"],
                )
            )
    if not rows:
        return None
    facts_dict = {eco: {"documented": d, "undocumented": u} for eco, _, d, u in rows}
    lines = [
        "## Documentation coverage",
        "",
        "| Ecosystem | Convention | Documented | Undocumented |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(f"| {eco} | {conv} | {d} | {u} |" for eco, conv, d, u in rows)
    lines.append("")
    return SectionPlan(
        name="doc-coverage",
        facts=facts_dict,
        facts_hash=digest_facts(facts_dict),
        generated="\n".join(lines),
        brief=None,
    )
