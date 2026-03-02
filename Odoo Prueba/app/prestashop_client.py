import json
import re
import xml.etree.ElementTree as ET
from urllib import parse, request
from urllib.error import HTTPError, URLError

from fastapi import HTTPException

from app.config import settings


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PrestashopClient:
    def __init__(self) -> None:
        self.store_url = settings.prestashop_url.strip().rstrip("/")
        self.access_token = settings.prestashop_api_key.strip()
        self.language_id = settings.prestashop_language_id
        self.host_header = settings.prestashop_host_header.strip()

    def _validate_config(self) -> None:
        if not self.store_url:
            raise HTTPException(status_code=500, detail="Falta configurar PRESTASHOP_URL")
        if not self.access_token:
            raise HTTPException(status_code=500, detail="Falta configurar PRESTASHOP_API_KEY")
        if "/admin" in self.store_url:
            raise HTTPException(status_code=500, detail="PRESTASHOP_URL debe ser la base del sitio (ej: http://prestashop o http://localhost:8081), no la URL de admin")

    def _build_url(self, path: str, query: dict | None = None, output_json: bool = False) -> str:
        base_query = {"ws_key": self.access_token}
        if output_json:
            base_query["output_format"] = "JSON"
        if query:
            base_query.update(query)
        query_string = parse.urlencode(base_query, doseq=True)
        return f"{self.store_url}{path}?{query_string}"

    def _http(
        self,
        method: str,
        path: str,
        query: dict | None = None,
        body: bytes | None = None,
        content_type: str = "application/json",
        output_json: bool = False,
        redirect_depth: int = 0,
    ):
        self._validate_config()

        url = self._build_url(path, query=query, output_json=output_json)
        headers = {
            "Accept": "application/json" if output_json else "application/xml",
            "Content-Type": content_type,
        }
        if self.host_header:
            headers["Host"] = self.host_header
        req = request.Request(url=url, method=method, headers=headers, data=body)
        opener = request.build_opener(_NoRedirect())

        try:
            with opener.open(req, timeout=30) as response:
                return response.read().decode("utf-8")
        except HTTPError as exc:
            if exc.code in {301, 302, 303, 307, 308} and redirect_depth < 3:
                location = exc.headers.get("Location")
                if location:
                    parsed = parse.urlparse(location)
                    redirected_path = parsed.path or path
                    redirected_query = parse.parse_qs(parsed.query) if parsed.query else {}
                    return self._http(
                        method=method,
                        path=redirected_path,
                        query=redirected_query,
                        body=body,
                        content_type=content_type,
                        output_json=output_json,
                        redirect_depth=redirect_depth + 1,
                    )

            response_body = exc.read().decode("utf-8", errors="replace")
            detail = f"Error PrestaShop {exc.code} en {path}: {response_body}"
            raise HTTPException(status_code=502, detail=detail) from exc
        except URLError as exc:
            raise HTTPException(status_code=502, detail=f"No se pudo conectar a PrestaShop: {exc.reason}") from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Error inesperado PrestaShop: {exc}") from exc

    def get_resource(self, resource: str, query: dict | None = None):
        raw = self._http("GET", f"/api/{resource}", query=query, output_json=True)
        return json.loads(raw) if raw else {}

    def get_resource_xml(self, resource: str, resource_id: str | int):
        return self._http("GET", f"/api/{resource}/{resource_id}", output_json=False)

    def put_resource_xml(self, resource: str, resource_id: str | int, xml_payload: str):
        return self._http(
            "PUT",
            f"/api/{resource}/{resource_id}",
            body=xml_payload.encode("utf-8"),
            content_type="application/xml",
            output_json=False,
        )

    def post_resource_xml(self, resource: str, xml_payload: str):
        return self._http(
            "POST",
            f"/api/{resource}",
            body=xml_payload.encode("utf-8"),
            content_type="application/xml",
            output_json=False,
        )

    def create_or_update_product(self, *, product_id: str | int | None, title: str, reference: str, price: float, active: bool):
        schema_xml = self._http("GET", "/api/products", query={"schema": "blank"}, output_json=False)
        root = ET.fromstring(schema_xml)
        product_node = root.find("product")

        if product_node is None:
            raise HTTPException(status_code=502, detail="No se pudo preparar XML de producto para PrestaShop")

        def set_field(name: str, value: str):
            node = product_node.find(name)
            if node is not None:
                node.text = value

        def set_lang_field(name: str, value: str):
            parent = product_node.find(name)
            if parent is None:
                return
            lang = parent.find("language")
            if lang is None:
                lang = ET.SubElement(parent, "language")
                lang.set("id", str(self.language_id))
            lang.text = value

        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "producto"

        if product_id is not None:
            set_field("id", str(product_id))

        set_field("reference", reference)
        set_field("price", f"{price:.2f}")
        set_field("active", "1" if active else "0")
        set_field("state", "1")
        set_field("position_in_category", "1")
        set_field("available_for_order", "1")
        set_field("show_price", "1")
        set_field("minimal_quantity", "1")
        set_field("id_category_default", "2")
        set_field("id_tax_rules_group", "1")
        set_lang_field("name", title)
        set_lang_field("link_rewrite", slug)

        xml_payload = ET.tostring(root, encoding="unicode")
        if product_id is None:
            response_xml = self.post_resource_xml("products", xml_payload)
        else:
            response_xml = self.put_resource_xml("products", product_id, xml_payload)

        response_root = ET.fromstring(response_xml)
        response_product = response_root.find("product")
        resolved_id = None
        if response_product is not None:
            resolved_id = response_product.findtext("id")

        return {
            "id": resolved_id or str(product_id or ""),
            "title": title,
            "sku": reference,
            "active": active,
        }

    def post(self, endpoint: str, payload: dict):
        resource = endpoint.strip("/").replace(".json", "")
        if resource != "products":
            raise HTTPException(status_code=501, detail=f"POST no implementado para recurso PrestaShop: {resource}")

        product = payload.get("product", {})
        title = product.get("title") or "Producto"
        variants = product.get("variants") or [{}]
        variant = variants[0]
        reference = (variant.get("sku") or "").strip()
        price = float(variant.get("price") or 0.0)
        active = product.get("status", "active") == "active"
        created = self.create_or_update_product(product_id=None, title=title, reference=reference, price=price, active=active)
        return {"product": {"id": created["id"], "title": created["title"], "variants": [{"sku": created["sku"], "price": str(price)}], "status": "active" if active else "draft"}}

    def put(self, endpoint: str, payload: dict):
        resource_path = endpoint.strip("/")
        if not resource_path.startswith("products/"):
            raise HTTPException(status_code=501, detail=f"PUT no implementado para recurso PrestaShop: {resource_path}")

        product_id = resource_path.split("/")[1].replace(".json", "")
        product = payload.get("product", {})
        title = product.get("title") or "Producto"
        variants = product.get("variants") or [{}]
        variant = variants[0]
        reference = (variant.get("sku") or "").strip()
        price = float(variant.get("price") or 0.0)
        active = product.get("status", "active") == "active"
        updated = self.create_or_update_product(product_id=product_id, title=title, reference=reference, price=price, active=active)
        return {"product": {"id": updated["id"], "title": updated["title"], "variants": [{"sku": updated["sku"], "price": str(price)}], "status": "active" if active else "draft"}}

    def patch(self, endpoint: str, payload: dict):
        return self.put(endpoint, payload)
