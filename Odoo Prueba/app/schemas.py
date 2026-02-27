from typing import Any

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    list_price: float = 0.0
    standard_price: float = 0.0
    default_code: str | None = None
    categ_id: int | None = None
    type: str = "consu"


class ProductBulkCreate(BaseModel):
    products: list[ProductCreate] = Field(default_factory=list)


class ApiResponse(BaseModel):
    ok: bool
    data: Any
