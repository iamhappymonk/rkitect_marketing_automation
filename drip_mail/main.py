#!/usr/bin/env python3
"""CLI entry point for drip_mail automation."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Allow `python main.py` from drip_mail/ while using package imports
_ROOT = Path(__file__).resolve().parent
_REPO = _ROOT.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from drip_mail import config  # noqa: E402
from drip_mail.engine.check import run_checks  # noqa: E402
from drip_mail.engine.runner import FlowRunner, list_flows_summary  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Drip mail automation — Google Sheets → Resend"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Process eligible contacts")
    run_p.add_argument(
        "--watch",
        action="store_true",
        help="Poll continuously (uses DRIP_POLL_INTERVAL_SECONDS)",
    )
    run_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without sending or writing to sheet",
    )
    run_p.add_argument(
        "--flow",
        metavar="ID",
        help="Run only this flow id (e.g. welcome_on_signup)",
    )
    run_p.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Poll interval in seconds when using --watch",
    )

    sub.add_parser("list-flows", help="Show registered flows and audit columns")
    sub.add_parser(
        "check",
        help="Validate .env, credentials file, and Google Sheet access",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    args = _build_parser().parse_args(argv)

    if args.command == "list-flows":
        for item in list_flows_summary():
            print(json.dumps(item, indent=2))
        return 0

    if args.command == "check":
        report = run_checks()
        print(json.dumps(report, indent=2))
        if not report["ok"]:
            print(
                "\nFix failing checks, then run: python -m drip_mail check",
                file=sys.stderr,
            )
        return 0 if report["ok"] else 1

    if args.command == "run":
        dry_run = args.dry_run or config.DRIP_DRY_RUN
        runner = FlowRunner(dry_run=dry_run)
        if args.watch:
            runner.run_watch(
                interval_seconds=args.interval,
                flow_filter=args.flow,
            )
            return 0
        stats = runner.run_once(flow_filter=args.flow)
        print(json.dumps(stats, indent=2))
        return 0 if stats.get("failed", 0) == 0 else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
