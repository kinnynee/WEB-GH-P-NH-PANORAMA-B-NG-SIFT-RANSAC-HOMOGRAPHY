from __future__ import annotations

import cv2
import numpy as np

from models.result_models import FeatureResult, HomographyResult, StitchSettings, UserFacingError


def estimate_homography(
    base: FeatureResult,
    next_image: FeatureResult,
    matches: list[cv2.DMatch],
    settings: StitchSettings,
) -> HomographyResult:
    if len(matches) < 4:
        raise UserFacingError(
            "Homography Needs More Matches",
            "At least four corresponding points are required to estimate a Homography.",
            ["Use images with more overlap.", "Try increasing the Lowe Ratio slightly.", "Check image order."],
        )

    src_pts = np.float32([next_image.keypoints[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([base.keypoints[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, settings.ransac_threshold)

    if matrix is None or mask is None:
        raise UserFacingError(
            "Homography Failed",
            "RANSAC could not estimate a stable geometric transform for these images.",
            ["Use images from the same viewpoint.", "Increase visual overlap.", "Avoid strong parallax or moving objects."],
        )

    inlier_count = int(mask.ravel().sum())
    outlier_count = int(len(matches) - inlier_count)
    inlier_ratio = inlier_count / max(1, len(matches))
    if inlier_count < 4:
        raise UserFacingError(
            "RANSAC Rejected Most Matches",
            "Too few matches agree with one geometric transformation.",
            ["Check image order.", "Use images with more common scene content.", "Try a higher RANSAC threshold."],
        )

    return HomographyResult(
        matrix=matrix,
        mask=mask,
        inlier_count=inlier_count,
        outlier_count=outlier_count,
        inlier_ratio=inlier_ratio,
        status="success",
    )
