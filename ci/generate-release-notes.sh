#!/usr/bin/env bash
set -euo pipefail

OUTPUT="${1:-build/release-notes.md}"
mkdir -p "$(dirname "$OUTPUT")"

LAST_TAG="$(git describe --tags --abbrev=0 2>/dev/null || true)"
RANGE="HEAD"
if [ -n "$LAST_TAG" ]; then
  RANGE="${LAST_TAG}..HEAD"
fi

{
  echo "# CircleGuard Release Notes"
  echo
  echo "- Generated at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "- Commit: $(git rev-parse --short HEAD)"
  if [ -n "$LAST_TAG" ]; then
    echo "- Previous tag: ${LAST_TAG}"
  else
    echo "- Previous tag: none"
  fi
  echo
  echo "## Services"
  sed 's/^/- /' ci/services.txt
  echo
  echo "## Changes"
  git log --pretty=format:'- %h %s (%an)' "$RANGE"
  echo
  echo
  echo "## Validation"
  echo "- Unit tests: Gradle test suites for selected microservices."
  echo "- Integration tests: service-to-service API checks under tests/integration."
  echo "- E2E tests: user-oriented flows under tests/e2e."
  echo "- Performance: Locust scenarios under tests/performance."
} > "$OUTPUT"

cat "$OUTPUT"
