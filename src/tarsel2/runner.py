"""VCS / URG execution backend.

Coverage is acquired by re-running the same simulation once per time window,
with VCS coverage accumulation restricted to that window via
-cm_name / -cm_start / -cm_stop, then asking URG for one report per window.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import List, Optional, Sequence, Tuple

from .config import ProjectConfig


class CommandError(RuntimeError):
    """Raised when an external EDA command fails."""


class VcsRunner:
    """Drives vcs, simv and urg for one project."""

    def __init__(self, config: ProjectConfig) -> None:
        self.config = config

    # ------------------------------------------------------------- helpers

    def _run(self, command: str) -> str:
        """Run a shell command inside the build directory."""
        try:
            result = subprocess.run(
                command,
                cwd=self.config.build_dir,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise CommandError(f"timeout after {self.config.timeout}s: {command}") from exc
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode != 0:
            raise CommandError(
                f"command failed ({result.returncode}): {command}\n{output[-4000:]}"
            )
        return output

    @staticmethod
    def slice_name(t1: int, t2: int) -> str:
        return f"{t1}_{t2}"

    # ------------------------------------------------------------ lifecycle

    def prepare_dirs(self, clean: bool = False) -> None:
        build = self.config.build_dir
        if clean and os.path.isdir(build):
            shutil.rmtree(build)
        for path in (build, self.config.tests_dir, self.config.coverage_report_dir):
            os.makedirs(path, exist_ok=True)

    def compile_command(self) -> str:
        cfg = self.config
        files = " ".join(cfg.source_paths()) + " " + cfg.testbench_path()
        parts = [
            "vcs",
            f"+incdir+{cfg.project_dir}",
            files,
            cfg.vcs_options,
            f"-cm {cfg.coverage_metrics}",
            f"-cm_dir {cfg.vdb_dir()}",
        ]
        if cfg.verdi_pli:
            parts.append(f"-P {cfg.verdi_pli}/novas.tab {cfg.verdi_pli}/pli.a")
        return " ".join(parts)

    def compile(self, clean: bool = False) -> None:
        self.prepare_dirs(clean=clean)
        vdb = self.config.vdb_dir()
        if os.path.isdir(vdb):
            shutil.rmtree(vdb)
        self._run(self.compile_command())

    def sim_command(self, t1: Optional[int] = None, t2: Optional[int] = None) -> str:
        """Full run when no window given, otherwise one coverage window.

        Slice times come from the value-dump timestamps (timescale *precision*,
        e.g. ps). VCS ``-cm_start``/``-cm_stop`` expect the timescale *unit*,
        so the boundaries are divided by ``config.time_divisor`` while the test
        name keeps the original (precision-unit) label for consistency with the
        coverage matrix columns.
        """
        cfg = self.config
        exe = os.path.join(cfg.build_dir, "simv")
        if t1 is None or t2 is None:
            return exe
        name = self.slice_name(t1, t2)
        divisor = cfg.time_divisor
        vs1, vs2 = t1 // divisor, t2 // divisor
        if vs2 <= vs1:
            vs2 = vs1 + 1
        return (
            f"{exe} -cm {cfg.coverage_metrics} -cm_name {name} "
            f"-cm_start {vs1} -cm_stop {vs2}"
        )

    def run_full(self) -> None:
        """Run the design once so the testbench writes its full output dump."""
        self._run(self.sim_command())

    def run_slice(self, t1: int, t2: int) -> None:
        """Run one time window and record it as a URG test."""
        self._run(self.sim_command(t1, t2))
        self._record_test(t1, t2)

    def _record_test(self, t1: int, t2: int) -> None:
        name = self.slice_name(t1, t2)
        path = os.path.join(self.config.tests_dir, f"test{name}.f")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f"cov_test/{name}\n")

    def report_command(self, t1: int, t2: int) -> str:
        """URG invocation for one window.

        -dir is passed relative to the build directory on purpose: URG builds
        its test namespace from the -dir spelling, so an absolute -dir makes
        the relative entries in the tests file stop matching (URG-NMT).
        """
        name = self.slice_name(t1, t2)
        test_file = os.path.join(self.config.tests_dir, f"test{name}.f")
        vdb = os.path.basename(self.config.vdb_dir())
        return (
            f"urg -full64 -dir {vdb} -tests {test_file} "
            f"-format both -report {self.config.report_dir_for(t1, t2)}"
        )

    def gen_report(self, t1: int, t2: int) -> None:
        self._run(self.report_command(t1, t2))

    def run_slices(self, slices: Sequence[Tuple[int, int]]) -> None:
        for t1, t2 in slices:
            self.run_slice(t1, t2)

    def gen_reports(self, slices: Sequence[Tuple[int, int]]) -> None:
        for t1, t2 in slices:
            self.gen_report(t1, t2)


def require_tools(tools: Sequence[str] = ("vcs", "urg")) -> List[str]:
    """Return the subset of tools that are missing from PATH."""
    return [t for t in tools if shutil.which(t) is None]
