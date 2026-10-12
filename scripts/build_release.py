"""Build a minimal arXiv source archive without redistributing the corpus."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "release" / "arxiv_submission.zip"
FILES = {
    ROOT / "paper" / "main.tex": "main.tex",
    ROOT / "paper" / "references.bib": "references.bib",
    ROOT / "paper" / "generated" / "results_macros.tex": "generated/results_macros.tex",
    ROOT / "paper" / "generated" / "surrogate_macros.tex": "generated/surrogate_macros.tex",
    ROOT / "paper" / "generated" / "coverage_table.tex": "generated/coverage_table.tex",
    ROOT / "paper" / "generated" / "full_tree_table.tex": "generated/full_tree_table.tex",
    ROOT / "SIMULATION_PROTOCOL.md": "SIMULATION_PROTOCOL.md",
    ROOT / "FULL_TREE_INVENTORY_PROTOCOL.md": "FULL_TREE_INVENTORY_PROTOCOL.md",
    ROOT / "figures" / "artifact_coverage.pdf": "figures/artifact_coverage.pdf",
    ROOT / "figures" / "family_size_distribution.pdf": "figures/family_size_distribution.pdf",
    ROOT / "figures" / "trace_text_volume.pdf": "figures/trace_text_volume.pdf",
    ROOT / "figures" / "full_tree_composition.pdf": "figures/full_tree_composition.pdf",
    ROOT / "figures" / "surrogate_patching.pdf": "figures/surrogate_patching.pdf",
    ROOT / "figures" / "causal_analysis_workflow.png": "figures/causal_analysis_workflow.png",
}


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"cannot package missing inputs: {missing}")
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(ARCHIVE, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for source, target in FILES.items():
            archive.write(source, target)
    with ZipFile(ARCHIVE) as archive:
        names = set(archive.namelist())
    required = set(FILES.values())
    if names != required:
        raise RuntimeError("archive content verification failed")
    print(f"wrote {ARCHIVE.relative_to(ROOT)} with {len(names)} files")


if __name__ == "__main__":
    main()
