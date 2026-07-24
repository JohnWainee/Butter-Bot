# Agent 1 handoff — A11 remediation after the Agent 2 review

**Audience:** Agent 1, author of candidate amendment A11
**Prepared by:** Agent 2, 2026-07-24
**Companion document:** `docs/review/A11-agent2-review.md` (the full review; finding IDs below refer to it)
**Starting point:** this file lands on `main` when PR #5 merges; begin work from a fresh branch off `main`

---

## 1. Status snapshot

- **Review decision:** Accept with required remediation for a non-CUI Phase 1 pilot. The amendment's core shape survived: sovereign vaults, pinned pull-based federation, PR-shaped skill lifecycle, Backstage-spec-without-runtime. Do not redesign those.
- **What did not survive:** the amendment's account of this repository, the stack claim, and the gap between its authority principles and three mechanisms (gated proxy, signing chain, eval ownership).
- **Your task:** produce A11 revision 2 with every finding dispositioned, plus a small set of changes in this repository. The full remediation register with gate assignments is §7 of the review.

### Repository ground truth — verified 2026-07-24, do not rediscover

| Fact | Detail |
|---|---|
| Identity | This repo is Butter-Bot, a Python 3.11 documentation generator. No file contains "Kūkulu", "Koʻa", "waihona", "vault-template", or "koa-skills". |
| ADRs | All six exist in `docs/adr/`; every one is status "Proposed (awaiting plan approval)". None is a standing decision. |
| Managed sections | Implemented and tested in `src/butter_bot/core/managed.py` with a **dual-hash** marker (`facts=` and `content=`). ADR-002's text still shows the older single-hash format. |
| MCP server | `src/butter_bot/mcp/server.py` exposes 6 tools. `check_drift` (the 7th planned tool) and the `Drafter` interface are unbuilt. Adapters are Wave 1 only. |
| CI | `.github/workflows/ci.yml`: `ruff check .`, `pytest --cov=butter_bot`, then `python -m butter_bot.style README.md docs`. Style **errors** gate; warnings do not. |

---

## 2. Work queue, in order

### 2.1 A11 document edits that block G1

| ID | Section | Required change |
|---|---|---|
| F1 | §3.1, §6 | Describe the repository as it is (table above), not as an "existing Kūkulu engine". Cite ADRs 001–006 as proposed, or ratify them first (§2.3). Add `check_drift` and the Drafter interface to Phase 1 scope explicitly. |
| F2 | §1 (Q4), §4.4, §6 | Resolve the stack contradiction: either the approved stack admits Python for the Kūkulu plane, or the engine is rewritten, or the "first conforming instance" claim is dropped. State which. Also reconcile the K2-005 CI claim with the actual workflow. |
| A1 | §4.4 | Invert the indexer: vaults publish their descriptor through the Result Release Gate; the indexer reads only published artifacts and holds no repository credentials. |
| A2 | §5.2 | Redefine `refugia/` as a pinned-refs manifest (skill id → tag/digest), not content copies. |
| A3 | §9 Phase 1 | Replace the frontmatter schema "freeze" with a `schema_version` field and a stated compatibility rule. |

### 2.2 A11 document edits that block G2

| ID | Section | Required change |
|---|---|---|
| S1 | §5.3–§5.4 | Promotion requires gate-owned eval suites held outside the skill directory and outside any agent-writable path. The in-package `evals/evals.json` is a floor, never the gate. |
| S2 | §5.5 | Root key never enters Vault; Vault holds short-lived intermediates only. Name the signer. Bind the human promotion approval cryptographically to the signature (signed attestation referencing the approved merge commit). |
| S3 | §5.5 | Add a signed revocation/advisory manifest distributed through the bundle channel, checked at install and periodically at load. Required before any Phase 3 signing goes live. |
| S4 | §5.2, §5.5 | Mark `scripts/link-skills.sh` dev-profile only, with symlinked skills visibly unsigned, impossible in production installs. Put the `.claude-plugin` manifest inside the signature envelope. |
| S5 | §5.4, §5.6, §7 | Capture rejected proxy pushes as evidence (suppression audit). Put the proxy pipeline configuration under skill-grade change control. Reword the proxy as pre-screening under delegated, audited authority. |
| S6 | §4.3 | Spell out bundle verification order: unbundle into quarantine, `git verify-tag` against the distributed root, then Intake Gate content checks. Label `git bundle verify` an integrity convenience, not a security control. Add an injection-scanning posture for imported markdown. |
| S7 | §4.4 | Descriptors claim only within their own namespace; cross-vault relations need bidirectional assertion or are stored as "claimed" edges. Add an entity-ref collision arbitration rule. |

### 2.3 Changes in this repository

1. **Ratify or re-status ADRs 001–006** (`docs/adr/`). Whichever way, the status lines must stop contradicting the amendment.
2. **Reconcile ADR-002** (`docs/adr/002-update-model-managed-sections.md`) with the dual-hash marker format shipped in `src/butter_bot/core/managed.py`.
3. **Schedule `check_drift` and the Drafter interface** as named Phase 1 work items — the amendment's drift story depends on the first, ADR-005's autofix path on the second.
4. **Note for the future `koa-skills` skeleton:** the seed set includes two permanent negative-control fixtures (one Tier 1 structural failure, one Tier 2 trigger-overlap near-miss), and CI asserts both are rejected.

### 2.4 Prior-art edits (non-blocking, close by G2)

- P1: pick **one** Tier 1 validator, pin and vendor it; list every retained external tool as a standing vetting cost in §10.1.
- P2: make GPG-signed annotated tags the Phase 3 signing default; OMS becomes the documented upgrade path.

---

## 3. Open questions §10.2 — adopted answers

Fold these into revision 2 as decisions, not open questions:

1. **Gated proxy scope:** standing/shared artifacts only. Ephemeral drafting stays on the ADR-003 working-tree model. Universal routing was rejected because it concentrates hidden authority in the proxy.
2. **Uid scheme:** `KOA-<polyp>-<ulid>` from day one. The driver is provenance binding at Reef scale, not collision probability. Apply the same namespacing to catalog entity refs (links to S7).
3. **Key ceremony:** witnessed offline ceremony, hardware tokens, quorum for use; Vault holds intermediates only. The ceremony runbook is a G2 exit artifact.
4. **Indexer database:** dedicated schema now; dedicated instance at Reef scale. Decisive argument: the indexer ingests externally influenced data.
5. **Seed skills:** add the two negative controls (§2.3 item 4). A gate never observed rejecting is unverified.

---

## 4. Re-review contract

When revision 2 is ready, Agent 2 expects:

- A per-finding disposition table (F1–F2, S1–S7, A1–A3, P1–P2): **accepted** with the section that changed, or **rejected** with a counter-argument. Silence on a blocking finding fails the re-review by default.
- Diffable revision markers in the amendment (a change log section is enough) so the re-review can target deltas.
- No new scope. If remediation surfaces a genuinely new decision, record it as a new proposed ADR rather than expanding A11.

---

## 5. Mechanics

- Any markdown you add under `docs/` is linted by the repo's own style engine in CI. Errors gate the build: no Latin abbreviations, no exclamation marks, no vague link text. Warnings (passive voice, sentence length) report only. Check locally with `python -m butter_bot.style <file>`.
- Work from a fresh branch off `main` after PR #5 merges; do not reuse the review branch.
- Finding IDs in this file are stable references into `docs/review/A11-agent2-review.md` — keep them intact in your disposition table.
