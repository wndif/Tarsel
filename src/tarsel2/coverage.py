"""URG coverage report parsing and coverage-matrix construction.

A URG "modinfo.txt" contains one paragraph per module. Each covered line
appears as "<lineno> <covered>/<total> ...". A line is treated as covered
when its two counters are equal (fully covered).
"""

from __future__ import annotations

import os
import re
from typing import List, Optional, Sequence, Tuple

import pandas as pd

_SEPARATOR = re.compile(r"-{20,}")
_LINE_ENTRY = re.compile(r"^(\d+)\s+(\d+)/(\d+)", re.MULTILINE)


def split_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in _SEPARATOR.split(text) if p.strip()]


def is_testbench_module(module_name: str, testbench: str = "") -> bool:
    """A module is a testbench when its name carries 'tb'.

    The configured testbench stem is also matched, so a differently named
    testbench (for example ``top_harness``) is excluded as well.
    """
    if "tb" in module_name.lower():
        return True
    if testbench:
        stem = os.path.splitext(os.path.basename(testbench))[0]
        if stem and stem.lower() in module_name.lower():
            return True
    return False


def parse_modinfo(
    path: str, testbench: str = ""
) -> List[Tuple[str, int, int]]:
    """Return [(module, line, covered_flag)] for one URG modinfo.txt."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    entries: List[Tuple[str, int, int]] = []
    paragraph_header = re.compile(r"Line Coverage for Module\s*:?\s*(.*)")

    for para in split_paragraphs(text):
        header = paragraph_header.search(para)
        if not header:
            continue
        module_name = header.group(1).strip()
        if not module_name or is_testbench_module(module_name, testbench):
            continue
        for match in _LINE_ENTRY.finditer(para):
            line_no = int(match.group(1))
            left, right = match.group(2), match.group(3)
            entries.append((module_name, line_no, 1 if left == right else 0))

    return entries


def build_matrix(
    config_report_dir: str,
    slices: Sequence[Tuple[int, int]],
    testbench: str = "",
    report_prefix: str = "CoverageReport",
) -> pd.DataFrame:
    """Build the binary line-coverage matrix.

    Index: "<module>_<line>". Columns: "<t1>_<t2>" per time window.
    """
    matrix = pd.DataFrame()
    for t1, t2 in slices:
        column = f"{t1}_{t2}"
        report_dir = os.path.join(
            config_report_dir, f"{report_prefix}{t1}_{t2}.report"
        )
        modinfo = os.path.join(report_dir, "modinfo.txt")
        if not os.path.isfile(modinfo):
            continue
        entries = parse_modinfo(modinfo, testbench=testbench)
        if not entries:
            continue
        frame = pd.DataFrame(entries, columns=["module", "line", column])
        frame["key"] = frame["module"].astype(str) + "_" + frame["line"].astype(str)
        series = frame.drop_duplicates("key").set_index("key")[[column]]
        matrix = pd.concat([matrix, series], axis=1)

    if not matrix.empty:
        matrix = matrix.fillna(0).astype(int)
        matrix = matrix.sort_index()
    return matrix


def module_names_in(file_path: str) -> List[str]:
    """Return module names declared in a Verilog file.

    Missing or unreadable files yield an empty list: module-to-file renaming
    then falls back to the module name, which keeps scoring usable.
    """
    if not os.path.isfile(file_path):
        return []
    pattern = re.compile(r"^\s*module\s+([A-Za-z_]\w*)", re.MULTILINE)
    with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
        return pattern.findall(fh.read())


def build_module_to_file(source_paths: Sequence[str]) -> dict:
    mapping = {}
    for path in source_paths:
        stem = os.path.splitext(os.path.basename(path))[0]
        for module in module_names_in(path):
            mapping[module] = stem
    return mapping


def rename_modules_to_files(
    matrix: pd.DataFrame, module_to_file: dict, testbench_stem: str = ""
) -> pd.DataFrame:
    """Rename "<module>_<line>" rows to "<file>_<line>" and drop testbench rows."""
    renamed = {}
    drop: List[str] = []
    pattern = re.compile(r"^(.*?)(?:_(\d+))?$")
    for key in matrix.index:
        if key == "error":
            continue
        match = pattern.match(str(key))
        if not match:
            continue
        module, number = match.group(1), match.group(2)
        if module == testbench_stem or is_testbench_module(module):
            drop.append(key)
            continue
        file_stem = module_to_file.get(module, module)
        renamed[key] = f"{file_stem}_{number}"
    out = matrix.rename(index=renamed)
    if drop:
        out = out.drop(index=[d for d in drop if d in out.index], errors="ignore")
    return out
