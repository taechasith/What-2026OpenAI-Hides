# Final audit

**Audit date:** 2026-10-10 (Asia/Bangkok)
**Study:** *Reverse-Engineering Mathematical Reasoning from OpenAI’s 2026
Mathematics Corpus: Implications for Mechanistic Interpretability*

## Overall assessment

The repository is complete and reproducible as a **public-artifact audit,
an exhaustive structural census of the frozen mathematics release tree, and
an explicitly separate four-seed toy-surrogate causal simulation**. The
technical arXiv source package builds successfully. It is not evidence of
mechanistic interpretability for an OpenAI model, and it must not be
represented as such.

## Evidence of completed checks

| Gate | Result | Evidence |
|---|---|---|
| Governing study contract | PASS | `CODEX_MASTER_PROMPT.md`, `AGENTS.md`, `RESEARCH_PROTOCOL.md`, and `PREREGISTRATION.md` govern the frozen corpus audit; the surrogate and full-tree extensions were separately specified before their executions in `SIMULATION_PROTOCOL.md` and `FULL_TREE_INVENTORY_PROTOCOL.md`. |
| Corpus acquisition | PASS, object-database level | Upstream `openai/math` commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`, tree `08e6aaa9e4788dd81984b67a9cd97d952093ecd4`; `git fsck --no-dangling --no-progress` passed. The pipeline rejects any other `HEAD` and reads the resolved immutable commit throughout. |
| Platform path constraint | DOCUMENTED | Windows MAX_PATH prevented materializing 28 deeply nested upstream paths. The analysis reads immutable Git blobs, so those paths remain included rather than silently missing. |
| Full release-tree inventory | PASS, structural only | `data/derived/full_tree_inventory.csv` has exactly 133,955 unique-path rows, one for every versioned blob (2,214,297,422 bytes; 2.06 GiB). `full_tree_summary.json` records 133,582 unique blob object IDs, complete coverage, non-negative sizes, and path/extension roles. No corpus contents were copied. |
| Parser inclusion set | PASS | 372 families, 719 linked manuscripts, 10 named released summaries; no parse warnings. |
| Statistical analysis | PASS | Seed 20261009; Mann--Whitney U = 16,150, p = 0.638; 10,000-draw permutation p = 0.665; rank-biserial r = 0.03. |
| Literature expansion | PASS | Bibliography expanded from 7 to 31 cited primary/research sources spanning circuits, causal interventions, circuit evaluation, sparse probes/features, and reasoning faithfulness. |
| Figures | PASS | Five data-derived PDF/PNG figures were generated, including the whole-tree composition figure, and a user-supplied conceptual overview is Figure 1 before the abstract. The surrogate figure reports four seed-level estimates and 95% Student-t intervals. |
| Multi-seed causal simulation | PASS, surrogate only | Four fixed initialization seeds each fit the 100-pair modular-addition table at 100% training accuracy. Layer 1 left-addend recovery was 0.36 (95% t CI [0.20, 0.52]); the contextual operator control was 0.00. Seed-level records, summaries, and the paired contrast are in `data/derived/surrogate_patching_seed.csv`, `surrogate_patching_summary.csv`, and `surrogate_primary_contrast.json`. |
| Unit tests | PASS | `python -m pytest -q` completed: 6 passed, including complete-tree coverage, nested preprint linkage, pinned-commit rejection, and seed-level uncertainty checks. |
| Local manuscript build | PASS | Tectonic 0.17.0 built `paper/main.pdf`: 11 pages; 31 resolved bibliography entries; no unresolved citations, undefined controls, missing characters, or overfull/underfull boxes in the final log. PDF metadata uses an ASCII apostrophe for compatibility; the visible title uses the requested typographic apostrophe. |
| Visual PDF QA | PASS | All 11 rendered manuscript pages were inspected after the whole-tree extension. Title, author/affiliation, Figure 1 before the abstract, centered tables, full-tree composition figure, formula, four-seed uncertainty figure, captions, section order, and bibliography were legible. |
| arXiv archive contents | PASS | `release/arxiv_submission.zip` contains exactly 14 LaTeX, generated-result, figure, and registered-protocol inputs, including the full-tree table/figure and user-supplied Figure 1 image, with no corpus or `data/` files; SHA-256 `6E566331D1E60E98C8C8F06ABF157D0058FA65E07C8A83C6EF98967651ABBB3C`. |
| Clean archive build | PASS | A fresh archive extraction compiled independently with Tectonic to 11 pages; its metadata and body title match the requested title (ASCII apostrophe in metadata only), and its final log has zero layout or unresolved-reference markers. |

## Scientific boundaries and open gates

1. **OpenAI-internal mechanistic interpretability is not feasible from this
   corpus.** The release has no weights, activations, or inspectable inference
   interface. This is a hard evidence boundary, not a missing implementation
   task. The manuscript states it throughout.
2. **Whole-tree coverage is not a global OpenAI-publication claim.** The
   extension exhaustively indexes every versioned blob in the named frozen
   `openai/math` repository only. It does not establish coverage of OpenAI's
   other repositories, web pages, externally hosted papers, historical or
   deleted materials, or artifacts not enumerated by this release.
3. **Mathematical correctness was not independently adjudicated.** Presence
   of a PDF, source, Lean scope document, or even a Lean artifact is not
   treated as correctness. The upstream Lean project was not compiled because
   a Lean toolchain and its large pinned dependency graph are not installed in
   this environment. No result in the paper relies on successful Lean
   compilation.
4. **The surrogate result does not generalize to OpenAI.** It is a four-seed
   causal-methods demonstration on toy Transformers trained on their own
   100-item table. A repeated patching effect is not a recovered arithmetic
   circuit, nor evidence of necessity, sufficiency, or generalization.
5. **Author review remains required.** The project has not been submitted to
   arXiv, and no author identity or external submission action was performed.

## Readiness statement

`paper/main.pdf` and `release/arxiv_submission.zip` are technically ready for
author review and arXiv upload as a transparent public-artifact audit with an
exhaustive frozen-release-tree census and clearly bounded multi-seed surrogate
simulation. They are not submission-ready if the intended claim is that this
repository has reverse-engineered OpenAI model mechanisms, validated the
underlying mathematics, or exhaustively covered all OpenAI research worldwide;
the respective blockers are absent model internals, absent independent
mathematical/Lean verification, and no single pinned official global corpus.
