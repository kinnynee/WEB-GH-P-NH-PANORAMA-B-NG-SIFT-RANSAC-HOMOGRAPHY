from __future__ import annotations

import cv2
import numpy as np

from models.result_models import UserFacingError


def warp_to_shared_canvas(
    base: np.ndarray,
    next_image: np.ndarray,
    homography_next_to_base: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    h_base, w_base = base.shape[:2]
    h_next, w_next = next_image.shape[:2]

    base_corners = np.float32([[0, 0], [w_base, 0], [w_base, h_base], [0, h_base]]).reshape(-1, 1, 2)
    next_corners = np.float32([[0, 0], [w_next, 0], [w_next, h_next], [0, h_next]]).reshape(-1, 1, 2)
    warped_next_corners = cv2.perspectiveTransform(next_corners, homography_next_to_base)

    all_corners = np.concatenate((base_corners, warped_next_corners), axis=0)
    x_min, y_min = np.floor(all_corners.min(axis=0).ravel()).astype(int)
    x_max, y_max = np.ceil(all_corners.max(axis=0).ravel()).astype(int)

    translate_x = -x_min if x_min < 0 else 0
    translate_y = -y_min if y_min < 0 else 0
    width = int(x_max - x_min)
    height = int(y_max - y_min)

    if width <= 0 or height <= 0 or width > 12000 or height > 12000:
        raise UserFacingError(
            "Canvas Calculation Failed",
            "The estimated Homography creates an invalid or extremely large panorama canvas.",
            ["Check whether the images are in the correct order.", "Use images with less perspective difference."],
        )

    translation = np.array([[1, 0, translate_x], [0, 1, translate_y], [0, 0, 1]], dtype=np.float64)

    canvas_base = np.zeros((height, width, 3), dtype=np.uint8)
    canvas_base[translate_y : translate_y + h_base, translate_x : translate_x + w_base] = base
    base_mask = np.zeros((height, width), dtype=np.uint8)
    base_mask[translate_y : translate_y + h_base, translate_x : translate_x + w_base] = 255

    warped_next = cv2.warpPerspective(next_image, translation @ homography_next_to_base, (width, height))
    next_mask_source = np.ones((h_next, w_next), dtype=np.uint8) * 255
    next_mask = cv2.warpPerspective(next_mask_source, translation @ homography_next_to_base, (width, height))
    next_mask = (next_mask > 0).astype(np.uint8) * 255
    return canvas_base, warped_next, base_mask, next_mask
