from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import cv2
import numpy as np
import pytest

from core.blending import blend_images
from core.features import detect_sift_features
from core.homography import estimate_homography
from core.matching import apply_lowe_ratio_test, match_features
from core.warping import warp_to_shared_canvas
from models.result_models import StitchSettings, UserFacingError
from services.export_service import results_zip_bytes
from services.processing_service import build_image_inputs, run_panorama_pipeline


def _read_rgb(path: Path) -> np.ndarray:
    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    assert bgr is not None
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def _image_inputs(sample_paths: list[Path], count: int = 2):
    settings = StitchSettings(max_image_size=1000)
    files = [(path.name, path.read_bytes()) for path in sample_paths[:count]]
    return build_image_inputs(files, settings)


def test_sift_returns_keypoints(sample_paths: list[Path]) -> None:
    image = _read_rgb(sample_paths[0])
    result = detect_sift_features(image, sample_paths[0].name, StitchSettings())
    assert result.keypoint_count > 50
    assert result.descriptors is not None
    assert result.descriptors.shape[1] == 128


def test_matching_and_lowe_ratio(sample_paths: list[Path]) -> None:
    settings = StitchSettings()
    left = detect_sift_features(_read_rgb(sample_paths[0]), "left", settings)
    right = detect_sift_features(_read_rgb(sample_paths[1]), "right", settings)
    result = match_features(left, right, settings)
    assert result.raw_count > result.good_count > 20
    filtered = apply_lowe_ratio_test(result.raw_matches, 0.75)
    assert len(filtered) == result.good_count


def test_homography_with_valid_matches(sample_paths: list[Path]) -> None:
    settings = StitchSettings()
    left = detect_sift_features(_read_rgb(sample_paths[0]), "left", settings)
    right = detect_sift_features(_read_rgb(sample_paths[1]), "right", settings)
    matches = match_features(left, right, settings)
    homography = estimate_homography(left, right, matches.good_matches, settings)
    assert homography.matrix.shape == (3, 3)
    assert homography.inlier_count >= 4
    assert homography.inlier_ratio > 0.5


def test_homography_failure_is_user_facing(sample_paths: list[Path]) -> None:
    settings = StitchSettings()
    left = detect_sift_features(_read_rgb(sample_paths[0]), "left", settings)
    right = detect_sift_features(_read_rgb(sample_paths[1]), "right", settings)
    with pytest.raises(UserFacingError):
        estimate_homography(left, right, [], settings)


def test_warping_and_blending_do_not_crash(sample_paths: list[Path]) -> None:
    settings = StitchSettings()
    left = detect_sift_features(_read_rgb(sample_paths[0]), "left", settings)
    right = detect_sift_features(_read_rgb(sample_paths[1]), "right", settings)
    matches = match_features(left, right, settings)
    homography = estimate_homography(left, right, matches.good_matches, settings)
    base_canvas, warped_next, base_mask, next_mask = warp_to_shared_canvas(left.original, right.original, homography.matrix)
    panorama = blend_images(base_canvas, warped_next, base_mask, next_mask, "Feather")
    assert panorama.ndim == 3
    assert panorama.shape[0] > 0
    assert panorama.shape[1] > left.original.shape[1]


def test_pipeline_two_images_end_to_end(sample_paths: list[Path]) -> None:
    images = _image_inputs(sample_paths, 2)
    result = run_panorama_pipeline(images, StitchSettings(max_image_size=1000))
    assert result.final_panorama.shape[1] > images[0].image.shape[1]
    assert result.raw_match_counts[0] > result.good_match_counts[0] > 20
    assert result.inlier_counts[0] >= 4


def test_pipeline_three_images_end_to_end(sample_paths: list[Path]) -> None:
    images = _image_inputs(sample_paths, 3)
    result = run_panorama_pipeline(images, StitchSettings(max_image_size=1000))
    assert len(result.pair_results) == 2
    assert result.final_panorama.shape[1] > images[1].image.shape[1]


def test_pipeline_four_images_end_to_end(sample_paths: list[Path]) -> None:
    images = _image_inputs(sample_paths, 4)
    result = run_panorama_pipeline(images, StitchSettings(max_image_size=1000))
    assert len(result.pair_results) == 3
    assert result.final_panorama.shape[1] > images[2].image.shape[1]


def test_export_zip_contains_expected_files(sample_paths: list[Path]) -> None:
    images = _image_inputs(sample_paths, 2)
    result = run_panorama_pipeline(images, StitchSettings(max_image_size=1000))
    zip_bytes = results_zip_bytes(result)
    zip_path = Path("test_export.zip")
    zip_path.write_bytes(zip_bytes)
    try:
        with ZipFile(zip_path) as archive:
            names = set(archive.namelist())
        assert "output/metadata.json" in names
        assert "output/panorama/panorama_result.jpg" in names
        assert any(name.startswith("output/keypoints/") for name in names)
        assert any(name.startswith("output/matches/raw_matches/") for name in names)
    finally:
        zip_path.unlink(missing_ok=True)
