from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import require_admin
from app.models.hierarchy import HierarchyNode
from app.models.photo import Photo, Tag
from app.models.user import User
from app.schemas.photo import PhotoResponse, PhotoUpdate
from app.schemas.user import UserResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.put("/users/{user_id}/block", response_model=UserResponse)
async def toggle_block_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_blocked = not user.is_blocked
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    file_path = Path(photo.file_path)
    if file_path.exists():
        file_path.unlink()
    if photo.thumbnail_path:
        thumb = Path(photo.thumbnail_path)
        if thumb.exists():
            thumb.unlink()

    await db.delete(photo)
    await db.commit()


@router.put("/photos/{photo_id}", response_model=PhotoResponse)
async def admin_update_photo(
    photo_id: int,
    data: PhotoUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(
        select(Photo)
        .options(selectinload(Photo.owner), selectinload(Photo.hierarchy_node).selectinload(HierarchyNode.parent), selectinload(Photo.tags))
        .where(Photo.id == photo_id)
    )
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    update_data = data.model_dump(exclude_unset=True)
    tags_data = update_data.pop("tags", None)

    for field, value in update_data.items():
        setattr(photo, field, value)

    if tags_data is not None:
        tag_objects = []
        for tag_name in tags_data:
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            tag_objects.append(tag)
        photo.tags = tag_objects

    await db.commit()
    result = await db.execute(
        select(Photo)
        .options(selectinload(Photo.owner), selectinload(Photo.hierarchy_node).selectinload(HierarchyNode.parent), selectinload(Photo.tags))
        .where(Photo.id == photo_id)
    )
    photo = result.scalar_one()

    return PhotoResponse(
        id=photo.id,
        title=photo.title,
        description=photo.description,
        owner=photo.owner,
        hierarchy_node=photo.hierarchy_node,
        mime_type=photo.mime_type,
        file_size=photo.file_size,
        width=photo.width,
        height=photo.height,
        date_taken=photo.date_taken,
        date_precision=photo.date_precision,
        location_text=photo.location_text,
        tags=[t.name for t in photo.tags],
        created_at=photo.created_at,
        updated_at=photo.updated_at,
    )


@router.delete("/hierarchy/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_hierarchy_node(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    node = await db.get(HierarchyNode, node_id)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    to_delete: list[int] = []
    queue = [node_id]
    while queue:
        current = queue.pop()
        to_delete.append(current)
        result = await db.execute(
            select(HierarchyNode.id).where(HierarchyNode.parent_id == current)
        )
        queue.extend(result.scalars().all())

    await db.execute(
        update(Photo)
        .where(Photo.hierarchy_node_id.in_(to_delete))
        .values(hierarchy_node_id=None)
    )

    for nid in reversed(to_delete):
        n = await db.get(HierarchyNode, nid)
        if n:
            await db.delete(n)

    await db.commit()


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user_count = (await db.execute(select(func.count(User.id)))).scalar()
    photo_count = (await db.execute(select(func.count(Photo.id)))).scalar()
    blocked_count = (
        await db.execute(select(func.count(User.id)).where(User.is_blocked == True))
    ).scalar()

    return {
        "total_users": user_count,
        "total_photos": photo_count,
        "blocked_users": blocked_count,
    }
