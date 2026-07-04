"""Managed sections (ADR 002).

Generated content lives between HTML-comment markers. Each begin marker
records two hashes: `facts` covers the source facts that produced the
section, and `content` covers the rendered body. The bot rewrites only
inside its markers; prose outside them is never touched.
"""

import hashlib
import json
import re
from typing import Any

from pydantic import BaseModel

_BEGIN_TEMPLATE = "<!-- butter-bot:begin section={name} facts={facts} content={content} -->"
_END_TEMPLATE = "<!-- butter-bot:end section={name} -->"

_BEGIN_RE = re.compile(
    r"<!-- butter-bot:begin section=(?P<name>[\w-]+) "
    r"facts=(?P<facts>\S+) content=(?P<content>\S+) -->"
)


def digest_text(text: str) -> str:
    """Hash rendered content."""
    return "sha256:" + hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def digest_facts(facts: dict[str, Any]) -> str:
    """Hash source facts canonically, independent of dict ordering."""
    canonical = json.dumps(facts, sort_keys=True, default=str)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


class ManagedSection(BaseModel):
    """One managed section found in a document."""

    name: str
    facts_hash: str
    content_hash: str
    body: str


class UpsertResult(BaseModel):
    """Outcome of installing a section into a document."""

    text: str
    created: bool
    human_edited: bool


def parse_sections(text: str) -> list[ManagedSection]:
    """Find every managed section in a document."""
    sections: list[ManagedSection] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        match = _BEGIN_RE.search(lines[index])
        if not match:
            index += 1
            continue
        name = match.group("name")
        end_marker = _END_TEMPLATE.format(name=name)
        body_lines: list[str] = []
        index += 1
        while index < len(lines) and end_marker not in lines[index]:
            body_lines.append(lines[index])
            index += 1
        sections.append(
            ManagedSection(
                name=name,
                facts_hash=match.group("facts"),
                content_hash=match.group("content"),
                body="\n".join(body_lines).strip(),
            )
        )
        index += 1
    return sections


def render_section(name: str, body: str, facts_hash: str) -> str:
    """Render one managed section block."""
    body = body.strip()
    begin = _BEGIN_TEMPLATE.format(name=name, facts=facts_hash, content=digest_text(body))
    return f"{begin}\n{body}\n{_END_TEMPLATE.format(name=name)}"


def upsert_section(text: str, name: str, body: str, facts_hash: str) -> UpsertResult:
    """Replace a named section in place, or append it to the document.

    Sets `human_edited` when the existing body no longer matches its
    recorded content hash, so callers can warn before overwriting.
    """
    block = render_section(name, body, facts_hash)
    existing = next((s for s in parse_sections(text) if s.name == name), None)

    if existing is None:
        base = text.rstrip("\n")
        joined = f"{base}\n\n{block}\n" if base else f"{block}\n"
        return UpsertResult(text=joined, created=True, human_edited=False)

    human_edited = digest_text(existing.body) != existing.content_hash
    end_marker = _END_TEMPLATE.format(name=name)
    lines = text.splitlines()
    out: list[str] = []
    index = 0
    while index < len(lines):
        if _BEGIN_RE.search(lines[index]) and f"section={name} " in lines[index] + " ":
            match = _BEGIN_RE.search(lines[index])
            if match and match.group("name") == name:
                out.append(block)
                while index < len(lines) and end_marker not in lines[index]:
                    index += 1
                index += 1
                continue
        out.append(lines[index])
        index += 1
    new_text = "\n".join(out)
    if text.endswith("\n"):
        new_text += "\n"
    return UpsertResult(text=new_text, created=False, human_edited=human_edited)
