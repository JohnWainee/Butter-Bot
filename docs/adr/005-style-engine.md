# ADR 005: Deterministic style lint with opt-in LLM autofix

Summary: a deterministic rule engine enforces the mechanical IBM style rules
for free; an LLM drafter handles judgment calls, opt-in per run.

## Status

Proposed (awaiting plan approval), 2026-07-04.

## Context

The IBM Documentation Style Guide splits into rules a machine can check
(sentence length, Latin abbreviations, serial comma, exclamation marks,
heading case, link text) and rules that need judgment (active voice, one idea
per sentence, simple word choice). CI gates need determinism; rewrites need
judgment.

## Options

- **Lint plus LLM autofix.** Deterministic core, judgment layered on top.
- **Deterministic linter only.** Zero token cost, but catches roughly half the
  guide.
- **LLM-first rewrite.** Best coverage, highest cost, non-deterministic in CI.

## Decision

Lint plus LLM autofix. The rule engine is LLM-free and CI-gateable. Rules that
need judgment emit a drafting brief; the `Drafter` (ADR 001) proposes fixes,
and the deterministic linter re-validates the result before it is written.

Rule model: each rule carries an id, severity, location, message, and an
`autofixable` flag. Deterministic fixes (serial comma, Latin abbreviation
replacement) apply directly; the rest go to the brief.

## Consequences

- CI can gate on the linter with zero API cost.
- LLM output is never trusted blind: the linter re-checks every rewrite.
- Passive-voice detection starts as heuristics and will produce false
  positives; severity for it starts at `warning`, not `error`.

## Open questions

- Resolved 2026-07-04: build the engine in Python rather than adopt Vale.
  The engine must emit drafting briefs for the `Drafter` interface and run
  as a library inside the MCP server. Vale would add a Go binary to CI and
  a second rule toolchain for little coverage gain at this size. Revisit if
  the rule count grows past what a small module maintains well.
