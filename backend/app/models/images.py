from app.models.base import SQLModel
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

class Profile(SQLModel):
    id: Mapped[int] = mapped_column("id", primary_key=True)
    name: str

class ImageRecord(SQLModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(foreign_key="profile.id")
    image_hash: Mapped[str]