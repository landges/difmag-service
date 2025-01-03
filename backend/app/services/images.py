import io
from typing import List, Union
import warnings
from fastapi import UploadFile
from sqlalchemy import select
from app.services.base import BaseDataManager, BaseService
from PIL import Image
from pathlib import Path
import numpy as np
import imagehash
import torchvision.transforms as T
from app.core.embeder import feature_extractor
import torch
from app.models.images import ImageRecord, Profile

transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225])
])

def extract_embedding(image: Image.Image) -> torch.Tensor:
    img_t = transform(image).unsqueeze(0)
    with torch.no_grad():
        emb = feature_extractor(img_t)  # shape [1, 2048, 1, 1]
    emb = emb.squeeze()  # [2048]
    # Для косинусной близости можно нормализовать, но тут оставим "как есть".
    return emb

class ImageService(BaseService):
    def create_image(self, file: UploadFile):
        # fpath = Path(file.filename)
        # fpath.write_bytes(file.file.read())
        image = Image.open(file.file).convert("RGB")
        img_hash = str(imagehash.phash(image))
        
        emb = extract_embedding(image)
        
        # Превратим PyTorch-тензор в список (чтобы вставить в pgvector)
        emb_list = emb.tolist()  # длина 2048
        print(emb_list)
        # Сохраняем запись в базу данных
        new_image = ImageRecord(file_path=file.filename, hash=img_hash, mbedding=emb_list, profile_id=1)
        ImageDataManager(self.session).add_one(new_image)

    def check_image(self, file: UploadFile):
        image = Image.open(file.file).convert("RGB")
        
        emb = extract_embedding(image)
        emb_list = emb.tolist()
        return ImageDataManager(self.session).get_vector_distance(emb_list)


class ImageDataManager(BaseDataManager):
    def get_vector_distance(self, vector: List[float]):
        distances = self.session.scalars(select(ImageRecord.mbedding.cosine_distance(vector))).fetchall()
        return list(map(lambda x: 1 - x, distances))

class ProfileService(BaseService):
    def create_profile(self, name):
        profile = Profile(name=name)
        ProfileDataManager(self.session).add_one(profile)

    def get_profiles(self):
        return ProfileDataManager(self.session).get_all_profiles()
    
    def delete_profile(self, name:str):
        profile = ProfileDataManager(self.session).get_profile(name)
        ProfileDataManager(self.session).delete_one(profile)

class ProfileDataManager(BaseDataManager):
    def get_profile(self, name: str):
        return self.get_one(select(Profile).where(Profile.name==name))

    def get_all_profiles(self):
        return self.get_all(select(Profile))