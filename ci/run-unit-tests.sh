#!/usr/bin/env bash
set -euo pipefail

./gradlew \
  :services:circleguard-auth-service:test --tests "com.circleguard.auth.service.QrTokenServiceWorkshopTest" \
  :services:circleguard-form-service:test --tests "com.circleguard.form.service.SymptomMapperWorkshopTest" \
  --console=plain \
  --no-daemon
