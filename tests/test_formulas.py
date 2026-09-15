import numpy as np
import pandas as pd
import pytest

from tarsel2 import formulas


def test_counters():
    matrix = pd.DataFrame(
        {
            "f1": [1, 0, 1],
            "f2": [1, 1, 0],
            "p1": [1, 1, 0],
            "p2": [0, 1, 0],
        },
        index=["a", "b", "c"],
    )
    labels = pd.Series({"f1": 1, "f2": 1, "p1": 0, "p2": 0})

    counts = formulas.counters(matrix, labels)
    assert counts.loc["a"].tolist() == [2.0, 0.0, 1.0, 1.0]
    assert counts.loc["b"].tolist() == [1.0, 1.0, 2.0, 0.0]
    assert counts.loc["c"].tolist() == [1.0, 1.0, 0.0, 2.0]


def test_all_formulas_are_computed(sample_matrix):
    scored = formulas.rank_matrix(sample_matrix)
    for name in formulas.FORMULAS:
        assert name in scored.columns
    assert not scored[formulas.FORMULAS].isna().all().any()


def test_fault_only_covered_by_failing_window_scores_highest(sample_matrix):
    scored = formulas.rank_matrix(sample_matrix)
    ranking = formulas.ranking(scored, "D_star")
    assert ranking.index[0] == "updown_counter_16"
    # A line covered by both windows is less suspicious.
    assert (
        scored.loc["updown_counter_16", "D_star"]
        > scored.loc["updown_counter_12", "D_star"]
    )


def test_optimal_p_matches_op1():
    """OPTIMAL_P must be a11 - a01 / (a01 + a00 + 1)."""
    counts = pd.DataFrame(
        {"aef": [3.0], "anf": [1.0], "aep": [2.0], "anp": [4.0]}, index=["x"]
    )
    expected = 3.0 - 2.0 / (2.0 + 4.0 + 1.0)
    assert formulas.score(counts).loc["x", "OPTIMAL_P"] == pytest.approx(expected)


def test_russel_rao_is_aef_over_total():
    counts = pd.DataFrame(
        {"aef": [2.0], "anf": [1.0], "aep": [3.0], "anp": [4.0]}, index=["x"]
    )
    assert formulas.score(counts).loc["x", "Russel_Rao"] == pytest.approx(2.0 / 10.0)


def test_exam_score_lower_for_top_ranked_line(sample_matrix):
    scored = formulas.rank_matrix(sample_matrix)
    top = formulas.exam_score(scored, "updown_counter_16", "D_star")
    other = formulas.exam_score(scored, "updown_counter_19", "D_star")
    assert top is not None and other is not None
    assert top < other


def test_exam_scores_ignores_unknown_lines(sample_matrix):
    scored = formulas.rank_matrix(sample_matrix)
    assert formulas.exam_score(scored, "does_not_exist", "D_star") is None
    assert formulas.exam_scores(scored, ["does_not_exist"]) == {}


def test_missing_error_row_raises():
    with pytest.raises(ValueError):
        formulas.split_error_row(pd.DataFrame({"a": [1]}))
