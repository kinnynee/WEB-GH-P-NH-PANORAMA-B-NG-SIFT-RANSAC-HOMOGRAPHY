from __future__ import annotations

import cv2
import numpy as np

from core.preprocessing import to_gray
from models.result_models import FeatureResult, StitchSettings, UserFacingError


def detect_sift_features(image: np.ndarray, image_name: str, settings: StitchSettings) -> FeatureResult:
    gray = to_gray(image)
    sift = cv2.SIFT_create(nfeatures=settings.sift_nfeatures)
    keypoints, descriptors = sift.detectAndCompute(gray, None)

    if not keypoints:
        raise UserFacingError(
            "Not Enough Visual Features",
            f"{image_name} does not contain enough detectable SIFT keypoints.",
            ["Use images with more texture, corners, or edges.", "Avoid blank walls, sky-only frames, and heavy blur."],
        )
    if descriptors is None or len(descriptors) == 0:
        raise UserFacingError(
            "Empty SIFT Descriptors",
            f"{image_name} produced keypoints but no usable descriptors.",
            ["Use a sharper image with more local detail.", "Try reducing motion blur or compression artifacts."],
        )

    visualization = cv2.drawKeypoints(
        image,
        keypoints,
        None,
        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        color=(0, 88, 190),
    )
    return FeatureResult(
        image_name=image_name,
        original=image,
        gray=gray,
        keypoints=keypoints,
        descriptors=descriptors,
        visualization=visualization,
    )
