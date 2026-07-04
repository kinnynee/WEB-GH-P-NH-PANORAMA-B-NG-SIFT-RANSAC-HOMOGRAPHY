from __future__ import annotations

import cv2
import numpy as np


def blend_images(
    base_canvas: np.ndarray,
    warped_next: np.ndarray,
    base_mask: np.ndarray,
    next_mask: np.ndarray,
    mode: str,
) -> np.ndarray:
    if mode == "Simple":
        blended = _simple_blend(base_canvas, warped_next, base_mask, next_mask)
    else:
        blended = _feather_blend(base_canvas, warped_next, base_mask, next_mask)
    valid_mask = cv2.bitwise_or(base_mask, next_mask)
    return crop_valid_region(blended, valid_mask)


def _simple_blend(base_canvas: np.ndarray, warped_next: np.ndarray, base_mask: np.ndarray, next_mask: np.ndarray) -> np.ndarray:
    result = np.zeros_like(base_canvas)
    base_only = (base_mask > 0) & (next_mask == 0)
    next_only = (next_mask > 0) & (base_mask == 0)
    overlap = (base_mask > 0) & (next_mask > 0)
    result[base_only] = base_canvas[base_only]
    result[next_only] = warped_next[next_only]
    result[overlap] = ((base_canvas[overlap].astype(np.float32) + warped_next[overlap].astype(np.float32)) / 2).astype(np.uint8)
    return result


def _feather_blend(base_canvas: np.ndarray, warped_next: np.ndarray, base_mask: np.ndarray, next_mask: np.ndarray) -> np.ndarray:
    base_binary = (base_mask > 0).astype(np.uint8)
    next_binary = (next_mask > 0).astype(np.uint8)
    base_dist = cv2.distanceTransform(base_binary, cv2.DIST_L2, 5)
    next_dist = cv2.distanceTransform(next_binary, cv2.DIST_L2, 5)

    base_weight = base_dist / (base_dist + next_dist + 1e-6)
    next_weight = next_dist / (base_dist + next_dist + 1e-6)
    valid = ((base_binary | next_binary) > 0).astype(np.float32)

    weighted = (
        base_canvas.astype(np.float32) * base_weight[..., None]
        + warped_next.astype(np.float32) * next_weight[..., None]
    )
    weighted *= valid[..., None]
    return np.clip(weighted, 0, 255).astype(np.uint8)


def crop_valid_region(image: np.ndarray, valid_mask: np.ndarray) -> np.ndarray:
    coords = cv2.findNonZero((valid_mask > 0).astype(np.uint8))
    if coords is None:
        return image
    x, y, w, h = cv2.boundingRect(coords)
    return image[y : y + h, x : x + w]
