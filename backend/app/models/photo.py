import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DatePrecision(str, enum.Enum):
    YEAR = "year"
    MONTH = "month"
    DAY = "day"


class PhotoTag(Base):
    __tablename__ = "photo_tags"

    photo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    photos: Mapped[list["Photo"]] = relationship(
        secondary="photo_tags", back_populates="tags"
    )


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    hierarchy_node_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("hierarchy_nodes.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str] = mapped_column(String(500))
    thumbnail_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mime_type: Mapped[str] = mapped_column(String(50))
    file_size: Mapped[int] = mapped_column(Integer)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)

    date_taken: Mapped[str | None] = mapped_column(String(10), nullable=True)
    date_precision: Mapped[DatePrecision | None] = mapped_column(
        Enum(DatePrecision), nullable=True
    )

    location_text: Mapped[str | None] = mapped_column(String(500), nullable=True)

    exif_data: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="photos")
    hierarchy_node: Mapped["HierarchyNode | None"] = relationship(
        back_populates="photos"
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary="photo_tags", back_populates="photos"
    )
