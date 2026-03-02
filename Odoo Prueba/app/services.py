from app.odoo_client import OdooClient
from app.prestashop_client import PrestashopClient
from app.schemas import ProductCreate


class OdooService:
    def __init__(self) -> None:
        self.client = OdooClient()

    def get_orders(self):
        fields = ["name", "partner_id", "date_order", "amount_total", "state"]
        return self.client.execute_kw(
            "sale.order",
            "search_read",
            [[]],
            {"fields": fields, "limit": 100},
        )

    def get_products(self):
        fields = ["id", "name", "default_code", "list_price", "categ_id", "type"]
        return self.client.execute_kw(
            "product.template",
            "search_read",
            [[]],
            {"fields": fields, "limit": 200},
        )

    def get_product_stock(self):
        fields = ["id", "display_name", "default_code", "qty_available", "virtual_available"]
        return self.client.execute_kw(
            "product.product",
            "search_read",
            [[]],
            {"fields": fields, "limit": 200},
        )

    def get_products_for_prestashop_sync(self, limit: int = 200):
        fields = ["id", "display_name", "default_code", "list_price", "qty_available", "virtual_available", "active", "type"]
        return self.client.execute_kw(
            "product.product",
            "search_read",
            [[]],
            {"fields": fields, "limit": limit},
        )

    def get_product_for_prestashop_sync_by_reference(self, reference: str):
        fields = ["id", "display_name", "default_code", "list_price", "qty_available", "virtual_available", "active", "type"]
        products = self.client.execute_kw(
            "product.product",
            "search_read",
            [[["default_code", "=", reference]]],
            {"fields": fields, "limit": 1},
        )
        return products[0] if products else None

    def get_product_categories(self):
        fields = ["id", "name", "parent_id"]
        return self.client.execute_kw(
            "product.category",
            "search_read",
            [[]],
            {"fields": fields, "limit": 200},
        )

    def get_customers(self):
        fields = ["id", "name", "email", "phone", "mobile", "customer_rank"]
        return self.client.execute_kw(
            "res.partner",
            "search_read",
            [[["customer_rank", ">", 0]]],
            {"fields": fields, "limit": 200},
        )

    def get_suppliers(self):
        fields = ["id", "name", "email", "phone", "mobile", "supplier_rank"]
        return self.client.execute_kw(
            "res.partner",
            "search_read",
            [[["supplier_rank", ">", 0]]],
            {"fields": fields, "limit": 200},
        )

    def get_payments(self):
        fields = ["id", "name", "partner_id", "amount", "payment_type", "date", "state", "ref"]
        return self.client.execute_kw(
            "account.payment",
            "search_read",
            [[]],
            {"fields": fields, "limit": 200},
        )

    def get_product_by_sku(self, sku: str):
        fields = ["id", "display_name", "default_code", "list_price", "qty_available", "virtual_available"]
        return self.client.execute_kw(
            "product.product",
            "search_read",
            [[["default_code", "=", sku]]],
            {"fields": fields, "limit": 200},
        )

    def get_order_by_reference(self, reference: str):
        fields = ["id", "name", "partner_id", "date_order", "amount_total", "state"]
        return self.client.execute_kw(
            "sale.order",
            "search_read",
            [[["name", "ilike", reference]]],
            {"fields": fields, "limit": 200},
        )

    def create_product(self, product: ProductCreate):
        payload = {
            "name": product.name,
            "list_price": product.list_price,
            "standard_price": product.standard_price,
            "type": product.type,
        }

        if product.default_code:
            payload["default_code"] = product.default_code
        if product.categ_id:
            payload["categ_id"] = product.categ_id

        new_id = self.client.execute_kw("product.template", "create", [payload])
        return {"id": new_id, "name": product.name}

    def delete_product(self, product_template_id: int):
        return self.client.execute_kw("product.template", "unlink", [[product_template_id]])

    def bulk_create_products(self, products: list[ProductCreate]):
        created = []
        for product in products:
            created.append(self.create_product(product))

        return {"count": len(created), "items": created}


class PrestashopService:
    def __init__(self) -> None:
        self.client = PrestashopClient()

    @staticmethod
    def _as_resource_list(data, plural_key: str, singular_key: str):
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if isinstance(data.get(plural_key), list):
                return data.get(plural_key, [])
            if isinstance(data.get(singular_key), list):
                return data.get(singular_key, [])
            if isinstance(data.get(singular_key), dict):
                return [data.get(singular_key)]
        return []

    def get_products(self, limit: int = 50):
        data = self.client.get_resource("products", {"display": "full", "limit": f"[0,{max(limit - 1, 0)}]"})
        return self._as_resource_list(data, "products", "product")

    def get_existing_skus(self, limit: int = 250):
        data = self.client.get_resource("products", {"display": "full", "limit": f"[0,{max(limit - 1, 0)}]"})
        products = self._as_resource_list(data, "products", "product")
        skus = set()
        for product in products:
            sku = (product.get("reference") or "").strip().lower()
            if sku:
                skus.add(sku)
        return skus

    def find_product_by_reference(self, reference: str, limit: int = 250):
        data = self.client.get_resource(
            "products",
            {
                "display": "full",
                "filter[reference]": f"[{reference}]",
                "limit": f"[0,{max(limit - 1, 0)}]",
            },
        )
        products = self._as_resource_list(data, "products", "product")

        for product in products:
            sku = (product.get("reference") or "").strip()
            if sku.lower() == reference.strip().lower():
                return {
                    "product_id": product.get("id"),
                    "title": product.get("name") or product.get("id"),
                    "status": "active" if str(product.get("active", "1")) == "1" else "draft",
                    "variant_id": None,
                    "sku": sku,
                    "price": product.get("price"),
                }

        return None

    def create_product(self, product: ProductCreate):
        variant = {
            "price": str(product.list_price),
        }
        if product.default_code:
            variant["sku"] = product.default_code

        payload = {
            "product": {
                "title": product.name,
                "product_type": product.type,
                "variants": [variant],
            }
        }

        data = self.client.post("/products.json", payload)
        created = data.get("product", {})
        first_variant = (created.get("variants") or [{}])[0]
        return {
            "id": created.get("id"),
            "title": created.get("title"),
            "sku": first_variant.get("sku"),
        }

    def create_product_from_odoo(self, odoo_product: dict):
        reference = (odoo_product.get("default_code") or "").strip()
        title = odoo_product.get("display_name") or odoo_product.get("name") or reference
        price = float(odoo_product.get("list_price") or 0.0)

        variant = {
            "price": str(price),
        }
        if reference:
            variant["sku"] = reference

        payload = {
            "product": {
                "title": title,
                "variants": [variant],
                "status": "active" if odoo_product.get("active", True) else "draft",
            }
        }

        data = self.client.post("/products.json", payload)
        created = data.get("product", {})
        first_variant = (created.get("variants") or [{}])[0]
        return {
            "id": created.get("id"),
            "title": created.get("title"),
            "sku": first_variant.get("sku"),
        }

    def update_product_from_odoo_by_reference(self, reference: str, odoo_product: dict):
        found = self.find_product_by_reference(reference=reference)
        if not found:
            return None

        title = odoo_product.get("display_name") or odoo_product.get("name") or reference
        price = float(odoo_product.get("list_price") or 0.0)
        active = bool(odoo_product.get("active", True))

        payload = {
            "product": {
                "id": found["product_id"],
                "title": title,
                "status": "active" if active else "draft",
                "variants": [
                    {
                        "id": found["variant_id"],
                        "price": str(price),
                        "sku": reference,
                    }
                ],
            }
        }

        data = self.client.put(f"/products/{found['product_id']}.json", payload)
        updated = data.get("product", {})
        first_variant = (updated.get("variants") or [{}])[0]
        return {
            "id": updated.get("id"),
            "title": updated.get("title"),
            "status": updated.get("status"),
            "sku": first_variant.get("sku"),
            "price": first_variant.get("price"),
        }

    def deactivate_product_by_reference(self, reference: str):
        found = self.find_product_by_reference(reference=reference)
        if not found:
            return None

        payload = {
            "product": {
                "id": found["product_id"],
                "title": found.get("title") or reference,
                "status": "draft",
                "variants": [
                    {
                        "sku": found.get("sku") or reference,
                        "price": str(found.get("price") or 0.0),
                    }
                ],
            }
        }

        data = self.client.put(f"/products/{found['product_id']}.json", payload)
        updated = data.get("product", {})
        return {
            "id": updated.get("id"),
            "title": updated.get("title"),
            "status": updated.get("status"),
            "reference": reference,
        }

    def get_orders(self, limit: int = 50):
        data = self.client.get_resource("orders", {"display": "full", "limit": f"[0,{max(limit - 1, 0)}]"})
        return self._as_resource_list(data, "orders", "order")

    def get_customers(self, limit: int = 50):
        data = self.client.get_resource("customers", {"display": "full", "limit": f"[0,{max(limit - 1, 0)}]"})
        return self._as_resource_list(data, "customers", "customer")

    def get_suppliers(self, limit: int = 250):
        data = self.client.get_resource("suppliers", {"display": "full", "limit": f"[0,{max(limit - 1, 0)}]"})
        return self._as_resource_list(data, "suppliers", "supplier")

    def get_payments(self, order_limit: int = 20):
        data = self.client.get_resource("order_payments", {"display": "full", "limit": f"[0,{max(order_limit - 1, 0)}]"})
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if isinstance(data.get("order_payments"), list):
                return data.get("order_payments", [])
            if isinstance(data.get("order_payment"), list):
                return data.get("order_payment", [])
            if isinstance(data.get("order_payment"), dict):
                return [data.get("order_payment")]
        return []

    def get_product_by_sku(self, sku: str):
        found = self.find_product_by_reference(reference=sku)
        return [found] if found else []

    def get_order_by_reference(self, reference: str):
        data = self.client.get_resource("orders", {"display": "full", "filter[reference]": f"[{reference}]", "limit": "[0,50]"})
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if isinstance(data.get("orders"), list):
                return data.get("orders", [])
            if isinstance(data.get("order"), list):
                return data.get("order", [])
            if isinstance(data.get("order"), dict):
                return [data.get("order")]
        return []
