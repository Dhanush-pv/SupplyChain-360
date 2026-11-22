# ADR 0004 — Synthetic sample data and S3-server integration tests

- **Status:** accepted
- **Context:** The real datasets are large and licence-restricted, and CI has no Docker/MinIO.
- **Decision:** Commit a tiny deterministic synthetic sample (clearly labelled) and test the full ingestion
  path against moto's standalone S3 server on a real HTTP port.
- **Consequences:** CI exercises `endpoint_url`, path-style addressing, bucket creation, upload and manifest
  checks without Docker. This is a protocol-level simulation; a run against the real MinIO container is still
  listed as a manual verification step in the Definition of Done.
