from fastapi import Depends, UploadFile
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app.services.images import ImageService, ProfileService
from app.core.session import create_session

router = APIRouter(prefix="/images", tags=["Image"])


@router.post("/load")
def load_image(
    file: UploadFile, profile: str, session: Session = Depends(create_session)
):
    ImageService(session).create_image(file)


@router.post("/check")
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