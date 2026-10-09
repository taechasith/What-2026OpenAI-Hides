# Paper build

From the repository root, regenerate results and build:

```powershell
python -m oai_math_study.run_analysis --corpus external/openai-math-full --root .
python -m oai_math_study.surrogate --root .
tools\tectonic\tectonic.exe -X compile paper/main.tex --outdir paper --keep-logs --keep-intermediates
```

Run `python scripts\build_release.py` to produce
`release/arxiv_submission.zip`. The archive contains only manuscript
source, generated result inputs, bibliography, and figure PDFs. It excludes the
third-party corpus.
