"""ETL orchestrator: extract -> staging -> dimensions -> fact -> marts -> quality gate -> parquet export."""
import logging, sys, time
from pathlib import Path
import duckdb
from pipeline import extract, quality

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("pipeline")
STEPS = ["01_staging", "02_dimensions", "03_fact", "04_marts"]

def main(source="source", db="warehouse.duckdb") -> int:
    t0 = time.time()
    log.info("extract: %s", extract.land(source))
    con = duckdb.connect(db)
    for step in STEPS:
        con.execute(Path(f"sql/{step}.sql").read_text())
        log.info("step %s done", step)
    results = quality.run(con)
    bad = [(n, c) for n, c in results if c]
    for n, c in results:
        log.info("dq %-26s %s", n, "OK" if not c else f"FAIL ({c})")
    if bad:
        log.error("quality gate failed: %s (exports skipped)", bad)
        return 1
    Path("export").mkdir(exist_ok=True)
    for t in ("mart_team_season", "mart_season_summary", "fact_match"):
        con.execute(f"COPY {t} TO 'export/{t}.parquet' (FORMAT parquet)")
    log.info("done in %.1fs, rows: %s", time.time() - t0,
             con.execute("SELECT (SELECT count(*) FROM fact_match)").fetchone()[0])
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
