"""Project configuration for a single-fault Verilog design under localization."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml

# Time-unit scale expressed in femtoseconds. Used to derive the conversion
# between the timestamps a value-dump testbench writes (``%0t`` prints in the
# timescale *precision*) and the units VCS ``-cm_start``/``-cm_stop`` expect
# (the timescale *unit*).
_UNIT_SCALE = {
    "fs": 1,
    "ps": 1_000,
    "ns": 1_000_000,
    "us": 1_000_000_000,
    "ms": 1_000_000_000_000,
    "s": 1_000_000_000_000_000,
}

_TIMESCALE_RE = re.compile(
    r"`\s*timescale\s+(\d+)\s*(fs|ps|ns|us|ms|s)\s*/\s*(\d+)\s*(fs|ps|ns|us|ms|s)",
    re.IGNORECASE,
)


def parse_timescale_divisor(timescale: str) -> int:
    """Return ``golden_time // divisor == vcs_time`` for a ``<unit>/<prec>`` string.

    ``%0t`` prints the simulation time in the timescale *precision*; VCS
    ``-cm_start``/``-cm_stop`` accept the time in the timescale *unit*. The
    divisor converts the former to the latter.
    """
    m = re.match(
        r"\s*(\d+)\s*(fs|ps|ns|us|ms|s)\s*/\s*(\d+)\s*(fs|ps|ns|us|ms|s)\s*",
        timescale,
        re.IGNORECASE,
    )
    if not m:
        raise ValueError(f"cannot parse timescale: {timescale!r}")
    u_val, u_name, p_val, p_name = m.groups()
    unit_fs = int(u_val) * _UNIT_SCALE[u_name.lower()]
    prec_fs = int(p_val) * _UNIT_SCALE[p_name.lower()]
    # %0t value (precision units) / (unit / precision) == unit units.
    return max(1, unit_fs // prec_fs)


@dataclass
class ProjectConfig:
    """Everything Tarsel2 needs to localize one faulty design.

    Paths inside ``project_dir`` are relative to ``project_dir`` itself, which
    keeps a project directory movable between host and container.
    """

    project_name: str
    project_dir: str

    # Design under localization (the faulty version).
    source_files: List[str]
    testbench: str

    # Golden reference: output the correct version is expected to produce.
    golden_output: str
    # Name of the CSV the testbench writes at simulation time.
    output_filename: str = "output.txt"

    # Simulation window.
    start_time: int = 0
    end_time: int = 1000
    time_step: int = 10

    # Time-slicing strategy: "onset" (sliding windows around divergence
    # onsets) or "uniform" (fixed windows over the whole run, failing when any
    # mismatch falls inside the window).
    slice_strategy: str = "onset"
    slice_num: int = 100
    window_steps: int = 20
    n_windows: int = 3
    n_samples: int = 200

    # Optional matrix purification, applied in this order before scoring.
    optimizers: List[str] = field(default_factory=list)

    # Ground truth (optional). When present, exam scores are reported.
    fault_lines: List[str] = field(default_factory=list)

    # Toolchain.
    coverage_metrics: str = "line+cond+fsm+branch"
    vcs_options: str = "-timescale=1ns/100ps -full64 +vc +v2k -sverilog"
    # Optional Verdi PLI directory holding novas.tab / pli.a (FSDB builds).
    verdi_pli: str = ""
    timeout: int = 300

    # Time base. The value-dump testbench writes timestamps via ``%0t`` (in the
    # timescale *precision*), while VCS ``-cm_start``/``-cm_stop`` expect the
    # timescale *unit*. ``time_divisor`` converts the former to the latter. It
    # is auto-derived from the testbench's `` `timescale ` when possible and
    # falls back to this value.
    timescale: str = "1ns/1ps"

    # Runtime state (not persisted to the project yaml).
    work_dir: str = ""

    def __post_init__(self) -> None:
        self.project_dir = str(self.project_dir)
        if not self.work_dir:
            self.work_dir = os.path.join("work", self.project_name)
        self.resolve_paths()
        self._time_divisor = self._detect_divisor()

    def resolve_paths(self) -> None:
        """Make every path absolute.

        EDA commands run with cwd set to the build directory, so relative
        paths would be resolved twice (producing nested work dirs and a
        coverage database URG cannot find).
        """
        self.work_dir = os.path.abspath(self.work_dir)
        self.project_dir = os.path.abspath(self.project_dir)

    # ------------------------------------------------------- time base

    @property
    def time_divisor(self) -> int:
        """``golden_time // time_divisor == vcs_time`` for -cm_start/-cm_stop."""
        return getattr(self, "_time_divisor", 1000)

    def _detect_divisor(self) -> int:
        """Prefer the testbench's actual `` `timescale `, else the config field."""
        for path in [self.testbench_path()] + self.source_paths():
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            match = _TIMESCALE_RE.search(text)
            if match:
                unit_fs = int(match.group(1)) * _UNIT_SCALE[match.group(2).lower()]
                prec_fs = int(match.group(3)) * _UNIT_SCALE[match.group(4).lower()]
                return max(1, unit_fs // prec_fs)
        return parse_timescale_divisor(self.timescale)

    # ---------------------------------------------------------------- paths

    @property
    def build_dir(self) -> str:
        return os.path.join(self.work_dir, "build")

    @property
    def tests_dir(self) -> str:
        return os.path.join(self.build_dir, "tests")

    @property
    def coverage_report_dir(self) -> str:
        return os.path.join(self.build_dir, "coverage_reports")

    def source_paths(self) -> List[str]:
        return [os.path.join(self.project_dir, f) for f in self.source_files]

    def testbench_path(self) -> str:
        return os.path.join(self.project_dir, self.testbench)

    def golden_output_path(self) -> str:
        if os.path.isabs(self.golden_output):
            return self.golden_output
        return os.path.join(self.project_dir, self.golden_output)

    def observed_output_path(self) -> str:
        return os.path.join(self.build_dir, self.output_filename)

    def vdb_dir(self) -> str:
        return os.path.join(self.build_dir, "cov_test.vdb")

    def report_dir_for(self, t1: int, t2: int) -> str:
        return os.path.join(
            self.coverage_report_dir, f"CoverageReport{t1}_{t2}.report"
        )

    # ------------------------------------------------------------- (de)ser

    def to_dict(self) -> Dict[str, object]:
        data = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return data

    def dump(self, path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(self.to_dict(), fh, sort_keys=True)

    @classmethod
    def load(cls, path: str, work_dir: Optional[str] = None) -> "ProjectConfig":
        with open(path, "r", encoding="utf-8") as fh:
            raw: Dict[str, object] = yaml.safe_load(fh) or {}

        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        unexpected = set(raw) - known
        if unexpected:
            raise ValueError(f"unknown config keys: {sorted(unexpected)}")

        cfg = cls(**raw)  # type: ignore[arg-type]
        # Relative project dirs resolve against the config file location.
        # Use the raw value: __post_init__ already made cfg.project_dir
        # absolute, and os.path.join would otherwise discard the prefix.
        raw_project_dir = str(raw.get("project_dir", cfg.project_dir))
        if not os.path.isabs(raw_project_dir):
            cfg.project_dir = os.path.normpath(
                os.path.join(
                    os.path.dirname(os.path.abspath(path)), raw_project_dir
                )
            )
        if work_dir:
            cfg.work_dir = work_dir
        cfg.resolve_paths()
        return cfg
