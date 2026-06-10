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
    hash: Optional[str]

    class Config:
        from_attributes = True


class ImageLoadResponse(BaseModel):
    status: str
    image: ImageSchema


class SimilarImageSchema(BaseModel):
    image: ImageSchema
    similarity: float
    distance: float


class ImageCheckResponse(BaseModel):
    is_unique: bool
    max_similarity: float
    threshold: float
    created: bool
    best_match: Optional[SimilarImageSchema] = None
    image: Optional[ImageSchema] = None


class ImageSearchResponse(BaseModel):
    profile: str
    total: int
    matches: List[SimilarImageSchema]


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
