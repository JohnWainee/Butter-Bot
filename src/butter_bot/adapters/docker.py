"""Docker adapters: Dockerfile instructions and Compose service topology.

Environment variables are recorded by key only; values never enter the
facts, so secrets cannot leak into generated docs.
"""

import re
from typing import Any

import yaml

from butter_bot.core import RepoScan

from .base import LanguageAdapter

_INSTRUCTION = re.compile(r"^\s*(FROM|EXPOSE|ENV|ARG|CMD|ENTRYPOINT|WORKDIR|USER)\s+(.*)$")


class DockerfileAdapter(LanguageAdapter):
    ecosystem = "dockerfile"

    def detect(self, scan: RepoScan) -> bool:
        return bool(self._files(scan))

    def read_manifests(self, scan: RepoScan) -> dict[str, Any]:
        facts: dict[str, Any] = {}
        for path in self._files(scan):
            parsed: dict[str, Any] = {
                "base_images": [],
                "exposed_ports": [],
                "env_keys": [],
                "build_args": [],
                "workdir": None,
                "user": None,
                "command": None,
                "entrypoint": None,
            }
            for line in scan.read(path).splitlines():
                match = _INSTRUCTION.match(line)
                if not match:
                    continue
                keyword, rest = match.group(1), match.group(2).strip()
                if keyword == "FROM":
                    parsed["base_images"].append(rest.split(" AS ")[0].split(" as ")[0].strip())
                elif keyword == "EXPOSE":
                    parsed["exposed_ports"].extend(rest.split())
                elif keyword in ("ENV", "ARG"):
                    key = rest.split("=")[0].split()[0]
                    target = "env_keys" if keyword == "ENV" else "build_args"
                    parsed[target].append(key)
                elif keyword == "WORKDIR":
                    parsed["workdir"] = rest
                elif keyword == "USER":
                    parsed["user"] = rest
                elif keyword == "CMD":
                    parsed["command"] = rest
                elif keyword == "ENTRYPOINT":
                    parsed["entrypoint"] = rest
            facts[str(path)] = parsed
        return facts

    def parse_structure(self, scan: RepoScan) -> dict[str, Any]:
        return {"dockerfiles": [str(p) for p in self._files(scan)]}

    def harvest_docs(self, scan: RepoScan) -> dict[str, Any]:
        return {"convention": "inline comments"}

    @staticmethod
    def _files(scan: RepoScan) -> list:
        return [
            f
            for f in scan.files
            if f.name.startswith("Dockerfile") or f.suffix == ".dockerfile"
        ]


class ComposeAdapter(LanguageAdapter):
    ecosystem = "compose"

    def detect(self, scan: RepoScan) -> bool:
        return bool(self._files(scan))

    def read_manifests(self, scan: RepoScan) -> dict[str, Any]:
        facts: dict[str, Any] = {}
        for path in self._files(scan):
            data = yaml.safe_load(scan.read(path)) or {}
            services: dict[str, Any] = {}
            for name, service in (data.get("services") or {}).items():
                service = service or {}
                services[name] = {
                    "image": service.get("image"),
                    "build": service.get("build") is not None,
                    "ports": [str(p) for p in service.get("ports", [])],
                    "env_keys": self._env_keys(service.get("environment")),
                    "depends_on": list(service.get("depends_on") or []),
                    "volumes": [str(v) for v in service.get("volumes", [])],
                }
            facts[str(path)] = {"services": services}
        return facts

    def parse_structure(self, scan: RepoScan) -> dict[str, Any]:
        return {"compose_files": [str(p) for p in self._files(scan)]}

    def harvest_docs(self, scan: RepoScan) -> dict[str, Any]:
        return {"convention": "inline comments"}

    @staticmethod
    def _env_keys(environment: Any) -> list[str]:
        if isinstance(environment, dict):
            return sorted(environment)
        if isinstance(environment, list):
            return sorted(str(item).split("=")[0] for item in environment)
        return []

    @staticmethod
    def _files(scan: RepoScan) -> list:
        names = {"docker-compose", "compose"}
        return [
            f
            for f in scan.files
            if f.suffix in (".yml", ".yaml") and f.stem.split(".")[0] in names
        ]
