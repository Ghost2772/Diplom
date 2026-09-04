from app.main import app


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
