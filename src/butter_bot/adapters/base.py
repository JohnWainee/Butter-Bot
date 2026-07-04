"""Language-adapter interface (ADR 004).

Every adapter answers three questions about a repository: what structure
the code declares, what native documentation it carries, and what its
manifests say about how to build and run it.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from butter_bot.core import RepoScan


class AdapterFacts(BaseModel):
    """Everything one adapter extracted from a repository."""

    ecosystem: str
    manifests: dict[str, Any]
    structure: dict[str, Any]
    doc_conventions: dict[str, Any]


class LanguageAdapter(ABC):
    """Base class for ecosystem adapters."""

    ecosystem: str

    @abstractmethod
    def detect(self, scan: RepoScan) -> bool:
        """Return whether this ecosystem is present in the repository."""

    @abstractmethod
    def read_manifests(self, scan: RepoScan) -> dict[str, Any]:
        """Extract build and run facts from manifests."""

    @abstractmethod
    def parse_structure(self, scan: RepoScan) -> dict[str, Any]:
        """Extract code structure: modules, functions, services."""

    @abstractmethod
    def harvest_docs(self, scan: RepoScan) -> dict[str, Any]:
        """Extract native documentation and coverage statistics."""

    def extract(self, scan: RepoScan) -> AdapterFacts:
        return AdapterFacts(
            ecosystem=self.ecosystem,
            manifests=self.read_manifests(scan),
            structure=self.parse_structure(scan),
            doc_conventions=self.harvest_docs(scan),
        )
