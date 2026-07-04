"""IBM style rules.

Each rule inspects segmented markdown and yields violations. Rules marked
autofixable also know how to rewrite the offending span deterministically.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass

from .markdown import Line, Sentence, sentences
from .models import Severity, Violation

MAX_SENTENCE_WORDS = 20


@dataclass
class Replacement:
    """A deterministic textual fix for one regex pattern."""

    pattern: re.Pattern
    replacement: str


# --- latin abbreviations -----------------------------------------------------

_LATIN_FIXABLE = [
    Replacement(re.compile(r"\be\.g\.,?", re.IGNORECASE), "for example,"),
    Replacement(re.compile(r"\bi\.e\.,?", re.IGNORECASE), "that is,"),
    Replacement(re.compile(r"\bvs\.", re.IGNORECASE), "versus"),
]
_LATIN_FLAG_ONLY = [
    re.compile(r"\betc\.", re.IGNORECASE),
    re.compile(r"\bet al\.", re.IGNORECASE),
]


def check_latin(line: Line, path: str | None) -> Iterator[Violation]:
    for item in _LATIN_FIXABLE:
        for m in item.pattern.finditer(line.text):
            yield Violation(
                rule_id="latin-abbreviation",
                severity=Severity.ERROR,
                message=f'Replace "{m.group(0)}" with "{item.replacement.rstrip(",")}".',
                path=path,
                line=line.number,
                column=m.start() + 1,
                excerpt=m.group(0),
                autofixable=True,
            )
    for pattern in _LATIN_FLAG_ONLY:
        for m in pattern.finditer(line.text):
            yield Violation(
                rule_id="latin-abbreviation",
                severity=Severity.ERROR,
                message=f'Remove "{m.group(0)}" or replace it with plain English.',
                path=path,
                line=line.number,
                column=m.start() + 1,
                excerpt=m.group(0),
                autofixable=False,
            )


def fix_latin(text: str) -> str:
    for item in _LATIN_FIXABLE:
        text = item.pattern.sub(item.replacement, text)
    return text


# --- exclamation marks -------------------------------------------------------

_EXCLAMATION = re.compile(r"(?<!\!)\!(?!\[)")


def check_exclamation(line: Line, path: str | None) -> Iterator[Violation]:
    for m in _EXCLAMATION.finditer(line.text):
        yield Violation(
            rule_id="exclamation",
            severity=Severity.ERROR,
            message="Do not use exclamation marks in technical writing.",
            path=path,
            line=line.number,
            column=m.start() + 1,
            excerpt=line.text[max(0, m.start() - 20) : m.start() + 1].strip(),
            autofixable=True,
        )


def fix_exclamation(text: str) -> str:
    return _EXCLAMATION.sub(".", text)


# --- serial comma ------------------------------------------------------------

_SERIAL_COMMA = re.compile(r",\s+([A-Za-z][\w'\-]*)\s+(and|or)\s+")


def check_serial_comma(line: Line, path: str | None) -> Iterator[Violation]:
    for m in _SERIAL_COMMA.finditer(line.text):
        yield Violation(
            rule_id="serial-comma",
            severity=Severity.WARNING,
            message=f'Possible missing serial comma before "{m.group(2)}".',
            path=path,
            line=line.number,
            column=m.start() + 1,
            excerpt=m.group(0).strip(),
            autofixable=False,
        )


# --- link text ---------------------------------------------------------------

_BAD_LINK_TEXT = re.compile(
    r"\[(click here|here|this|this link|link|read more|more)\]", re.IGNORECASE
)


def check_link_text(line: Line, path: str | None) -> Iterator[Violation]:
    for m in _BAD_LINK_TEXT.finditer(line.text):
        yield Violation(
            rule_id="link-text",
            severity=Severity.ERROR,
            message="Use descriptive link text that names the destination.",
            path=path,
            line=line.number,
            column=m.start() + 1,
            excerpt=m.group(0),
            autofixable=False,
        )


# --- heading case ------------------------------------------------------------

_SMALL_WORDS = {"I", "API", "APIs", "CI", "CLI", "PR", "PRs", "IBM", "MCP", "ADR", "ADRs"}


def check_heading_case(line: Line, path: str | None) -> Iterator[Violation]:
    if line.kind != "heading":
        return
    words = line.text.lstrip("# ").split()
    for previous, word in zip(words, words[1:], strict=False):
        bare = word.strip(",:;()`\"'")
        if not bare or bare in _SMALL_WORDS or bare.isupper():
            continue
        # Sentence case allows a capital after a colon or a dash.
        if previous.endswith(":") or previous in {"—", "-", "–"} or previous.endswith("—"):
            continue
        if bare[0].isupper() and bare[1:].islower():
            yield Violation(
                rule_id="heading-case",
                severity=Severity.WARNING,
                message=(
                    "Use sentence case in headings; "
                    "capitalize only the first word and proper nouns."
                ),
                path=path,
                line=line.number,
                column=line.text.find(word) + 1,
                excerpt=line.text.strip(),
                autofixable=False,
            )
            return


# --- passive voice (heuristic) -----------------------------------------------

_IRREGULAR_PARTICIPLES = (
    "written|given|taken|done|made|seen|known|shown|held|kept|built|sent|found|"
    "left|put|set|run|chosen|driven|drawn|thrown|brought|bought|caught|taught"
)
_PASSIVE = re.compile(
    rf"\b(is|are|was|were|be|been|being)\s+(\w+ed|{_IRREGULAR_PARTICIPLES})\b",
    re.IGNORECASE,
)


def check_passive(line: Line, path: str | None) -> Iterator[Violation]:
    for m in _PASSIVE.finditer(line.text):
        yield Violation(
            rule_id="passive-voice",
            severity=Severity.WARNING,
            message=f'Possible passive voice: "{m.group(0)}". Prefer active voice.',
            path=path,
            line=line.number,
            column=m.start() + 1,
            excerpt=m.group(0),
            autofixable=False,
        )


# --- sentence length ---------------------------------------------------------


def check_sentence_length(sentence: Sentence, path: str | None) -> Iterator[Violation]:
    count = len(sentence.text.split())
    if count > MAX_SENTENCE_WORDS:
        yield Violation(
            rule_id="sentence-length",
            severity=Severity.WARNING,
            message=f"Sentence has {count} words; prefer {MAX_SENTENCE_WORDS} or fewer.",
            path=path,
            line=sentence.line,
            column=1,
            excerpt=sentence.text[:80],
            autofixable=False,
        )


# --- registry ----------------------------------------------------------------

LINE_RULES = {
    "prose": [check_latin, check_exclamation, check_serial_comma, check_link_text, check_passive],
    "heading": [check_latin, check_heading_case],
    "table": [check_latin, check_exclamation],
    "skip": [],
}


def run_rules(lines: list[Line], path: str | None) -> list[Violation]:
    """Run every rule over segmented lines and return sorted violations."""
    violations: list[Violation] = []
    for line in lines:
        for rule in LINE_RULES[line.kind]:
            violations.extend(rule(line, path))
    for sentence in sentences(lines):
        violations.extend(check_sentence_length(sentence, path))
    violations.sort(key=lambda v: (v.line, v.column, v.rule_id))
    return violations
