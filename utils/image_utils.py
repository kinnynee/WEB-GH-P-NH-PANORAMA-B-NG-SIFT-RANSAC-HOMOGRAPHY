from __future__ import annotations

from io import BytesIO

import cv2
import numpy as np
from PIL import Image


def image_to_png_bytes(image: np.ndarray) -> bytes:
    pil = Image.fromarray(_ensure_rgb(image))
    buffer = BytesIO()
    pil.save(buffer, format="PNG")
    return buffer.getvalue()


def image_to_jpeg_bytes(image: np.ndarray, quality: int = 95) -> bytes:
    pil = Image.fromarray(_ensure_rgb(image))
    buffer = BytesIO()
    pil.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()


def save_image(path: str, image: np.ndarray) -> None:
    rgb = _ensure_rgb(image)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    cv2.imwrite(path, bgr)


def _ensure_rgb(image: np.ndarray) -> np.ndarray:
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    return image
