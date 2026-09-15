"""Golden vs observed output comparison."""

from __future__ import annotations

import pandas as pd


def load_dump(path: str) -> pd.DataFrame:
    """Load a value-dump CSV written by the testbench (first column: time)."""
    frame = pd.read_csv(path, dtype=str)
    first = frame.columns[0]
    frame = frame.rename(columns={first: "time"})
    frame["time"] = frame["time"].astype(str).str.strip()
    return frame.set_index("time")


def compare_dumps(
    golden_path: str, observed_path: str
) -> pd.Series:
    """Return a boolean Series indexed by time: True where rows differ.

    Only the common prefix of both dumps is compared.
    """
    golden = load_dump(golden_path)
    observed = load_dump(observed_path)

    common = golden.index.intersection(observed.index)
    if len(common) == 0:
        # Fall back to positional comparison when time columns disagree.
        n = min(len(golden), len(observed))
        golden_cmp = golden.iloc[:n]
        observed_cmp = observed.iloc[:n]
        diff = (golden_cmp != observed_cmp).any(axis=1)
        diff.index = golden_cmp.index
        return diff

    golden_cmp = golden.loc[common]
    observed_cmp = observed.loc[common]
    return (golden_cmp != observed_cmp).any(axis=1)


def error_series(golden_path: str, observed_path: str) -> pd.Series:
    """Integer error series (1/0) indexed by integer time."""
    diff = compare_dumps(golden_path, observed_path)
    series = diff.astype(int)
    try:
        series.index = series.index.astype(int)
    except (TypeError, ValueError):
        series.index = pd.RangeIndex(len(series)) * 10
    return series.sort_index()
