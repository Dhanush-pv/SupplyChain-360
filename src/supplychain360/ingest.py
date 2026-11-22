from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from .inspection import inspect_csv, sha256_file, write_json
from .storage import ensure_bucket, upload_file


def validate_ingestion_date(value: str | None) -> str:
    """Return a normalised YYYY-MM-DD string; default to today's date when value is empty."""
    if not value:
        return date.today().isoformat()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError as exc:
        raise ValueError(f"Ingestion date must be YYYY-MM-DD, got {value!r}") from exc


def load_dataset_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)

def discover_files(source_dir: Path, allowed_extensions: list[str]) -> list[Path]:
    if not source_dir.exists():
        return []
    allowed = {ext.lower() for ext in allowed_extensions}
    return sorted(p for p in source_dir.rglob("*") if p.is_file() and p.suffix.lower() in allowed)

def build_object_key(source: str, ingestion_date: str, relative_path: str) -> str:
    """Build a stable Bronze key and preserve paths beneath the source folder."""
    normalized = Path(relative_path).as_posix().lstrip("/")
    if ".." in Path(normalized).parts:
        raise ValueError("relative_path must not escape the source directory")
    return f"bronze/{source}/ingestion_date={ingestion_date}/{normalized}"

def run_ingestion(config_path: Path, client, bucket: str, ingestion_date: str | None = None,
                  project_root: Path | None = None) -> dict[str, Any]:
    ingest_date = validate_ingestion_date(ingestion_date)
    root = project_root or config_path.resolve().parents[1]
    config = load_dataset_config(config_path)
    ensure_bucket(client, bucket)
    report: dict[str, Any] = {"ingestion_date": ingest_date, "bucket": bucket, "sources": {}}

    for source, details in config["sources"].items():
        source_dir = root / details["directory"]
        files = discover_files(source_dir, details.get("allowed_extensions", [".csv"]))
        source_result = {
            "description": details.get("description", ""),
            "directory": str(details["directory"]),
            "expected_files": details.get("expected_files", []),
            "found_files": [],
            "missing_expected_files": [],
            "files": [],
            "license_note": details.get("license_note", ""),
        }
        found_names = {p.name for p in files}
        source_result["missing_expected_files"] = [
            name for name in source_result["expected_files"] if name not in found_names
        ]
        for path in files:
            relative_source_path = path.relative_to(source_dir).as_posix()
            key = build_object_key(source, ingest_date, relative_source_path)
            upload_file(client, bucket, path, key)
            file_info = {
                "filename": path.name,
                "local_path": str(path.relative_to(root)),
                "object_key": key,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "csv_inspection": inspect_csv(path) if path.suffix.lower() == ".csv" else None,
            }
            source_result["found_files"].append(path.name)
            source_result["files"].append(file_info)
        report["sources"][source] = source_result

    report_dir = root / "reports" / ingest_date
    write_json(report_dir / "ingestion_manifest.json", report)
    return report
