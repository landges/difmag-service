from functools import lru_cache
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

from app.core.config import config

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def _resize_short_side(image: Image.Image, size: int = 256) -> Image.Image:
    width, height = image.size
    if width <= height:
        new_width = size
        new_height = round(height * size / width)
    else:
        new_height = size
        new_width = round(width * size / height)

    return image.resize((new_width, new_height), Image.Resampling.BILINEAR)


def _center_crop(image: Image.Image, size: int = 224) -> Image.Image:
    width, height = image.size
    left = (width - size) // 2
    top = (height - size) // 2
    return image.crop((left, top, left + size, top + size))


def _preprocess(image: Image.Image) -> np.ndarray:
    image = _resize_short_side(image.convert("RGB"))
    image = _center_crop(image)

    array = np.asarray(image, dtype=np.float32) / 255.0
    array = (array - IMAGENET_MEAN) / IMAGENET_STD
    array = np.transpose(array, (2, 0, 1))
    return np.expand_dims(array, axis=0).astype(np.float32)


@lru_cache(maxsize=1)
def _get_session() -> ort.InferenceSession:
    model_path = Path(config.model_path)
    if not model_path.exists():
        raise FileNotFoundError(
            f"ONNX model was not found at {model_path}. "
            "Run scripts/export_resnet50_onnx.py or mount MYAPI_MODEL_PATH."
        )

    return ort.InferenceSession(
        str(model_path),
        providers=["CPUExecutionProvider"],
    )


def extract_embedding(image: Image.Image) -> list[float]:
    session = _get_session()
    input_name = session.get_inputs()[0].name
    output = session.run(None, {input_name: _preprocess(image)})[0]
    return output.reshape(-1).astype(np.float32).tolist()
