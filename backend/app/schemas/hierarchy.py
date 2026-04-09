from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HierarchyNodeCreate(BaseModel):
    name: str
    slug: str
    level: str
    parent_id: int | None = None


class HierarchyNodeResponse(BaseModel):
    id: int
    name: str
    slug: str
    level: str
    parent_id: int | None
    parent: Optional[HierarchyNodeResponse] = None
    created_at: datetime

    model_config = {"from_attributes": True}


HierarchyNodeResponse.model_rebuild()


class HierarchyNodeWithChildren(HierarchyNodeResponse):
    children: list[HierarchyNodeResponse] = []
