"""Canal: in-time detection.

Keeps only the time windows up to and including the first failing window.
"""

from __future__ import annotations

import re

import pandas as pd

from .base import BaseMatrixOptimizer

_WINDOW = re.compile(r"^\d+_\d+$")


class CanalOptimizer(BaseMatrixOptimizer):
    name = "canal"

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        time_cols = [c for c in df.columns if _WINDOW.match(str(c))]
        if not time_cols:
            return df
        if "error" not in df.index:
            return df

        time_cols = sorted(time_cols, key=lambda c: int(str(c).split("_")[0]))

        # -1 labels (used by the onset slicer) are not failures here.
        error_values = df.loc["error", time_cols].replace(-1, 0)

        first_fail = None
        for col in time_cols:
            if pd.to_numeric(error_values[col], errors="coerce") == 1:
                first_fail = col
                break

        if first_fail is None:
            return df

        keep = time_cols[: time_cols.index(first_fail) + 1]
        drop = [c for c in time_cols if c not in keep]
        return df.drop(columns=drop)
