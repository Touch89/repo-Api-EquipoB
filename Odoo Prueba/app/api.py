from fastapi import APIRouter, HTTPException

from app.schemas import ApiResponse, ProductBulkCreate, ProductCreate
from app.services import OdooService, PrestashopService

router = APIRouter(prefix="/api", tags=["odoo"])
service = OdooService()
prestashop_service = PrestashopService()


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


@router.get("/sync/products", response_model=ApiResponse)
def sync_products_to_prestashop(limit: int = 200):
    source_products = service.get_products_for_prestashop_sync(limit=limit)
    existing_skus = prestashop_service.get_existing_skus()

    created = []
    skipped_duplicates = []
    skipped_zero_price_and_stock = []
    skipped_without_reference = []
    errors = []

    for product in source_products:
        reference = (product.get("default_code") or "").strip()
        price = float(product.get("list_price") or 0.0)
        stock = float(product.get("qty_available") or 0.0)

        if not reference:
            skipped_without_reference.append({
                "id": product.get("id"),
                "name": product.get("display_name"),
            })
            continue

        if price == 0.0 and stock == 0.0:
            skipped_zero_price_and_stock.append({
                "id": product.get("id"),
                "reference": reference,
                "price": price,
                "stock": stock,
            })
            continue

        normalized_reference = reference.lower()
        if normalized_reference in existing_skus:
            skipped_duplicates.append({
                "id": product.get("id"),
                "reference": reference,
            })
            continue

        try:
            created_product = prestashop_service.create_product_from_odoo(product)
            created.append(
                {
                    "odoo_id": product.get("id"),
                    "reference": reference,
                    "prestashop": created_product,
                }
            )
            existing_skus.add(normalized_reference)
        except HTTPException as exc:
            errors.append(
                {
                    "odoo_id": product.get("id"),
                    "reference": reference,
                    "detail": exc.detail,
                }
            )

    return {
        "ok": True,
        "data": {
            "total_odoo_products": len(source_products),
            "created_count": len(created),
            "skipped_duplicates_count": len(skipped_duplicates),
            "skipped_zero_price_and_stock_count": len(skipped_zero_price_and_stock),
            "skipped_without_reference_count": len(skipped_without_reference),
            "errors_count": len(errors),
            "created": created,
            "skipped_duplicates": skipped_duplicates,
            "skipped_zero_price_and_stock": skipped_zero_price_and_stock,
            "skipped_without_reference": skipped_without_reference,
            "errors": errors,
        },
    }


@router.get("/sync/products/by-reference/{reference}", response_model=ApiResponse)
def sync_product_to_prestashop_by_reference(reference: str):
    product = service.get_product_for_prestashop_sync_by_reference(reference=reference)
    if not product:
        raise HTTPException(status_code=404, detail=f"No existe producto en Odoo con referencia: {reference}")

    product_reference = (product.get("default_code") or "").strip()
    price = float(product.get("list_price") or 0.0)
    stock = float(product.get("qty_available") or 0.0)

    if price == 0.0 and stock == 0.0:
        return {
            "ok": True,
            "data": {
                "status": "skipped_zero_price_and_stock",
                "reference": product_reference,
                "odoo_id": product.get("id"),
            },
        }

    existing_skus = prestashop_service.get_existing_skus()
    if product_reference.lower() in existing_skus:
        return {
            "ok": True,
            "data": {
                "status": "skipped_duplicate",
                "reference": product_reference,
                "odoo_id": product.get("id"),
            },
        }

    created = prestashop_service.create_product_from_odoo(product)
    return {
        "ok": True,
        "data": {
            "status": "created",
            "reference": product_reference,
            "odoo_id": product.get("id"),
            "prestashop": created,
        },
    }


@router.get("/sync/products/update/by-reference/{reference}", response_model=ApiResponse)
def update_product_in_prestashop_by_reference(reference: str):
    product = service.get_product_for_prestashop_sync_by_reference(reference=reference)
    if not product:
        raise HTTPException(status_code=404, detail=f"No existe producto en Odoo con referencia: {reference}")

    found = prestashop_service.find_product_by_reference(reference=reference)
    if not found:
        raise HTTPException(status_code=404, detail=f"No existe producto en PrestaShop con referencia: {reference}")

    updated = prestashop_service.update_product_from_odoo_by_reference(reference=reference, odoo_product=product)
    if not updated:
        raise HTTPException(status_code=404, detail=f"No fue posible actualizar en PrestaShop la referencia: {reference}")

    return {
        "ok": True,
        "data": {
            "status": "updated",
            "reference": reference,
            "odoo_id": product.get("id"),
            "prestashop": updated,
        },
    }


@router.get("/sync/products/deactivate/by-reference/{reference}", response_model=ApiResponse)
def deactivate_product_in_prestashop_by_reference(reference: str):
    found = prestashop_service.find_product_by_reference(reference=reference)
    if not found:
        raise HTTPException(status_code=404, detail=f"No existe producto en PrestaShop con referencia: {reference}")

    deactivated = prestashop_service.deactivate_product_by_reference(reference=reference)
    if not deactivated:
        raise HTTPException(status_code=404, detail=f"No fue posible desactivar en PrestaShop la referencia: {reference}")

    return {
        "ok": True,
        "data": {
            "status": "deactivated",
            "reference": reference,
            "prestashop": deactivated,
        },
    }


@router.post("/products", response_model=ApiResponse)
def create_product(payload: ProductCreate):
    odoo_product = service.create_product(payload)
    try:
        prestashop_product = prestashop_service.create_product(payload)
    except HTTPException as exc:
        try:
            service.delete_product(odoo_product["id"])
        except Exception:
            pass
        raise HTTPException(
            status_code=502,
            detail=f"Fallo creando en PrestaShop. Se revirtió producto en Odoo. Detalle: {exc.detail}",
        ) from exc

    return {"ok": True, "data": {"odoo": odoo_product, "prestashop": prestashop_product}}


@router.post("/products/bulk", response_model=ApiResponse)
def bulk_create_products(payload: ProductBulkCreate):
    created_pairs = []

    for product in payload.products:
        odoo_product = service.create_product(product)
        try:
            prestashop_product = prestashop_service.create_product(product)
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
                    "Fallo creación masiva en PrestaShop; se revirtieron los productos creados en Odoo en esta petición. "
                    f"Detalle: {exc.detail}"
                ),
            ) from exc

        created_pairs.append({"odoo": odoo_product, "prestashop": prestashop_product})

    return {"ok": True, "data": {"count": len(created_pairs), "items": created_pairs}}


@router.get("/prestashop/products", response_model=ApiResponse, tags=["prestashop"])
def get_prestashop_products(limit: int = 50):
    return {"ok": True, "data": prestashop_service.get_products(limit=limit)}


@router.get("/prestashop/orders", response_model=ApiResponse, tags=["prestashop"])
def get_prestashop_orders(limit: int = 50):
    return {"ok": True, "data": prestashop_service.get_orders(limit=limit)}


@router.get("/prestashop/customers", response_model=ApiResponse, tags=["prestashop"])
def get_prestashop_customers(limit: int = 50):
    return {"ok": True, "data": prestashop_service.get_customers(limit=limit)}


@router.get("/prestashop/suppliers", response_model=ApiResponse, tags=["prestashop"])
def get_prestashop_suppliers(limit: int = 250):
    return {"ok": True, "data": prestashop_service.get_suppliers(limit=limit)}


@router.get("/prestashop/payments", response_model=ApiResponse, tags=["prestashop"])
def get_prestashop_payments(order_limit: int = 20):
    return {"ok": True, "data": prestashop_service.get_payments(order_limit=order_limit)}


@router.get("/prestashop/products/by-sku/{sku}", response_model=ApiResponse, tags=["prestashop"])
def get_prestashop_product_by_sku(sku: str):
    return {"ok": True, "data": prestashop_service.get_product_by_sku(sku=sku)}


@router.get("/prestashop/orders/by-reference/{reference}", response_model=ApiResponse, tags=["prestashop"])
def get_prestashop_order_by_reference(reference: str):
    return {"ok": True, "data": prestashop_service.get_order_by_reference(reference=reference)}
