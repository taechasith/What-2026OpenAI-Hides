"""Parsing and provenance helpers for public, pinned corpus artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from html import unescape
import hashlib
from io import BytesIO
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Iterable

from pypdf import PdfReader


FAMILY_RE = re.compile(r"\*\*(?P<id>\d{3})\.\s*(?P<title>.*?)\*\*", re.DOTALL)
MANUSCRIPT_RE = re.compile(
    r"\[(?P<title>[^\]]+)\]\((?P<path>preprints/[^\n]+?\.pdf)\)", re.IGNORECASE
)
TRACE_RE = re.compile(
    r"\|\s*(?P<id>\d{3})\s*\|.*?\]\((?P<path>reasoning_traces/[^)]+?\.pdf)\)",
    re.IGNORECASE,
)
WORD_RE = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)?")
EXPECTED_UPSTREAM_COMMIT = "fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb"


@dataclass(frozen=True)
class Family:
    family_id: str
    title: str
    description: str
    manuscript_count: int
    lean_document: bool


@dataclass(frozen=True)
class Manuscript:
    family_id: str
    title: str
    pdf_path: str
    pdf_exists: bool
    pdf_bytes: int
    source_tex_files: int
    source_available: bool
    readme_available: bool


def clean_text(value: str) -> str:
    """Convert a catalogue HTML/Markdown fragment to conservative plain text."""
    value = unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("`", "").replace("*", "")
    return re.sub(r"\s+", " ", value).strip()


def text_words(value: str) -> int:
    return len(WORD_RE.findall(value))


def _run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def _git_bytes(root: Path, relative_path: str, ref: str = "HEAD") -> bytes:
    """Read a source blob, including blobs too deep for a Windows checkout."""
    return subprocess.check_output(["git", "-C", str(root), "show", f"{ref}:{relative_path}"])


def _tree(root: Path, ref: str = "HEAD") -> dict[str, int]:
    """Map each path in the immutable release tree to its Git-recorded size."""
    paths: dict[str, int] = {}
    for line in _run_git(root, "ls-tree", "-r", "-l", ref).splitlines():
        try:
            left, name = line.split("\t", 1)
            paths[name] = int(left.rsplit(maxsplit=1)[1])
        except (IndexError, ValueError):
            continue
    return paths


def tree_blobs(root: Path, ref: str = "HEAD") -> list[dict[str, object]]:
    """Return one metadata record for every immutable blob in ``ref``.

    ``-z`` avoids ambiguity from whitespace or non-ASCII path names and makes
    this work without materializing every upstream path on Windows.
    """
    payload = subprocess.check_output(
        ["git", "-C", str(root), "ls-tree", "-r", "-l", "-z", ref]
    )
    records: list[dict[str, object]] = []
    for entry in payload.split(b"\0"):
        if not entry:
            continue
        header, separator, raw_path = entry.partition(b"\t")
        fields = header.decode("ascii", errors="strict").split()
        if not separator or len(fields) != 4:
            raise ValueError("unexpected git ls-tree record")
        mode, object_type, blob_sha1, raw_size = fields
        if object_type != "blob":
            raise ValueError(f"tree entry is not a blob: {object_type}")
        path = raw_path.decode("utf-8", errors="surrogateescape")
        records.append(
            {
                "path": path,
                "mode": mode,
                "blob_sha1": blob_sha1,
                "bytes": int(raw_size),
            }
        )
    return records


def _artifact_role(path: str) -> str:
    """Assign every tree blob one deliberately structural artifact role."""
    parts = PurePosixPath(path).parts
    extension = PurePosixPath(path).suffix.lower()
    top_level = parts[0] if len(parts) > 1 else "(root)"
    if top_level == "lean":
        if len(parts) == 3 and parts[1] == "docs" and re.fullmatch(r"\d{3}\.md", parts[2]):
            return "lean_scope_document"
        if extension == ".lean":
            return "lean_source"
        if extension == ".json":
            return "lean_structured_metadata"
        return "lean_support_file"
    if top_level == "preprints":
        if extension == ".pdf":
            return "preprint_pdf"
        if extension == ".tex":
            return "preprint_tex_source"
        if extension == ".bib":
            return "preprint_bibliography"
        return "preprint_support_file"
    if top_level == "reasoning_traces":
        return "released_reasoning_summary_pdf" if extension == ".pdf" else "reasoning_trace_support_file"
    if len(parts) == 1:
        return "root_release_metadata" if path in {"README.md", "CONTENTS.md", "LICENSE", "history.md"} else "root_release_file"
    return "other_release_file"


def full_tree_inventory(
    root: Path,
    manuscripts: Iterable[Manuscript],
    traces: Iterable[dict[str, object]],
    ref: str = "HEAD",
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Index every release blob without copying third-party source contents."""
    linked_pdfs = {item.pdf_path for item in manuscripts}
    linked_directories: dict[str, set[str]] = {}
    for item in manuscripts:
        directory = PurePosixPath(item.pdf_path).parent.as_posix()
        linked_directories.setdefault(directory, set()).add(item.family_id)
    trace_paths = {str(item["trace_path"]) for item in traces}

    records: list[dict[str, object]] = []
    for item in tree_blobs(root, ref):
        path = str(item["path"])
        pure_path = PurePosixPath(path)
        top_level = pure_path.parts[0] if len(pure_path.parts) > 1 else "(root)"
        extension = pure_path.suffix.lower() or "(none)"
        family_ids: set[str] = set()
        for depth in range(1, len(pure_path.parts)):
            family_ids.update(linked_directories.get("/".join(pure_path.parts[:depth]), set()))
        sorted_family_ids = sorted(family_ids)
        if path in linked_pdfs:
            catalogue_relation = "catalogue_linked_pdf"
        elif sorted_family_ids:
            catalogue_relation = "catalogue_linked_preprint_directory"
        else:
            catalogue_relation = "not_catalogue_linked"
        records.append(
            {
                **item,
                "top_level": top_level,
                "extension": extension,
                "artifact_role": _artifact_role(path),
                "catalogue_relation": catalogue_relation,
                "catalogue_family_ids": ";".join(sorted_family_ids),
                "named_released_summary": path in trace_paths,
            }
        )

    paths = [str(item["path"]) for item in records]
    blob_ids = [str(item["blob_sha1"]) for item in records]
    if not records:
        raise RuntimeError("full-tree inventory is empty")
    if len(set(paths)) != len(paths):
        raise RuntimeError("full-tree inventory contains duplicate paths")
    if any(not re.fullmatch(r"[0-9a-f]{40}", blob_id) for blob_id in blob_ids):
        raise RuntimeError("full-tree inventory contains malformed Git blob identifiers")
    if any(int(item["bytes"]) < 0 for item in records):
        raise RuntimeError("full-tree inventory contains negative blob sizes")

    def grouped(field: str) -> list[dict[str, object]]:
        groups: dict[str, dict[str, int]] = {}
        for record in records:
            key = str(record[field])
            bucket = groups.setdefault(key, {"files": 0, "bytes": 0})
            bucket["files"] += 1
            bucket["bytes"] += int(record["bytes"])
        return [{field: key, **groups[key]} for key in sorted(groups)]

    return records, {
        "inventory_protocol": "FULL_TREE_INVENTORY_PROTOCOL.md",
        "inventory_classifier": "path-extension-roles-v1",
        "tree_blobs_indexed": len(records),
        "total_bytes": sum(int(item["bytes"]) for item in records),
        "unique_blob_object_ids": len(set(blob_ids)),
        "empty_blobs": sum(int(item["bytes"]) == 0 for item in records),
        "longest_path_characters": max(len(path) for path in paths),
        "named_released_summaries": sum(bool(item["named_released_summary"]) for item in records),
        "by_top_level": grouped("top_level"),
        "by_artifact_role": grouped("artifact_role"),
        "by_extension": grouped("extension"),
        "by_catalogue_relation": grouped("catalogue_relation"),
        "validation": {
            "path_unique": True,
            "all_blob_ids_are_40_hex_characters": True,
            "all_bytes_nonnegative": True,
            "coverage_fraction": 1.0,
        },
    }


def repository_manifest(root: Path) -> dict[str, object]:
    """Return source identifiers and validity evidence for a corpus Git tree."""
    required = ["README.md", "CONTENTS.md", "LICENSE"]
    commit = _run_git(root, "rev-parse", "HEAD")
    if commit != EXPECTED_UPSTREAM_COMMIT:
        raise RuntimeError(
            "unexpected upstream commit; expected "
            f"{EXPECTED_UPSTREAM_COMMIT}, found {commit}"
        )
    tree = _tree(root, commit)
    missing = [path for path in required if path not in tree]
    if missing:
        raise FileNotFoundError(f"not a corpus Git tree; missing {missing}")
    _run_git(root, "fsck", "--no-dangling", "--no-progress")
    return {
        "upstream_repository": "https://github.com/openai/math",
        "commit": commit,
        "tree": _run_git(root, "rev-parse", f"{commit}^{{tree}}"),
        "tree_blob_count": len(tree),
        "git_object_integrity": "git fsck --no-dangling --no-progress passed",
        "working_tree_note": (
            "Analysis reads Git blobs directly. Windows MAX_PATH can prevent "
            "materializing some deeply nested upstream paths in a working tree."
        ),
        "key_file_sha256": {
            path: hashlib.sha256(_git_bytes(root, path, commit)).hexdigest() for path in required
        },
        "license_observed": "Apache-2.0 (upstream LICENSE file)",
    }


def _family_segments(catalogue: str) -> Iterable[tuple[re.Match[str], str]]:
    matches = list(FAMILY_RE.finditer(catalogue))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(catalogue)
        yield match, catalogue[match.end() : end]


def _formalized_family_ids(tree: dict[str, int]) -> set[str]:
    return {
        Path(path).stem
        for path in tree
        if re.fullmatch(r"lean/docs/\d{3}\.md", path)
    }


def _source_metadata(tree: dict[str, int]) -> tuple[dict[str, int], set[str]]:
    tex_counts: dict[str, int] = {}
    readme_dirs: set[str] = set()
    for source_path in tree:
        parts = Path(source_path).parts
        if len(parts) < 3 or parts[0] != "preprints":
            continue
        manuscript_dir = "/".join(parts[:2])
        if parts[-1] == "README.md":
            readme_dirs.add(manuscript_dir)
        if source_path.endswith(".tex") and "vendor" not in parts:
            tex_counts[manuscript_dir] = tex_counts.get(manuscript_dir, 0) + 1
    return tex_counts, readme_dirs


def parse_catalogue(root: Path, ref: str = "HEAD") -> tuple[list[Family], list[Manuscript], list[dict[str, str]]]:
    """Parse every family and manuscript link from `CONTENTS.md`."""
    catalogue = _git_bytes(root, "CONTENTS.md", ref).decode("utf-8", errors="replace")
    tree = _tree(root, ref)
    formalized = _formalized_family_ids(tree)
    tex_counts, readme_dirs = _source_metadata(tree)
    families: list[Family] = []
    manuscripts: list[Manuscript] = []
    warnings: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for match, segment in _family_segments(catalogue):
        family_id = match.group("id")
        if family_id in seen_ids:
            warnings.append({"kind": "duplicate_family_id", "detail": family_id})
            continue
        seen_ids.add(family_id)
        links = list(MANUSCRIPT_RE.finditer(segment))
        description = clean_text(segment[: links[0].start()] if links else segment)
        families.append(
            Family(
                family_id=family_id,
                title=clean_text(match.group("title")),
                description=description,
                manuscript_count=len(links),
                lean_document=family_id in formalized,
            )
        )
        if not links:
            warnings.append({"kind": "family_without_manuscript_link", "detail": family_id})
        for link in links:
            rel = Path(link.group("path"))
            rel_string = rel.as_posix()
            directory = rel.parent.as_posix()
            if rel_string not in tree:
                warnings.append({"kind": "missing_linked_pdf", "detail": rel_string})
            tex_count = tex_counts.get(directory, 0)
            manuscripts.append(
                Manuscript(
                    family_id=family_id,
                    title=clean_text(link.group("title")),
                    pdf_path=rel_string,
                    pdf_exists=rel_string in tree,
                    pdf_bytes=tree.get(rel_string, 0),
                    source_tex_files=tex_count,
                    source_available=tex_count > 0,
                    readme_available=directory in readme_dirs,
                )
            )
    return families, manuscripts, warnings


def parse_traces(root: Path, ref: str = "HEAD") -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    """Extract transparent descriptive measurements from released summaries only."""
    readme = _git_bytes(root, "README.md", ref).decode("utf-8", errors="replace")
    tree = _tree(root, ref)
    traces: list[dict[str, object]] = []
    warnings: list[dict[str, str]] = []
    marker_patterns = {
        "attempt_mentions": r"\battempt\w*\b",
        "verify_mentions": r"\bverif\w*\b",
        "lemma_mentions": r"\blemma\w*\b",
        "proof_mentions": r"\bproof\w*\b",
        "error_fail_mentions": r"\b(?:error|fail\w*)\b",
    }
    for match in TRACE_RE.finditer(readme):
        rel_string = Path(match.group("path")).as_posix()
        record: dict[str, object] = {
            "family_id": match.group("id"),
            "trace_path": rel_string,
            "pdf_exists": rel_string in tree,
            "pages": 0,
            "extracted_words": 0,
            **{key: 0 for key in marker_patterns},
        }
        if rel_string not in tree:
            warnings.append({"kind": "missing_trace_pdf", "detail": rel_string})
            traces.append(record)
            continue
        try:
            reader = PdfReader(BytesIO(_git_bytes(root, rel_string, ref)))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            record["pages"] = len(reader.pages)
            record["extracted_words"] = text_words(text)
            for key, pattern in marker_patterns.items():
                record[key] = len(re.findall(pattern, text, flags=re.IGNORECASE))
        except Exception as exc:
            warnings.append(
                {"kind": "trace_pdf_extraction_failure", "detail": f"{rel_string}: {type(exc).__name__}"}
            )
        traces.append(record)
    return traces, warnings


def rows(items: Iterable[object]) -> list[dict[str, object]]:
    return [asdict(item) if hasattr(item, "__dataclass_fields__") else dict(item) for item in items]
