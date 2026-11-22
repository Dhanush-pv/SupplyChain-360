
## Decisions

1. **Local object storage:** MinIO provides an S3-compatible endpoint for laptop development.
2. **Raw preservation:** uploaded objects are original source files. Transformations happen in later layers.
3. **Bronze key convention:** `bronze/<source>/ingestion_date=<date>/<filename>`.
4. **Repeatable ingestion:** date partitioning keeps separate ingestion runs. Re-running on the same date and filename replaces that same object key; the SHA-256 in the manifest makes the uploaded source version auditable. Use a new date partition when you need to preserve a new source snapshot.
5. **Manifest:** local JSON records file metadata and bounded CSV inspection. It is not yet a centralized catalog.
6. **No raw data in Git:** datasets remain local and in MinIO; repository contains instructions and code only.
7. **Dataset boundaries:** M5, DataCo and Olist have different grains and identifiers. Do not join them directly without explicit mapping and business rules in later phases.

Each decision is recorded in more detail in [`docs/adr/`](adr/).

## Data flow

External dataset download -> local `data/raw/<source>/` -> Python discovery and inspection -> MinIO Bronze -> local JSON manifest.

## Known limitations

- CSV inspection samples at most 1,000 rows; it is not a full data-quality scan.
- Full-file SHA-256 requires reading each file and may take time for large M5 files.
- MinIO local credentials are development-only.
- The package does not download third-party datasets automatically; users must accept each source's terms and download them.
- The initial ingestion stores CSVs as CSV objects. Parquet conversion belongs to later processing stages and must not overwrite raw source files.
