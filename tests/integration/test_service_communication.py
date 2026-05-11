import uuid

import requests

from tests.conftest import assert_json_response, map_identity, token_for, unique_identity


def test_identity_returns_same_anonymous_id_for_same_real_identity(urls):
    real_identity = unique_identity("integration-repeat")
    first = map_identity(urls["identity"], real_identity)
    second = map_identity(urls["identity"], real_identity)
    assert first == second


def test_identity_registers_visitor_for_auth_handoff(urls):
    response = requests.post(
        f"{urls['identity']}/api/v1/identities/visitor",
        json={
            "name": "Integration Visitor",
            "email": unique_identity("visitor"),
            "reason_for_visit": "pipeline validation",
        },
        timeout=10,
    )
    body = assert_json_response(response)
    assert uuid.UUID(body["anonymousId"])


def test_auth_visitor_handoff_issues_bearer_token(urls):
    anonymous_id = str(uuid.uuid4())
    response = requests.post(
        f"{urls['auth']}/api/v1/auth/visitor/handoff",
        json={"anonymousId": anonymous_id},
        timeout=10,
    )
    body = assert_json_response(response)
    assert body["token"]
    assert body["handoffPayload"].startswith(f"HANDOFF_TOKEN:{anonymous_id}:")


def test_form_submission_publishes_survey_contract(urls):
    anonymous_id = map_identity(urls["identity"], unique_identity("survey"))
    response = requests.post(
        f"{urls['form']}/api/v1/surveys",
        json={
            "anonymousId": anonymous_id,
            "hasFever": True,
            "hasCough": False,
            "otherSymptoms": "integration pipeline symptom",
        },
        timeout=10,
    )
    body = assert_json_response(response)
    assert body["anonymousId"] == anonymous_id
    assert body["hasFever"] is True


def test_promotion_accepts_authorized_health_status_report(urls):
    anonymous_id = map_identity(urls["identity"], unique_identity("promotion"))
    token = token_for(anonymous_id)
    response = requests.post(
        f"{urls['promotion']}/api/v1/health/report",
        json={"anonymousId": anonymous_id, "status": "SUSPECT", "adminOverride": True},
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    assert response.status_code in (200, 204), response.text


def test_gateway_rejects_malformed_qr_token(urls):
    response = requests.post(
        f"{urls['gateway']}/api/v1/gate/validate",
        json={"token": "not-a-jwt"},
        timeout=10,
    )
    body = assert_json_response(response)
    assert body["valid"] is False
    assert body["status"] == "RED"
