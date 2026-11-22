from __future__ import annotations

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from .config import Settings


def make_s3_client(settings: Settings):
    return boto3.client(
        "s3",
        endpoint_url=settings.endpoint_url,
        aws_access_key_id=settings.access_key,
        aws_secret_access_key=settings.secret_key,
        region_name=settings.region,
        config=Config(s3={"addressing_style": "path"}),
    )

def ensure_bucket(client, bucket: str) -> None:
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError as exc:
        code = str(exc.response.get("Error", {}).get("Code", ""))
        if code not in {"404", "NoSuchBucket", "NotFound"}:
            raise
        client.create_bucket(Bucket=bucket)

def upload_file(client, bucket: str, local_path, object_key: str) -> None:
    client.upload_file(str(local_path), bucket, object_key)
