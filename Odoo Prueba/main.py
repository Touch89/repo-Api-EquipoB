from fastapi import FastAPI

from app.config import settings
from app.api import router
from app.json_logger import JsonRequestLogger

app = FastAPI(title="Odoo API", version="1.0.0")
app.include_router(router)
json_logger = JsonRequestLogger()
shopify_json_logger = JsonRequestLogger(output_dir=settings.json_shopify_output_dir)


@app.middleware("http")
async def generate_json_per_request(request, call_next):
	response = await call_next(request)
	if request.url.path.startswith("/api/shopify"):
		return await shopify_json_logger.log(request, response)
	return await json_logger.log(request, response)


@app.get("/health")
def health_check():
	return {"ok": True, "message": "API activa"}