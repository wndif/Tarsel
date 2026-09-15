"""End-to-end scoring over the URG fixture reports (no VCS required)."""

import os

import pandas as pd
import pytest

from tarsel2 import coverage, formulas
from tarsel2.config import ProjectConfig
from tarsel2.pipeline import localize_from_reports

URG_SAMPLE = os.path.join(
    os.path.dirname(__file__), "fixtures", "urg_sample"
)


def make_config(tmp_path, **overrides):
    kwargs = dict(
        project_name="updown_counter",
        project_dir=str(tmp_path),
        source_files=["updown_counter_buggy.v"],
        testbench="updown_counter_tb.v",
        golden_output="golden_output.txt",
        fault_lines=["updown_counter_buggy_16"],
        work_dir=str(tmp_path / "work"),
    )
    kwargs.update(overrides)
    return ProjectConfig(**kwargs)


def test_build_matrix_from_urg_reports():
    matrix = coverage.build_matrix(
        URG_SAMPLE, [(0, 10), (10, 20)], testbench="updown_counter_tb.v"
    )

    assert list(matrix.columns) == ["0_10", "10_20"]
    # Testbench module rows are dropped.
    assert not any("tb" in idx for idx in matrix.index)
    # Faulty line: uncovered in the first window, covered in the second.
    assert int(matrix.loc["updown_counter_16", "0_10"]) == 0
    assert int(matrix.loc["updown_counter_16", "10_20"]) == 1
    # A line that always executes.
    assert int(matrix.loc["updown_counter_12", "0_10"]) == 1


def test_module_rows_renamed_to_files(tmp_path):
    matrix = coverage.build_matrix(
        URG_SAMPLE, [(0, 10), (10, 20)], testbench="updown_counter_tb.v"
    )
    mapping = {"updown_counter": "updown_counter_buggy"}
    renamed = coverage.rename_modules_to_files(matrix, mapping, "updown_counter_tb")

    assert "updown_counter_buggy_16" in renamed.index
    assert "updown_counter_16" not in renamed.index


def test_localize_from_reports_ranks_fault_first(tmp_path):
    # The module -> file mapping is derived from the declared module names,
    # so the source must exist next to the project.
    (tmp_path / "updown_counter_buggy.v").write_text(
        "module updown_counter;\nendmodule\n"
    )
    config = make_config(tmp_path)
    result = localize_from_reports(
        config, [(0, 10), (10, 20)], [0, 1], report_dir=URG_SAMPLE
    )

    top = list(result.ranking["D_star"].index)
    assert top[0] == "updown_counter_buggy_16"

    scored = result.scored
    assert scored.loc["updown_counter_buggy_16", "aef"] == 1
    assert scored.loc["updown_counter_buggy_16", "aep"] == 0

    # EXAM: the faulty line is found before half the code is inspected.
    assert result.exam["D_star"] <= 0.5
