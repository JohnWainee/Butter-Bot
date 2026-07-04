"""Butter-Bot MCP server (stdio).

Exposes the style engine to a driving session. The session drafts prose;
these tools validate and deterministically fix it (see ADR 001 and ADR 005).
"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from butter_bot.style import brief_from_violations, fix_paths, lint_paths

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


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
