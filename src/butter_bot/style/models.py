"""Data models for the IBM style engine."""

from enum import StrEnum

from pydantic import BaseModel


class Severity(StrEnum):
    """Violation severity. Errors gate CI; warnings inform."""

    ERROR = "error"
    WARNING = "warning"


class Violation(BaseModel):
    """One style-rule violation at a location in a markdown document."""

    rule_id: str
    severity: Severity
    message: str
    path: str | None = None
    line: int
    column: int
    excerpt: str
    autofixable: bool = False


class FixResult(BaseModel):
    """Outcome of applying deterministic fixes to one document."""

    path: str | None = None
    text: str
    applied: list[Violation]
    remaining: list[Violation]

    @property
    def changed(self) -> bool:
        return bool(self.applied)


class DraftingBriefItem(BaseModel):
    """One judgment-call violation, phrased as an instruction for a drafter."""

    rule_id: str
    path: str | None = None
    line: int
    excerpt: str
    instruction: str


def brief_from_violations(violations: list[Violation]) -> list[DraftingBriefItem]:
    """Convert non-autofixable violations into drafter instructions."""
    instructions = {
        "sentence-length": (
            "Split this sentence so each sentence carries one idea in 20 words or fewer."
        ),
        "passive-voice": "Rewrite in active voice: name who or what performs the action.",
        "heading-case": (
            "Rewrite the heading in sentence case; keep proper nouns and acronyms capitalized."
        ),
        "serial-comma": "Add the serial comma before the final conjunction if this is a list.",
        "latin-abbreviation": "Replace the Latin abbreviation with plain English.",
        "link-text": "Rewrite the link text to describe the destination.",
    }
    return [
        DraftingBriefItem(
            rule_id=v.rule_id,
            path=v.path,
            line=v.line,
            excerpt=v.excerpt,
            instruction=instructions.get(v.rule_id, v.message),
        )
        for v in violations
        if not v.autofixable
    ]
