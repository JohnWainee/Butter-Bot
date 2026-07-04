"""Core building blocks: repo scanning and managed sections."""

from .managed import (
    ManagedSection,
    UpsertResult,
    digest_facts,
    digest_text,
    parse_sections,
    render_section,
    upsert_section,
)
from .scan import RepoScan, scan_repo

__all__ = [
    "ManagedSection",
    "RepoScan",
    "UpsertResult",
    "digest_facts",
    "digest_text",
    "parse_sections",
    "render_section",
    "scan_repo",
    "upsert_section",
]
