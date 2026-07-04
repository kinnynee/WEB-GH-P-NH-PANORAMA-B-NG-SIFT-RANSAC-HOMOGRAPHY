from __future__ import annotations

import cv2
import numpy as np


def make_placeholder_illustration(kind: str, width: int = 900, height: int = 420) -> np.ndarray:
    image = np.full((height, width, 3), 249, dtype=np.uint8)
    blue = (0, 88, 190)
    slate = (66, 71, 84)
    light = (194, 198, 214)

    if kind == "sift":
        for i in range(7):
            x = 90 + i * 115
            cv2.circle(image, (x, 210 + (i % 3 - 1) * 40), 8 + (i % 4) * 3, blue, 2)
        cv2.putText(image, "SIFT keypoints", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, slate, 2)
    elif kind == "matching":
        cv2.rectangle(image, (70, 110), (360, 320), light, 2)
        cv2.rectangle(image, (540, 110), (830, 320), light, 2)
        for i in range(12):
            p1 = (100 + (i * 43) % 230, 140 + (i * 29) % 150)
            p2 = (570 + (i * 47) % 230, 140 + (i * 31) % 150)
            cv2.line(image, p1, p2, blue, 1)
            cv2.circle(image, p1, 3, blue, -1)
            cv2.circle(image, p2, 3, blue, -1)
        cv2.putText(image, "Feature correspondences", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, slate, 2)
    elif kind == "ransac":
        rng = np.random.default_rng(42)
        points = rng.normal(size=(120, 2))
        points[:, 0] = points[:, 0] * 130 + 430
        points[:, 1] = points[:, 0] * 0.35 + rng.normal(0, 28, 120) + 40
        for x, y in points.astype(int):
            cv2.circle(image, (x, y), 3, blue if abs(y - (x * 0.35 + 40)) < 42 else light, -1)
        cv2.line(image, (160, 96), (800, 320), blue, 3)
        cv2.putText(image, "RANSAC inliers and outliers", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, slate, 2)
    elif kind == "homography":
        src = np.array([[90, 120], [330, 70], [360, 270], [70, 330]], np.int32)
        dst = np.array([[560, 120], [820, 120], [820, 320], [560, 320]], np.int32)
        cv2.polylines(image, [src], True, blue, 2)
        cv2.polylines(image, [dst], True, blue, 2)
        for a, b in zip(src, dst):
            cv2.line(image, tuple(a), tuple(b), light, 1)
        cv2.putText(image, "Projective transform", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, slate, 2)
    else:
        cv2.putText(image, kind.title(), (40, 210), cv2.FONT_HERSHEY_SIMPLEX, 1.0, slate, 2)
    return image
