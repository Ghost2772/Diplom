from urllib.parse import urljoin

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.parametrize("root_path", ["", "/api"])
def test_docs_and_auth_urls_work_with_and_without_proxy_prefix(root_path):
    test_app = FastAPI()
    test_app.include_router(app.router)
    origin = "https://demo.example.com"

    with TestClient(test_app, base_url=origin, root_path=root_path) as client:
        assert client.get(f"{root_path}/health").status_code == 200
        assert client.get(f"{root_path}/").json()["docs"] == f"{root_path}/docs"

        docs = client.get(f"{root_path}/docs")
        assert docs.status_code == 200
        assert f"{root_path}/openapi.json" in docs.text

        schema = client.get(f"{root_path}/openapi.json").json()
        server_path = schema.get("servers", [{"url": "/"}])[0]["url"]
        api_base = urljoin(origin, server_path.rstrip("/") + "/")
        token_url = schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"][
            "password"
        ]["tokenUrl"]
        assert urljoin(api_base, token_url) == f"{origin}{root_path}/auth/login"

        redirect = client.get(f"{root_path}/health/", follow_redirects=False)
        assert redirect.status_code == 307
        assert redirect.headers["location"] == f"{origin}{root_path}/health"
