from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

SAMPLE_ROWS = 1000

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()

def inspect_csv(path: Path, sample_rows: int = SAMPLE_ROWS) -> dict[str, Any]:
    """Read header and a bounded sample; full row count is deliberately not scanned."""
    with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return {"file": path.name, "empty": True, "columns": [], "sample_rows": 0}
        rows = []
        for _, row in zip(range(sample_rows), reader, strict=False):
            rows.append(row)
    width = len(header)
    malformed_sample_rows = sum(1 for row in rows if len(row) != width)
    return {
        "file": path.name,
        "empty": False,
        "columns": header,
        "column_count": width,
        "sample_rows": len(rows),
        "malformed_sample_rows": malformed_sample_rows,
        "sample_null_counts": {
            header[i]: sum(1 for row in rows if i >= len(row) or row[i].strip() == "")
            for i in range(width)
        },
    }

def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
