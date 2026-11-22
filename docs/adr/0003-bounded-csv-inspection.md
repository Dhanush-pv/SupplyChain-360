# ADR 0003 — Bounded CSV inspection, not full profiling

- **Status:** accepted
- **Context:** M5 files are large; a full scan during ingestion would be slow and is not the purpose of Bronze.
- **Decision:** Read only the header and up to 1,000 data rows per CSV for column names, blank counts and
  malformed-row counts. Full-file profiling is deferred to the Spark Silver job (Week 2).
- **Consequences:** The manifest never claims whole-file row counts or quality. Checksums are computed on
  the whole file.
