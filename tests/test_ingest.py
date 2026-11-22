from pathlib import Path

from supplychain360.ingest import build_object_key, discover_files
from supplychain360.inspection import inspect_csv, sha256_file


def test_object_key_layout():
    assert build_object_key("m5", "2026-11-16", "calendar.csv") == \
        "bronze/m5/ingestion_date=2026-11-16/calendar.csv"


def test_object_key_preserves_nested_source_path():
    assert build_object_key("olist", "2026-11-16", "archive/orders.csv") == \
        "bronze/olist/ingestion_date=2026-11-16/archive/orders.csv"


def test_object_key_rejects_parent_traversal():
    import pytest
    with pytest.raises(ValueError):
        build_object_key("olist", "2026-11-16", "../orders.csv")

def test_discover_csv_files(tmp_path: Path):
    (tmp_path / "a.csv").write_text("x\n1\n")
    (tmp_path / "b.txt").write_text("ignore")
    assert [p.name for p in discover_files(tmp_path, [".csv"])] == ["a.csv"]

def test_inspect_csv(tmp_path: Path):
    file = tmp_path / "sample.csv"
    file.write_text("id,name\n1,Ada\n2,\n", encoding="utf-8")
    result = inspect_csv(file)
    assert result["columns"] == ["id", "name"]
    assert result["sample_rows"] == 2
    assert result["sample_null_counts"]["name"] == 1

def test_sha256(tmp_path: Path):
    file = tmp_path / "x.txt"
    file.write_text("hello", encoding="utf-8")
    assert len(sha256_file(file)) == 64

def test_ingestion_writes_manifest_and_uploads(tmp_path: Path):
    import yaml

    from supplychain360.ingest import run_ingestion

    root = tmp_path
    source_dir = root / "data" / "raw" / "demo"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "tiny.csv"
    source_file.write_text("id,value\n1,alpha\n", encoding="utf-8")
    config_dir = root / "config"
    config_dir.mkdir()
    config_path = config_dir / "datasets.yaml"
    config_path.write_text(yaml.safe_dump({"sources": {"demo": {
        "description": "test source", "directory": "data/raw/demo",
        "expected_files": ["tiny.csv"], "allowed_extensions": [".csv"]
    }}}), encoding="utf-8")

    class FakeS3:
        def __init__(self):
            self.objects = {}
            self.bucket_created = False
        def head_bucket(self, Bucket):
            if not self.bucket_created:
                from botocore.exceptions import ClientError
                raise ClientError({"Error": {"Code": "404"}}, "HeadBucket")
        def create_bucket(self, Bucket):
            self.bucket_created = True
        def upload_file(self, filename, bucket, key):
            self.objects[(bucket, key)] = Path(filename).read_bytes()

    fake = FakeS3()
    report = run_ingestion(config_path, fake, "unit-test-bucket", "2026-11-16", root)
    assert fake.bucket_created is True
    key = ("unit-test-bucket", "bronze/demo/ingestion_date=2026-11-16/tiny.csv")
    assert fake.objects[key] == source_file.read_bytes()
    assert report["sources"]["demo"]["missing_expected_files"] == []
    assert (root / "reports" / "2026-11-16" / "ingestion_manifest.json").exists()
