# schemas/common.py
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Generic, TypeVar

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T

class Meta(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    page: int
    limit: int
    total: int
    total_pages: int
    has_next_page: bool
    has_previous_page: bool