from fastapi import APIRouter, HTTPException

from app.schemas import ApiResponse, ProductBulkCreate, ProductCreate
from app.services import OdooService, ShopifyService

router = APIRouter(prefix="/api", tags=["odoo"])
service = OdooService()
shopify_service = ShopifyService()


@router.get("/orders", response_model=ApiResponse)
def get_orders():
    return {"ok": True, "data": service.get_orders()}


@router.get("/products", response_model=ApiResponse)
def get_products():
    return {"ok": True, "data": service.get_products()}


@router.get("/products/stock", response_model=ApiResponse)
def get_products_stock():
    return {"ok": True, "data": service.get_product_stock()}


@router.get("/products/categories", response_model=ApiResponse)
def get_product_categories():
    return {"ok": True, "data": service.get_product_categories()}


@router.get("/customers", response_model=ApiResponse)
def get_customers():
    return {"ok": True, "data": service.get_customers()}


@router.get("/suppliers", response_model=ApiResponse)
def get_suppliers():
    return {"ok": True, "data": service.get_suppliers()}


@router.get("/payments", response_model=ApiResponse)
def get_payments():
    return {"ok": True, "data": service.get_payments()}


@router.get("/products/by-sku/{sku}", response_model=ApiResponse)
def get_product_by_sku(sku: str):
    return {"ok": True, "data": service.get_product_by_sku(sku=sku)}


@router.get("/orders/by-reference/{reference}", response_model=ApiResponse)
def get_order_by_reference(reference: str):
    return {"ok": True, "data": service.get_order_by_reference(reference=reference)}


@router.post("/products", response_model=ApiResponse)
def create_product(payload: ProductCreate):
    odoo_product = service.create_product(payload)
    try:
        shopify_product = shopify_service.create_product(payload)
    except HTTPException as exc:
        try:
            service.delete_product(odoo_product["id"])
        except Exception:
            pass
        raise HTTPException(
            status_code=502,
            detail=f"Fallo creando en Shopify. Se revirtió producto en Odoo. Detalle: {exc.detail}",
        ) from exc

    return {"ok": True, "data": {"odoo": odoo_product, "shopify": shopify_product}}


@router.post("/products/bulk", response_model=ApiResponse)
def bulk_create_products(payload: ProductBulkCreate):
    created_pairs = []

    for product in payload.products:
        odoo_product = service.create_product(product)
        try:
            shopify_product = shopify_service.create_product(product)
        except HTTPException as exc:
            rollback_ids = [item["odoo"]["id"] for item in created_pairs] + [odoo_product["id"]]
            for product_id in rollback_ids:
                try:
                    service.delete_product(product_id)
                except Exception:
                    pass
            raise HTTPException(
                status_code=502,
                detail=(
                    "Fallo creación masiva en Shopify; se revirtieron los productos creados en Odoo en esta petición. "
                    f"Detalle: {exc.detail}"
                ),
            ) from exc

        created_pairs.append({"odoo": odoo_product, "shopify": shopify_product})

    return {"ok": True, "data": {"count": len(created_pairs), "items": created_pairs}}


@router.get("/shopify/products", response_model=ApiResponse, tags=["shopify"])
def get_shopify_products(limit: int = 50):
    return {"ok": True, "data": shopify_service.get_products(limit=limit)}


@router.get("/shopify/orders", response_model=ApiResponse, tags=["shopify"])
def get_shopify_orders(limit: int = 50):
    return {"ok": True, "data": shopify_service.get_orders(limit=limit)}


@router.get("/shopify/customers", response_model=ApiResponse, tags=["shopify"])
def get_shopify_customers(limit: int = 50):
    return {"ok": True, "data": shopify_service.get_customers(limit=limit)}


@router.get("/shopify/suppliers", response_model=ApiResponse, tags=["shopify"])
def get_shopify_suppliers(limit: int = 250):
    return {"ok": True, "data": shopify_service.get_suppliers(limit=limit)}


@router.get("/shopify/payments", response_model=ApiResponse, tags=["shopify"])
def get_shopify_payments(order_limit: int = 20):
    return {"ok": True, "data": shopify_service.get_payments(order_limit=order_limit)}


@router.get("/shopify/products/by-sku/{sku}", response_model=ApiResponse, tags=["shopify"])
def get_shopify_product_by_sku(sku: str):
    return {"ok": True, "data": shopify_service.get_product_by_sku(sku=sku)}


@router.get("/shopify/orders/by-reference/{reference}", response_model=ApiResponse, tags=["shopify"])
def get_shopify_order_by_reference(reference: str):
    return {"ok": True, "data": shopify_service.get_order_by_reference(reference=reference)}
