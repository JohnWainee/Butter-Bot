# ADR 002: Managed sections for doc updates

Summary: generated content lives between HTML-comment markers with a content
hash; the bot rewrites only inside its markers and never touches human prose.

## Status

Proposed (awaiting plan approval), 2026-07-04.

## Context

Butter-Bot updates docs that humans also edit. The update contract decides the
core data model and is painful to change later. Lost human edits destroy trust
in the tool immediately.

## Options

- **Managed sections.** Markers plus a hash of the source facts. Deterministic,
  diffable, and safe for mixed human and generated content.
- **Full regeneration.** Docs are bot-owned; humans edit sources instead.
  Simple, but any manual fix gets clobbered.
- **LLM-aware merge.** Regenerate while preserving human edits by judgment.
  Flexible, unpredictable, and every update costs tokens.

## Decision

Managed sections. Format:

```markdown
<!-- butter-bot:begin section=deploy hash=sha256:... -->
...generated content...
<!-- butter-bot:end section=deploy -->
```

The hash covers the source facts, not the rendered prose. `check_drift`
compares stored hashes against freshly extracted facts to find stale sections.

## Consequences

- Human edits outside markers are never at risk.
- Drift detection is a cheap hash comparison, no LLM needed.
- Edits made inside a managed section are overwritten on regeneration; the
  markers state this explicitly.
- Every generator must emit section-shaped output, which constrains templates.

## Open questions

- Whether to warn when a human edited inside a managed block (detectable by
  hashing the rendered content too). Recommendation: yes, warn before
  overwriting.
