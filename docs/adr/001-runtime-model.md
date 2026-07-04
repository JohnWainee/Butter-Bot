# ADR 001: Shared core with MCP-first frontends

Summary: build one Python core with all logic; ship an MCP server frontend
first, and add a CLI and GitHub Action frontend later.

## Status

Proposed (awaiting plan approval), 2026-07-04.

## Context

Butter-Bot must work interactively today and unattended in CI later. The
biggest fork is who calls the LLM. An MCP server lets a Claude Code session
drive the tools, so drafting rides on the existing subscription. A standalone
bot calls an API through litellm and pays per token, but runs without a human.
The owner is cost-sensitive and already runs a litellm-based Python stack in
the adversarial reviewer.

## Options

- **Shared core, MCP first.** One package; frontends are thin. Cheap now,
  unattended later. Slightly more up-front interface design.
- **MCP server only.** Simplest, but nothing runs without a session attached.
- **Standalone bot only.** Unattended from day one, but every doc costs tokens
  and interactive quality steering is lost.

## Decision

Shared core, MCP first. The core exposes a `Drafter` interface: in MCP mode the
calling session drafts prose from a structured brief; in bot mode a litellm
drafter fills the same interface.

## Consequences

- Default mode has near-zero marginal cost.
- The core stays LLM-free and fully unit-testable.
- The CLI and Action frontends (milestone M4) reuse the core unchanged.
- The drafting brief format becomes a stable internal contract early.

## Open questions

- None.
