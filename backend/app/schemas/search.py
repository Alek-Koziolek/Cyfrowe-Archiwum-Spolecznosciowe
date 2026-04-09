from pydantic import BaseModel

from app.schemas.photo import PhotoResponse


class SearchParams(BaseModel):
    q: str | None = None
    node_id: int | None = None
    date_from: str | None = None
    date_to: str | None = None
    tags: list[str] | None = None
    page: int = 1
    per_page: int = 20


class SearchResult(BaseModel):
    items: list[PhotoResponse]
    total: int
    page: int
    per_page: int


class SuggestResult(BaseModel):
    suggestions: list[str]
