from __future__ import annotations

from pathlib import Path
from typing import Iterable

from core.preprocessing import SUPPORTED_EXTENSIONS
from models.result_models import UserFacingError


def validate_image_count(count: int) -> None:
    if count < 2:
        raise UserFacingError(
            "Not Enough Images",
            "At least 2 overlapping images are required to create a panorama.",
            ["Upload one or more additional images.", "Use images from the same scene with visible overlap."],
        )
    if count > 4:
        raise UserFacingError(
            "Too Many Images",
            "This version supports up to 4 images per panorama project.",
            ["Remove extra images and keep the best left-to-right sequence.", "Run multiple smaller projects if needed."],
        )


def validate_file_extension(filename: str) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UserFacingError(
            "Unsupported File Format",
            f"{filename} is not a supported image format.",
            ["Use JPG, JPEG, or PNG files.", "Export the image to a supported format and try again."],
        )


def validate_uploaded_filenames(filenames: Iterable[str]) -> None:
    names = list(filenames)
    validate_image_count(len(names))
    for name in names:
        validate_file_extension(name)
