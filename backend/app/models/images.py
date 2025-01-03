from sqlalchemy import Index, ForeignKey
from app.models.base import SQLModel
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from pgvector.sqlalchemy import Vector

class Profile(SQLModel):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column("id", primary_key=True)
    name: Mapped[str] = mapped_column("name")


class ImageRecord(SQLModel):
    __tablename__ = "images"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column("id", primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("public.profiles.id", name="img2profile"))
    file_path: Mapped[str] = mapped_column("file_path") 
    hash: Mapped[str] = mapped_column("hash", nullable=True)
    mbedding:Mapped[Vector] = mapped_column(Vector(2048))

    # __table_args__ = (
    #     Index("idx_images_hash", "hash", postgresql_using="smlarhash"),
    # )
