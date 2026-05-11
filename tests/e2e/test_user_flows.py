import uuid

import requests

from tests.conftest import (
    assert_json_response,
    map_identity,
    qr_token_for,
    token_for,
    unique_identity,
)


def test_visitor_can_be_registered_handed_off_and_allowed_at_gate(urls):
    visitor = requests.post(
        f"{urls['identity']}/api/v1/identities/visitor",
        json={
            "name": "E2E Visitor",
            "email": unique_identity("e2e-visitor"),
            "reason_for_visit": "campus visit",
        },
        timeout=10,
    )
    anonymous_id = assert_json_response(visitor)["anonymousId"]

    handoff = requests.post(
        f"{urls['auth']}/api/v1/auth/visitor/handoff",
        json={"anonymousId": anonymous_id},
        timeout=10,
    )
    assert assert_json_response(handoff)["token"]

    gate = requests.post(
        f"{urls['gateway']}/api/v1/gate/validate",
        json={"token": qr_token_for(anonymous_id)},
        timeout=10,
    )
    body = assert_json_response(gate)
    assert body["valid"] is True
    assert body["status"] == "GREEN"


def test_symptomatic_survey_flow_is_accepted_for_existing_identity(urls):
    anonymous_id = map_identity(urls["identity"], unique_identity("e2e-symptoms"))
    response = requests.post(
        f"{urls['form']}/api/v1/surveys",
        json={
            "anonymousId": anonymous_id,
            "responses": {"fever": "YES", "cough": "YES"},
            "otherSymptoms": "fever and cough reported by E2E test",
        },
        timeout=10,
    )
    body = assert_json_response(response)
    assert body["id"]
    assert body["anonymousId"] == anonymous_id


def test_certificate_upload_flow_enters_pending_validation(urls):
    anonymous_id = map_identity(urls["identity"], unique_identity("e2e-certificate"))
    response = requests.post(
        f"{urls['form']}/api/v1/surveys",
        json={
            "anonymousId": anonymous_id,
            "attachmentPath": "s3://circleguard-test/certificate-negative.pdf",
            "hasFever": False,
            "hasCough": False,
        },
        timeout=10,
    )
    body = assert_json_response(response)
    assert body["validationStatus"] == "PENDING"


def test_health_center_can_report_confirmed_case(urls):
    anonymous_id = map_identity(urls["identity"], unique_identity("e2e-confirmed"))
    response = requests.post(
        f"{urls['promotion']}/api/v1/health/confirmed",
        json={"anonymousId": anonymous_id},
        headers={"Authorization": f"Bearer {token_for(anonymous_id)}"},
        timeout=15,
    )
    assert response.status_code in (200, 204), response.text


def test_privacy_dashboard_exposes_aggregate_health_stats_only(urls):
    response = requests.get(f"{urls['promotion']}/api/v1/health-status/stats", timeout=10)
    body = assert_json_response(response)
    assert "totalUsers" in body
    assert "realIdentity" not in body
    assert "email" not in body


def test_invalid_qr_flow_blocks_campus_entry(urls):
    response = requests.post(
        f"{urls['gateway']}/api/v1/gate/validate",
        json={"token": str(uuid.uuid4())},
        timeout=10,
    )
    body = assert_json_response(response)
    assert body["valid"] is False
    assert body["message"] == "Invalid or Expired Token"
