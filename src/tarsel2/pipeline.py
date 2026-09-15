"""End-to-end localization pipeline.

Stages:
    1. compile the faulty design with VCS coverage instrumentation
    2. run it once to obtain the observed output dump
    3. compare observed vs golden -> per-timestamp divergence
    4. derive time windows and run one instrumented simulation per window
    5. ask URG for one report per window
    6. build the binary coverage matrix and attach the window labels
    7. optionally purify, then score with all formulas
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd

from . import compare, coverage, formulas, slices as slices_mod
from .config import ProjectConfig
from .optimizers import build_optimizers
from .runner import VcsRunner


@dataclass
class LocalizationResult:
    matrix: pd.DataFrame
    scored: pd.DataFrame
    ranking: Dict[str, pd.DataFrame] = field(default_factory=dict)
    exam: Dict[str, float] = field(default_factory=dict)
    windows: List[Tuple[Tuple[int, int], int]] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)

    @property
    def top_lines(self) -> List[str]:
        if "D_star" not in self.ranking:
            return []
        return list(self.ranking["D_star"].index[:10])


def acquire(config: ProjectConfig, runner: Optional[VcsRunner] = None) -> Tuple[pd.DataFrame, List]:
    """Stages 1-6. Returns (matrix with error row, windows)."""
    runner = runner or VcsRunner(config)

    runner.compile(clean=False)
    runner.run_full()

    errors = compare.error_series(
        config.golden_output_path(), config.observed_output_path()
    )
    if errors.empty:
        raise RuntimeError("observed output dump is empty; check the testbench")

    windows = slices_mod.build_slices(config, errors)
    if not windows:
        raise RuntimeError("no time windows could be derived from the output dump")

    pairs = [(t1, t2) for (t1, t2), _ in windows]
    runner.run_slices(pairs)
    runner.gen_reports(pairs)

    matrix = coverage.build_matrix(
        config.coverage_report_dir, pairs, testbench=config.testbench
    )
    if matrix.empty:
        raise RuntimeError(
            "coverage matrix is empty; check the URG reports under "
            f"{config.coverage_report_dir}"
        )

    labels = slices_mod.labeled_slices(windows).set_index("slice_name")["error"]
    matrix_with_error = attach_error_row(matrix, labels)
    return matrix_with_error, windows


def attach_error_row(matrix: pd.DataFrame, labels: pd.Series) -> pd.DataFrame:
    """Append the pass/fail labels as the 'error' row of a coverage matrix."""
    aligned = pd.to_numeric(
        labels.reindex(matrix.columns).fillna(0), errors="coerce"
    ).fillna(0).astype(int)
    error_row = pd.DataFrame(
        [aligned.tolist()], columns=matrix.columns, index=[formulas.ERROR_ROW]
    )
    return pd.concat([matrix, error_row])


def purify(config: ProjectConfig, matrix: pd.DataFrame) -> pd.DataFrame:
    """Rename module rows to file rows, drop testbench rows, run optimizers."""
    sources = config.source_paths() + [config.testbench_path()]
    mapping = coverage.build_module_to_file(sources)
    tb_stem = os.path.splitext(os.path.basename(config.testbench))[0]
    out = coverage.rename_modules_to_files(matrix, mapping, testbench_stem=tb_stem)

    for optimizer in build_optimizers(config.optimizers):
        out = optimizer.apply(out.copy())
    return out


def localize(config: ProjectConfig, runner: Optional[VcsRunner] = None) -> LocalizationResult:
    """Run the full pipeline and write every artifact under the work dir."""
    matrix, windows = acquire(config, runner)

    raw_path = os.path.join(config.work_dir, "df_matrix_errors.csv")
    os.makedirs(config.work_dir, exist_ok=True)
    matrix.to_csv(raw_path)

    purified = purify(config, matrix)
    purified_path = os.path.join(config.work_dir, "df_matrix_errors_purified.csv")
    purified.to_csv(purified_path)

    scored = formulas.rank_matrix(purified)
    scored_path = os.path.join(config.work_dir, "suspicious_values.csv")
    scored.to_csv(scored_path)

    rankings = {
        name: formulas.ranking(scored, name) for name in formulas.FORMULAS
    }
    ranking_path = os.path.join(config.work_dir, "ranking_D_star.csv")
    rankings["D_star"].to_csv(ranking_path)

    exam: Dict[str, float] = {}
    artifacts = {
        "matrix": raw_path,
        "purified": purified_path,
        "suspicious_values": scored_path,
        "ranking_D_star": ranking_path,
    }
    if config.fault_lines:
        exam = formulas.exam_scores(scored, config.fault_lines)
        exam_path = os.path.join(config.work_dir, "exam_result.csv")
        pd.Series(exam, name="exam").to_csv(exam_path)
        artifacts["exam_result"] = exam_path

    return LocalizationResult(
        matrix=matrix,
        scored=scored,
        ranking=rankings,
        exam=exam,
        windows=windows,
        artifacts=artifacts,
    )


def localize_from_reports(
    config: ProjectConfig,
    pairs: Sequence[Tuple[int, int]],
    labels: Sequence[int],
    report_dir: Optional[str] = None,
) -> LocalizationResult:
    """Score directly from URG reports already on disk (no VCS needed).

    This is the portable entry point: reports can be produced on a licensed
    machine and scored anywhere.
    """
    report_dir = report_dir or config.coverage_report_dir
    matrix = coverage.build_matrix(report_dir, pairs, testbench=config.testbench)
    if matrix.empty:
        raise RuntimeError(f"no URG reports found under {report_dir}")
    label_series = pd.Series(list(labels), index=[f"{a}_{b}" for a, b in pairs])
    matrix = attach_error_row(matrix, label_series)

    purified = purify(config, matrix)
    scored = formulas.rank_matrix(purified)
    rankings = {name: formulas.ranking(scored, name) for name in formulas.FORMULAS}
    exam = formulas.exam_scores(scored, config.fault_lines) if config.fault_lines else {}
    return LocalizationResult(matrix, scored, rankings, exam, list(zip(pairs, labels)), {})
