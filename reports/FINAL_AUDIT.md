# Final audit

**Audit date:** 2026-10-09 (Asia/Bangkok)
**Study:** *Reverse-Engineering Mathematical Reasoning from OpenAI's 2026
Mathematics Corpus: Implications for Mechanistic Interpretability*

## Overall assessment

The repository is complete and reproducible as a **public-artifact audit plus
an explicitly separate toy-surrogate causal intervention**. The technical
arXiv source package builds successfully. It is not evidence of mechanistic
interpretability for an OpenAI model, and it must not be represented as such.

## Evidence of completed checks

| Gate | Result | Evidence |
|---|---|---|
| Governing study contract | PASS | `CODEX_MASTER_PROMPT.md`, `AGENTS.md`, `RESEARCH_PROTOCOL.md__, and `PREREGISTRATION.md` were created before analysis because the checkout contained none. |
| Corpus acquisition | PASS, object-database level | Upstream `openai/math` commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`; `git fsck --no-dangling --no-progress` passed; 133,955 tree blobs recorded in `data/derived/corpus_manifest.json`. |
| Platform path constraint | DOCUMENTED | Windows MAX_PATH prevented materializing 28 deeply nested upstream paths. The analysis reads immutable Git blobs, so those paths remain included rather than silently missing. |
| Parser inclusion set | PASS | 372 families, 719 linked manuscripts, 10 named released summaries; no parse warnings. |
| Statistical analysis | PASS | Seed 20261009; Mann--Whitney U = 16,150, p = 0.638; 10,000-draw permutation p = 0.665; rank-biserial r = 0.03. |
| Figures | PASS | Four data-derived PDF/PNG figures generated and inspected. |
| Toy causal intervention | PASS, surrogate only | Two-layer 39,264-parameter Transformer fit the 100-pair modular-addition table at 100% training accuracy; residual-stream patching outputs are in `data/derived/surrogate_patching.csv`. |
| Unit tests | PASS | `python -m pytest -q` completed: 3 passed. |
| Local manuscript build | PASS | Tectonic 0.17.0 built `paper/main.pdf`; 6 pages; no overfull/underfull boxes, unresolved citations, or undefined markers. |
| Visual PDF QA | PASS | All six rendered pages inspected; figures, table, section order, references, headers, and page numbering were legible and correctly placed. |
| arXiv archive contents | PASS | `release/arxiv_submission.zip` contains 9 source, generated-result, and figure files; no corpus files. |
| Clean archive build | PASS | Extracted archive compiled independently with Tectonic to 6 pages; title present; zero unresolved markers and zero layout warnings. |

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
3. **The surrogate result does not generalize to OpenAI.** It is a
   deterministic methodological demonstration on a toy Transformer trained on
   its own 100-item table.
4. **Author review remains required.** The project has not been submitted to
   arXiv, and no author identity or external submission action was performed.

## Readiness statement

`paper/main.pdf` and `release/arxiv_submission.zip` are
technically ready for author review and arXiv upload as a transparent
public-artifact audit. They are not submission-ready if the intended claim is
that this repository has reverse-engineered OpenAI model mechanisms or
validated the underlying mathematics; the specific blockers are the absence of
OpenAI model internals and independent mathematical/Lean verification.
