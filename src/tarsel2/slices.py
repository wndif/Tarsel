"""Time-window generation.

Two strategies are available:

onset
    Sliding windows centred on divergence onsets, and a window is labelled
    failing when the divergence transition fires at its end.

uniform
    Fixed windows covering the whole run, labelled failing when any
    divergence falls inside the window. Cleaner semantics, usually a better
    input for the formulas.
"""

from __future__ import annotations

import random
from typing import List, Sequence, Tuple

import pandas as pd

Slice = Tuple[Tuple[int, int], int]


def uniform_slices(
    errors: pd.Series, time_step: int, slice_num: int = 100, start: int = 0
) -> List[Slice]:
    """Fixed windows over the observed time range."""
    times = [int(t) for t in errors.index]
    if not times:
        return []
    lower, upper = min(times), max(times)
    span = max(time_step, (upper - lower + time_step) // max(slice_num, 1))

    boundaries = list(range(lower, upper, span))
    if len(boundaries) - 1 > slice_num:
        boundaries = boundaries[: slice_num + 1]
    if boundaries[-1] != upper:
        boundaries.append(upper)
    if len(boundaries) < 2:
        return []

    slices: List[Slice] = []
    last = len(boundaries) - 2
    for i in range(len(boundaries) - 1):
        t1, t2 = boundaries[i], boundaries[i + 1]
        if i == last:
            # The final window includes its upper bound so that the last
            # sample of the dump is not silently dropped.
            window = errors[errors.index >= t1]
        else:
            window = errors[(errors.index >= t1) & (errors.index < t2)]
        label = 1 if len(window) and int(window.max()) == 1 else 0
        slices.append(((t1, t2), label))
    return slices


def onset_slices(
    errors: pd.Series,
    num_steps: int = 20,
    n_windows: int = 3,
    n_samples: int = 200,
    delta_f: int = 1,
    seed: int = 0,
) -> List[Slice]:
    """Sliding windows around divergence onsets."""
    if errors.empty:
        return []

    frame = pd.DataFrame({"err": errors.astype(int)})
    frame.index = frame.index.astype(int)
    time_step = int(frame.index[:5].to_series().diff().mean() or 1)
    frame = frame.sort_index()
    frame["diff"] = frame["err"].diff().fillna(frame["err"]).astype(int)
    pivots = [int(t) for t in frame.index[frame["diff"] == 1]]

    if not pivots:
        # No onset inside the dump: treat the whole run as one passing window.
        times = list(frame.index)
        return [((times[0], times[-1]), 0)] if len(times) > 1 else []

    windows: List[List[int]] = []
    for pivot in pivots:
        lower = max(pivot - num_steps * time_step, int(frame.index[0]))
        upper = min(pivot + num_steps * time_step, int(frame.index[-1]))
        windows.append(list(range(lower, upper, time_step * delta_f)))

    rng = random.Random(seed)
    sampled = rng.sample(windows, min(len(windows), n_windows)) if n_windows > 0 else windows

    segment_set = set()
    for window in sampled:
        points = [x for x in window if x in set(frame.index)]
        for i in range(len(points) - 1):
            segment_set.add((points[i], points[i + 1]))

    results: List[Slice] = []
    for segment in sorted(segment_set):
        end = segment[1]
        label = int(frame["diff"].loc[end]) if end in frame.index else 0
        results.append((segment, label))
    if n_samples and n_samples > 0:
        results = results[:n_samples]
    return results


def build_slices(config, errors: pd.Series) -> List[Slice]:
    """Dispatch on ``config.slice_strategy``."""
    strategy = (config.slice_strategy or "onset").lower()
    if strategy == "uniform":
        return uniform_slices(
            errors,
            time_step=config.time_step,
            slice_num=config.slice_num,
            start=config.start_time,
        )
    if strategy == "onset":
        return onset_slices(
            errors,
            num_steps=config.window_steps,
            n_windows=config.n_windows,
            n_samples=config.n_samples,
        )
    raise ValueError(f"unknown slice_strategy: {config.slice_strategy}")


def labeled_slices(slices: Sequence[Slice]) -> pd.DataFrame:
    """Window list -> DataFrame with slice_name / error columns."""
    return pd.DataFrame(
        [
            {"slice_name": f"{t1}_{t2}", "error": label}
            for (t1, t2), label in slices
        ]
    )
