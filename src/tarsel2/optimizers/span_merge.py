"""SpanMerge: merge adjacent time windows into longer ones.

A merged window is covered when any member window was covered; its label is
1 when any member window failed.
"""

from __future__ import annotations

import re

import pandas as pd

from .base import BaseMatrixOptimizer

_WINDOW = re.compile(r"^\d+_\d+$")


class SpanMergeOptimizer(BaseMatrixOptimizer):
    name = "span_merge"

    def __init__(self, max_span: int = 5) -> None:
        self.max_span = max_span

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        time_cols = [c for c in df.columns if _WINDOW.match(str(c))]
        if not time_cols:
            return df

        time_cols = sorted(time_cols, key=lambda c: int(str(c).split("_")[0]))

        for span in range(2, self.max_span + 1):
            for i in range(len(time_cols) - span + 1):
                group = time_cols[i : i + span]
                start = int(str(group[0]).split("_")[0])
                end = int(str(group[-1]).split("_")[1])
                name = f"{start}_{end}"
                if name in df.columns:
                    continue
                df[name] = (df[group] == 1).any(axis=1).astype(int)
        return df
