# Proof extraction audit, Version 2

**Run date:** 2026-10-12 (Asia/Bangkok)  
**Run type:** exploratory, deterministic source-structure extraction  
**Corpus:** `openai/math` commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`

## Scope

The extractor read immutable Git blobs from all 8,007 `preprints/**/*.tex`
files at the pinned commit. It did not read an incomplete Windows working tree
as evidence. It emitted candidate TeX environments and literal cross-reference
edges, then applied pre-registered lexical rules for candidate proof motifs.

| Output | Count |
| --- | ---: |
| TeX source files considered | 8,007 |
| Candidate statement/proof nodes | 45,620 |
| Explicit source-reference edges | 97,343 |
| Repeated literal references collapsed | 22,049 |
| Unresolved local reference labels | 15,824 |
| Rule-based motif records | 42,143 |
| Source files without a candidate environment | 2,283 |
| Source documents represented | 745 |

## Motif candidates

| Rule-based motif | Records |
| --- | ---: |
| construction | 10,719 |
| limit | 7,935 |
| case split | 6,148 |
| invariant | 4,779 |
| equivalence | 4,528 |
| reduction | 3,270 |
| contradiction | 2,419 |
| induction | 2,345 |

## Integrity checks

- All node IDs are unique.
- All edge IDs are unique after collapsing repeated literal references.
- Every retained edge endpoint resolves to a retained node.
- Every node carries source commit, blob hash, document ID, path and line span.
- 22,489 retained literal references are self-references. These are preserved
  as source facts, not treated as causal or mathematical dependencies.
- Labels are resolved only within the same document identifier, avoiding
  accidental cross-paper connections from repeated TeX labels.

## Interpretation boundary

Graph A records literal TeX references. It is not an entailment graph, a proof
checker, or evidence that a cited statement is necessary. Graph B records
lexical matches to fixed regular expressions. It is not semantic annotation,
human validation, or evidence of an authorial proof strategy.

No model outputs, activation values, or intervention effects were used in this
run. The results therefore do not test H1 and do not support claims about
OpenAI's unreleased models.

## Reproduction

```powershell
python -m oai_math_study.v2_proof_extraction --root . --corpus external/openai-math-full
```

The command regenerates `data/derived/v2/proof_nodes.parquet`,
`proof_edges.parquet`, `proof_motifs.parquet`,
`proof_extraction_exclusions.csv`, and `proof_extraction_manifest.json`.
