# Butter-Bot project plan

Status: awaiting approval. No implementation starts until you approve this plan.

Butter-Bot generates and maintains repository documentation: runbooks, architecture
and module explanation docs, and IBM style compliance. It ships as a shared Python
core with an MCP server frontend first, and a CLI and GitHub Action frontend later.

## Goals

- Generate runbooks from what a repository declares: Dockerfiles, Compose files,
  CI configs, manifests, and scripts.
- Generate architecture overviews and per-module deep dives from parsed code
  structure.
- Enforce the IBM Documentation Style Guide with a deterministic linter and an
  optional LLM autofix.
- Keep generated docs current without destroying human edits.
- Support multiple language ecosystems through one adapter interface.
- Keep marginal cost near zero in the default (MCP) mode.

## Non-goals

- No live infrastructure queries in version 1. Runbooks derive from repository
  content only (ADR 006).
- No GitHub write access in the core. Tools write to the working tree; your
  normal PR flow handles delivery (ADR 003).
- No duplicate of the adversarial reviewer. Butter-Bot explains and documents;
  the reviewer critiques.

## Decisions

Each decision has an ADR in `docs/adr/`.

| ADR | Decision |
| --- | --- |
| 001 | Shared Python core; MCP server frontend first, CLI and Action later |
| 002 | Managed sections: generated blocks live between hashed markers |
| 003 | Working-tree delivery only; no GitHub credentials in the core |
| 004 | One language-adapter interface; adapters ship in three waves |
| 005 | Style engine: deterministic lint plus opt-in LLM autofix through a drafter interface |
| 006 | Runbook sources: repository-derived facts only |

## Architecture

One Python package, `butter_bot`, mirroring the adversarial reviewer stack
(Python 3.11+, hatchling, pydantic, pyyaml, pytest).

```
src/butter_bot/
  core/        # repo scanner, managed-section engine, doc models
  adapters/    # language adapter interface + per-ecosystem adapters
  style/       # IBM style rule engine (deterministic, LLM-free)
  generators/  # runbook, architecture overview, module deep dives
  drafting/    # Drafter interface: MCP mode = caller drafts; bot mode = litellm
  mcp/         # MCP server (stdio) exposing the tool surface
```

### Key mechanism: who drafts the prose

The core never calls an LLM directly. Generators produce structured facts and a
drafting brief. In MCP mode, your Claude Code session drafts the prose from the
brief, then hands it back to a validating writer tool. In bot mode (later), a
litellm drafter fills the same interface. This keeps the default mode free of
API cost and keeps the core testable.

### MCP tool surface (version 0.1–0.2)

| Tool | Purpose |
| --- | --- |
| `scan_repo` | Detect ecosystems, manifests, and doc inventory |
| `extract_facts` | Run adapters; return structured facts for a doc type |
| `lint_style` | Run IBM style rules over markdown; return violations with locations |
| `apply_style_fixes` | Apply deterministic fixes; return judgment-call items as a drafting brief |
| `plan_doc` | Return the drafting brief for a runbook, overview, or deep dive |
| `write_managed_doc` | Validate drafted content (style lint), install it into managed sections |
| `check_drift` | Compare managed-section hashes against current facts; report stale docs |

## Implementation milestones

Each milestone lands through the standard flow: issue, branch, plan, verify,
PR, review. Conventional commits throughout.

### M0 — Scaffold (this PR plus one follow-up)

- Repo scaffolding: `pyproject.toml`, package layout, pytest, ruff.
- CI: GitHub Actions workflow running lint and tests.
- PR template and branch protection notes.

### M1 — Style engine MVP (version 0.1)

- Deterministic IBM style rules: sentence length, Latin abbreviations, serial
  comma, exclamation marks, heading case, link text, passive-voice heuristics.
- MCP server with `lint_style` and `apply_style_fixes`.
- Dogfood: lint Butter-Bot's own docs and the reviewer repo's docs in CI.

### M2 — Managed docs and first generators

- Managed-section engine with markers and content hashes.
- Wave 1 adapters: Python (stdlib `ast`), shell, Dockerfile, Compose.
- Architecture overview generator and repo-derived runbook generator.
- `scan_repo`, `extract_facts`, `plan_doc`, `write_managed_doc`.

### M3 — IaC wave and drift (version 0.2)

- Wave 2 adapters: GitHub Actions, Jenkinsfile, Kubernetes manifests, Terraform.
- `check_drift` tool; per-module deep-dive generator.

### M4 — Broad languages and unattended mode (version 0.3)

- Wave 3 adapters: TypeScript/JavaScript and Go through tree-sitter.
- CLI frontend and GitHub Action wrapper with the litellm drafter.
- Cost controls: token budget cap per run, deterministic-only mode for CI gates.

## Verification

- Unit tests per style rule and per adapter (pytest, golden files).
- Generator tests against fixture repositories.
- Dogfooding gate: CI fails if Butter-Bot's own docs fail `lint_style`.
- Manual end-to-end check per milestone: run the MCP server against both
  existing repos and inspect the output.

## Cost posture

- Default mode costs nothing beyond your Claude subscription: the session
  drafts, the core validates.
- The linter and all adapters are deterministic and free.
- The litellm bot mode is opt-in, arrives last, and ships with a budget cap.

## Open questions

- Package and distribution name: `butter-bot` on PyPI, or install from the repo
  through `uvx`? Recommendation: repo-only through `uvx` until version 0.3.
- Passive-voice detection depth: heuristic regex first, or pull in a small NLP
  dependency? Recommendation: heuristics first; measure false positives.
