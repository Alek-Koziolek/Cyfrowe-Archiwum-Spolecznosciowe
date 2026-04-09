import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_active_contributor
from app.models.hierarchy import HierarchyNode
from app.models.photo import Photo, Tag
from app.models.user import User
from app.schemas.photo import PhotoListResponse, PhotoResponse, PhotoUpdate
from app.utils.image import (
    create_thumbnail,
    extract_exif,
    generate_filename,
    get_image_dimensions,
    get_upload_path,
)

router = APIRouter(prefix="/api/photos", tags=["photos"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/tiff"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def _photo_to_response(photo: Photo) -> dict:
    data = {
        "id": photo.id,
        "title": photo.title,
        "description": photo.description,
        "owner": photo.owner,
        "hierarchy_node": photo.hierarchy_node,
        "mime_type": photo.mime_type,
        "file_size": photo.file_size,
        "width": photo.width,
        "height": photo.height,
        "date_taken": photo.date_taken,
        "date_precision": photo.date_precision,
        "location_text": photo.location_text,
        "tags": [t.name for t in photo.tags],
        "created_at": photo.created_at,
        "updated_at": photo.updated_at,
    }
    return data


@router.get("/", response_model=PhotoListResponse)
async def list_photos(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page
    count_result = await db.execute(select(func.count(Photo.id)))
    total = count_result.scalar()

    result = await db.execute(
        select(Photo)
        .options(selectinload(Photo.owner), selectinload(Photo.hierarchy_node).selectinload(HierarchyNode.parent), selectinload(Photo.tags))
        .order_by(Photo.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    photos = result.scalars().all()

    return PhotoListResponse(
        items=[PhotoResponse(**_photo_to_response(p)) for p in photos],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/mine", response_model=PhotoListResponse)
async def list_my_photos(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_contributor),
):
    offset = (page - 1) * per_page
    count_result = await db.execute(
        select(func.count(Photo.id)).where(Photo.owner_id == user.id)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(Photo)
        .options(selectinload(Photo.owner), selectinload(Photo.hierarchy_node).selectinload(HierarchyNode.parent), selectinload(Photo.tags))
        .where(Photo.owner_id == user.id)
        .order_by(Photo.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    photos = result.scalars().all()

    return PhotoListResponse(
        items=[PhotoResponse(**_photo_to_response(p)) for p in photos],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Photo)
        .options(selectinload(Photo.owner), selectinload(Photo.hierarchy_node).selectinload(HierarchyNode.parent), selectinload(Photo.tags))
        .where(Photo.id == photo_id)
    )
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return PhotoResponse(**_photo_to_response(photo))


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    hierarchy_node_id: int | None = Form(None),
    date_taken: str | None = Form(None),
    date_precision: str | None = Form(None),
    location_text: str | None = Form(None),
    tags: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_contributor),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 20MB)")

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "jpg"
    filename = generate_filename(ext)
    file_path = get_upload_path(filename)
    file_path.write_bytes(content)

    width, height = get_image_dimensions(file_path)
    exif_data = extract_exif(file_path)

    thumbnail_path = create_thumbnail(file_path, 300)
    create_thumbnail(file_path, 600)

    tag_objects = []
    if tags:
        tag_names = [t.strip() for t in tags.split(",") if t.strip()]
        for tag_name in tag_names:
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            tag_objects.append(tag)

    photo = Photo(
        owner_id=user.id,
        hierarchy_node_id=hierarchy_node_id,
        title=title,
        description=description,
        file_path=str(file_path),
        thumbnail_path=str(thumbnail_path),
        mime_type=file.content_type,
        file_size=len(content),
        width=width,
        height=height,
        date_taken=date_taken,
        date_precision=date_precision,
        location_text=location_text,
        exif_data=json.dumps(exif_data) if exif_data else None,
        tags=tag_objects,
    )
    db.add(photo)
    await db.commit()
    result = await db.execute(
        select(Photo)
        .options(selectinload(Photo.owner), selectinload(Photo.hierarchy_node).selectinload(HierarchyNode.parent), selectinload(Photo.tags))
        .where(Photo.id == photo.id)
    )
    photo = result.scalar_one()

    return PhotoResponse(**_photo_to_response(photo))


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: int,
    data: PhotoUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_contributor),
):
    result = await db.execute(
        select(Photo)
        .options(selectinload(Photo.owner), selectinload(Photo.hierarchy_node).selectinload(HierarchyNode.parent), selectinload(Photo.tags))
        .where(Photo.id == photo_id)
    )
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    if photo.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner")

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
        .where(Photo.id == photo.id)
    )
    photo = result.scalar_one()
    return PhotoResponse(**_photo_to_response(photo))


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_contributor),
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    if photo.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner")

    file_path = Path(photo.file_path)
    if file_path.exists():
        file_path.unlink()
    if photo.thumbnail_path:
        thumb = Path(photo.thumbnail_path)
        if thumb.exists():
            thumb.unlink()

    await db.delete(photo)
    await db.commit()


@router.get("/{photo_id}/thumbnail")
async def get_thumbnail(photo_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo or not photo.thumbnail_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found")
    return FileResponse(photo.thumbnail_path, media_type="image/webp")


@router.get("/{photo_id}/full")
async def get_full_image(photo_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return FileResponse(photo.file_path, media_type=photo.mime_type)
