"""Extract provenance-preserving proof-structure candidates from a pinned corpus.

This is deliberately conservative. It records explicit TeX references as
source references, not mathematical entailment, and records lexical motif
matches as rule-based, unvalidated candidates. It never uses a Windows working
tree as the source of truth: content is read from immutable Git blobs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Iterable

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .corpus import EXPECTED_UPSTREAM_COMMIT, repository_manifest, tree_blobs


STATEMENT_RE = re.compile(
    r"\\begin\{(?P<kind>theorem|lemma|proposition|corollary|definition|remark|proof)\}",
    re.IGNORECASE,
)
LABEL_RE = re.compile(r"\\label\{(?P<label>[^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|eqref|autoref|(?:C|c)ref)\{(?P<label>[^}]+)\}")
MOTIF_RULES = {
    "contradiction": re.compile(r"\b(?:contradiction|contrary|suppose not)\b", re.I),
    "induction": re.compile(r"\b(?:induction|inductive|induct on)\b", re.I),
    "case_split": re.compile(r"\b(?:case[s]?|it suffices to consider)\b", re.I),
    "construction": re.compile(r"\b(?:construct|construction|define|let us define)\b", re.I),
    "reduction": re.compile(r"\b(?:reduce|reduction|it suffices to show)\b", re.I),
    "invariant": re.compile(r"\b(?:invariant|preserved)\b", re.I),
    "limit": re.compile(r"\b(?:compactness|converge|convergence|limit)\b", re.I),
    "equivalence": re.compile(r"\b(?:equivalent|equivalence|isomorphic|isomorphism)\b", re.I),
}


def _node_id(path: str, start: int, kind: str) -> str:
    digest = hashlib.sha256(f"{path}:{start}:{kind}".encode("utf-8")).hexdigest()[:16]
    return f"v2-{kind}-{digest}"


def _document_id(path: str) -> str:
    parts = PurePosixPath(path).parts
    return "/".join(parts[:2]) if len(parts) >= 2 else path


def _clean_tex(value: str) -> str:
    value = re.sub(r"%.*$", "", value, flags=re.M)
    # Preserve human-readable one-level command arguments (for example
    # ``\emph{by contradiction}``) before dropping remaining control words.
    value = re.sub(r"\\[A-Za-z@]+(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\[A-Za-z@]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _blob_texts(corpus: Path, blob_ids: Iterable[str]) -> Iterable[str]:
    """Yield immutable Git blob content through one batch process."""
    process = subprocess.Popen(
        ["git", "-C", str(corpus), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin and process.stdout
    try:
        for blob_id in blob_ids:
            process.stdin.write((blob_id + "\n").encode("ascii"))
            process.stdin.flush()
            header = process.stdout.readline().decode("ascii", errors="strict").strip().split()
            if len(header) != 3 or header[1] != "blob":
                raise RuntimeError(f"cannot read blob {blob_id}: {' '.join(header)}")
            size = int(header[2])
            payload = process.stdout.read(size)
            process.stdout.read(1)
            yield payload.decode("utf-8", errors="replace")
    finally:
        if process.stdin:
            process.stdin.close()
        process.wait(timeout=120)
    if process.returncode:
        raise RuntimeError(process.stderr.read().decode("utf-8", errors="replace"))


def _catalogue_relations(root: Path) -> dict[str, tuple[str, str]]:
    """Map each source path to its prior inventory family relation."""
    inventory = root / "data" / "derived" / "full_tree_inventory.csv"
    relations: dict[str, tuple[str, str]] = {}
    with inventory.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["artifact_role"] == "preprint_tex_source":
                relations[row["path"]] = (
                    row["catalogue_family_ids"] or "unlinked",
                    row["catalogue_relation"],
                )
    return relations


def extract(root: Path, corpus: Path) -> dict[str, object]:
    manifest = repository_manifest(corpus)
    if manifest["commit"] != EXPECTED_UPSTREAM_COMMIT:
        raise RuntimeError("unexpected corpus commit")
    relations = _catalogue_relations(root)
    candidates = [
        item for item in tree_blobs(corpus, str(manifest["commit"]))
        if str(item["path"]).startswith("preprints/") and str(item["path"]).lower().endswith(".tex")
    ]
    candidates.sort(key=lambda item: str(item["path"]))
    nodes: list[dict[str, object]] = []
    references: list[dict[str, object]] = []
    motifs: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    label_nodes: dict[tuple[str, str], str] = {}
    pending_refs: list[tuple[dict[str, object], str]] = []

    for item, content in zip(candidates, _blob_texts(corpus, [str(x["blob_sha1"]) for x in candidates])):
        path, blob = str(item["path"]), str(item["blob_sha1"])
        family_id, relation = relations.get(path, ("unlinked", "not_inventory_matched"))
        lines = content.splitlines()
        starts = [
            (index, match)
            for index, line in enumerate(lines, 1)
            if (match := STATEMENT_RE.search(line))
        ]
        if not starts:
            exclusions.append({"source_commit": manifest["commit"], "path": path, "blob_sha1": blob, "reason": "no_candidate_environment"})
            continue
        for index, (start, match) in enumerate(starts):
            end = starts[index + 1][0] - 1 if index + 1 < len(starts) else len(lines)
            kind = match.group("kind").lower()
            node_id = _node_id(path, start, kind)
            segment = "\n".join(lines[start - 1 : end])
            node = {
                "node_id": node_id,
                "source_commit": manifest["commit"],
                "document_id": _document_id(path),
                "result_family_ids": family_id,
                "catalogue_relation": relation,
                "path": path,
                "blob_sha1": blob,
                "line_start": start,
                "line_end": end,
                "node_kind": kind,
                "extraction_method": "deterministic_tex_environment_v1",
                "verification_status": "source_extracted_not_mathematically_verified",
                "confidence": "high_for_literal_environment_match",
            }
            nodes.append(node)
            document_id = _document_id(path)
            for label in LABEL_RE.findall(segment):
                label_nodes.setdefault((document_id, label), node_id)
            for label in REF_RE.findall(segment):
                pending_refs.append((node, label))
            plain = _clean_tex(segment)
            for name, rule in MOTIF_RULES.items():
                if rule.search(plain):
                    motifs.append({
                        "node_id": node_id,
                        "source_commit": manifest["commit"],
                        "document_id": _document_id(path),
                        "result_family_ids": family_id,
                        "path": path,
                        "line_start": start,
                        "line_end": end,
                        "motif": name,
                        "extraction_method": f"lexical_rule_v1:{rule.pattern}",
                        "verification_status": "inferred_not_human_validated",
                        "confidence": "rule_based_unvalidated",
                    })
    unresolved = 0
    duplicate_references = 0
    seen_edge_ids: set[str] = set()
    for source, label in pending_refs:
        target = label_nodes.get((str(source["document_id"]), label))
        if not target:
            unresolved += 1
            continue
        edge_id = hashlib.sha256(f"{source['node_id']}->{target}:{label}".encode()).hexdigest()[:20]
        if edge_id in seen_edge_ids:
            duplicate_references += 1
            continue
        seen_edge_ids.add(edge_id)
        references.append({
            "edge_id": edge_id,
            "source_node_id": source["node_id"],
            "target_node_id": target,
            "source_commit": source["source_commit"],
            "document_id": source["document_id"],
            "result_family_ids": source["result_family_ids"],
            "edge_type": "explicit_source_ref",
            "reference_label": label,
            "extraction_method": "deterministic_tex_ref_v1",
            "verification_status": "literal_reference_not_entailment",
            "confidence": "high_for_literal_reference_match",
        })
    output = root / "data" / "derived" / "v2"
    output.mkdir(parents=True, exist_ok=True)
    for name, values in (("proof_nodes", nodes), ("proof_edges", references), ("proof_motifs", motifs)):
        pd.DataFrame(values).to_parquet(output / f"{name}.parquet", index=False)
    pd.DataFrame(exclusions).to_csv(output / "proof_extraction_exclusions.csv", index=False)
    summary = {
        "run_type": "exploratory_rule_based_proof_structure_extraction",
        "source_commit": manifest["commit"],
        "source_tree": manifest["tree"],
        "source_files_considered": len(candidates),
        "proof_nodes": len(nodes),
        "explicit_source_edges": len(references),
        "unresolved_reference_labels": unresolved,
        "duplicate_explicit_references_collapsed": duplicate_references,
        "inferred_motif_records": len(motifs),
        "motif_counts": dict(sorted(Counter(row["motif"] for row in motifs).items())),
        "files_without_candidate_environment": len(exclusions),
        "limitations": [
            "Literal TeX environments and references are not proof correctness or mathematical entailment.",
            "Motifs are lexical rule matches, not semantic or human validation.",
            "This run does not create formal counterfactual cases or execute model interventions.",
        ],
    }
    (output / "proof_extraction_manifest.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    generated = root / "paper" / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    (generated / "v2_proof_macros.tex").write_text(
        "\n".join(
            [
                rf"\newcommand{{\VTwoTexFiles}}{{{len(candidates):,}}}",
                rf"\newcommand{{\VTwoProofNodes}}{{{len(nodes):,}}}",
                rf"\newcommand{{\VTwoExplicitEdges}}{{{len(references):,}}}",
                rf"\newcommand{{\VTwoMotifRecords}}{{{len(motifs):,}}}",
                rf"\newcommand{{\VTwoUnresolvedRefs}}{{{unresolved:,}}}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    motif_counts = Counter(row["motif"] for row in motifs)
    figure, axis = plt.subplots(figsize=(7.2, 3.7))
    labels = list(sorted(motif_counts))
    values = [motif_counts[label] for label in labels]
    axis.bar(labels, values, color="#007C91")
    axis.set_ylabel("Rule-based candidate records")
    axis.set_title("Exploratory lexical motif candidates in pinned TeX sources")
    axis.tick_params(axis="x", rotation=35)
    figure.tight_layout()
    for suffix in ("png", "pdf"):
        figure.savefig(root / "figures" / f"v2_proof_motifs.{suffix}", dpi=240, bbox_inches="tight")
    plt.close(figure)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--corpus", type=Path, default=Path("external/openai-math-full"))
    args = parser.parse_args()
    print(json.dumps(extract(args.root.resolve(), args.corpus.resolve()), indent=2))


if __name__ == "__main__":
    main()
