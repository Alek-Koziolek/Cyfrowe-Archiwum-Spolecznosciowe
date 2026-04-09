from datetime import datetime

from pydantic import BaseModel

from app.schemas.hierarchy import HierarchyNodeResponse
from app.schemas.user import UserResponse


class PhotoCreate(BaseModel):
    title: str
    description: str | None = None
    hierarchy_node_id: int | None = None
    date_taken: str | None = None
    date_precision: str | None = None
    location_text: str | None = None
    tags: list[str] = []


class PhotoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    hierarchy_node_id: int | None = None
    date_taken: str | None = None
    date_precision: str | None = None
    location_text: str | None = None
    tags: list[str] | None = None


class PhotoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    owner: UserResponse
    hierarchy_node: HierarchyNodeResponse | None
    mime_type: str
    file_size: int
    width: int | None
    height: int | None
    date_taken: str | None
    date_precision: str | None
    location_text: str | None
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PhotoListResponse(BaseModel):
    items: list[PhotoResponse]
    total: int
    page: int
    per_page: int
