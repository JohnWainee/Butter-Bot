# ADR 004: One adapter interface, three shipping waves

Summary: design a single language-adapter interface up front; ship adapters in
waves so the first release is not blocked on broad language coverage.

## Status

Proposed (awaiting plan approval), 2026-07-04.

## Context

Butter-Bot needs three capabilities per ecosystem: parse code structure,
harvest native doc conventions (docstrings, JSDoc, godoc), and detect manifests
(pyproject, package.json, go.mod, Dockerfile, CI configs). Building all target
ecosystems before the first release quadruples the pre-MVP surface.

## Options

- **Phased waves behind one interface.** Nothing is a rewrite later; a
  shippable milestone arrives weeks earlier.
- **All ecosystems at launch.** No release until Python, shell, Docker,
  Compose, YAML IaC, TypeScript/JavaScript, and Go all work.

## Decision

Phased waves. Each adapter implements:

```python
class LanguageAdapter(Protocol):
    def detect(self, repo: RepoScan) -> bool: ...
    def parse_structure(self, files: list[Path]) -> StructureFacts: ...
    def harvest_docs(self, files: list[Path]) -> DocConventionFacts: ...
    def read_manifests(self, repo: RepoScan) -> ManifestFacts: ...
```

- **Wave 1 (version 0.1–0.2):** Python (stdlib `ast`), shell, Dockerfile,
  Compose.
- **Wave 2 (version 0.2):** GitHub Actions, Jenkinsfile, Kubernetes manifests,
  Terraform.
- **Wave 3 (version 0.3):** TypeScript/JavaScript and Go through tree-sitter.

## Consequences

- The first demo runs on the owner's two existing Python repos immediately.
- Tree-sitter (a heavier dependency) stays out of the install until wave 3.
- The adapter protocol must be validated against wave 3 needs during design,
  before wave 1 code is written.

## Open questions

- Whether wave 3 should move all parsers to tree-sitter for uniformity, or
  keep stdlib `ast` for Python. Recommendation: keep `ast`; revisit if adapter
  divergence hurts.
