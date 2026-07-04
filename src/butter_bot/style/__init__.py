"""IBM style engine: deterministic lint and fix for markdown."""

from .engine import fix_paths, fix_text, lint_paths, lint_text
from .models import DraftingBriefItem, FixResult, Severity, Violation, brief_from_violations

__all__ = [
    "DraftingBriefItem",
    "FixResult",
    "Severity",
    "Violation",
    "brief_from_violations",
    "fix_paths",
    "fix_text",
    "lint_paths",
    "lint_text",
]
