from typing import Optional

from fastapi import Depends, Query, UploadFile
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app.services.images import ImageService, ProfileService
from app.core.session import create_session
from app.schemas.images import ImageCheckResponse, ImageLoadResponse, ImageSearchResponse

router = APIRouter(prefix="/images", tags=["Image"])


@router.post("/load", response_model=ImageLoadResponse)
def load_image(
    file: UploadFile, profile: str, session: Session = Depends(create_session)
):
    image = ImageService(session).create_image(file=file, profile_name=profile)
    return {"status": "created", "image": image}


@router.post("/check", response_model=ImageCheckResponse)
def check_image(
    file: UploadFile,
    profile: str,
    threshhold: float,
    uniq_create: bool,
    session: Session = Depends(create_session),
):
    return ImageService(session).check_image(
        file=file, profile_name=profile, threshold=threshhold, create=uniq_create
    )


@router.post("/search", response_model=ImageSearchResponse)
def search_similar_images(
    file: UploadFile,
    profile: str,
    limit: int = Query(default=10, ge=1, le=100),
    threshold: Optional[float] = Query(default=None, ge=0, le=1),
    session: Session = Depends(create_session),
):
    return ImageService(session).search_similar_images(
        file=file,
        profile_name=profile,
        limit=limit,
        threshold=threshold,
    )


@router.delete("/profile/delete")
def delete_profile(
    name: str, 
    session: Session = Depends(create_session)
):
    return ProfileService(session).delete_profile(name)


@router.post("/profile/create")
def create_profile(
    name: str, 
    session: Session = Depends(create_session)
):
    return ProfileService(session).create_profile(name)


@router.get("/profile")
def get_profiles(
    name: str,
    session: Session = Depends(create_session)
):
    return ProfileService(session).get_profile(name)
