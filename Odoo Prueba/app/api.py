from fastapi import APIRouter

from app.schemas import ApiResponse, ProductBulkCreate, ProductCreate
from app.services import OdooService

router = APIRouter(prefix="/api", tags=["odoo"])
service = OdooService()


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
