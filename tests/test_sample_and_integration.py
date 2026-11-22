"""End-to-end checks against a local S3-compatible server (moto server mode) using the synthetic sample.

moto's standalone server speaks the real S3 protocol on a real HTTP port, so this exercises
`endpoint_url`, path-style addressing, bucket creation and upload exactly as the code would use them
against MinIO. It does NOT replace a run against the real MinIO container.
"""

import hashlib
import json
from pathlib import Path

import pytest
import yaml

pytest.importorskip("moto")

from generate_sample_data import main as generate_sample  # noqa: E402
from moto.server import ThreadedMotoServer  # noqa: E402

from supplychain360.config import Settings  # noqa: E402
from supplychain360.ingest import run_ingestion  # noqa: E402
from supplychain360.storage import make_s3_client  # noqa: E402

BUCKET = "unit-test-lake"
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SAMPLE_FILES = 10


@pytest.fixture(scope="module")
def s3_endpoint():
    server = ThreadedMotoServer(port=0, verbose=False)
    server.start()
    host, port = server.get_host_and_port()
    yield f"http://{host}:{port}"
    server.stop()


@pytest.fixture()
def client(s3_endpoint, monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    settings = Settings(
        endpoint_url=s3_endpoint, access_key="test", secret_key="test", region="us-east-1", bucket=BUCKET
    )
    c = make_s3_client(settings)
    yield c
    # clean the bucket between tests so each test starts empty
    try:
        for obj in c.list_objects_v2(Bucket=BUCKET).get("Contents", []):
            c.delete_object(Bucket=BUCKET, Key=obj["Key"])
        c.delete_bucket(Bucket=BUCKET)
    except Exception:  # bucket may not exist if the test failed early
        pass


@pytest.fixture()
def sample_project(tmp_path: Path) -> Path:
    generate_sample(["--out", str(tmp_path / "data" / "sample")])
    cfg = yaml.safe_load((ROOT / "config" / "datasets.sample.yaml").read_text())
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "datasets.sample.yaml").write_text(yaml.safe_dump(cfg))
    return tmp_path


def test_sample_generation_is_deterministic(tmp_path: Path):
    generate_sample(["--out", str(tmp_path / "a"), "--seed", "7"])
    generate_sample(["--out", str(tmp_path / "b"), "--seed", "7"])
    files = list((tmp_path / "a").rglob("*.csv"))
    assert len(files) == EXPECTED_SAMPLE_FILES
    for f in files:
        assert f.read_bytes() == (tmp_path / "b" / f.relative_to(tmp_path / "a")).read_bytes()


def test_committed_sample_matches_generator(tmp_path: Path):
    generate_sample(["--out", str(tmp_path)])
    for f in tmp_path.rglob("*.csv"):
        committed = ROOT / "data" / "sample" / f.relative_to(tmp_path)
        assert committed.read_bytes() == f.read_bytes(), f"{committed} is stale; run `make sample`"


def test_ingest_sample_end_to_end(sample_project: Path, client):
    cfg = sample_project / "config" / "datasets.sample.yaml"
    report = run_ingestion(cfg, client, BUCKET, "2026-11-16", sample_project)

    total = 0
    for source, result in report["sources"].items():
        assert result["missing_expected_files"] == [], source
        for info in result["files"]:
            body = client.get_object(Bucket=BUCKET, Key=info["object_key"])["Body"].read()
            assert hashlib.sha256(body).hexdigest() == info["sha256"]
            assert len(body) == info["size_bytes"]
            assert info["object_key"].startswith(f"bronze/{source}/ingestion_date=2026-11-16/")
            total += 1
    assert total == EXPECTED_SAMPLE_FILES
    assert len(client.list_objects_v2(Bucket=BUCKET)["Contents"]) == EXPECTED_SAMPLE_FILES

    manifest = json.loads((sample_project / "reports" / "2026-11-16" / "ingestion_manifest.json").read_text())
    assert manifest["bucket"] == BUCKET


def test_same_date_rerun_is_idempotent(sample_project: Path, client):
    cfg = sample_project / "config" / "datasets.sample.yaml"
    run_ingestion(cfg, client, BUCKET, "2026-11-16", sample_project)
    run_ingestion(cfg, client, BUCKET, "2026-11-16", sample_project)
    assert len(client.list_objects_v2(Bucket=BUCKET)["Contents"]) == EXPECTED_SAMPLE_FILES


def test_new_date_creates_a_separate_snapshot(sample_project: Path, client):
    cfg = sample_project / "config" / "datasets.sample.yaml"
    run_ingestion(cfg, client, BUCKET, "2026-11-16", sample_project)
    run_ingestion(cfg, client, BUCKET, "2026-11-17", sample_project)
    assert len(client.list_objects_v2(Bucket=BUCKET)["Contents"]) == 2 * EXPECTED_SAMPLE_FILES


def test_missing_expected_file_is_reported_not_fatal(sample_project: Path, client):
    (sample_project / "data" / "sample" / "m5" / "calendar.csv").unlink()
    cfg = sample_project / "config" / "datasets.sample.yaml"
    report = run_ingestion(cfg, client, BUCKET, "2026-11-16", sample_project)
    assert report["sources"]["m5"]["missing_expected_files"] == ["calendar.csv"]
