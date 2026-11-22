# ADR 0001 — MinIO as the local S3-compatible object store

- **Status:** accepted
- **Context:** The blueprint targets AWS S3 for the lakehouse. Development happens on a laptop, with no cloud cost.
- **Decision:** Use MinIO (Docker) and access it through `boto3` with a configurable `S3_ENDPOINT_URL` and
  path-style addressing.
- **Consequences:** Code is S3-API compatible, so pointing it at real S3 is a configuration change
  (endpoint, credentials, bucket). MinIO-specific features are not used. Local credentials are development-only.
