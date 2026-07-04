# ADR 003: Working-tree delivery only

Summary: tools write files to the checked-out repository; the calling session
or CI job owns branch, commit, and PR. The core holds no GitHub credentials.

## Status

Proposed (awaiting plan approval), 2026-07-04.

## Context

Generated docs must land in repositories through the owner's audit-shop flow:
branch protection, conventional commits, PR review. Putting GitHub write access
in the core means building and securing token handling in phase 1.

## Options

- **Working tree only.** Core stays GitHub-free; the session or the Action
  wrapper handles git. Smallest security surface.
- **Bot opens PRs itself.** Unattended-friendly from day one, but credentials,
  scopes, and failure modes enter the core immediately.
- **Direct commit to the default branch.** Bypasses the PR discipline in the
  working agreement. Rejected outright.

## Decision

Working tree only. The GitHub Action wrapper (milestone M4) adds PR-opening at
the frontend layer, where CI already holds a scoped token.

## Consequences

- The core is testable against plain directories, no network needed.
- Every doc change passes through normal PR review.
- Unattended PR creation waits until M4; that is an accepted delay.

## Open questions

- None.
