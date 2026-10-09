"""Run the frozen public-artifact analysis and write all derived outputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import mannwhitneyu

from .corpus import parse_catalogue, parse_traces, repository_manifest, rows


SEED = 20261009


def write_csv(path: Path, values: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(values[0]) if values else ["kind", "detail"]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(values)


def coverage_stats(families: list[dict[str, object]], manuscripts: list[dict[str, object]]) -> dict[str, object]:
    positive = [int(item["manuscript_count"]) for item in families if bool(item["lean_document"])]
    negative = [int(item["manuscript_count"]) for item in families if not bool(item["lean_document"])]
    if not positive or not negative:
        raise ValueError("Lean-document comparison needs both groups")
    u_result = mannwhitneyu(positive, negative, alternative="two-sided", method="asymptotic")
    u = float(u_result.statistic)
    n_pos, n_neg = len(positive), len(negative)
    effect = (2 * u / (n_pos * n_neg)) - 1
    observed = float(np.mean(positive) - np.mean(negative))
    all_values = np.array(positive + negative, dtype=float)
    generator = np.random.default_rng(SEED)
    exceed = 0
    draws = 10_000
    for _ in range(draws):
        selected = generator.choice(len(all_values), size=n_pos, replace=False)
        mask = np.zeros(len(all_values), dtype=bool)
        mask[selected] = True
        difference = float(all_values[mask].mean() - all_values[~mask].mean())
        exceed += abs(difference) >= abs(observed) - 1e-12
    linked_pdfs = sum(bool(item["pdf_exists"]) for item in manuscripts)
    sources = sum(bool(item["source_available"]) for item in manuscripts)
    return {
        "seed": SEED,
        "families": len(families),
        "manuscripts": len(manuscripts),
        "lean_document_families": n_pos,
        "lean_document_proportion": n_pos / len(families),
        "linked_pdfs_present": linked_pdfs,
        "source_available_manuscripts": sources,
        "comparison": {
            "outcome": "catalogue-linked manuscript count per family",
            "group_1": "Lean document present",
            "group_0": "Lean document absent",
            "group_1_n": n_pos,
            "group_0_n": n_neg,
            "group_1_median": float(np.median(positive)),
            "group_0_median": float(np.median(negative)),
            "mean_difference": observed,
            "mann_whitney_u": u,
            "mann_whitney_asymptotic_p": float(u_result.pvalue),
            "rank_biserial": effect,
            "permutation_draws": draws,
            "permutation_two_sided_p": (exceed + 1) / (draws + 1),
            "interpretation": "Associational artifact comparison; families are not independent model runs.",
        },
    }


def make_figures(
    figures: Path,
    families: list[dict[str, object]],
    manuscripts: list[dict[str, object]],
    traces: list[dict[str, object]],
) -> None:
    figures.mkdir(parents=True, exist_ok=True)
    teal, orange, slate = "#007C91", "#E58606", "#4C566A"
    total = len(families)
    coverage = [
        ("Catalogue families", total),
        ("Lean-document families", sum(bool(row["lean_document"]) for row in families)),
        ("Linked manuscript PDFs", sum(bool(row["pdf_exists"]) for row in manuscripts)),
        ("Manuscripts with TeX", sum(bool(row["source_available"]) for row in manuscripts)),
        ("Released abridged summaries", len(traces)),
    ]
    fig, ax = plt.subplots(figsize=(8.3, 4.5))
    labels, values = zip(*coverage)
    bars = ax.barh(labels[::-1], values[::-1], color=[teal, teal, orange, orange, slate][::-1])
    for bar, value in zip(bars, values[::-1]):
        ax.text(bar.get_width() + max(total * 0.01, 1), bar.get_y() + bar.get_height() / 2, str(value), va="center", fontsize=9)
    ax.set_xlabel("Count (units differ; see caption)")
    ax.set_title("Public artifact coverage in the pinned release")
    ax.set_xlim(0, max(total, len(manuscripts)) * 1.11)
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(figures / f"artifact_coverage.{suffix}", dpi=240, bbox_inches="tight")
    plt.close(fig)

    counts = [int(row["manuscript_count"]) for row in families]
    fig, ax = plt.subplots(figsize=(7.3, 4.4))
    bins = np.arange(0.5, max(counts) + 1.6, 1)
    ax.hist(counts, bins=bins, color=teal, edgecolor="white")
    ax.set_xlabel("Linked manuscripts per result family")
    ax.set_ylabel("Families")
    ax.set_title("Catalogue family size distribution")
    ax.set_xticks(range(1, max(counts) + 1))
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(figures / f"family_size_distribution.{suffix}", dpi=240, bbox_inches="tight")
    plt.close(fig)

    ordered = sorted(traces, key=lambda row: int(row["extracted_words"]))
    fig, ax = plt.subplots(figsize=(8.3, 4.7))
    ax.barh([row["family_id"] for row in ordered], [int(row["extracted_words"]) for row in ordered], color=slate)
    ax.set_xlabel("Extracted word-like tokens")
    ax.set_ylabel("Result family")
    ax.set_title("Released abridged reasoning summaries: text volume")
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(figures / f"trace_text_volume.{suffix}", dpi=240, bbox_inches="tight")
    plt.close(fig)


def write_latex_generated(output: Path, stats: dict[str, object], traces: list[dict[str, object]]) -> None:
    generated = output / "paper" / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    comparison = stats["comparison"]
    trace_words = [int(row["extracted_words"]) for row in traces]
    trace_pages = [int(row["pages"]) for row in traces]
    macros = [
        f"\\newcommand{{\\TotalFamilies}}{{{stats['families']}}}",
        f"\\newcommand{{\\TotalManuscripts}}{{{stats['manuscripts']}}}",
        f"\\newcommand{{\\LeanFamilies}}{{{stats['lean_document_families']}}}",
        f"\\newcommand{{\\TraceCount}}{{{len(traces)}}}",
        f"\\newcommand{{\\LeanShare}}{{{100 * stats['lean_document_proportion']:.1f}\\%}}",
        f"\\newcommand{{\\MannWhitneyP}}{{{comparison['mann_whitney_asymptotic_p']:.3f}}}",
        f"\\newcommand{{\\PermutationP}}{{{comparison['permutation_two_sided_p']:.3f}}}",
        f"\\newcommand{{\\RankBiserial}}{{{comparison['rank_biserial']:.2f}}}",
        f"\\newcommand{{\\TraceMinWords}}{{{min(trace_words):,}}}",
        f"\\newcommand{{\\TraceMaxWords}}{{{max(trace_words):,}}}",
        f"\\newcommand{{\\TraceMinPages}}{{{min(trace_pages)}}}",
        f"\\newcommand{{\\TraceMaxPages}}{{{max(trace_pages)}}}",
    ]
    (generated / "results_macros.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")
    linebreak = r"\\"
    rows_tex = [
        "\\begin{tabular}{lr}",
        "\\toprule",
        "Artifact & Count " + linebreak,
        "\\midrule",
        f"Result families & {stats['families']} {linebreak}",
        f"Catalogue-linked manuscripts & {stats['manuscripts']} {linebreak}",
        f"Families with Lean document & {stats['lean_document_families']} {linebreak}",
        f"Linked manuscript PDFs present & {stats['linked_pdfs_present']} {linebreak}",
        f"Manuscripts with TeX source & {stats['source_available_manuscripts']} {linebreak}",
        f"Released abridged summaries & {len(traces)} {linebreak}",
        "\\bottomrule",
        "\\end{tabular}",
    ]
    (generated / "coverage_table.tex").write_text("\n".join(rows_tex) + "\n", encoding="utf-8")


def run(root: Path, corpus: Path) -> dict[str, object]:
    output = root / "data" / "derived"
    output.mkdir(parents=True, exist_ok=True)
    manifest = repository_manifest(corpus)
    families_objects, manuscripts_objects, warnings = parse_catalogue(corpus)
    traces, trace_warnings = parse_traces(corpus)
    warnings.extend(trace_warnings)
    families, manuscripts = rows(families_objects), rows(manuscripts_objects)
    if not families or not manuscripts:
        raise RuntimeError("Parser produced an empty inclusion set")
    if len({row["family_id"] for row in families}) != len(families):
        raise RuntimeError("Duplicate family identifiers after parsing")
    if not traces:
        raise RuntimeError("No released trace entries parsed")
    manifest.update({
        "parsed_families": len(families),
        "parsed_manuscripts": len(manuscripts),
        "parsed_released_traces": len(traces),
    })
    stats = coverage_stats(families, manuscripts)
    write_csv(output / "families.csv", families)
    write_csv(output / "manuscripts.csv", manuscripts)
    write_csv(output / "trace_metrics.csv", traces)
    write_csv(output / "parse_warnings.csv", warnings)
    (output / "corpus_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output / "summary_statistics.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    figures = root / "figures"
    make_figures(figures, families, manuscripts, traces)
    write_latex_generated(root, stats, traces)
    return {"manifest": manifest, "stats": stats, "warnings": warnings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path("external/openai-math-full"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = run(args.root.resolve(), args.corpus.resolve())
    print(json.dumps({"manifest": result["manifest"], "stats": result["stats"]}, indent=2))


if __name__ == "__main__":
    main()
