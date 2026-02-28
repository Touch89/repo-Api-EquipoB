import json
from urllib import parse, request
from urllib.error import HTTPError, URLError

from fastapi import HTTPException

from app.config import settings


class ShopifyClient:
    def __init__(self) -> None:
        self.store_url = settings.shopify_store_url.strip().rstrip("/")
        self.access_token = settings.shopify_access_token.strip()
        self.api_version = settings.shopify_api_version.strip() or "2024-10"

    def _validate_config(self) -> None:
        if not self.store_url:
            raise HTTPException(status_code=500, detail="Falta configurar SHOPIFY_STORE_URL")
        if not self.access_token:
            raise HTTPException(status_code=500, detail="Falta configurar SHOPIFY_ACCESS_TOKEN")

    def get(self, endpoint: str, query: dict | None = None):
        self._validate_config()

        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        url = f"{self.store_url}/admin/api/{self.api_version}{path}"
        if query:
            url = f"{url}?{parse.urlencode(query, doseq=True)}"

        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        req = request.Request(url=url, method="GET", headers=headers)

        try:
            with request.urlopen(req, timeout=30) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload) if payload else {}
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            detail = f"Error Shopify {exc.code} en {endpoint}: {body}"
            raise HTTPException(status_code=502, detail=detail) from exc
        except URLError as exc:
            raise HTTPException(status_code=502, detail=f"No se pudo conectar a Shopify: {exc.reason}") from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Error inesperado Shopify: {exc}") from exc
