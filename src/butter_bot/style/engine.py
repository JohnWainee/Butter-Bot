"""Lint and fix orchestration for the IBM style engine."""

from pathlib import Path

from .markdown import segment
from .models import FixResult, Violation
from .rules import fix_exclamation, fix_latin, run_rules


def lint_text(text: str, path: str | None = None) -> list[Violation]:
    """Lint one markdown document and return its violations."""
    return run_rules(segment(text), path)


def fix_text(text: str, path: str | None = None) -> FixResult:
    """Apply deterministic fixes to one document.

    Fixes apply only to prose, heading, and table lines; fenced code is
    untouched. Judgment-call violations are returned in `remaining`.
    """
    before = lint_text(text, path)
    applied = [v for v in before if v.autofixable]

    fixed_lines: list[str] = []
    for line in segment(text):
        if line.kind == "skip":
            fixed_lines.append(line.raw)
            continue
        fixed_lines.append(fix_exclamation(fix_latin(line.raw)))
    new_text = "\n".join(fixed_lines)
    if text.endswith("\n"):
        new_text += "\n"

    remaining = lint_text(new_text, path)
    return FixResult(path=path, text=new_text, applied=applied, remaining=remaining)


def lint_paths(paths: list[Path]) -> list[Violation]:
    """Lint every markdown file under the given files and directories."""
    violations: list[Violation] = []
    for file in _markdown_files(paths):
        violations.extend(lint_text(file.read_text(encoding="utf-8"), str(file)))
    return violations


def fix_paths(paths: list[Path], write: bool = True) -> list[FixResult]:
    """Fix every markdown file under the given files and directories."""
    results: list[FixResult] = []
    for file in _markdown_files(paths):
        result = fix_text(file.read_text(encoding="utf-8"), str(file))
        if write and result.changed:
            file.write_text(result.text, encoding="utf-8")
        results.append(result)
    return results


def _markdown_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        else:
            files.append(path)
    return files
