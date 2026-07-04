"""Runbook generator: repository-derived facts only (ADR 006).

Every section states its provenance so readers know the runbook reflects
declared state, not observed state.
"""

from butter_bot.adapters import AdapterFacts
from butter_bot.core import digest_facts

from .models import DocPlan, SectionPlan


def build_runbook_plan(facts_list: list[AdapterFacts]) -> DocPlan:
    """Assemble a runbook plan from adapter facts."""
    by_ecosystem = {facts.ecosystem: facts for facts in facts_list}
    sections = [
        _build_section(by_ecosystem),
        _run_section(by_ecosystem),
        _configuration_section(by_ecosystem),
        _verification_section(by_ecosystem),
    ]
    return DocPlan(
        doc_type="runbook",
        title="Runbook",
        target_path="docs/runbook.md",
        sections=[s for s in sections if s is not None],
    )


def _provenance(paths: list[str]) -> str:
    joined = ", ".join(f"`{p}`" for p in sorted(paths))
    return f"Source files: {joined}."


def _build_section(by_ecosystem: dict[str, AdapterFacts]) -> SectionPlan | None:
    facts: dict = {}
    lines: list[str] = ["## Build", ""]
    sources: list[str] = []

    python = by_ecosystem.get("python")
    if python and python.manifests:
        for path, manifest in python.manifests.items():
            sources.append(path)
            facts[path] = manifest
            extras = ", ".join(manifest.get("optional_dependencies", {}))
            lines.append(f"Install the Python package from `{path}`:")
            lines.append("")
            lines.append("```bash")
            install = 'pip install -e ".[dev]"' if "dev" in extras else "pip install -e ."
            lines.append(install)
            lines.append("```")
            lines.append("")

    docker = by_ecosystem.get("dockerfile")
    if docker and docker.manifests:
        for path, manifest in docker.manifests.items():
            sources.append(path)
            facts[path] = manifest
            bases = ", ".join(f"`{b}`" for b in manifest["base_images"])
            lines.append(f"Build the container image from `{path}` (base: {bases}):")
            lines.append("")
            lines.append("```bash")
            lines.append(f"docker build -f {path} -t IMAGE_NAME .")
            lines.append("```")
            lines.append("")

    if not facts:
        return None
    lines.append(_provenance(sources))
    return SectionPlan(
        name="build",
        facts=facts,
        facts_hash=digest_facts(facts),
        generated="\n".join(lines),
        brief="Replace IMAGE_NAME with the image name this project publishes, if known.",
    )


def _run_section(by_ecosystem: dict[str, AdapterFacts]) -> SectionPlan | None:
    facts: dict = {}
    lines: list[str] = ["## Run", ""]
    sources: list[str] = []

    compose = by_ecosystem.get("compose")
    if compose and compose.manifests:
        for path, manifest in compose.manifests.items():
            sources.append(path)
            facts[path] = manifest
            lines.append(f"Start the service stack from `{path}`:")
            lines.append("")
            lines.append("```bash")
            lines.append(f"docker compose -f {path} up -d")
            lines.append("```")
            lines.append("")
            services = manifest["services"]
            if services:
                lines.append("| Service | Image | Ports | Depends on |")
                lines.append("| --- | --- | --- | --- |")
                for name, service in services.items():
                    image = service["image"] or ("local build" if service["build"] else "")
                    ports = ", ".join(service["ports"]) or "none"
                    depends = ", ".join(service["depends_on"]) or "none"
                    lines.append(f"| {name} | {image} | {ports} | {depends} |")
                lines.append("")

    python = by_ecosystem.get("python")
    if python and python.manifests:
        for path, manifest in python.manifests.items():
            scripts = manifest.get("scripts", {})
            if scripts:
                sources.append(path)
                facts.setdefault(path, {})["scripts"] = scripts
                lines.append("Command line entry points:")
                lines.append("")
                for name, target in scripts.items():
                    lines.append(f"- `{name}` runs `{target}`")
                lines.append("")

    dockerfiles = by_ecosystem.get("dockerfile")
    if dockerfiles and dockerfiles.manifests and not (compose and compose.manifests):
        for path, manifest in dockerfiles.manifests.items():
            command = ["docker", "run", "--rm"]
            for port in manifest["exposed_ports"]:
                bare = port.split("/")[0]
                command.extend(["-p", f"{bare}:{bare}"])
            command.append("IMAGE_NAME")
            sources.append(path)
            facts[path] = manifest
            lines.append("Run the container:")
            lines.append("")
            lines.append("```bash")
            lines.append(" ".join(command))
            lines.append("```")
            lines.append("")

    if not facts:
        return None
    lines.append(_provenance(sources))
    return SectionPlan(
        name="run",
        facts=facts,
        facts_hash=digest_facts(facts),
        generated="\n".join(lines),
        brief=(
            "Add one sentence per service describing what it does. "
            "State how to check that the stack is healthy."
        ),
    )


def _configuration_section(by_ecosystem: dict[str, AdapterFacts]) -> SectionPlan | None:
    facts: dict = {}
    sources: list[str] = []
    keys: set[str] = set()

    docker = by_ecosystem.get("dockerfile")
    if docker:
        for path, manifest in docker.manifests.items():
            if manifest["env_keys"] or manifest["build_args"]:
                sources.append(path)
                facts[path] = {
                    "env_keys": manifest["env_keys"],
                    "build_args": manifest["build_args"],
                }
                keys.update(manifest["env_keys"])

    compose = by_ecosystem.get("compose")
    if compose:
        for path, manifest in compose.manifests.items():
            for service in manifest["services"].values():
                if service["env_keys"]:
                    keys.update(service["env_keys"])
                    if path not in sources:
                        sources.append(path)
                        facts[path] = manifest

    if not keys:
        return None
    lines = [
        "## Configuration",
        "",
        "Environment variables (keys only; set values at deploy time):",
        "",
    ]
    lines.extend(f"- `{key}`" for key in sorted(keys))
    lines.append("")
    lines.append(_provenance(sources))
    return SectionPlan(
        name="configuration",
        facts=facts,
        facts_hash=digest_facts(facts),
        generated="\n".join(lines),
        brief="Describe each variable's purpose and its safe default, if one exists.",
    )


def _verification_section(by_ecosystem: dict[str, AdapterFacts]) -> SectionPlan | None:
    python = by_ecosystem.get("python")
    if not python or not python.manifests:
        return None
    facts: dict = {}
    commands: list[str] = []
    sources: list[str] = []
    for path, manifest in python.manifests.items():
        dev = manifest.get("optional_dependencies", {}).get("dev", [])
        joined = " ".join(dev)
        sources.append(path)
        facts[path] = {"dev_dependencies": dev}
        if "ruff" in joined:
            commands.append("ruff check .")
        if "pytest" in joined:
            commands.append("pytest")
    if not commands:
        return None
    lines = ["## Verify", "", "Run the project's checks after any change:", "", "```bash"]
    lines.extend(commands)
    lines.append("```")
    lines.append("")
    lines.append(_provenance(sources))
    return SectionPlan(
        name="verify",
        facts=facts,
        facts_hash=digest_facts(facts),
        generated="\n".join(lines),
        brief=None,
    )
