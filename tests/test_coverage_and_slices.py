import os

import pandas as pd
import pytest

from tarsel2 import compare, coverage, slices

URG_SAMPLE = os.path.join(os.path.dirname(__file__), "fixtures", "urg_sample")


# --------------------------------------------------------------- coverage


def test_parse_modinfo_skips_testbench_modules(tmp_path):
    path = os.path.join(
        URG_SAMPLE, "CoverageReport0_10.report", "modinfo.txt"
    )
    entries = coverage.parse_modinfo(path, testbench="updown_counter_tb.v")
    modules = {module for module, _, _ in entries}
    assert "updown_counter" in modules
    assert "updown_counter_tb" not in modules


def test_is_testbench_module():
    assert coverage.is_testbench_module("updown_counter_tb")
    assert coverage.is_testbench_module("TB_TOP")
    assert not coverage.is_testbench_module("updown_counter")


def test_module_names_in_and_mapping(tmp_path):
    src = tmp_path / "updown_counter_buggy.v"
    src.write_text("module updown_counter;\nendmodule\n")
    assert coverage.module_names_in(str(src)) == ["updown_counter"]
    mapping = coverage.build_module_to_file([str(src)])
    assert mapping["updown_counter"] == "updown_counter_buggy"


# ---------------------------------------------------------------- compare


def _dump(path, rows):
    path.write_text("time,count\n" + "".join(f"{t},{v}\n" for t, v in rows))


def test_compare_detects_divergence(tmp_path):
    golden = tmp_path / "golden.txt"
    observed = tmp_path / "output.txt"
    _dump(golden, [(10, 1), (20, 2), (30, 3)])
    _dump(observed, [(10, 1), (20, 9), (30, 3)])

    errors = compare.error_series(str(golden), str(observed))
    assert list(errors.index) == [10, 20, 30]
    assert errors.tolist() == [0, 1, 0]


def test_compare_ignores_extra_rows(tmp_path):
    golden = tmp_path / "golden.txt"
    observed = tmp_path / "output.txt"
    _dump(golden, [(10, 1), (20, 2)])
    _dump(observed, [(10, 1), (20, 2), (30, 3)])
    errors = compare.error_series(str(golden), str(observed))
    assert errors.tolist() == [0, 0]


# ----------------------------------------------------------------- slices


def test_uniform_slices_labels_window_containing_divergence():
    errors = pd.Series([0, 0, 1, 1], index=[0, 10, 20, 30])
    out = slices.uniform_slices(errors, time_step=10, slice_num=10)
    labels = {(t1, t2): label for (t1, t2), label in out}
    assert labels[(0, 10)] == 0
    assert labels[(20, 30)] == 1


def test_onset_slices_centres_on_onset():
    errors = pd.Series([0, 0, 1, 1, 1], index=[0, 10, 20, 30, 40])
    out = slices.onset_slices(errors, num_steps=2, n_windows=3, n_samples=200)
    assert out, "expected at least one window"
    assert any(label == 1 for _, label in out), "onset window must be labelled failing"


def test_onset_slices_without_divergence_is_single_passing_window():
    errors = pd.Series([0, 0, 0], index=[0, 10, 20])
    out = slices.onset_slices(errors)
    assert out == [((0, 20), 0)]


def test_build_slices_rejects_unknown_strategy():
    errors = pd.Series([0, 1], index=[0, 10])

    class Cfg:
        slice_strategy = "nope"
        time_step = 10
        slice_num = 5
        window_steps = 2
        n_windows = 2
        n_samples = 10
        start_time = 0

    with pytest.raises(ValueError):
        slices.build_slices(Cfg(), errors)
