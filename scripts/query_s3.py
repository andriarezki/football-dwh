"""Athena-style query: DuckDB reads the curated Parquet straight from S3-compatible storage.
Needs AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_ENDPOINT_URL in the environment (see s3store/)."""
import os, sys
from urllib.parse import urlparse
import duckdb

bucket = sys.argv[1] if len(sys.argv) > 1 else "football-lake"
ep = urlparse(os.environ["AWS_ENDPOINT_URL"])
c = duckdb.connect()
c.execute("INSTALL httpfs; LOAD httpfs;")
c.execute("CREATE SECRET (TYPE S3, KEY_ID ?, SECRET ?, ENDPOINT ?, USE_SSL ?, URL_STYLE 'path', REGION 'us-east-1')",
          [os.environ["AWS_ACCESS_KEY_ID"], os.environ["AWS_SECRET_ACCESS_KEY"], ep.netloc, ep.scheme == "https"])
for row in c.execute(f"""SELECT season_label, matches, avg_goals, home_win_pct
    FROM read_parquet('s3://{bucket}/football-dwh/curated/mart_season_summary/*.parquet') ORDER BY 1""").fetchall():
    print(row)
