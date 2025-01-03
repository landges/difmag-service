
from fastapi import Depends, UploadFile
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from app.services.images import ImageService, ProfileService
from app.core.session import create_session

router = APIRouter(prefix="/images", tags=['Image'])


@router.post("/load")
def load_image(
    file: UploadFile,
    profile: str,
    session: Session = Depends(create_session)
):
    ImageService(session).create_image(file)


@router.post("/check")
def check_image(
    file: UploadFile,
    profile: str,
    threshhold: float,
    uniq_create: bool,
    session: Session = Depends(create_session)
):
    return ImageService(session).check_image(file)

@router.post("/profiles")
def create_profile(
    name: str,
    session: Session = Depends(create_session)
):
    return ProfileService(session).get_profiles()