from fastapi.testclient import TestClient

from app.main import app
from app.config import settings


client = TestClient(app)


def test_authenticated_user_cannot_spoof_user_id():
    response = client.post(
        "/chat",
        headers={
            "Authorization": f"Bearer {settings.client_token}",
        },
        json={
            "conversation_id": "authz-test-001",
            "user_id": "EMP002",
            "message": "What is my casual leave balance?",
        },
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Access denied: user_id does not match the authenticated employee."
    )