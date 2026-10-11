from oai_math_study.v2_proof_extraction import STATEMENT_RE, _clean_tex, _node_id


def test_node_identifiers_are_stable_and_location_sensitive() -> None:
    assert _node_id("preprints/a.tex", 4, "lemma") == _node_id("preprints/a.tex", 4, "lemma")
    assert _node_id("preprints/a.tex", 4, "lemma") != _node_id("preprints/a.tex", 5, "lemma")


def test_tex_environment_and_cleaning_are_conservative() -> None:
    assert STATEMENT_RE.search(r"\begin{theorem}")
    assert STATEMENT_RE.search(r"\begin{proof}")
    assert _clean_tex("\\emph{By contradiction} % ignored\n") == "By contradiction"
