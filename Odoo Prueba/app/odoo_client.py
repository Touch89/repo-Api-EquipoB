import xmlrpc.client

from fastapi import HTTPException

from app.config import settings


class OdooClient:
    def __init__(self) -> None:
        self.url = settings.odoo_url
        self.db = settings.odoo_db
        self.username = settings.odoo_username
        self.password = settings.odoo_password

        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def authenticate(self) -> int:
        try:
            uid = self.common.authenticate(self.db, self.username, self.password, {})
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Error conectando con Odoo: {exc}") from exc

        if not uid:
            raise HTTPException(status_code=401, detail="No fue posible autenticar con Odoo")

        return uid

    def execute_kw(self, model: str, method: str, args: list, kwargs: dict | None = None):
        uid = self.authenticate()
        kwargs = kwargs or {}

        try:
            return self.models.execute_kw(
                self.db,
                uid,
                self.password,
                model,
                method,
                args,
                kwargs,
            )
        except Exception as exc:
            detail = str(exc)
            if "no existe" in detail.lower() and model in {"product.template", "product.product", "sale.order", "product.category"}:
                detail = (
                    f"Error Odoo en {model}.{method}: {exc}. "
                    "Parece que faltan módulos funcionales. Instala en Odoo las apps de Ventas e Inventario y vuelve a intentar."
                )
            elif "no puede acceder" in detail.lower() or "operation is allowed" in detail.lower():
                detail = (
                    f"Error Odoo en {model}.{method}: {exc}. "
                    "El usuario API no tiene permisos suficientes. Asígnale permisos de Ventas/Inventario o usa un usuario con acceso."
                )
            else:
                detail = f"Error Odoo en {model}.{method}: {exc}"

            raise HTTPException(status_code=502, detail=detail) from exc
