from __future__ import annotations

from io import BytesIO

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

from models.result_models import ImageInput, StitchSettings, UserFacingError


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def read_image_bytes(data: bytes, name: str, settings: StitchSettings) -> ImageInput:
    try:
        pil_image = Image.open(BytesIO(data)).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise UserFacingError(
            "Cannot Read Image",
            f"{name} is not a readable image file.",
            ["Use a valid JPG, JPEG, or PNG file.", "Try opening the image locally and saving it again."],
        ) from exc

    original_size = pil_image.size
    image = np.array(pil_image)
    resized, scale = resize_if_needed(image, settings.max_image_size)
    height, width = resized.shape[:2]
    return ImageInput(name=name, image=resized, original_size=original_size, size=(width, height), scale=scale)


def resize_if_needed(image: np.ndarray, max_size: int) -> tuple[np.ndarray, float]:
    height, width = image.shape[:2]
    longest = max(width, height)
    if longest <= max_size:
        return image, 1.0
    scale = max_size / float(longest)
    new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    resized = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return resized, scale


def to_gray(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
