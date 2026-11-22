from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .config import Settings
from .ingest import run_ingestion, validate_ingestion_date
from .storage import make_s3_client


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SupplyChain 360 Week 1 raw data ingestion")
    parser.add_argument("--config", default="config/datasets.yaml", help="Dataset configuration YAML")
    parser.add_argument(
        "--date",
        default=os.getenv("INGESTION_DATE") or None,
        help="Ingestion date YYYY-MM-DD (default: today)",
    )
    parser.add_argument("--env-file", default=".env", help="Environment file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        ingestion_date = validate_ingestion_date(args.date)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    config_path = Path(args.config)
    if not config_path.is_file():
        print(f"error: config file not found: {config_path}", file=sys.stderr)
        return 2
    settings = Settings.from_env(args.env_file)
    client = make_s3_client(settings)
    report = run_ingestion(config_path, client, settings.bucket, ingestion_date)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
