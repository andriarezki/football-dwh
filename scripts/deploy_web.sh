#!/bin/sh
# Daily refresh: run pipeline, rebuild dashboard, publish to the web root (cron 03:30 UTC+7 = 20:30 UTC).
set -e
cd "$(dirname "$0")/.."
export PYTHONPATH=.deps
python3 run_pipeline.py >> pipeline.log 2>&1
python3 scripts/build_dashboard.py
install -d /var/www/andriarezki.tech/dwh
install -m 644 web/index.html /var/www/andriarezki.tech/dwh/index.html
