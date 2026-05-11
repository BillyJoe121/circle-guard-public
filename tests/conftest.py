import os
import time
import uuid

import jwt
import pytest
import requests


JWT_SECRET = os.getenv("JWT_SECRET", "my-super-secret-dev-key-32-chars-long-12345678")
QR_SECRET = os.getenv("QR_SECRET", "my-qr-secret-key-for-dev-1234567890")


@pytest.fixture(scope="session")
def urls():
    return {
        "auth": os.getenv("AUTH_URL", "http://localhost:8180"),
        "identity": os.getenv("IDENTITY_URL", "http://localhost:8083"),
        "form": os.getenv("FORM_URL", "http://localhost:8086"),
        "promotion": os.getenv("PROMOTION_URL", "http://localhost:8088"),
        "gateway": os.getenv("GATEWAY_URL", "http://localhost:8087"),
    }


def unique_identity(prefix="user"):
    return f"{prefix}-{uuid.uuid4()}@circleguard.edu"


def token_for(anonymous_id, permissions=None, secret=JWT_SECRET):
    now = int(time.time())
    return jwt.encode(
        {
            "sub": str(anonymous_id),
            "iat": now,
            "exp": now + 600,
            "permissions": permissions or ["ROLE_HEALTH_CENTER"],
        },
        secret,
        algorithm="HS256",
    )


def qr_token_for(anonymous_id):
    now = int(time.time())
    return jwt.encode(
        {"sub": str(anonymous_id), "iat": now, "exp": now + 300},
        QR_SECRET,
        algorithm="HS256",
    )


def assert_json_response(response, expected_status=200):
    assert response.status_code == expected_status, response.text
    assert response.headers.get("content-type", "").startswith("application/json")
    return response.json()


def map_identity(identity_url, real_identity=None):
    payload = {"realIdentity": real_identity or unique_identity()}
    response = requests.post(f"{identity_url}/api/v1/identities/map", json=payload, timeout=10)
    body = assert_json_response(response)
    assert "anonymousId" in body
    return body["anonymousId"]
