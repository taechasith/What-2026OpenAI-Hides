from pathlib import Path
import subprocess

import pytest

from oai_math_study.corpus import clean_text, full_tree_inventory, parse_catalogue, repository_manifest, text_words


def test_clean_text_removes_markup():
    assert clean_text("<i>R</i> &amp; $`x`$") == "R & $x$"
    assert text_words("A well-formed proof") == 3


def test_parser_fixture(tmp_path: Path):
    (tmp_path / "lean" / "docs").mkdir(parents=True)
    (tmp_path / "lean" / "docs" / "001.md").write_text("proof", encoding="utf-8")
    (tmp_path / "preprints" / "alpha").mkdir(parents=True)
    (tmp_path / "preprints" / "alpha" / "CAT(0)-paper.pdf").write_bytes(b"%PDF")
    (tmp_path / "preprints" / "alpha" / "source.tex").write_text("x", encoding="utf-8")
    (tmp_path / "CONTENTS.md").write_text(
        "**001. <i>First</i> family.** Description one.\n"
        "[Paper title](preprints/alpha/CAT(0)-paper.pdf)\nAbstract.\n"
        "**002. Second family.** Description two.\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "fixture"], check=True)
    families, manuscripts, warnings = parse_catalogue(tmp_path)
    assert [family.family_id for family in families] == ["001", "002"]
    assert families[0].lean_document is True
    assert families[0].manuscript_count == 1
    assert manuscripts[0].source_available is True
    assert warnings and warnings[0]["kind"] == "family_without_manuscript_link"


def test_full_tree_inventory_covers_every_blob(tmp_path: Path):
    (tmp_path / "lean" / "docs").mkdir(parents=True)
    (tmp_path / "lean" / "docs" / "001.md").write_text("scope", encoding="utf-8")
    (tmp_path / "lean" / "proof.lean").write_text("theorem x : True := trivial", encoding="utf-8")
    (tmp_path / "preprints" / "alpha" / "nested").mkdir(parents=True)
    (tmp_path / "preprints" / "alpha" / "paper.pdf").write_bytes(b"%PDF")
    (tmp_path / "preprints" / "alpha" / "nested" / "source.tex").write_text("\\documentclass{article}", encoding="utf-8")
    (tmp_path / "CONTENTS.md").write_text(
        "**001. First family.** Description.\n[Paper](preprints/alpha/paper.pdf)\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "fixture"], check=True)
    _, manuscripts, _ = parse_catalogue(tmp_path)
    inventory, summary = full_tree_inventory(tmp_path, manuscripts, [])
    roles = {item["path"]: item["artifact_role"] for item in inventory}
    relation = {item["path"]: item["catalogue_relation"] for item in inventory}
    assert summary["tree_blobs_indexed"] == len(inventory) == 5
    assert summary["validation"]["coverage_fraction"] == 1.0
    assert roles["lean/docs/001.md"] == "lean_scope_document"
    assert roles["lean/proof.lean"] == "lean_source"
    assert roles["preprints/alpha/nested/source.tex"] == "preprint_tex_source"
    assert relation["preprints/alpha/paper.pdf"] == "catalogue_linked_pdf"
    assert relation["preprints/alpha/nested/source.tex"] == "catalogue_linked_preprint_directory"


def test_repository_manifest_rejects_an_unpinned_checkout(tmp_path: Path):
    for name in ("README.md", "CONTENTS.md", "LICENSE"):
        (tmp_path / name).write_text(name, encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "fixture"], check=True)
    with pytest.raises(RuntimeError, match="unexpected upstream commit"):
        repository_manifest(tmp_path)
