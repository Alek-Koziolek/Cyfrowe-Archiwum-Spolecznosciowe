from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_active_contributor
from app.models.hierarchy import HierarchyNode
from app.models.user import User
from app.schemas.hierarchy import (
    HierarchyNodeCreate,
    HierarchyNodeResponse,
    HierarchyNodeWithChildren,
)

router = APIRouter(prefix="/api/hierarchy", tags=["hierarchy"])


@router.get("/", response_model=list[HierarchyNodeResponse])
async def get_root_nodes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(HierarchyNode)
        .where(HierarchyNode.parent_id.is_(None))
        .order_by(HierarchyNode.name)
    )
    return result.scalars().all()


@router.get("/{node_id}", response_model=HierarchyNodeWithChildren)
async def get_node(node_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(HierarchyNode)
        .options(
            selectinload(HierarchyNode.parent),
            selectinload(HierarchyNode.children).selectinload(HierarchyNode.parent),
        )
        .where(HierarchyNode.id == node_id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return node


@router.get("/{node_id}/children", response_model=list[HierarchyNodeResponse])
async def search_children(
    node_id: int,
    q: str = "",
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(HierarchyNode)
        .options(selectinload(HierarchyNode.parent))
        .where(HierarchyNode.parent_id == node_id)
    )
    if q:
        stmt = stmt.where(HierarchyNode.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(HierarchyNode.name).limit(20)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=HierarchyNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    data: HierarchyNodeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_contributor),
):
    if data.parent_id:
        parent = await db.get(HierarchyNode, data.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Parent node not found"
            )

    node = HierarchyNode(
        name=data.name,
        slug=data.slug,
        level=data.level,
        parent_id=data.parent_id,
    )
    db.add(node)
    await db.commit()

    result = await db.execute(
        select(HierarchyNode)
        .options(selectinload(HierarchyNode.parent))
        .where(HierarchyNode.id == node.id)
    )
    return result.scalar_one()
