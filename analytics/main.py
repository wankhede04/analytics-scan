#!/usr/bin/env python3
"""analytics.main — daily report builder.

Pulls remote_jobs.xlsx and applications/_state.json from career-scan, computes
funnel metrics, and writes:
  reports/latest.md
  reports/<YYYY-MM-DD>.md
  reports/summary.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from analytics.compute import build_summary
from analytics.fetch import fetch_inputs
from analytics.render import render

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("analytics")

REPORTS = Path("reports")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="career-scan daily analytics")
    parser.add_argument("--cache", type=Path, default=Path("_cache"))
    parser.add_argument("--reports", type=Path, default=REPORTS)
    parser.add_argument(
        "--local-excel",
        type=Path,
        default=None,
        help="bypass remote fetch and read this local xlsx instead",
    )
    parser.add_argument(
        "--local-state",
        type=Path,
        default=None,
        help="bypass remote fetch and read this local _state.json instead",
    )
    args = parser.parse_args(argv)

    if args.local_excel and args.local_state:
        excel_path, state_path = args.local_excel, args.local_state
    else:
        paths = fetch_inputs(args.cache)
        excel_path, state_path = paths["excel"], paths["state"]

    summary = build_summary(excel_path, state_path)
    report_md = render(summary)

    args.reports.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).date().isoformat()
    (args.reports / "latest.md").write_text(report_md)
    (args.reports / f"{today}.md").write_text(report_md)
    (args.reports / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    logger.info("wrote reports to %s", args.reports)

    print(report_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
