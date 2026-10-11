# Final scientific audit, Version 2 checkpoint

**Audit date:** 2026-10-12 (Asia/Bangkok)  
**Status:** **PARTIAL EMPIRICAL COMPLETION**

## Executed and verified

| Check | Result | Evidence |
| --- | --- | --- |
| Version 1 baseline | Preserved | Original protocols, derived outputs, toy-surrogate records, and paper remain in place. |
| Continuation isolation | Pass | Branch `research/v2-proof-to-circuit`. |
| Corpus integrity | Pass | Pinned commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`; Git object validation passed. |
| Source extraction | Pass, exploratory only | 8,007 TeX blobs; 45,620 nodes; 97,343 deduplicated literal reference edges; 42,143 lexical motif records. |
| Extraction checks | Pass | Unique IDs, complete node provenance, document-scoped reference resolution, and resolvable retained endpoints. |
| Tests | Pass | `python -m pytest -q`: 8 passed. |
| Manuscript build | Pass | `paper/main.pdf`: 13 pages; no unresolved, overfull, or underfull markers. |
| Visual PDF review | Pass | All 13 rasterized pages inspected. |
| Release archive | Pass | 18 entries; SHA-256 `042201ACF58292EF2A3408FBC12937E6F9F6A26C82C82DB60FF4273CBABBAE90`; clean extraction compiled successfully. |

## Gates

- **G1:** partial pass. Corpus pinning and artifact provenance are complete.
- **G2:** partial pass. Literal references and rule-based candidates are clearly
  separated, but no independent semantic extraction validation was performed.
- **G3:** not entered. No kernel-checked and semantically audited
  counterfactual cases exist.
- **G4--G7:** not entered. No accessible-model behavioral competence result,
  held-out predictive comparison, intervention result, or robustness analysis
  exists.

## Scientific boundary

The Version 2 counts describe source-text structure under fixed extraction
rules. They do not establish proof correctness, proof-strategy prevalence,
mathematical entailment, causal neural computation, or a mechanism in an
unreleased OpenAI model. The absence of a Lean toolchain, a valid
counterfactual set, and a locally available open-weight model are reported as
infrastructure/validation limits, not converted into a negative H1 finding.

## Readiness

This branch is ready for human author review as a reproducible partial Version
2 checkpoint. It is not ready to claim that H1 was tested or that causal
transfer from public proof structures to open-weight-model mechanisms was
demonstrated.
