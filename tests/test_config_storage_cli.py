import datetime as dt

import pytest
from botocore.exceptions import ClientError

from supplychain360 import cli
from supplychain360.config import Settings
from supplychain360.ingest import validate_ingestion_date
from supplychain360.storage import ensure_bucket


def test_settings_defaults(monkeypatch, tmp_path):
    for key in ("S3_ENDPOINT_URL", "S3_ACCESS_KEY", "S3_SECRET_KEY", "S3_REGION", "S3_BUCKET"):
        monkeypatch.delenv(key, raising=False)
    s = Settings.from_env(tmp_path / "missing.env")
    assert s.endpoint_url == "http://localhost:9000"
    assert s.bucket == "supplychain360-lake"


def test_settings_reads_env_file(monkeypatch, tmp_path):
    for key in ("S3_ENDPOINT_URL", "S3_BUCKET"):
        monkeypatch.delenv(key, raising=False)
    env = tmp_path / ".env"
    env.write_text("S3_BUCKET=my-bucket\nS3_ENDPOINT_URL=http://minio:9000\n")
    s = Settings.from_env(env)
    assert s.bucket == "my-bucket"
    assert s.endpoint_url == "http://minio:9000"


def test_validate_date_accepts_iso_and_defaults_to_today():
    assert validate_ingestion_date("2026-11-16") == "2026-11-16"
    assert validate_ingestion_date(None) == dt.date.today().isoformat()
    assert validate_ingestion_date("") == dt.date.today().isoformat()


@pytest.mark.parametrize("bad", ["16-11-2026", "2026/11/16", "2026-13-01", "yesterday"])
def test_validate_date_rejects_bad_values(bad):
    with pytest.raises(ValueError):
        validate_ingestion_date(bad)


class _Client:
    def __init__(self, code=None):
        self.code, self.created = code, False

    def head_bucket(self, Bucket):
        if self.code:
            raise ClientError({"Error": {"Code": self.code}}, "HeadBucket")

    def create_bucket(self, Bucket):
        self.created = True


def test_ensure_bucket_noop_when_present():
    c = _Client()
    ensure_bucket(c, "b")
    assert c.created is False


def test_ensure_bucket_creates_on_404():
    c = _Client("404")
    ensure_bucket(c, "b")
    assert c.created is True


def test_ensure_bucket_reraises_other_errors():
    with pytest.raises(ClientError):
        ensure_bucket(_Client("403"), "b")


def test_cli_rejects_bad_date(capsys):
    assert cli.main(["--date", "not-a-date"]) == 2
    assert "YYYY-MM-DD" in capsys.readouterr().err


def test_cli_rejects_missing_config(capsys):
    assert cli.main(["--config", "does/not/exist.yaml", "--date", "2026-11-16"]) == 2
    assert "config file not found" in capsys.readouterr().err
