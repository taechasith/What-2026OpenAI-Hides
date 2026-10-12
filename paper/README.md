# Paper build

From the repository root, regenerate results and build:

```powershell
python -m oai_math_study.run_analysis --corpus external/openai-math-full --root .
python -m oai_math_study.surrogate --root .
python -m oai_math_study.v2_proof_extraction --corpus external/openai-math-full --root .
python -m oai_math_study.v3_experiments --root .
tools\tectonic\tectonic.exe -X compile paper/main.tex --outdir paper --keep-logs --keep-intermediates
```

Run `python scripts\build_release.py` to produce
`release/reproducibility_bundle.zip`. The bundle contains manuscript source,
generated result inputs, bibliography, registered protocols, and figure PDFs.
It excludes the third-party corpus.
