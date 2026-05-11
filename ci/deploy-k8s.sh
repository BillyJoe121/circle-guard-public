#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
REGISTRY="${2:-circleguard}"
TAG="${3:-${ENVIRONMENT}}"
NAMESPACE="circleguard-${ENVIRONMENT}"

kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -k "k8s/${ENVIRONMENT}"

while read -r service; do
  [ -z "$service" ] && continue
  kubectl -n "$NAMESPACE" set image "deployment/${service}" "app=${REGISTRY}/${service}:${TAG}"
done < ci/services.txt

kubectl -n "$NAMESPACE" rollout status deployment/postgres --timeout=180s
kubectl -n "$NAMESPACE" rollout status deployment/redis --timeout=120s
kubectl -n "$NAMESPACE" rollout status deployment/neo4j --timeout=240s
kubectl -n "$NAMESPACE" rollout status deployment/kafka --timeout=240s

while read -r service; do
  [ -z "$service" ] && continue
  kubectl -n "$NAMESPACE" rollout status "deployment/${service}" --timeout=300s
done < ci/services.txt
