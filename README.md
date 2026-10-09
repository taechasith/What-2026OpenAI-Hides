# OpenAI Mathematics Corpus Artifact Audit

> **Reverse-Engineering Mathematical Reasoning from OpenAI's 2026 Mathematics Corpus: Implications for Mechanistic Interpretability**<br>
> Taechasith Kangkhuntod · School of Engineering, University of the Thai Chamber of Commerce, Thailand

[Paper](paper/main.pdf) · [arXiv source archive](release/arxiv_submission.zip) · [Final audit](reports/FINAL_AUDIT.md) · [Simulation protocol](SIMULATION_PROTOCOL.md) · [Project home](https://github.com/taechasith/What-2026OpenAI-Hides)

## What this repository establishes

This is a reproducible audit of the public, Apache-2.0-licensed
[openai/math](https://github.com/openai/math) release at immutable commit
<code>fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb</code>. It measures catalogue
structure, linked-artifact availability, Lean scope-document availability, and
the ten explicitly released abridged reasoning summaries.

It also contains a separate, genuinely executed four-seed causal
residual-stream-patching simulation in fully inspectable toy Transformers.
That simulation demonstrates a mechanistic-interpretability method; it is not
evidence about OpenAI model weights, activations, hidden reasoning, or neural
circuits.

## At a glance

| Public-release audit | Inspectable surrogate simulation |
| --- | --- |
| 372 result families | 4 independently initialized models |
| 719 catalogue-linked manuscripts | 2 layers · 3 heads · 39,264 parameters |
| 242 Lean scope documents | 100 modulo-10 addition prompts per model |
| 10 released abridged summaries | 100% in-table fit for every seed |
| Family-size comparison: Mann--Whitney <i>p</i> = 0.638 | Layer-1 left-addend recovery: 0.36, 95% t CI [0.20, 0.52] |

## Evidence boundary

The public corpus contains outputs and supporting artifacts, not an
inspectable OpenAI model. The study therefore makes claims only about public
artifact availability, catalogue structure, and descriptive text measures.
It does not claim to recover OpenAI's neural mechanisms, validate every
manuscript's mathematics, or infer hidden reasoning from released prose.

The causal simulation is deliberately isolated from the corpus analysis:

1. Train each toy Transformer from scratch on the fixed full addition table.
2. Corrupt the left addend in every prompt.
3. Replace one post-block residual state with its clean counterpart.
4. Measure clean-answer-logit recovery, treating random initialization seed as
   the uncertainty unit.

The frozen design, controls, stopping rule, and interpretation limits are in
[SIMULATION_PROTOCOL.md](SIMULATION_PROTOCOL.md).

## Key outputs

| Deliverable | Description |
| --- | --- |
| [paper/main.pdf](paper/main.pdf) | Nine-page, arXiv-ready manuscript with 28 cited sources. |
| [release/arxiv_submission.zip](release/arxiv_submission.zip) | Clean ten-file source package; independently compiled after extraction. |
| [reports/FINAL_AUDIT.md](reports/FINAL_AUDIT.md) | Build, archive, visual-QA, and scientific-boundary record. |
| [data/derived/surrogate_patching_summary.csv](data/derived/surrogate_patching_summary.csv) | Four-seed mean, sample SD, and t-interval estimates. |
| [data/derived/surrogate_primary_contrast.json](data/derived/surrogate_primary_contrast.json) | Prespecified paired Layer-1 left-addend versus operator contrast. |

<p align="center">
  <img src="figures/surrogate_patching.png" width="880" alt="Four-seed causal residual-stream patching results">
</p>

<p align="center"><em>Inspectable surrogate: mean residual-patching recovery and seed-level 95% Student-t intervals.</em></p>

## Reproduce

Requirements: Python 3.10+, Git, and Tectonic for the PDF build.

~~~powershell
python -m pip install -e .
git -c core.longpaths=true clone --depth 1 https://github.com/openai/math.git external/openai-math-full

python -m oai_math_study.run_analysis --corpus external/openai-math-full --root .
python -m oai_math_study.surrogate --root .
python -m pytest -q

tools\tectonic\tectonic.exe -X compile paper/main.tex --outdir paper --keep-logs --keep-intermediates
python scripts\build_release.py
~~~

On Windows, ordinary working-tree traversal can miss deeply nested upstream
paths when MAX_PATH blocks checkout. The analysis reads verified Git blobs
directly from the immutable object database so such paths are not silently
excluded.

## Repository map

| Path | Contents |
| --- | --- |
| <code>src/</code> | Deterministic corpus parser, statistics, figure generation, and multi-seed simulation. |
| <code>data/derived/</code> | Provenance manifest, generated measurements, seed-level results, and summaries. |
| <code>figures/</code> | Publication figures generated from the released derived data. |
| <code>paper/</code> | LaTeX manuscript, bibliography, generated macros, and compiled PDF. |
| <code>release/</code> | Verified arXiv source archive. |
| <code>reports/</code> | Final audit and reproducibility evidence. |
| <code>external/</code> | Ignored third-party corpus clone; never redistributed in this repository. |

## License and citation

Repository-authored code and documentation are Apache-2.0 licensed. The
upstream corpus is not redistributed; its separate license and provenance are
recorded in <code>data/derived/corpus_manifest.json</code>. Please cite the
accompanying manuscript using [CITATION.cff](CITATION.cff).
