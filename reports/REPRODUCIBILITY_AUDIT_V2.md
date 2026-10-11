# Reproducibility audit, Version 2 checkpoint

## Executed evidence

- Branch: `research/v2-proof-to-circuit`.
- Corpus commit: `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`.
- Git object validation: `git fsck --no-dangling` passed before extraction.
- Extraction command: `python -m oai_math_study.v2_proof_extraction --root . --corpus external/openai-math-full`.
- Outputs: 45,620 nodes, 97,343 deduplicated literal edges, 42,143 motif records, and a manifest/exclusion log under `data/derived/v2/`.

## Environment limits

The machine has CPU-only PyTorch and no cached open-weight model; Lean/Lake was not detected. Therefore no claim of Lean kernel verification or open-weight mechanistic experimentation is reproducible from this checkpoint.

## Regeneration requirements

Python 3.10+, Git, pandas, pyarrow, matplotlib, and the pinned upstream corpus are required. The project dependency declaration includes pandas and pyarrow. The manuscript needs Tectonic. The release package intentionally excludes the third-party corpus and records acquisition rather than redistributing it.
