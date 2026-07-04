"""Adapter registry: wave-1 ecosystems (ADR 004)."""

from butter_bot.core import RepoScan

from .base import AdapterFacts, LanguageAdapter
from .docker import ComposeAdapter, DockerfileAdapter
from .python import PythonAdapter
from .shell import ShellAdapter

ADAPTERS: list[LanguageAdapter] = [
    PythonAdapter(),
    ShellAdapter(),
    DockerfileAdapter(),
    ComposeAdapter(),
]


def detect_adapters(scan: RepoScan) -> list[LanguageAdapter]:
    """Return the adapters whose ecosystem is present in the repository."""
    return [adapter for adapter in ADAPTERS if adapter.detect(scan)]


def extract_all(scan: RepoScan) -> list[AdapterFacts]:
    """Run every detected adapter and return its facts."""
    return [adapter.extract(scan) for adapter in detect_adapters(scan)]


__all__ = [
    "ADAPTERS",
    "AdapterFacts",
    "LanguageAdapter",
    "detect_adapters",
    "extract_all",
]
