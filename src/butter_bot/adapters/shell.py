"""Shell adapter: header comments and function definitions from scripts."""

import re
from typing import Any

from butter_bot.core import RepoScan

from .base import LanguageAdapter

_FUNCTION = re.compile(r"^\s*(?:function\s+)?([A-Za-z_]\w*)\s*\(\)\s*\{", re.MULTILINE)


class ShellAdapter(LanguageAdapter):
    ecosystem = "shell"

    def detect(self, scan: RepoScan) -> bool:
        return bool(scan.by_suffix(".sh"))

    def read_manifests(self, scan: RepoScan) -> dict[str, Any]:
        return {}

    def parse_structure(self, scan: RepoScan) -> dict[str, Any]:
        scripts: dict[str, Any] = {}
        for path in scan.by_suffix(".sh"):
            text = scan.read(path)
            scripts[str(path)] = {
                "header": self._header(text),
                "functions": _FUNCTION.findall(text),
            }
        return {"scripts": scripts}

    def harvest_docs(self, scan: RepoScan) -> dict[str, Any]:
        scripts = self.parse_structure(scan)["scripts"]
        documented = sum(1 for s in scripts.values() if s["header"])
        return {
            "convention": "header comments",
            "documented": documented,
            "undocumented": len(scripts) - documented,
        }

    @staticmethod
    def _header(text: str) -> str | None:
        lines: list[str] = []
        for line in text.splitlines():
            if line.startswith("#!"):
                continue
            if line.startswith("#"):
                lines.append(line.lstrip("# ").strip())
                continue
            break
        header = " ".join(part for part in lines if part)
        return header or None
