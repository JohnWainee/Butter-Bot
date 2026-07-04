# ADR 006: Runbooks derive from repository content only

Summary: version 1 runbooks describe what the repository declares; no live
infrastructure queries and no credentials in scope.

## Status

Proposed (awaiting plan approval), 2026-07-04.

## Context

Runbooks could draw on repository files, operator knowledge, or live systems
(docker, kubectl, cloud APIs). Live queries give the most accurate picture but
put secrets and production read access inside a documentation tool.

## Options

- **Repository-derived only.** Dockerfiles, Compose, CI configs, manifests,
  scripts, READMEs. No credentials, cleanly testable.
- **Repository plus operator interview.** Adds tribal knowledge through a
  structured Q&A tool in the session.
- **Repository plus live infra queries.** Most accurate, biggest risk and
  scope jump.

## Decision

Repository-derived only for version 1. Runbooks state their provenance: every
managed section records which files produced it, so a reader knows the runbook
reflects declared state, not observed state.

## Consequences

- Version 1 handles no secrets and needs no network or cluster access.
- Runbooks can be wrong where the repository and reality diverge; provenance
  notes make that limit visible.
- The operator-interview option remains the natural version 2 enrichment and
  fits the MCP session model well.

## Open questions

- None.
