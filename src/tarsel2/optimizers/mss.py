"""MSS: drop misleading passing windows using a minimal suspicious set.

A passing window that covers (almost) the whole minimal suspicious set is
likely a window where the fault is active but was not observed, so it is
removed before scoring.
"""

from __future__ import annotations

import pandas as pd

from .base import BaseMatrixOptimizer


class MSSOptimizer(BaseMatrixOptimizer):
    name = "mss"

    def __init__(self, alpha: float = 0.9, theta: float = 0.9) -> None:
        self.alpha = alpha
        self.theta = theta

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if "error" not in df.index:
            return df

        error_row = pd.to_numeric(df.loc["error"], errors="coerce").fillna(0)
        cover_df = df.drop(index="error")
        if cover_df.empty:
            return df

        time_cols = list(cover_df.columns)
        fail_cols = [c for c in time_cols if error_row.get(c, 0) == 1]
        if not fail_cols:
            return df

        freq = (cover_df[fail_cols] == 1).sum(axis=1) / len(fail_cols)
        mss = freq[freq >= self.alpha].index.tolist()
        if not mss:
            return df

        mss_df = cover_df.loc[mss]
        pass_cols = [c for c in time_cols if error_row.get(c, 0) == 0]

        to_delete = []
        for col in pass_cols:
            ratio = (mss_df[col] == 1).sum() / len(mss)
            if ratio >= self.theta:
                to_delete.append(col)

        keep = [c for c in df.columns if c not in to_delete]
        return df[keep]
