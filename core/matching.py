from __future__ import annotations

import cv2
import numpy as np

from models.result_models import FeatureResult, MatchResult, StitchSettings, UserFacingError


def match_features(left: FeatureResult, right: FeatureResult, settings: StitchSettings) -> MatchResult:
    if left.descriptors is None or right.descriptors is None:
        raise UserFacingError(
            "Descriptor Data Missing",
            "One or more images do not have SIFT descriptors for matching.",
            ["Use images with more texture.", "Check that both images are readable and not blank."],
        )

    knn_matches = _knn_match(left.descriptors, right.descriptors, settings.matcher)
    raw_pairs = [pair for pair in knn_matches if len(pair) >= 2]
    if not raw_pairs:
        raise UserFacingError(
            "No Feature Matches",
            "The selected images did not produce descriptor matches.",
            ["Use images from the same scene.", "Increase overlap to around 35-50%.", "Check image order."],
        )

    good_matches = apply_lowe_ratio_test(raw_pairs, settings.lowe_ratio)
    if len(good_matches) < settings.min_good_matches:
        raise UserFacingError(
            "Not Enough Matching Features",
            "The images may not contain enough overlapping visual information after Lowe Ratio filtering.",
            ["Use images with 35-50% overlap.", "Check left-to-right image order.", "Avoid large blank areas."],
        )

    raw_visualization = draw_matches(left, right, [pair[0] for pair in raw_pairs[:120]])
    good_visualization = draw_matches(left, right, good_matches[:120])
    return MatchResult(
        raw_matches=raw_pairs,
        good_matches=good_matches,
        raw_visualization=raw_visualization,
        good_visualization=good_visualization,
    )


def _knn_match(desc1: np.ndarray, desc2: np.ndarray, matcher: str) -> list[list[cv2.DMatch]]:
    if matcher == "FLANN":
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=64)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        return flann.knnMatch(desc1.astype(np.float32), desc2.astype(np.float32), k=2)
    bf = cv2.BFMatcher(cv2.NORM_L2)
    return bf.knnMatch(desc1, desc2, k=2)


def apply_lowe_ratio_test(knn_matches: list[list[cv2.DMatch]], ratio: float) -> list[cv2.DMatch]:
    good_matches: list[cv2.DMatch] = []
    for pair in knn_matches:
        if len(pair) < 2:
            continue
        first, second = pair[0], pair[1]
        if first.distance < ratio * second.distance:
            good_matches.append(first)
    return good_matches


def draw_matches(left: FeatureResult, right: FeatureResult, matches: list[cv2.DMatch]) -> np.ndarray:
    return cv2.drawMatches(
        left.original,
        left.keypoints,
        right.original,
        right.keypoints,
        matches,
        None,
        matchColor=(0, 88, 190),
        singlePointColor=(114, 119, 133),
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )
