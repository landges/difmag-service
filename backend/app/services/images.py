from typing import List, Optional

import imagehash
from fastapi import UploadFile
from PIL import Image
from sqlalchemy import select

from app.core.embeder import extract_embedding
from app.models.images import ImageRecord, Profile
from app.schemas.images import (
    ImageCheckResponse,
    ImageSearchResponse,
    ImageSchema,
    ProfileImagesSchema,
    ProfileSchema,
    SimilarImageSchema,
)
from app.services.base import BaseDataManager, BaseService


class ImageService(BaseService):
    def create_image(
        self,
        file: UploadFile,
        profile_name: str,
        embed: Optional[List[float]] = None,
    ):
        profile: ProfileSchema = ProfileService(self.session).get_profile(profile_name)
        image = Image.open(file.file).convert("RGB")
        img_hash = str(imagehash.phash(image))
        emb_list = embed or extract_embedding(image)

        new_image = ImageRecord(
            file_path=file.filename,
            hash=img_hash,
            mbedding=emb_list,
            profile_id=profile.id,
        )
        ImageDataManager(self.session).add_one(new_image)
        return ImageSchema.model_validate(new_image)

    def check_image(
        self,
        file: UploadFile,
        profile_name: str,
        threshold: float,
        create: bool,
    ):
        profile: ProfileSchema = ProfileService(self.session).get_profile(profile_name)
        image = Image.open(file.file).convert("RGB")
        emb_list = extract_embedding(image)
        best_match = ImageDataManager(self.session).get_similar_images(
            vector=emb_list,
            profile_id=profile.id,
            limit=1,
        )
        best_match = best_match[0] if best_match else None
        max_similarity = best_match.similarity if best_match else 0.0

        if max_similarity >= threshold:
            return ImageCheckResponse(
                is_unique=False,
                max_similarity=max_similarity,
                threshold=threshold,
                created=False,
                best_match=best_match,
            )

        created_image = None
        if create:
            file.file.seek(0)
            created_image = self.create_image(file, profile_name, emb_list)

        return ImageCheckResponse(
            is_unique=True,
            max_similarity=max_similarity,
            threshold=threshold,
            created=created_image is not None,
            best_match=best_match,
            image=created_image,
        )

    def search_similar_images(
        self,
        file: UploadFile,
        profile_name: str,
        limit: int = 10,
        threshold: Optional[float] = None,
    ):
        profile: ProfileSchema = ProfileService(self.session).get_profile(profile_name)
        image = Image.open(file.file).convert("RGB")
        emb_list = extract_embedding(image)
        matches = ImageDataManager(self.session).get_similar_images(
            vector=emb_list,
            profile_id=profile.id,
            limit=limit,
            threshold=threshold,
        )

        return ImageSearchResponse(
            profile=profile.name,
            total=len(matches),
            matches=matches,
        )


class ImageDataManager(BaseDataManager):
    def get_max_similarity(self, vector: List[float], profile_id: int) -> float:
        distance = ImageRecord.mbedding.cosine_distance(vector)
        similarity = 1 - distance

        max_similarity = self.session.scalar(
            select(similarity)
            .where(ImageRecord.profile_id == profile_id)
            .order_by(distance.asc())
            .limit(1)
        )
        return float(max_similarity or 0)

    def get_similar_images(
        self,
        vector: List[float],
        profile_id: int,
        limit: int,
        threshold: Optional[float] = None,
    ) -> List[SimilarImageSchema]:
        distance = ImageRecord.mbedding.cosine_distance(vector)
        similarity = 1 - distance

        stmt = (
            select(ImageRecord, similarity.label("similarity"), distance.label("distance"))
            .where(ImageRecord.profile_id == profile_id)
            .order_by(distance.asc())
            .limit(limit)
        )

        if threshold is not None:
            stmt = stmt.where(similarity >= threshold)

        rows = self.session.execute(stmt).all()
        return [
            SimilarImageSchema(
                image=ImageSchema.model_validate(image),
                similarity=float(row_similarity),
                distance=float(row_distance),
            )
            for image, row_similarity, row_distance in rows
        ]


class ProfileService(BaseService):
    def get_profile(self, name: str):
        profile = ProfileDataManager(self.session).get_profile(name)
        return ProfileImagesSchema.model_validate(profile)

    def create_profile(self, name):
        profile = Profile(name=name)
        ProfileDataManager(self.session).add_one(profile)
        return ProfileSchema.model_validate(profile)

    def get_profiles(self):
        return ProfileDataManager(self.session).get_all_profiles()

    def delete_profile(self, name: str):
        profile = ProfileDataManager(self.session).get_profile(name)
        ProfileDataManager(self.session).delete_one(profile)


class ProfileDataManager(BaseDataManager):
    def get_profile(self, name: str):
        return self.get_one(select(Profile).where(Profile.name == name))

    def get_all_profiles(self):
        return self.get_all(select(Profile))
