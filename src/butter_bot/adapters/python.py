"""Python adapter: stdlib ast and tomllib, no third-party parsers."""

import ast
import tomllib
from typing import Any

from butter_bot.core import RepoScan

from .base import LanguageAdapter


class PythonAdapter(LanguageAdapter):
    ecosystem = "python"

    def detect(self, scan: RepoScan) -> bool:
        return bool(scan.by_suffix(".py") or scan.by_name("pyproject.toml"))

    def read_manifests(self, scan: RepoScan) -> dict[str, Any]:
        facts: dict[str, Any] = {}
        for path in scan.by_name("pyproject.toml"):
            data = tomllib.loads(scan.read(path))
            project = data.get("project", {})
            facts[str(path)] = {
                "name": project.get("name"),
                "description": project.get("description"),
                "requires_python": project.get("requires-python"),
                "dependencies": project.get("dependencies", []),
                "optional_dependencies": project.get("optional-dependencies", {}),
                "scripts": project.get("scripts", {}),
            }
        return facts

    def parse_structure(self, scan: RepoScan) -> dict[str, Any]:
        modules: dict[str, Any] = {}
        for path in scan.by_suffix(".py"):
            try:
                tree = ast.parse(scan.read(path))
            except SyntaxError:
                continue
            doc = ast.get_docstring(tree)
            modules[str(path)] = {
                "doc": doc.splitlines()[0] if doc else None,
                "classes": [
                    {
                        "name": node.name,
                        "doc": (ast.get_docstring(node) or "").split("\n")[0] or None,
                        "methods": [
                            item.name
                            for item in node.body
                            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)
                        ],
                    }
                    for node in tree.body
                    if isinstance(node, ast.ClassDef)
                ],
                "functions": [
                    {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "doc": (ast.get_docstring(node) or "").split("\n")[0] or None,
                    }
                    for node in tree.body
                    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
                ],
            }
        return {"modules": modules}

    def harvest_docs(self, scan: RepoScan) -> dict[str, Any]:
        documented = 0
        undocumented = 0
        for module in self.parse_structure(scan)["modules"].values():
            for item in [module, *module["classes"], *module["functions"]]:
                if item.get("doc"):
                    documented += 1
                else:
                    undocumented += 1
        return {
            "convention": "docstrings",
            "documented": documented,
            "undocumented": undocumented,
        }
