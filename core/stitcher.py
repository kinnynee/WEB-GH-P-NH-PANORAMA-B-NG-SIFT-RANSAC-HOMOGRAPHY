from __future__ import annotations

import time

import cv2
import numpy as np

from core.blending import blend_images
from core.features import detect_sift_features
from core.homography import estimate_homography
from core.matching import draw_matches, match_features
from core.warping import warp_to_shared_canvas
from models.result_models import ImageInput, PairStitchResult, PanoramaResult, StitchSettings, UserFacingError


def stitch_pair(
    base_image: np.ndarray,
    next_image: np.ndarray,
    base_name: str,
    next_name: str,
    settings: StitchSettings,
    pair_index: int = 1,
) -> PairStitchResult:
    started = time.perf_counter()
    base_features = detect_sift_features(base_image, base_name, settings)
    next_features = detect_sift_features(next_image, next_name, settings)
    matches = match_features(base_features, next_features, settings)
    homography = estimate_homography(base_features, next_features, matches.good_matches, settings)

    inlier_matches = [
        match for match, keep in zip(matches.good_matches, homography.mask.ravel().tolist()) if keep
    ]
    ransac_visualization = draw_matches(base_features, next_features, inlier_matches[:120])

    base_canvas, warped_next, base_mask, next_mask = warp_to_shared_canvas(
        base_image,
        next_image,
        homography.matrix,
    )
    warped_visualization = _compose_warp_preview(base_canvas, warped_next, base_mask, next_mask)
    panorama = blend_images(base_canvas, warped_next, base_mask, next_mask, settings.blend_mode)
    elapsed = time.perf_counter() - started

    return PairStitchResult(
        pair_index=pair_index,
        base_name=base_name,
        next_name=next_name,
        base_features=base_features,
        next_features=next_features,
        matches=matches,
        homography=homography,
        ransac_visualization=ransac_visualization,
        warped_visualization=warped_visualization,
        blended_visualization=panorama,
        panorama=panorama,
        processing_time=elapsed,
    )


def stitch_sequence(images: list[ImageInput], settings: StitchSettings) -> PanoramaResult:
    if not 2 <= len(images) <= 4:
        raise UserFacingError(
            "Invalid Image Count",
            "Panorama Vision Studio processes from 2 to 4 images per project.",
            ["Upload at least 2 images.", "Keep at most 4 images for this version."],
        )

    started = time.perf_counter()
    current = images[0].image
    current_name = images[0].name
    pair_results: list[PairStitchResult] = []

    for index, image_input in enumerate(images[1:], start=1):
        pair = stitch_pair(current, image_input.image, current_name, image_input.name, settings, pair_index=index)
        pair_results.append(pair)
        current = pair.panorama
        current_name = f"panorama_after_pair_{index}.png"

    elapsed = time.perf_counter() - started
    if current is None or current.size == 0:
        raise UserFacingError(
            "Panorama Failed",
            "The pipeline finished without producing a valid panorama image.",
            ["Try different images with stronger overlap.", "Try BFMatcher and Feather blending."],
        )
    return PanoramaResult(
        input_images=images,
        pair_results=pair_results,
        final_panorama=current,
        settings=settings,
        processing_time=elapsed,
    )


def _compose_warp_preview(base_canvas: np.ndarray, warped_next: np.ndarray, base_mask: np.ndarray, next_mask: np.ndarray) -> np.ndarray:
    preview = np.zeros_like(base_canvas)
    preview[base_mask > 0] = base_canvas[base_mask > 0]
    preview[next_mask > 0] = warped_next[next_mask > 0]
    overlap = (base_mask > 0) & (next_mask > 0)
    preview[overlap] = cv2.addWeighted(base_canvas[overlap], 0.5, warped_next[overlap], 0.5, 0)
    return preview
