#!/usr/bin/env bash
set -euo pipefail
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
mode="${1:---verify-existing}"
case "$mode" in --verify-existing|--run) ;; *) echo 'Usage: bash run_pipeline.sh [--verify-existing|--run]'; exit 2;; esac
test -f compose.yaml || { echo 'Missing compose.yaml; see README.md'; exit 1; }
test -s data/demo.fastq || { echo 'Missing data/demo.fastq'; exit 1; }
docker compose config --quiet
docker info >/dev/null
mkdir -p reports/logs
image_id=$(docker image inspect rnaseq-miniproject:bookworm-arm64-v1 --format '{{.Id}}')
stamp=$(date +%Y%m%d_%H%M%S)
docker compose run --rm -T -e "RNASEQ_IMAGE_ID=$image_id" bio \
  python3 tools/pipeline.py "$mode" 2>&1 | tee "reports/logs/pipeline_${stamp}.log"
