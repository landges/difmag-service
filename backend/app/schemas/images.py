from typing import List, Optional
from pydantic import BaseModel


class ProfileSchema(BaseModel):
    id: Optional[int]
    name: str

    class Config:
        from_attributes = True

class ImageSchema(BaseModel):
    id: int
    file_path: str
    hash: str

    class Config:
        from_attributes = True


class ProfileImagesSchema(BaseModel):
    id: int
    name: str
    images: List[ImageSchema]

    class Config:
        from_attributes = True


class ProfilesSchema(BaseModel):
    profiles: List[ProfileSchema]
    
    class Config:
        from_attributes = True