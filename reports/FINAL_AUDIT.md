# Final audit

**Audit date:** 2026-10-09 (Asia/Bangkok)
**Study:** *Reverse-Engineering Mathematical Reasoning from OpenAI’s 2026
Mathematics Corpus: Implications for Mechanistic Interpretability*

## Overall assessment

The repository is complete and reproducible as a **public-artifact audit plus
an explicitly separate, four-seed toy-surrogate causal simulation**. The
technical arXiv source package builds successfully. It is not evidence of
mechanistic interpretability for an OpenAI model, and it must not be
represented as such.

## Evidence of completed checks

| Gate | Result | Evidence |
|---|---|---|
| Governing study contract | PASS | `CODEX_MASTER_PROMPT.md`, `AGENTS.md`, `RESEARCH_PROTOCOL.md`, and `PREREGISTRATION.md` governed the corpus audit; the post-analysis surrogate extension was fixed before execution in `SIMULATION_PROTOCOL.md`. |
| Corpus acquisition | PASS, object-database level | Upstream `openai/math` commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`; `git fsck --no-dangling --no-progress` passed; 133,955 tree blobs recorded in `data/derived/corpus_manifest.json`. |
| Platform path constraint | DOCUMENTED | Windows MAX_PATH prevented materializing 28 deeply nested upstream paths. The analysis reads immutable Git blobs, so those paths remain included rather than silently missing. |
| Parser inclusion set | PASS | 372 families, 719 linked manuscripts, 10 named released summaries; no parse warnings. |
| Statistical analysis | PASS | Seed 20261009; Mann--Whitney U = 16,150, p = 0.638; 10,000-draw permutation p = 0.665; rank-biserial r = 0.03. |
| Literature expansion | PASS | Bibliography expanded from 7 to 28 cited primary/research sources spanning circuits, causal interventions, circuit evaluation, features, and reasoning faithfulness. |
| Figures | PASS | Four data-derived PDF/PNG figures were generated, and a user-supplied conceptual overview is included as Figure 1 before the abstract. The surrogate figure reports four seed-level estimates and 95% Student-t intervals. |
| Multi-seed causal simulation | PASS, surrogate only | Four fixed initialization seeds each fit the 100-pair modular-addition table at 100% training accuracy. Layer 1 left-addend recovery was 0.36 (95% t CI [0.20, 0.52]); the contextual operator control was 0.00. Seed-level records, summaries, and the paired contrast are in `data/derived/surrogate_patching_seed.csv`, `surrogate_patching_summary.csv`, and `surrogate_primary_contrast.json`. |
| Unit tests | PASS | `python -m pytest -q` completed: 4 passed, including a seed-level uncertainty calculation. |
| Local manuscript build | PASS | Tectonic 0.17.0 built `paper/main.pdf`: 9 pages; 28 resolved bibliography entries; no unresolved citations, undefined controls, missing characters, or overfull/underfull boxes in the final log. |
| Visual PDF QA | PASS | All nine rendered manuscript pages were inspected after adding the overview; title, author/affiliation, Figure 1 before the abstract, formula, four-seed uncertainty figure, captions, section order, and bibliography were legible. |
| arXiv archive contents | PASS | `release/arxiv_submission.zip` contains exactly 11 LaTeX, generated-result, figure, and registered-protocol inputs, including the user-supplied Figure 1 image and no corpus files; SHA-256 `EECB4E3E955F0767A9273B7A292A4BA0DF7886971BE2E4DD8E7C8958C964E521`. |
| Clean archive build | PASS | A fresh archive extraction compiled independently with Tectonic to 9 pages; its PDF title and body title match the requested title exactly and its final log has zero layout or unresolved-reference markers. |

## Scientific boundaries and open gates

1. **OpenAI-internal mechanistic interpretability is not feasible from this
   corpus.** The release has no weights, activations, or inspectable inference
   interface. This is a hard evidence boundary, not a missing implementation
   task. The manuscript states it throughout.
2. **Mathematical correctness of the 719 manuscripts was not independently
   adjudicated.** Presence of a PDF, source, Lean scope document, or even a
   Lean artifact is not treated as correctness. The upstream Lean project was
   not compiled because a Lean toolchain and its large pinned dependency graph
   are not installed in this environment. No result in the paper relies on
   successful Lean compilation.
3. **The surrogate result does not generalize to OpenAI.** It is a four-seed
   causal-methods demonstration on toy Transformers trained on their own
   100-item table. A repeated patching effect is not a recovered arithmetic
   circuit, nor evidence of necessity, sufficiency, or generalization.
4. **Author review remains required.** The project has not been submitted to
   arXiv, and no author identity or external submission action was performed.

## Readiness statement

`paper/main.pdf` and `release/arxiv_submission.zip` are
technically ready for author review and arXiv upload as a transparent
public-artifact audit with a clearly bounded multi-seed surrogate simulation.
They are not submission-ready if the intended claim is
that this repository has reverse-engineered OpenAI model mechanisms or
validated the underlying mathematics; the specific blockers are the absence of
OpenAI model internals and independent mathematical/Lean verification.
