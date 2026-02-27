from app.odoo_client import OdooClient
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

    def bulk_create_products(self, products: list[ProductCreate]):
        created = []
        for product in products:
            created.append(self.create_product(product))

        return {"count": len(created), "items": created}
