import pandas as pd

from tarsel2.optimizers import CanalOptimizer, MSSOptimizer, SpanMergeOptimizer, build_optimizers


def _matrix():
    data = {
        "0_10": [1, 0, 1],
        "10_20": [1, 1, 0],
        "20_30": [0, 1, 1],
        "30_40": [1, 1, 0],
    }
    frame = pd.DataFrame(data, index=["a", "b", "c"])
    frame.loc["error"] = [0, 1, 1, 0]
    return frame


def test_canal_truncates_after_first_failure():
    out = CanalOptimizer().apply(_matrix())
    assert list(out.columns) == ["0_10", "10_20"]


def test_canal_keeps_everything_without_failure():
    frame = _matrix()
    frame.loc["error"] = [0, 0, 0, 0]
    assert list(CanalOptimizer().apply(frame).columns) == list(frame.columns)


def test_mss_drops_misleading_passing_window():
    out = MSSOptimizer(alpha=0.5, theta=0.5).apply(_matrix())
    # 0_10 and 30_40 are passing windows; whichever covers the MSS is dropped.
    assert "10_20" in out.columns
    assert len(out.columns) < len(_matrix().columns)


def test_span_merge_adds_merged_windows():
    out = SpanMergeOptimizer(max_span=2).apply(_matrix())
    assert "0_20" in out.columns
    assert "10_30" in out.columns
    # merged label is 1 when any member failed
    assert int(out.loc["error", "10_30"]) == 1


def test_build_optimizers_by_name():
    optimizers = build_optimizers(["canal", "span_merge"])
    assert [o.name for o in optimizers] == ["canal", "span_merge"]


def test_build_optimizers_rejects_unknown():
    import pytest

    with pytest.raises(ValueError):
        build_optimizers(["does_not_exist"])
