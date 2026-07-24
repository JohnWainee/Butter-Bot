# Agent 2 adversarial review — candidate amendment A11

**Reviewed artifact:** Koʻa Architecture v2.x, Candidate Amendment A11 — Kūkulu Vault Architecture, Governed Skills Supply Chain, and Waihona Replacement (prepared 2026-07-23)
**Reviewer role:** Agent 2, adversarial review prior to ARB gates G1–G3
**Review date:** 2026-07-24
**Staging repository examined:** `JohnWainee/Butter-Bot` at commit `3c90065` (branch `main` equivalent)

---

## 1. Decision

**Accept with required remediation** for a non-CUI Phase 1 pilot.

This concurs with the author's position on the decision class, but not on the remediation list. This review adds findings the author did not surface, promotes two of them to blocking status before G1 rather than later gates, and rejects one author assumption outright: the claim that the staging repository is an "existing Kūkulu engine" is false as written, and the design's Phase 1 scope is understated as a result.

Summary against the five review questions from §1 of the candidate:

| Review question | Verdict |
|---|---|
| Q1 Architectural fit | Sound with remediations A1–A3. No second policy authority beside Kiaʻi. |
| Q2 Security | Seven findings S1–S7. Three compromise paths are open as designed: self-authored evals, symlink installs, and no revocation channel. |
| Q3 Sovereignty | Preserved in intent. Finding A1 must close to make it structural rather than behavioral. |
| Q4 Implementability | Understated. Blocked on F1 and F2. Phase 1 is buildable by a small team once scoped honestly. |
| Q5 Prior-art risk | Acceptable as patterns. The tooling dependency list must shrink and pin (P1, P2). |

---

## 2. Blocking findings — close before G1

### F1 — False premise: the "existing Kūkulu engine" does not exist as described

§3.1 lists the staging repository as the "Existing Kūkulu engine" and §6 says it retains "ADRs 001–006 as standing decisions." I verified the repository directly. The gap between the document and reality is material:

- **The name does not exist.** A case-insensitive content search for `Kūkulu`, `kukulu`, `Koʻa`, `koa`, `waihona`, `vault-template`, and `koa-skills` returns zero matches in any tracked file. The identity exists only as an unbacked branch label.
- **No ADR is a standing decision.** All six ADRs exist under `docs/adr/` and match the candidate's summaries in substance, but every one carries status "Proposed (awaiting plan approval)." The candidate cites them as ratified baseline. They are not.
- **The engine surface is incomplete.** The MCP server (`src/butter_bot/mcp/server.py`) exposes six of the seven planned tools; `check_drift` — the tool the managed-section drift story depends on — is unbuilt. The `Drafter` interface from ADR-001 and ADR-005 has no implementation. Language adapters cover Wave 1 only.
- **ADR-002 has already drifted from its own implementation.** The ADR documents a single-hash marker; the shipped code (`src/butter_bot/core/managed.py`) uses a dual-hash marker (`facts=` and `content=`). The candidate quotes the ADR, not the code. A design whose central claim is "drift is detectable per-block" resting on a drifted ADR is an irony the ARB should not let stand.

**Why this blocks G1.** The candidate's implementability answer, its Phase 1 scope, and its constitutional-alignment table all inherit capabilities the engine does not have. The remediation is cheap and mechanical: correct §3.1 and §6 to describe actual repository state, ratify or re-status ADRs 001–006 before citing them as baseline, reconcile the ADR-002 text with `core/managed.py`, and add `check_drift` plus the Drafter interface to the Phase 1 work plan explicitly.

### F2 — Stack contradiction between the constitution and the staging repo

§1 (Q4) constrains delivery to the approved on-prem stack — Node.js, PostgreSQL, RKE2, Vault, Argo CD — and §4.4 specifies a "small Node.js indexer service." The staging repository, which §6 designates "the first conforming instance of its own rules," is Python 3.11 end to end (hatchling, pydantic, FastMCP). Additionally, the K2-005 documentation CI that §6 promises (markdown lint, link validation, traceability validation) does not match the repository's actual CI, which runs `ruff`, `pytest`, and the repo's own style linter; link validation and traceability validation do not exist.

One of three things must be true, and the candidate must say which: the stack constraint admits Python for the Kūkulu plane; the staging engine gets rewritten (which resets the Phase 1 baseline); or the "first conforming instance" claim is dropped. Silence here invalidates the candidate's own answer to Q4.

---

## 3. Security findings — close before G2

The review question asks for any path by which a compromised skill, Context Unit, or catalog descriptor gains authority. Three such paths are open as designed (S1, S4, S3's persistence effect), and four further findings weaken the control story.

### S1 — The proposer authors its own promotion tests

§5.3 packages `evals/evals.json` inside the skill directory. §5.6 allows agents to propose skill changes as SkillPatch PRs. Combined: an agent (or a compromised author) proposing a skill also proposes the eval suite that gates its promotion. The held-out-set rule in §5.6 applies only to optimizer-generated changes, not to the general promotion path in §5.4.

Tier 2's promptfoo trigger suite and A/B eval draw scenarios from the package under review. A skill crafted together with evals that avoid its malicious trigger surface passes Tier 2 legitimately. **Remediation:** promotion requires eval suites maintained outside the skill directory and outside any agent-writable path, owned by the gate operator, in addition to the in-package suite. The in-package suite is a floor, never the gate.

### S2 — Signing key placement contradicts the offline root, and nobody is named as the signer

§5.5 stores signing keys in HashiCorp Vault — an online, network-reachable system — under an "offline Koʻa root certificate." An offline root whose operational keys live in an online secret store is offline in name only. Separately, the candidate never states *who or what signs on promotion*. If CI signs automatically on merge, then CI holds signing capability, and a compromised CI runner mints valid signatures over arbitrary content — the classic supply-chain failure the whole section exists to prevent.

**Remediation:** the root key never enters Vault; it lives in the ceremony artifact (see §6, answer 3). Vault holds intermediates only, with short lifetimes. The promotion approval must be cryptographically bound to the signature — the signing operation consumes an artifact of the human approval (for example, a signed attestation referencing the approved merge commit), not merely follow it procedurally.

### S3 — No revocation or advisory channel exists

Pinned, offline, air-gapped consumption is precisely the distribution model in which a known-bad artifact persists forever: consumers deliberately do not track upstream, so they never learn the artifact went bad. The candidate specifies signing, pinning, and verification — and no mechanism at all for un-trusting. A skill found malicious after promotion remains validly signed at every pinned consumer indefinitely.

**Remediation before any Phase 3 signing goes live:** a signed revocation/advisory manifest distributed through the same bundle channel as content, checked at install time and periodically at load time, plus a runbook entry making advisory consumption part of the Intake Gate. Without this, the signing chain creates false confidence rather than safety.

### S4 — `scripts/link-skills.sh` bypasses the entire signing chain

Symlink installs serve live working-tree content. Every control in §5.4–§5.5 — CI tiers, promotion review, directory-tree signatures, pinned tags — is void for a symlinked skill, which tracks whatever the working tree contains at load time, unsigned and unreviewed. The candidate lists the script as ordinary repo tooling with no caveat.

**Remediation:** symlink installs are a development-profile convenience only, must mark the installed skill visibly as unsigned/dev, and must be impossible in production install profiles. Relatedly, the `.claude-plugin` manifest must itself be inside the signature envelope; an unsigned manifest permits a swap attack that points consumers at nursery content while promoted signatures still verify.

### S5 — Gate output is authorization in practice, whatever the principle says

§5.6: agent pushes route through the gated proxy and "only green results are forwarded as PRs." The candidate simultaneously asserts (§5.4, §7) that gate output is "diagnostic evidence, never authorization." Both cannot hold. If red results never become PRs, the gate decides what humans ever see — that is authorization by construction, exercised before any human is in the loop. It is also a suppression channel: whoever controls the proxy's pipeline configuration controls which agent proposals surface, silently.

**Remediation:** (a) rejected pushes are captured as evidence too — a suppression audit trail reviewable by the skill owner; (b) the proxy's pipeline configuration is itself under the same change-control regime as promoted skills (owner approval, Kiaʻi review), because the proxy is the single most authority-dense component this amendment introduces; (c) the candidate's language is corrected: the proxy performs *pre-screening under delegated, audited authority*, not "evidence, not authorization."

### S6 — Signatures verify origin, not benignity; and `git bundle verify` is not a security check

Two related weaknesses in §4.3:

1. A validly signed bundle from a *compromised partner Polyp* delivers whatever the partner signs — including markdown carrying prompt-injection payloads that consuming agents will read through the vault MCP server. The candidate cites the prompts-leak corpus for extraction risk but is silent on injection via imported content, which is the higher-consequence direction. The Intake Gate needs a stated content-quarantine and scanning posture for imported markdown, beyond signature verification.
2. `git bundle verify` checks bundle completeness and prerequisites. It verifies **no signature**. The candidate lists it alongside `git verify-tag` in a way that reads as a cryptographic control. The verification sequence must be spelled out: unbundle into quarantine, then `git verify-tag` against the distributed root, then Intake Gate content checks — in that order, with the bundle-verify step labeled as an integrity convenience only.

### S7 — Descriptor poisoning: metadata is influence even without authority

§4.4's indexer harvests `catalog-info.yaml` descriptors from many sovereign vaults into a graph that agents consult via MCP. The candidate's defense is A04: context never grants authority. True — but the practical attack is not authority, it is *steering*. A forged `dependsOn`, `ownedBy`, or `partOf` relation reshapes what agents believe about the system and which Context Packs they assemble. Schema validation confirms shape, not truth.

**Remediation:** descriptors may make claims only about entities within their own vault's namespace; cross-vault relations require corroboration from the target's descriptor (bidirectional assertion) or are stored as "claimed" edges distinguishable in the graph. Entity-ref namespace collisions across Polyps need a stated arbitration rule — this is the same problem as open question 10.2, which the candidate scopes to uids only; it applies equally to `metadata.name` entity refs.

---

## 4. Architectural and sovereignty findings

### A1 — Invert the indexer's access relationship

"Harvests descriptors only (never content)" is a behavioral promise, not a structural property, if the indexer holds read access to whole vault repositories. Sovereignty by policy is exactly what the Reef edge/gate model exists to avoid. **Remediation:** vaults *publish* their descriptor through their own Result Release Gate (the descriptor is an export artifact); the indexer reads only published artifacts and holds no repository credentials. This makes "metadata only" true by construction and closes the question of what a compromised indexer can read.

### A2 — `refugia/` as a directory of copies is redundant and divergence-prone

Signed annotated tags already provide immutable known-good states. A `refugia/` directory containing *copies* of skill content creates a second source of truth that can diverge from the signed artifact it mirrors. **Remediation:** refugia is a pinned-refs manifest (skill id → tag/digest), not content. Consumers resolve refugia entries through the same verified-tag path as everything else.

### A3 — Do not "freeze" the frontmatter schema in Phase 1

Freezing a schema before any consumer exists is premature lock-in; the first real vault will discover missing fields within weeks. Use a `schema_version` field and an explicit compatibility rule (additive changes minor, breaking changes major with migration tooling) instead of a freeze.

### A4 — What is right and should be affirmed

To be a useful adversary I state what survived attack:

- **Rejecting the Backstage runtime while adopting its descriptor spec** is the correct call, for exactly the reasons given: its permission framework would stand beside Kiaʻi, and the spec-as-convention keeps the fallback open. No second policy authority enters through this design.
- **Pull-based, pinned, review-gated federation with live sync explicitly excluded** from the vault plane is sound and correctly assigns real-time coordination elsewhere.
- **Deterministic-before-behavioral CI tiers** honor A05 in structure. (One caveat: Tier 2's fixed thresholds sit atop nondeterministic model evals; expect flake, and specify a retry-and-quorum rule rather than letting threshold flake erode trust in the gate.)
- **Managed sections are real.** The dual-hash implementation in the staging repo works and is tested; the incremental generated-projection path to A09 is credible once F1's gaps close.
- **The lifecycle taxonomy** (nursery → promoted → refugia → deprecated as PR-gated promotion) maps cleanly onto Git primitives and keeps humans at every transition.

---

## 5. Prior-art findings

### P1 — The supply-chain argument cuts against the candidate's own tooling list

§4.4 rejects the Backstage runtime partly because "its npm supply chain is a continuous re-vetting burden in an air-gapped environment." §5.4 and Appendix A then adopt promptfoo, three overlapping Tier 1 validators (`skillscheck`, `skill-lint`, `skill-validator`), and two signing toolchains as candidates — external tools, several individually maintained. The same argument applies with the same force. **Remediation:** select exactly one Tier 1 validator, pin it, and vendor it into the repo; treat `mattpocock/skills`, `no-mistakes`, and `OpenMontage` strictly as pattern references (which the candidate mostly already does); recognize each retained external tool as a standing vetting cost and list it as such in the risk register.

### P2 — OMS is doubly experimental; invert the signing default

OpenSSF Model Signing is self-described experimental, and the candidate's own production reference (NVIDIA/skills) describes *its* signing layer as experimental. Basing the primary recommendation on it inverts the maturity ordering. **Remediation:** GPG-signed annotated tags — canonical, boring, air-gap-native, already required for Layer 2 federation — are the Phase 3 default. OMS is the documented upgrade path once it stabilizes, evaluated at a later gate. This also halves the key-management surface, since vault federation and skill signing then share one mechanism initially.

Minor notes: the `hermes-agent-self-evolution` and SkillOpt references are appropriately treated as study-first with local held-out evals as the only acceptance basis; no change requested. The Snyk ToxicSkills audit as motivating threat evidence is apt.

---

## 6. Answers to the open questions (§10.2)

1. **Gated proxy for all agent vault writes?** No. Universal routing makes the proxy a mandatory choke point and concentrates precisely the hidden authority this review flags in S5 — the more traffic it gates, the more its configuration becomes the real policy engine. Scope it to writes that touch standing or shared artifacts (skills, promoted vault content, anything leaving the local plane). Ephemeral drafting stays on the ADR-003 working-tree model, which already denies the core any credentials.
2. **ULID sufficiency.** Namespace per Polyp from day one: `KOA-<polyp>-<ulid>`. The argument is not collision probability — ULID collisions are negligible — it is provenance. A bare ULID cannot tell a Reef-scale consumer which Polyp minted it, so authenticity and arbitration checks would need origin binding retrofitted later, which is exactly the expensive path. The same namespacing rule must extend to catalog entity refs (see S7).
3. **Air-gap key distribution.** Offline root generated in a witnessed ceremony on an air-gapped machine, stored on hardware tokens (YubiKey per the Yocto reference) with a documented quorum for use; Vault holds only intermediate and operational keys with short lifetimes. The root never touches Vault or any networked system (see S2). The ceremony runbook is a G2 exit artifact.
4. **Indexer database placement.** Dedicated schema at minimum, from day one — and note the decisive argument is not blast radius in the abstract: the indexer's write path ingests *externally influenced data* (descriptors authored in other vaults). That alone justifies isolation from the Polyp data plane. Move to a dedicated instance when Reef-scale federation begins.
5. **Phase 1 seed set.** Three well-formed skills cannot exercise the gates, because a gate that has never been observed rejecting is unverified. Add two permanent negative-control fixtures: one deliberately failing skill (Tier 1 structural violations) and one deliberately trigger-overlapping skill (Tier 2 near-miss routing). CI asserts that both are rejected; a release in which a negative control passes is itself a gate failure.

---

## 7. Consolidated remediation register

| ID | Gate | Remediation | Blocking |
|---|---|---|---|
| F1 | G1 | Correct staging-repo claims; ratify or re-status ADRs 001–006; reconcile ADR-002 with code; add `check_drift` and Drafter to Phase 1 scope | Yes |
| F2 | G1 | Resolve the Node.js/Python stack contradiction and the K2-005 CI claim | Yes |
| S1 | G2 | Gate-owned held-out eval suites outside any agent-writable path | Yes |
| S2 | G2 | Root key off-Vault; bind human approval cryptographically to the signature | Yes |
| S3 | G2 (before Phase 3) | Signed revocation/advisory manifest in the bundle channel | Yes |
| S4 | G2 | Dev-only symlink installs; manifest inside the signature envelope | Yes |
| S5 | G2/G3 | Suppression audit; proxy config under skill-grade change control; correct the "evidence" language | Yes |
| S6 | G2 | Intake Gate content quarantine; spell out the bundle verification sequence | Yes |
| S7 | G2/G3 | Namespace-scoped descriptor claims; bidirectional cross-vault relations; entity-ref arbitration rule | Yes |
| A1 | G1 | Vaults publish descriptors; indexer holds no repo credentials | Yes |
| A2 | G1 | Refugia as pinned-refs manifest, not content copies | No |
| A3 | G1 | Versioned schema instead of Phase 1 freeze | No |
| P1 | G2 | One pinned, vendored Tier 1 validator; external tools in the risk register | No |
| P2 | G2 | GPG tags as signing default; OMS as upgrade path | No |

---

## 8. Closing statement

The candidate's core shape is right: sovereign vaults, pull-based pinned federation, a PR-shaped skill lifecycle, humans at every transition, and a deliberate refusal to adopt a second platform runtime. Those choices survived adversarial examination and deserve to proceed.

What does not survive is the candidate's account of its own starting point, and the gap between its authority principles and three of its mechanisms. The staging repository is a promising engine, not the one described. The proxy authorizes while claiming not to. The signing chain trusts an online store with offline keys, lets a shell script route around itself, and cannot take anything back once granted. All of these are fixable within the amendment's own architecture — which is why the decision is accept with required remediation rather than defer.

*End of Agent 2 review.*
