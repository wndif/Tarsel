"""Command line entry point."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Optional, Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tarsel2",
        description="Fault localization for single-fault Verilog designs",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    localize = sub.add_parser(
        "localize", help="localize the fault in a project described by a yaml config"
    )
    localize.add_argument("--config", required=True, help="project yaml")
    localize.add_argument("--work-dir", help="override the work directory")
    localize.add_argument(
        "--top", type=int, default=10, help="how many lines to print per metric"
    )
    localize.add_argument(
        "--json", dest="json_out", help="write a machine-readable summary here"
    )
    localize.add_argument(
        "--slice-strategy",
        choices=("onset", "uniform"),
        help="override config.slice_strategy",
    )
    localize.add_argument(
        "--optimizer",
        action="append",
        default=None,
        help="enable a matrix optimizer (canal|mss|span_merge), repeatable",
    )

    show = sub.add_parser("show-config", help="print the resolved configuration")
    show.add_argument("--config", required=True)

    check = sub.add_parser("check", help="verify the VCS/URG toolchain is reachable")
    return parser


def _print_table(title: str, frame, top: int) -> None:
    print(f"\n=== {title} ===")
    if frame is None or frame.empty:
        print("(empty)")
        return
    print(frame.head(top).to_string())


def cmd_localize(args) -> int:
    from .config import ProjectConfig
    from .pipeline import localize
    from .runner import require_tools

    missing = require_tools(("vcs", "urg"))
    if missing:
        print(
            "error: missing tool(s): " + ", ".join(missing)
            + "\nTarsel2 drives Synopsys VCS/URG; supply a licensed installation "
            "on PATH (see docker/README.md).",
            file=sys.stderr,
        )
        return 2

    config = ProjectConfig.load(args.config, work_dir=args.work_dir)
    if args.slice_strategy:
        config.slice_strategy = args.slice_strategy
    if args.optimizer is not None:
        config.optimizers = list(args.optimizer)

    print(f"project      : {config.project_name}")
    print(f"sources      : {', '.join(config.source_files)}")
    print(f"testbench    : {config.testbench}")
    print(f"golden output: {config.golden_output_path()}")
    print(f"slice strategy: {config.slice_strategy}")
    print(f"optimizers   : {config.optimizers or '(none)'}")

    result = localize(config)

    print(f"\nwindows      : {len(result.windows)}")
    failing = sum(1 for _, label in result.windows if label == 1)
    print(f"failing      : {failing}")

    _print_table("Top lines by D_star", result.ranking.get("D_star"), args.top)

    if result.exam:
        print("\n=== EXAM score (lower is better) ===")
        for metric, value in sorted(result.exam.items(), key=lambda kv: kv[1]):
            print(f"{metric:<12} {value:.4f}")

    print("\nartifacts:")
    for name, path in result.artifacts.items():
        print(f"  {name}: {path}")

    if args.json_out:
        payload = {
            "project": config.project_name,
            "windows": len(result.windows),
            "failing": failing,
            "exam": result.exam,
            "top": {
                metric: list(frame.index[: args.top])
                for metric, frame in result.ranking.items()
            },
        }
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"\nsummary written to {args.json_out}")
    return 0


def cmd_show_config(args) -> int:
    from .config import ProjectConfig

    config = ProjectConfig.load(args.config, work_dir=args.work_dir)
    print(json.dumps(config.to_dict(), indent=2, default=str))
    return 0


def cmd_check(args) -> int:
    from .runner import require_tools

    missing = require_tools(("vcs", "urg"))
    for tool in ("vcs", "urg"):
        status = "MISSING" if tool in missing else "OK"
        print(f"{tool}: {status}")
    return 1 if missing else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "localize": cmd_localize,
        "show-config": cmd_show_config,
        "check": cmd_check,
    }
    return handlers[args.command](args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
