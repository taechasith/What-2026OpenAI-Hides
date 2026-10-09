"""Parsing and provenance helpers for public, pinned corpus artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from html import unescape
import hashlib
from io import BytesIO
from pathlib import Path
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


def _git_bytes(root: Path, relative_path: str) -> bytes:
    """Read a source blob, including blobs too deep for a Windows checkout."""
    return subprocess.check_output(["git", "-C", str(root), "show", f"HEAD:{relative_path}"])


def _tree(root: Path) -> dict[str, int]:
    """Map each path in the immutable release tree to its Git-recorded size."""
    paths: dict[str, int] = {}
    for line in _run_git(root, "ls-tree", "-r", "-l", "HEAD").splitlines():
        try:
            left, name = line.split("\t", 1)
            paths[name] = int(left.rsplit(maxsplit=1)[1])
        except (IndexError, ValueError):
            continue
    return paths


def repository_manifest(root: Path) -> dict[str, object]:
    """Return source identifiers and validity evidence for a corpus Git tree."""
    required = ["README.md", "CONTENTS.md", "LICENSE"]
    commit = _run_git(root, "rev-parse", "HEAD")
    tree = _tree(root)
    missing = [path for path in required if path not in tree]
    if missing:
        raise FileNotFoundError(f"not a corpus Git tree; missing {missing}")
    _run_git(root, "fsck", "--no-dangling", "--no-progress")
    return {
        "upstream_repository": "https://github.com/openai/math",
        "commit": commit,
        "tree_blob_count": len(tree),
        "git_object_integrity": "git fsck --no-dangling --no-progress passed",
        "working_tree_note": (
            "Analysis reads Git blobs directly. Windows MAX_PATH can prevent "
            "materializing some deeply nested upstream paths in a working tree."
        ),
        "key_file_sha256": {
            path: hashlib.sha256(_git_bytes(root, path)).hexdigest() for path in required
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


def parse_catalogue(root: Path) -> tuple[list[Family], list[Manuscript], list[dict[str, str]]]:
    """Parse every family and manuscript link from `CONTENTS.md`."""
    catalogue = _git_bytes(root, "CONTENTS.md").decode("utf-8", errors="replace")
    tree = _tree(root)
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


def parse_traces(root: Path) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    """Extract transparent descriptive measurements from released summaries only."""
    readme = _git_bytes(root, "README.md").decode("utf-8", errors="replace")
    tree = _tree(root)
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
            reader = PdfReader(BytesIO(_git_bytes(root, rel_string)))
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
