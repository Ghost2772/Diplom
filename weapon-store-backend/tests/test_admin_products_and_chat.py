import asyncio
import io
from urllib.parse import parse_qs
from uuid import UUID

import httpx
import pytest
from PIL import Image

from app.ai import ai_service
from app.core.security import create_access_token
from app.models.category import Category
from app.models.chat_message import ChatMessage
from app.models.user import User


@pytest.fixture
def admin_catalog(api_client):
    client, session_factory = api_client

    async def prepare():
        async with session_factory.begin() as db:
            admin = User(email="editor@example.com", hashed_password="unused", is_admin=True)
            customer = User(email="customer@example.com", hashed_password="unused")
            categories = [
                Category(name="Оптика", slug="optics"),
                Category(name="Амуниция", slug="ammunition-and-gear"),
            ]
            db.add_all([admin, customer, *categories])
            await db.flush()
            return admin.id, customer.id, [category.id for category in categories]

    admin_id, customer_id, categories = asyncio.run(prepare())
    admin_headers = {
        "Authorization": "Bearer " + create_access_token({"sub": "editor@example.com"})
    }
    customer_headers = {
        "Authorization": "Bearer " + create_access_token({"sub": "customer@example.com"})
    }
    product = {
        "name": "Новый прицел",
        "sku": "EDITOR-001",
        "brand": "Demo",
        "category_id": categories[0],
        "price": "1500.50",
        "old_price": "1700.00",
        "stock": 8,
        "short_description": "Краткое описание",
        "description": "Полное описание",
        "attributes": {"Увеличение": "3×"},
        "image_url": "/images/test.webp",
        "is_active": True,
        "is_featured": True,
        "is_regulated": False,
    }
    return (
        client,
        session_factory,
        admin_headers,
        customer_headers,
        product,
        (
            admin_id,
            customer_id,
            categories,
        ),
    )


def test_admin_creates_and_edits_product_without_changing_order_snapshot(admin_catalog):
    client, _, admin, customer, data, (_, _, categories) = admin_catalog
    assert client.post("/products", json=data).status_code == 401
    assert client.post("/products", json=data, headers=customer).status_code == 403
    created_response = client.post("/products", json=data, headers=admin)
    assert created_response.status_code == 200
    created = created_response.json()
    url = f"/products/{created['id']}"
    assert client.get(url).json()["description"] == data["description"]

    assert (
        client.post(
            "/cart/items", json={"product_id": created["id"], "quantity": 1}, headers=customer
        ).status_code
        == 200
    )
    order = client.post("/orders/create-from-cart", headers=customer).json()
    edited = {
        **data,
        "name": "Обновлённый товар",
        "category_id": categories[1],
        "price": "1900.00",
        "old_price": None,
        "stock": 3,
        "is_active": False,
        "attributes": {"Материал": "Металл"},
        "image_url": None,
    }
    assert client.put(url, json=edited).status_code == 401
    assert client.put(url, json=edited, headers=customer).status_code == 403
    response = client.put(url, json=edited, headers=admin)
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == created["id"] and updated["slug"] == created["slug"]
    assert updated["attributes"] == {"Материал": "Металл"}
    assert updated["old_price"] is None and updated["image_url"] is None
    assert updated["category_id"] == categories[1] and updated["stock"] == 3
    assert client.get("/products", params={"is_active": True}).json() == []
    assert client.get(url).json()["name"] == edited["name"]
    saved_order = client.get(f"/orders/{order['id']}", headers=customer).json()
    assert saved_order["items"][0]["product_name"] == data["name"]
    assert saved_order["items"][0]["price"] == 1500.5
    assert saved_order["total_amount"] == 1500.5


def test_product_editor_rejects_invalid_values_and_duplicate_skus(admin_catalog):
    client, _, admin, _, data, _ = admin_catalog
    created = client.post("/products", json=data, headers=admin).json()
    url = f"/products/{created['id']}"
    assert client.post("/products", json=data, headers=admin).status_code == 400
    other = client.post("/products", json={**data, "sku": "EDITOR-002"}, headers=admin).json()
    assert other["slug"] != created["slug"]
    assert client.put(url, json={**data, "sku": other["sku"]}, headers=admin).status_code == 400
    for invalid in [
        {"name": "   "},
        {"price": "-1"},
        {"price": "1.001"},
        {"stock": -1},
        {"old_price": "100"},
        {"image_url": "javascript:alert(1)"},
        {"attributes": {"Калибр": " "}},
        {"attributes": {"Материал": "Сталь", "материал": "Дерево"}},
    ]:
        response = client.put(url, json={**data, **invalid}, headers=admin)
        assert response.status_code == 422, response.text
    assert client.put(url, json={**data, "category_id": 999999}, headers=admin).status_code == 404
    assert client.put("/products/999999", json=data, headers=admin).status_code == 404
    assert client.get(url).json()["name"] == data["name"]


@pytest.mark.parametrize("image_format", ["PNG", "JPEG", "WEBP"])
def test_admin_image_upload_and_public_delivery(admin_catalog, monkeypatch, tmp_path, image_format):
    from app.routers import uploads

    client, _, admin, customer, data, _ = admin_catalog
    monkeypatch.setattr(uploads.settings, "PRODUCT_UPLOAD_DIR", str(tmp_path / "photos"))
    image = io.BytesIO()
    Image.new("RGB", (20, 10), color="gray").save(image, format=image_format)
    contents = image.getvalue()
    files = {"file": ("../../untrusted-name.svg", contents, "application/octet-stream")}
    assert client.post("/products/images", files=files).status_code == 401
    assert client.post("/products/images", files=files, headers=customer).status_code == 403
    response = client.post("/products/images", files=files, headers=admin)
    assert response.status_code == 201
    image_url = response.json()["image_url"]
    served = client.get(image_url.removeprefix("/api"))
    assert served.status_code == 200 and served.content == contents
    assert served.headers["content-type"].startswith("image/")
    assert served.headers["x-content-type-options"] == "nosniff"
    assert len(list((tmp_path / "photos").iterdir())) == 1
    product = client.post("/products", json={**data, "image_url": image_url}, headers=admin).json()
    assert client.get(f"/products/{product['id']}").json()["image_url"] == image_url
    assert client.get("/media/products/not-an-image.png").status_code == 404
    for bad_data in [b"not an image", b"<svg><script>alert(1)</script></svg>"]:
        result = client.post(
            "/products/images", headers=admin, files={"file": ("fake.png", bad_data, "image/png")}
        )
        assert result.status_code == 400
    monkeypatch.setattr(uploads, "MAX_IMAGE_BYTES", 10)
    assert client.post("/products/images", files=files, headers=admin).status_code == 413


def test_clearing_chat_is_private_persistent_and_resets_model_context(admin_catalog, monkeypatch):
    client, session_factory, admin, customer, _, (admin_id, customer_id, _) = admin_catalog

    async def history():
        async with session_factory.begin() as db:
            for user_id in [admin_id, customer_id]:
                db.add_all(
                    [
                        ChatMessage(user_id=user_id, role="user", content="Старый вопрос"),
                        ChatMessage(user_id=user_id, role="assistant", content="Старый ответ"),
                    ]
                )

    asyncio.run(history())
    other_history = client.get("/ai/history", headers=admin).json()
    assert client.delete("/ai/history").status_code == 401
    assert client.delete("/ai/history", headers=customer).status_code == 204
    assert client.get("/ai/history", headers=customer).json() == []
    assert client.get("/ai/history", headers=admin).json() == other_history
    assert client.delete("/ai/history", headers=customer).status_code == 204

    async def fresh_response(message, db, history):
        assert message == "Что есть в каталоге?"
        assert history == []
        return "Новый ответ"

    monkeypatch.setattr(ai_service, "call_gigachat", fresh_response)
    result = client.post("/ai/chat", json={"message": "Что есть в каталоге?"}, headers=customer)
    assert result.json()["answer"] == "Новый ответ"
    assert [item["content"] for item in client.get("/ai/history", headers=customer).json()] == [
        "Что есть в каталоге?",
        "Новый ответ",
    ]


def test_late_ai_reply_does_not_reappear_after_clear_in_another_tab(admin_catalog, monkeypatch):
    client, _, _, customer, _, _ = admin_catalog

    async def delayed_response(message, db, history):
        response = await asyncio.to_thread(client.delete, "/ai/history", headers=customer)
        assert response.status_code == 204
        return "Запоздавший ответ"

    monkeypatch.setattr(ai_service, "call_gigachat", delayed_response)
    response = client.post("/ai/chat", json={"message": "Что есть в каталоге?"}, headers=customer)
    assert response.status_code == 200
    assert "очищена" in response.json()["answer"]
    assert client.get("/ai/history", headers=customer).json() == []


def test_gigachat_auth_and_catalog_context_contract(admin_catalog, monkeypatch):
    import json

    client, _, admin, customer, data, _ = admin_catalog
    client.post("/products", json=data, headers=admin)
    monkeypatch.setattr(ai_service.settings, "GIGACHAT_AUTH_KEY", "test-authorization-key")
    monkeypatch.setattr(ai_service.settings, "GIGACHAT_CA_BUNDLE", None)
    calls = []

    def upstream(request):
        calls.append(request)
        if request.url.path.endswith("/oauth"):
            assert request.headers["authorization"] == "Basic test-authorization-key"
            assert UUID(request.headers["rquid"]).version == 4
            assert parse_qs(request.content.decode())["scope"] == ["GIGACHAT_API_PERS"]
            return httpx.Response(200, json={"access_token": "test-access-token"})
        assert request.headers["authorization"] == "Bearer test-access-token"
        payload = json.loads(request.content)
        assert "Увеличение: 3×" in payload["messages"][0]["content"]
        assert payload["messages"][-1] == {"role": "user", "content": "Что есть в каталоге?"}
        assert len(payload["messages"]) == 2
        return httpx.Response(200, json={"choices": [{"message": {"content": "Ответ GigaChat"}}]})

    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        ai_service.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            **kwargs,
            transport=httpx.MockTransport(upstream),
        ),
    )
    response = client.post("/ai/chat", json={"message": "Что есть в каталоге?"}, headers=customer)
    assert response.json()["answer"] == "Ответ GigaChat"
    assert len(calls) == 2
