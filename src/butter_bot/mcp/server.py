"""Butter-Bot MCP server (stdio).

Exposes the style engine to a driving session. The session drafts prose;
these tools validate and deterministically fix it (see ADR 001 and ADR 005).
"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from butter_bot.adapters import detect_adapters, extract_all
from butter_bot.core import scan_repo as _scan_repo
from butter_bot.core import upsert_section
from butter_bot.generators import build_architecture_plan, build_runbook_plan
from butter_bot.style import Severity, brief_from_violations, fix_paths, lint_paths, lint_text

app = FastMCP("butter-bot")


@app.tool()
def lint_style(paths: list[str]) -> dict:
    """Lint markdown files or directories against the IBM style rules.

    Returns violations with rule id, severity, location, and whether a
    deterministic autofix exists.
    """
    violations = lint_paths([Path(p) for p in paths])
    return {
        "violations": [v.model_dump() for v in violations],
        "errors": sum(1 for v in violations if v.severity == "error"),
        "warnings": sum(1 for v in violations if v.severity == "warning"),
    }


@app.tool()
def apply_style_fixes(paths: list[str], write: bool = True) -> dict:
    """Apply deterministic IBM style fixes to markdown files.

    Rewrites files in place when `write` is true. Judgment-call violations
    that need a human or LLM rewrite come back as a drafting brief: fix
    those by editing the file, then run lint_style again to confirm.
    """
    results = fix_paths([Path(p) for p in paths], write=write)
    remaining = [v for r in results for v in r.remaining]
    return {
        "files_changed": [r.path for r in results if r.changed],
        "fixes_applied": [v.model_dump() for r in results for v in r.applied],
        "drafting_brief": [item.model_dump() for item in brief_from_violations(remaining)],
    }


@app.tool()
def scan_repo(root: str) -> dict:
    """Scan a repository: detected ecosystems and markdown inventory."""
    scan = _scan_repo(Path(root))
    return {
        "ecosystems": [adapter.ecosystem for adapter in detect_adapters(scan)],
        "markdown_files": [str(f) for f in scan.by_suffix(".md")],
        "file_count": len(scan.files),
    }


@app.tool()
def extract_facts(root: str) -> dict:
    """Run every detected language adapter and return its structured facts."""
    scan = _scan_repo(Path(root))
    return {"facts": [facts.model_dump() for facts in extract_all(scan)]}


@app.tool()
def plan_doc(root: str, doc_type: str) -> dict:
    """Plan a runbook or architecture doc from repository facts.

    Returns per-section deterministic markdown, the facts behind it, a
    facts hash for write_managed_doc, and a drafting brief where prose
    needs judgment. Improve the content per the briefs, then install
    each section with write_managed_doc.
    """
    builders = {"runbook": build_runbook_plan, "architecture": build_architecture_plan}
    if doc_type not in builders:
        return {"error": f"Unknown doc_type; choose one of {sorted(builders)}."}
    facts_list = extract_all(_scan_repo(Path(root)))
    return builders[doc_type](facts_list).model_dump()


@app.tool()
def write_managed_doc(
    root: str, doc_path: str, section: str, content: str, facts_hash: str, title: str = ""
) -> dict:
    """Install content into a managed section of a markdown document.

    Validates the content against the IBM style rules first and rejects
    it when error-severity violations exist. Creates the document with
    the given title when it does not exist. Warns when a human edited
    the previous section body.
    """
    root_path = Path(root).resolve()
    target = (root_path / doc_path).resolve()
    if not target.is_relative_to(root_path):
        return {"written": False, "error": "doc_path must stay inside root."}

    errors = [v for v in lint_text(content, doc_path) if v.severity is Severity.ERROR]
    if errors:
        return {
            "written": False,
            "error": "Content fails the IBM style rules; fix the errors and retry.",
            "violations": [v.model_dump() for v in errors],
        }

    if target.exists():
        text = target.read_text(encoding="utf-8")
    else:
        heading = title or section.replace("-", " ").capitalize()
        text = f"# {heading}\n"
    result = upsert_section(text, section, content, facts_hash)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(result.text, encoding="utf-8")
    return {
        "written": True,
        "created_section": result.created,
        "human_edit_overwritten": result.human_edited,
        "path": str(target),
    }


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
