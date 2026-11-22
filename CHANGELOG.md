# Changelog

**Project author:** Dhanush

## Week 1 — Data foundation & raw ingestion (v0.1.0)

### Added
- Local MinIO infrastructure (Docker Compose) with persistent volume and healthcheck.
- Dataset registry and expected-file layout for M5, DataCo and Olist.
- Raw-file ingestion to a date-partitioned Bronze zone; SHA-256, size and bounded CSV inspection; JSON manifest.
- Path-traversal protection for object keys; relative source paths preserved to prevent collisions.
- Ingestion-date validation and friendly CLI errors (exit code 2).
- Deterministic **synthetic** sample dataset, `scripts/generate_sample_data.py`, and `config/datasets.sample.yaml`
  for a no-download demo (`make demo`).
- Integration tests against a local S3 server (moto), plus edge-case tests for CSV inspection, settings and bucket handling.
- Business requirements, dataset licence/attribution notes, ADRs 0001–0004, runbook and definition of done.
- Project README describing features, setup, architecture and roadmap.

### Fixed
- Healthcheck now uses `mc ready local` (the MinIO image is not guaranteed to ship `curl`).
- Removed unused dependencies (`pandas`, `pyarrow`, `tqdm`) from the Week 1 package.
- `.gitignore` no longer drops the per-source `data/raw/*/.gitkeep` placeholders; ignores build artefacts.
- LICENSE copyright holder set to Dhanush.
- Lint: import ordering, explicit `zip(strict=...)`, line length; CI split into lint + Python 3.10–3.12 test matrix.
