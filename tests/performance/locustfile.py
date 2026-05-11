import os
import time
import uuid

import jwt
from locust import HttpUser, between, task


IDENTITY_URL = os.getenv("IDENTITY_URL", "http://localhost:8083")
FORM_URL = os.getenv("FORM_URL", "http://localhost:8086")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8087")
PROMOTION_URL = os.getenv("PROMOTION_URL", "http://localhost:8088")
JWT_SECRET = os.getenv("JWT_SECRET", "my-super-secret-dev-key-32-chars-long-12345678")
QR_SECRET = os.getenv("QR_SECRET", "my-qr-secret-key-for-dev-1234567890")


def make_qr_token(anonymous_id):
    now = int(time.time())
    return jwt.encode({"sub": anonymous_id, "iat": now, "exp": now + 300}, QR_SECRET, algorithm="HS256")


def make_admin_token(anonymous_id):
    now = int(time.time())
    return jwt.encode(
        {
            "sub": anonymous_id,
            "iat": now,
            "exp": now + 600,
            "permissions": ["ROLE_HEALTH_CENTER"],
        },
        JWT_SECRET,
        algorithm="HS256",
    )


class CircleGuardUser(HttpUser):
    host = "http://localhost"
    wait_time = between(1, 3)

    def on_start(self):
        real_identity = f"locust-{uuid.uuid4()}@circleguard.edu"
        response = self.client.post(
            f"{IDENTITY_URL}/api/v1/identities/map",
            json={"realIdentity": real_identity},
            name="identity map",
        )
        self.anonymous_id = response.json().get("anonymousId", str(uuid.uuid4()))

    @task(5)
    def submit_health_survey(self):
        self.client.post(
            f"{FORM_URL}/api/v1/surveys",
            json={
                "anonymousId": self.anonymous_id,
                "hasFever": False,
                "hasCough": False,
                "otherSymptoms": "",
            },
            name="submit survey",
        )

    @task(4)
    def validate_gate_access(self):
        self.client.post(
            f"{GATEWAY_URL}/api/v1/gate/validate",
            json={"token": make_qr_token(self.anonymous_id)},
            name="validate QR",
        )

    @task(2)
    def read_aggregate_stats(self):
        self.client.get(f"{PROMOTION_URL}/api/v1/health-status/stats", name="health stats")

    @task(1)
    def report_suspect_case(self):
        self.client.post(
            f"{PROMOTION_URL}/api/v1/health/report",
            json={"anonymousId": self.anonymous_id, "status": "SUSPECT", "adminOverride": True},
            headers={"Authorization": f"Bearer {make_admin_token(self.anonymous_id)}"},
            name="report suspect",
        )
