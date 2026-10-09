from pathlib import Path
import subprocess

from oai_math_study.corpus import clean_text, parse_catalogue, text_words


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
