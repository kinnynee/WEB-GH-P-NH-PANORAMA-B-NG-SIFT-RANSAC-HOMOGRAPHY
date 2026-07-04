from __future__ import annotations

from collections.abc import Sequence

import cv2

from core.preprocessing import read_image_bytes
from core.stitcher import stitch_sequence
from models.result_models import ImageInput, PanoramaResult, StitchSettings, UserFacingError
from utils.validation import validate_file_extension, validate_image_count


def build_image_inputs(files: Sequence[tuple[str, bytes]], settings: StitchSettings) -> list[ImageInput]:
    validate_image_count(len(files))
    images: list[ImageInput] = []
    for filename, data in files:
        validate_file_extension(filename)
        images.append(read_image_bytes(data, filename, settings))
    return images


def run_panorama_pipeline(images: list[ImageInput], settings: StitchSettings) -> PanoramaResult:
    try:
        return stitch_sequence(images, settings)
    except UserFacingError:
        raise
    except cv2.error as exc:
        raise UserFacingError(
            "Image Processing Failed",
            "OpenCV could not complete one of the panorama processing steps.",
            ["Try smaller images.", "Use images with stronger overlap.", "Check image order and rerun."],
        ) from exc
    except Exception as exc:
        raise UserFacingError(
            "Panorama Failed",
            "The panorama pipeline could not complete for this image set.",
            ["Try BFMatcher instead of FLANN.", "Use images with similar camera angles.", "Adjust Lowe Ratio or RANSAC threshold."],
        ) from exc
