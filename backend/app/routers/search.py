from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.photo import Photo, Tag
from app.models.hierarchy import HierarchyNode
from app.schemas.photo import PhotoResponse
from app.schemas.search import SearchResult, SuggestResult

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/", response_model=SearchResult)
async def search_photos(
    q: str | None = None,
    node_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    tags: list[str] | None = Query(None),
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Photo)
        .options(
            selectinload(Photo.owner),
            selectinload(Photo.hierarchy_node).selectinload(HierarchyNode.parent),
            selectinload(Photo.tags),
        )
    )
    count_query = select(func.count(Photo.id))

    if q:
        like_pattern = f"%{q}%"
        text_filter = (
            Photo.title.ilike(like_pattern)
            | Photo.description.ilike(like_pattern)
            | Photo.location_text.ilike(like_pattern)
        )
        query = query.where(text_filter)
        count_query = count_query.where(text_filter)

    if node_id:
        descendants_cte = (
            select(HierarchyNode.id)
            .where(HierarchyNode.id == node_id)
            .cte(name="descendants", recursive=True)
        )
        descendants_cte = descendants_cte.union_all(
            select(HierarchyNode.id).where(
                HierarchyNode.parent_id == descendants_cte.c.id
            )
        )
        node_ids = select(descendants_cte.c.id)
        query = query.where(Photo.hierarchy_node_id.in_(node_ids))
        count_query = count_query.where(Photo.hierarchy_node_id.in_(node_ids))

    if date_from:
        query = query.where(Photo.date_taken >= date_from)
        count_query = count_query.where(Photo.date_taken >= date_from)

    if date_to:
        query = query.where(Photo.date_taken <= date_to)
        count_query = count_query.where(Photo.date_taken <= date_to)

    if tags:
        for tag_name in tags:
            query = query.where(Photo.tags.any(Tag.name == tag_name))
            count_query = count_query.where(Photo.tags.any(Tag.name == tag_name))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * per_page
    result = await db.execute(query.order_by(Photo.created_at.desc()).offset(offset).limit(per_page))
    photos = result.scalars().all()

    items = []
    for p in photos:
        items.append(
            PhotoResponse(
                id=p.id,
                title=p.title,
                description=p.description,
                owner=p.owner,
                hierarchy_node=p.hierarchy_node,
                mime_type=p.mime_type,
                file_size=p.file_size,
                width=p.width,
                height=p.height,
                date_taken=p.date_taken,
                date_precision=p.date_precision,
                location_text=p.location_text,
                tags=[t.name for t in p.tags],
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
        )

    return SearchResult(items=items, total=total, page=page, per_page=per_page)


@router.get("/suggest", response_model=SuggestResult)
async def suggest(
    q: str = "",
    tags_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    if len(q) < 2:
        return SuggestResult(suggestions=[])

    like_pattern = f"%{q}%"
    suggestions = set()

    result = await db.execute(
        select(Tag.name).where(Tag.name.ilike(like_pattern)).limit(5)
    )
    for row in result.scalars():
        suggestions.add(row)

    if not tags_only:
        result = await db.execute(
            select(HierarchyNode.name).where(HierarchyNode.name.ilike(like_pattern)).limit(5)
        )
        for row in result.scalars():
            suggestions.add(row)

    return SuggestResult(suggestions=sorted(suggestions)[:10])
