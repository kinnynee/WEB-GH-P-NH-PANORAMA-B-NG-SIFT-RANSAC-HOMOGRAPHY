from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_sample_images import main as generate_sample_images


@pytest.fixture(scope="session")
def sample_paths() -> list[Path]:
    generate_sample_images()
    root = Path(__file__).resolve().parents[1] / "data" / "sample"
    return [
        root / "sample_01_left.png",
        root / "sample_02_center.png",
        root / "sample_03_right.png",
        root / "sample_04_far_right.png",
    ]
