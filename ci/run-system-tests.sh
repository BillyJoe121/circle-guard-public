#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-stage}"
NAMESPACE="circleguard-${ENVIRONMENT}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" -m venv .venv-ci
. .venv-ci/bin/activate
python -m pip install --upgrade pip
python -m pip install -r tests/system/requirements.txt

declare -a PIDS=()
cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

kubectl -n "$NAMESPACE" port-forward svc/circleguard-auth-service 8180:8180 >/tmp/cg-auth.log 2>&1 &
PIDS+=("$!")
kubectl -n "$NAMESPACE" port-forward svc/circleguard-identity-service 8083:8083 >/tmp/cg-identity.log 2>&1 &
PIDS+=("$!")
kubectl -n "$NAMESPACE" port-forward svc/circleguard-form-service 8086:8086 >/tmp/cg-form.log 2>&1 &
PIDS+=("$!")
kubectl -n "$NAMESPACE" port-forward svc/circleguard-promotion-service 8088:8088 >/tmp/cg-promotion.log 2>&1 &
PIDS+=("$!")
kubectl -n "$NAMESPACE" port-forward svc/circleguard-gateway-service 8087:8087 >/tmp/cg-gateway.log 2>&1 &
PIDS+=("$!")

sleep 10
python -m pytest tests/integration tests/e2e --junitxml=build/system-tests.xml
