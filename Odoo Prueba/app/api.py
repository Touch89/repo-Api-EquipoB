from fastapi import APIRouter

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


@router.post("/products", response_model=ApiResponse)
def create_product(payload: ProductCreate):
    return {"ok": True, "data": service.create_product(payload)}


@router.post("/products/bulk", response_model=ApiResponse)
def bulk_create_products(payload: ProductBulkCreate):
    return {"ok": True, "data": service.bulk_create_products(payload.products)}


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
