
## Start / stop

```bash
docker compose up -d
docker compose ps
docker compose logs -f minio
docker compose down
```

Keep the named `minio_data` volume when stopping the stack. To delete all local MinIO data intentionally, use `docker compose down -v`.

## Pre-ingestion checks

1. Confirm Docker Desktop is running.
2. Confirm MinIO is healthy at `http://localhost:9000/minio/health/live`.
3. Confirm `.env` exists and contains local-only credentials.
4. Confirm dataset files are extracted into the directories listed in `config/datasets.yaml`.
5. Confirm dataset terms and attribution have been reviewed.

## Demo mode (no downloads needed)

```bash
make up      # start MinIO
make demo    # ingest the tiny SYNTHETIC sample in data/sample/
```

Expected: 10 objects under `bronze/` in bucket `supplychain360-lake` and a manifest at
`reports/<date>/ingestion_manifest.json`.

## Execute and verify (real datasets)

```bash
python -m supplychain360.cli
pytest -q
```

Open the MinIO Console at `http://localhost:9001`, inspect bucket `supplychain360-lake`, and compare object names with `reports/<date>/ingestion_manifest.json`.

## Recovery

- If MinIO is unavailable, inspect `docker compose ps` and `docker compose logs minio`.
- If credentials fail, compare `.env` with the MinIO container environment and restart after changes.
- If an upload fails, retain the source files and error output, correct the cause, then rerun. A same-date rerun overwrites the same object keys.
- If a source file is missing, do not create a fake replacement. Record it as missing.

## Data handling

Never commit `.env`, downloaded datasets, local manifests, or customer-level data. Synthetic test fixtures must be labelled as synthetic.
