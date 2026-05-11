#!/usr/bin/env bash
set -euo pipefail

REGISTRY="${1:-circleguard}"
TAG="${2:-dev}"
PUSH_IMAGES="${3:-false}"

while read -r service; do
  [ -z "$service" ] && continue
  echo "Building ${REGISTRY}/${service}:${TAG}"
  ./gradlew ":services:${service}:bootJar" --console=plain --no-daemon
  docker build \
    -t "${REGISTRY}/${service}:${TAG}" \
    "services/${service}"

  if [ "$PUSH_IMAGES" = "true" ]; then
    docker push "${REGISTRY}/${service}:${TAG}"
  fi
done < ci/services.txt
