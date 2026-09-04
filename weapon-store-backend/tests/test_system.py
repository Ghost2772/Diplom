from datetime import UTC, datetime

from app.main import app
from app.schemas.user import UserResponse


def test_health_endpoint(api_client) -> None:
    client, _ = api_client
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_openapi_contains_core_routes() -> None:
    paths = app.openapi()["paths"]

    assert "/auth/login" in paths
    assert "/products" in paths
    assert "/cart" in paths
    assert "/orders/my" in paths
    assert "/ai/chat" in paths


def test_user_response_accepts_internal_demo_email() -> None:
    profile = UserResponse(
        id=1,
        email="admin@mullers.local",
        full_name="Demo Administrator",
        phone=None,
        is_active=True,
        is_admin=True,
        created_at=datetime.now(UTC),
    )

    assert profile.email == "admin@mullers.local"
