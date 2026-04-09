import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HierarchyLevel(str, enum.Enum):
    WOJEWODZTWO = "województwo"
    MIASTO = "miasto"


class HierarchyNode(Base):
    __tablename__ = "hierarchy_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    level: Mapped[HierarchyLevel] = mapped_column(Enum(HierarchyLevel))
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("hierarchy_nodes.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    parent: Mapped["HierarchyNode | None"] = relationship(
        back_populates="children", remote_side=[id]
    )
    children: Mapped[list["HierarchyNode"]] = relationship(back_populates="parent")
    photos: Mapped[list["Photo"]] = relationship(back_populates="hierarchy_node")
