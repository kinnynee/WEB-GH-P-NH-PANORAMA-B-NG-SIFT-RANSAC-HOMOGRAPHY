from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class UserFacingError(Exception):
    title: str
    explanation: str
    suggestions: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.title}: {self.explanation}"


@dataclass
class StitchSettings:
    matcher: str = "BFMatcher"
    lowe_ratio: float = 0.75
    ransac_threshold: float = 5.0
    blend_mode: str = "Feather"
    max_image_size: int = 1600
    sift_nfeatures: int = 2000
    min_good_matches: int = 10


@dataclass
class ImageInput:
    name: str
    image: np.ndarray
    original_size: tuple[int, int]
    size: tuple[int, int]
    scale: float = 1.0


@dataclass
class FeatureResult:
    image_name: str
    original: np.ndarray
    gray: np.ndarray
    keypoints: list[Any]
    descriptors: np.ndarray | None
    visualization: np.ndarray

    @property
    def keypoint_count(self) -> int:
        return len(self.keypoints)


@dataclass
class MatchResult:
    raw_matches: list[Any]
    good_matches: list[Any]
    raw_visualization: np.ndarray
    good_visualization: np.ndarray

    @property
    def raw_count(self) -> int:
        return len(self.raw_matches)

    @property
    def good_count(self) -> int:
        return len(self.good_matches)

    @property
    def retention_rate(self) -> float:
        if not self.raw_count:
            return 0.0
        return self.good_count / self.raw_count


@dataclass
class HomographyResult:
    matrix: np.ndarray | None
    mask: np.ndarray | None
    inlier_count: int
    outlier_count: int
    inlier_ratio: float
    status: str


@dataclass
class PairStitchResult:
    pair_index: int
    base_name: str
    next_name: str
    base_features: FeatureResult
    next_features: FeatureResult
    matches: MatchResult
    homography: HomographyResult
    ransac_visualization: np.ndarray
    warped_visualization: np.ndarray
    blended_visualization: np.ndarray
    panorama: np.ndarray
    processing_time: float


@dataclass
class PanoramaResult:
    input_images: list[ImageInput]
    pair_results: list[PairStitchResult]
    final_panorama: np.ndarray
    settings: StitchSettings
    processing_time: float
    status: str = "success"

    @property
    def keypoint_counts(self) -> list[int]:
        if not self.pair_results:
            return []
        counts = [self.pair_results[0].base_features.keypoint_count]
        counts.extend(pair.next_features.keypoint_count for pair in self.pair_results)
        return counts

    @property
    def raw_match_counts(self) -> list[int]:
        return [pair.matches.raw_count for pair in self.pair_results]

    @property
    def good_match_counts(self) -> list[int]:
        return [pair.matches.good_count for pair in self.pair_results]

    @property
    def inlier_counts(self) -> list[int]:
        return [pair.homography.inlier_count for pair in self.pair_results]

    @property
    def inlier_ratios(self) -> list[float]:
        return [pair.homography.inlier_ratio for pair in self.pair_results]
