# ADR 0002 — Bronze is raw, immutable and date-partitioned

- **Status:** accepted
- **Context:** Later layers need to be traceable to an exact source file version.
- **Decision:** Upload source files byte-for-byte to `bronze/<source>/ingestion_date=<YYYY-MM-DD>/<relative path>`.
  Record size and SHA-256 in a local JSON manifest. Never transform data in Bronze.
- **Consequences:** Re-running on the same date overwrites the same keys (idempotent); a new date keeps a
  new snapshot. Relative paths are kept so same-named files in different folders cannot collide, and keys
  containing `..` are rejected.
