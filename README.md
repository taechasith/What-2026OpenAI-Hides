# OpenAI Mathematics Corpus Artifact Audit

This repository contains the reproducible empirical study:

> **Reverse-Engineering Mathematical Reasoning from OpenAI's 2026 Mathematics
> Corpus: Implications for Mechanistic Interpretability**
> Taechasith Kangkhuntod, School of Engineering, University of the Thai
> Chamber of Commerce, Thailand

## What was studied

The study audits public artifacts in the Apache-2.0 licensed
[openai/math](https://github.com/openai/math) release at commit
`fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`. It measures catalogue
structure, linked-artifact availability, Lean scope-document availability, and
the ten explicitly released abridged reasoning summaries.

This is **not** a claim to inspect OpenAI model weights, activations, hidden
reasoning, or neural circuits. The separate toy-surrogate experiment is a real
causal residual-stream patching demonstration on a fully inspectable model; it
does not transfer any result to an OpenAI model.

## Results at the pinned release

- 372 result families and 719 catalogue-linked manuscripts.
- All 719 linked PDFs and manuscript source directories are available in the
  verified Git tree.
- 242 families have a Lean scope document. This is not a compiler-validation
  or correctness claim.
- 10 released abridged reasoning-summary PDFs.
- The preregistered family-size comparison is small and non-significant
  (Mann--Whitney p = 0.638; 10,000-draw label permutation p = 0.665;
  rank-biserial r = 0.03).

See `RESEARCH_PROTOCOL.md`, `PREREGISTRATION.md`, and
`reports/FINAL_AUDIT.md` for scope, method, and audit status.

## Reproduce

Python 3.10+ is required. Install the declared package dependencies:

```powershell
python -m pip install -e .
```

Acquire the upstream corpus with Git. On Windows, do not treat an ordinary
working-tree traversal as complete if MAX_PATH prevents checkout of deep paths;
the pipeline reads verified blobs from the Git object database.

```powershell
git -c core.longpaths=true clone --depth 1 https://github.com/openai/math.git external/openai-math-full
python -m oai_math_study.run_analysis --corpus external/openai-math-full --root .
python -m oai_math_study.surrogate --root .
python -m pytest -q
```

Build the paper using Tectonic:

```powershell
tools\tectonic\tectonic.exe -X compile paper/main.tex --outdir paper --keep-logs --keep-intermediates
python scripts\build_release.py
```

## Repository layout

- `src/`: deterministic parser, statistics, figures, and surrogate test.
- `data/derived/`: generated tables, statistics, and provenance manifest.
- `figures/`: generated publication figures.
- `paper/`: LaTeX manuscript, generated macros, bibliography, and PDF.
- `release/`: arXiv source archive.
- `reports/`: final audit and reproduction evidence.
- `external/`: ignored third-party corpus clones; never in the release.

## License and third-party material

Repository-authored code and documentation are Apache-2.0 licensed. The
upstream corpus is not redistributed. Its own upstream Apache-2.0 license and
provenance are recorded in `data/derived/corpus_manifest.json`.
