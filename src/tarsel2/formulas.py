"""Suspiciousness formulas and exam-score evaluation.

Counters follow the operational taxonomic unit convention:

    aef  covered by a failing window
    anf  not covered by a failing window
    aep  covered by a passing window
    anp  not covered by a passing window

Windows whose label is neither 1 nor 0 (possible with the `onset` slicing
strategy, which can emit -1) are ignored.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

FORMULAS: List[str] = [
    "Russel_Rao",
    "OPTIMAL_P",
    "GP02",
    "GP03",
    "GP19",
    "D_star",
]

ERROR_ROW = "error"


def split_error_row(matrix: pd.DataFrame) -> tuple:
    """Split a matrix that carries an 'error' row into (coverage, labels)."""
    if ERROR_ROW not in matrix.index:
        raise ValueError(f"matrix has no '{ERROR_ROW}' row")
    labels = matrix.loc[ERROR_ROW]
    coverage = matrix.drop(index=ERROR_ROW)
    return coverage, labels


def counters(coverage: pd.DataFrame, labels: pd.Series) -> pd.DataFrame:
    """Compute aef / anf / aep / anp for every line."""
    labels = pd.to_numeric(labels, errors="coerce").fillna(0).astype(int)
    failing = [c for c in coverage.columns if labels.get(c, 0) == 1]
    passing = [c for c in coverage.columns if labels.get(c, 0) == 0]

    fail = coverage[failing] if failing else coverage.iloc[:, 0:0]
    pas = coverage[passing] if passing else coverage.iloc[:, 0:0]

    out = pd.DataFrame(index=coverage.index)
    out["aef"] = (fail == 1).sum(axis=1) if failing else 0
    out["anf"] = (fail == 0).sum(axis=1) if failing else 0
    out["aep"] = (pas == 1).sum(axis=1) if passing else 0
    out["anp"] = (pas == 0).sum(axis=1) if passing else 0
    return out.astype(float)


def score(counters_df: pd.DataFrame) -> pd.DataFrame:
    """Apply every suspiciousness formula to the counters."""
    aef = counters_df["aef"]
    anf = counters_df["anf"]
    aep = counters_df["aep"]
    anp = counters_df["anp"]

    total = aef + anf + aep + anp

    out = pd.DataFrame(index=counters_df.index)
    out["Russel_Rao"] = aef / total.replace(0, np.nan)

    # OPTIMAL_P: a11 - a01 / (a01 + a00 + 1), written with the coverage
    # counters as aef - aep / (aep + anp + 1). The +1 keeps the penalty below
    # one and avoids division by zero.
    out["OPTIMAL_P"] = aef - aep / (aep + anp + 1)

    out["GP02"] = 2 * (aef + np.sqrt(anp)) + np.sqrt(aep)
    out["GP03"] = np.sqrt(np.abs(aef * aef - np.sqrt(aep)))
    out["GP19"] = aef * np.sqrt(np.abs(aep - aef + anf - anp))
    out["D_star"] = aef * aef / (anf + aep + 0.001)
    return out


def rank_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    """Coverage matrix (with error row) -> counters + six formula scores."""
    coverage, labels = split_error_row(matrix)
    counts = counters(coverage, labels)
    return pd.concat([counts, score(counts)], axis=1)


def exam_score(scored: pd.DataFrame, line: str, metric: str) -> Optional[float]:
    """EXAM score for one faulty line under one metric (lower is better)."""
    if line not in scored.index:
        return None
    body = scored.drop(index=ERROR_ROW, errors="ignore")
    if body.empty or metric not in body.columns:
        return None
    value = body.loc[line, metric]
    greater = int((body[metric] > value).sum())
    equal = int((body[metric] == value).sum())
    return (greater + equal / 2) / body.shape[0]


def exam_scores(
    scored: pd.DataFrame, fault_lines: Sequence[str], metrics: Sequence[str] = FORMULAS
) -> Dict[str, float]:
    """Best (minimum) EXAM score per metric over the known faulty lines."""
    results: Dict[str, float] = {}
    for metric in metrics:
        values = [
            v
            for v in (exam_score(scored, line, metric) for line in fault_lines)
            if v is not None
        ]
        if values:
            results[metric] = min(values)
    return results


def ranking(scored: pd.DataFrame, metric: str = "D_star") -> pd.DataFrame:
    """Lines sorted by suspiciousness, most suspicious first."""
    body = scored.drop(index=ERROR_ROW, errors="ignore")
    if metric not in body.columns:
        raise ValueError(f"unknown metric: {metric}")
    return body.sort_values(by=metric, ascending=False)
