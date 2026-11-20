"""Publish pipeline outputs to S3 (data lake: raw zone + curated Parquet zone).
Credentials come from the standard AWS chain (env vars / profile / IAM role); nothing is hard-coded.
Usage: python -m pipeline.s3_publish <bucket> [prefix]"""
import sys
from pathlib import Path
import boto3

def publish(bucket: str, prefix: str = "football-dwh", s3=None) -> list[str]:
    s3 = s3 or boto3.client("s3")
    keys = []
    for zone, root in (("raw", Path("lake/raw")), ("curated", Path("export"))):
        for f in sorted(root.rglob("*")):
            if f.is_file():
                rel = f.relative_to(root).as_posix()
                if zone == "curated":  # one folder per table so Athena can point a table at it
                    rel = f"{f.stem}/{f.name}"
                key = f"{prefix}/{zone}/{rel}"
                s3.upload_file(str(f), bucket, key)
                keys.append(key)
    return keys

if __name__ == "__main__":
    uploaded = publish(sys.argv[1], *(sys.argv[2:3]))
    print(f"uploaded {len(uploaded)} objects")
