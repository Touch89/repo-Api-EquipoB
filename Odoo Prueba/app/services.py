from app.odoo_client import OdooClient
from app.shopify_client import ShopifyClient
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


class ShopifyService:
    def __init__(self) -> None:
        self.client = ShopifyClient()

    def get_products(self, limit: int = 50):
        data = self.client.get("/products.json", {"limit": limit})
        return data.get("products", [])

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

    def get_orders(self, limit: int = 50):
        data = self.client.get("/orders.json", {"status": "any", "limit": limit})
        return data.get("orders", [])

    def get_customers(self, limit: int = 50):
        data = self.client.get("/customers.json", {"limit": limit})
        return data.get("customers", [])

    def get_suppliers(self, limit: int = 250):
        data = self.client.get("/products.json", {"limit": limit, "fields": "vendor"})
        products = data.get("products", [])
        vendors = sorted({(item.get("vendor") or "").strip() for item in products if (item.get("vendor") or "").strip()})
        return [{"name": vendor} for vendor in vendors]

    def get_payments(self, order_limit: int = 20):
        orders = self.get_orders(limit=order_limit)
        payments = []
        for order in orders:
            order_id = order.get("id")
            if not order_id:
                continue

            tx_data = self.client.get(f"/orders/{order_id}/transactions.json")
            transactions = tx_data.get("transactions", [])
            for tx in transactions:
                payments.append(
                    {
                        "order_id": order_id,
                        "order_name": order.get("name"),
                        "transaction_id": tx.get("id"),
                        "kind": tx.get("kind"),
                        "status": tx.get("status"),
                        "amount": tx.get("amount"),
                        "currency": tx.get("currency"),
                        "gateway": tx.get("gateway"),
                        "created_at": tx.get("created_at"),
                    }
                )

        return payments

    def get_product_by_sku(self, sku: str):
        data = self.client.get("/products.json", {"limit": 250, "fields": "id,title,variants,vendor,product_type,status,created_at,updated_at"})
        products = data.get("products", [])
        normalized_sku = sku.strip().lower()

        result = []
        for product in products:
            for variant in product.get("variants", []):
                variant_sku = (variant.get("sku") or "").strip().lower()
                if variant_sku == normalized_sku:
                    result.append(
                        {
                            "product_id": product.get("id"),
                            "title": product.get("title"),
                            "vendor": product.get("vendor"),
                            "product_type": product.get("product_type"),
                            "status": product.get("status"),
                            "variant_id": variant.get("id"),
                            "sku": variant.get("sku"),
                            "price": variant.get("price"),
                            "inventory_quantity": variant.get("inventory_quantity"),
                        }
                    )

        return result

    def get_order_by_reference(self, reference: str):
        data = self.client.get("/orders.json", {"status": "any", "limit": 250})
        orders = data.get("orders", [])
        normalized_ref = reference.strip().lower()

        matched = []
        for order in orders:
            name = (order.get("name") or "").strip().lower()
            order_number = str(order.get("order_number") or "").strip().lower()
            if normalized_ref in {name, order_number}:
                matched.append(order)

        return matched
