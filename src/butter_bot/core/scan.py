"""Repository scanning: the shared input for adapters and generators."""

from dataclasses import dataclass, field
from pathlib import Path

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "dist",
    "build",
}


@dataclass
class RepoScan:
    """A snapshot of a repository's files, relative to its root."""

    root: Path
    files: list[Path] = field(default_factory=list)

    def by_suffix(self, suffix: str) -> list[Path]:
        return [f for f in self.files if f.suffix == suffix]

    def by_name(self, prefix: str) -> list[Path]:
        return [f for f in self.files if f.name.startswith(prefix)]

    def read(self, relative: Path) -> str:
        return (self.root / relative).read_text(encoding="utf-8")


def scan_repo(root: Path) -> RepoScan:
    """Walk a repository and collect files, skipping junk directories."""
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        files.append(relative)
    return RepoScan(root=root, files=files)
