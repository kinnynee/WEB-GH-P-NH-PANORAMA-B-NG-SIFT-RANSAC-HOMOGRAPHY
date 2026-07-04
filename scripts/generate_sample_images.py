from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "data" / "sample"


def generate_scene() -> np.ndarray:
    rng = np.random.default_rng(7)
    height, width = 720, 2140
    scene = np.full((height, width, 3), (248, 250, 252), dtype=np.uint8)

    for x in range(0, width, 80):
        cv2.line(scene, (x, 0), (x + 140, height), (226, 232, 240), 1)
    for y in range(80, height, 80):
        cv2.line(scene, (0, y), (width, y + 40), (226, 232, 240), 1)

    for _ in range(260):
        center = (int(rng.integers(30, width - 30)), int(rng.integers(30, height - 30)))
        radius = int(rng.integers(4, 18))
        color = tuple(int(v) for v in rng.integers(40, 220, size=3))
        cv2.circle(scene, center, radius, color, -1)

    for _ in range(70):
        p1 = (int(rng.integers(0, width)), int(rng.integers(0, height)))
        p2 = (int(np.clip(p1[0] + rng.integers(-180, 180), 0, width - 1)), int(np.clip(p1[1] + rng.integers(-120, 120), 0, height - 1)))
        color = tuple(int(v) for v in rng.integers(30, 190, size=3))
        cv2.line(scene, p1, p2, color, int(rng.integers(1, 4)))

    labels = ["SIFT", "RANSAC", "H", "Vision", "Panorama", "CV", "Overlap", "Warp", "Blend"]
    for i, label in enumerate(labels):
        x = 90 + i * 215
        y = 130 + (i % 3) * 170
        cv2.putText(scene, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (25, 40, 65), 3, cv2.LINE_AA)

    return scene


def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    scene = generate_scene()
    crops = [
        ("sample_01_left.png", 0, 760),
        ("sample_02_center.png", 460, 1220),
        ("sample_03_right.png", 920, 1680),
        ("sample_04_far_right.png", 1380, 2140),
    ]
    for name, x1, x2 in crops:
        crop = scene[:, x1:x2]
        cv2.imwrite(str(SAMPLE_DIR / name), cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(SAMPLE_DIR / "sample_full_reference.png"), cv2.cvtColor(scene, cv2.COLOR_RGB2BGR))


if __name__ == "__main__":
    main()
