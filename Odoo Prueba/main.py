from fastapi import FastAPI

from app.api import router
from app.json_logger import JsonRequestLogger

app = FastAPI(title="Odoo API", version="1.0.0")
app.include_router(router)
json_logger = JsonRequestLogger()


@app.middleware("http")
async def generate_json_per_request(request, call_next):
	response = await call_next(request)
	return await json_logger.log(request, response)


@app.get("/health")
def health_check():
	return {"ok": True, "message": "API activa"}