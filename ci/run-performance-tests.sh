#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-master}"
USERS="${2:-20}"
SPAWN_RATE="${3:-5}"
RUN_TIME="${4:-1m}"
NAMESPACE="circleguard-${ENVIRONMENT}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" -m venv .venv-ci
. .venv-ci/bin/activate
python -m pip install --upgrade pip
python -m pip install -r tests/system/requirements.txt
mkdir -p build/locust

declare -a PIDS=()
cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

kubectl -n "$NAMESPACE" port-forward svc/circleguard-identity-service 8083:8083 >/tmp/cg-perf-identity.log 2>&1 &
PIDS+=("$!")
kubectl -n "$NAMESPACE" port-forward svc/circleguard-form-service 8086:8086 >/tmp/cg-perf-form.log 2>&1 &
PIDS+=("$!")
kubectl -n "$NAMESPACE" port-forward svc/circleguard-promotion-service 8088:8088 >/tmp/cg-perf-promotion.log 2>&1 &
PIDS+=("$!")
kubectl -n "$NAMESPACE" port-forward svc/circleguard-gateway-service 8087:8087 >/tmp/cg-perf-gateway.log 2>&1 &
PIDS+=("$!")

sleep 10
locust \
  -f tests/performance/locustfile.py \
  --headless \
  --users "$USERS" \
  --spawn-rate "$SPAWN_RATE" \
  --run-time "$RUN_TIME" \
  --csv build/locust/circleguard \
  --html build/locust/report.html
