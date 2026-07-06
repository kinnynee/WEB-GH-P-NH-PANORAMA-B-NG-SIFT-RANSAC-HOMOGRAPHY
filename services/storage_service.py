from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from models.result_models import PanoramaResult
from services.export_service import build_metadata, panorama_download_bytes
from utils.image_utils import image_to_png_bytes


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def save_uploaded_file(filename: str, data: bytes, root: Path = DATA_DIR) -> Path:
    upload_dir = root / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = _unique_path(upload_dir, f"{_timestamp()}_{_safe_filename(filename)}")
    path.write_bytes(data)
    return path


def save_run_artifacts(
    result: PanoramaResult,
    original_files: list[dict[str, Any]],
    root: Path = DATA_DIR,
) -> Path:
    run_dir = root / "results" / _timestamp()
    run_dir.mkdir(parents=True, exist_ok=False)

    _save_original_inputs(run_dir, original_files)
    _save_processed_inputs(run_dir, result)
    _save_pair_results(run_dir, result)
    _save_final_panorama(run_dir, result)
    _save_metadata(run_dir, result)

    return run_dir


def _save_original_inputs(run_dir: Path, original_files: list[dict[str, Any]]) -> None:
    input_dir = run_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(original_files, start=1):
        name = _safe_filename(str(item["name"]))
        path = _unique_path(input_dir, f"{index:02d}_{name}")
        path.write_bytes(item["data"])


def _save_processed_inputs(run_dir: Path, result: PanoramaResult) -> None:
    processed_dir = run_dir / "processed_input"
    processed_dir.mkdir(parents=True, exist_ok=True)
    for index, image in enumerate(result.input_images, start=1):
        path = processed_dir / f"{index:02d}_{_safe_stem(image.name)}.png"
        path.write_bytes(image_to_png_bytes(image.image))


def _save_pair_results(run_dir: Path, result: PanoramaResult) -> None:
    for index, pair in enumerate(result.pair_results, start=1):
        (run_dir / "keypoints").mkdir(parents=True, exist_ok=True)
        (run_dir / "matches" / "raw_matches").mkdir(parents=True, exist_ok=True)
        (run_dir / "matches" / "good_matches").mkdir(parents=True, exist_ok=True)
        (run_dir / "matches" / "ransac_inliers").mkdir(parents=True, exist_ok=True)
        (run_dir / "warped").mkdir(parents=True, exist_ok=True)
        (run_dir / "blended").mkdir(parents=True, exist_ok=True)
        (run_dir / "panorama").mkdir(parents=True, exist_ok=True)

        (run_dir / "keypoints" / f"pair_{index:02d}_base_keypoints.png").write_bytes(
            image_to_png_bytes(pair.base_features.visualization)
        )
        (run_dir / "keypoints" / f"pair_{index:02d}_next_keypoints.png").write_bytes(
            image_to_png_bytes(pair.next_features.visualization)
        )
        (run_dir / "matches" / "raw_matches" / f"pair_{index:02d}_raw_matches.png").write_bytes(
            image_to_png_bytes(pair.matches.raw_visualization)
        )
        (run_dir / "matches" / "good_matches" / f"pair_{index:02d}_good_matches.png").write_bytes(
            image_to_png_bytes(pair.matches.good_visualization)
        )
        (run_dir / "matches" / "ransac_inliers" / f"pair_{index:02d}_ransac_inliers.png").write_bytes(
            image_to_png_bytes(pair.ransac_visualization)
        )
        (run_dir / "warped" / f"pair_{index:02d}_warped.png").write_bytes(
            image_to_png_bytes(pair.warped_visualization)
        )
        (run_dir / "blended" / f"pair_{index:02d}_blended.png").write_bytes(
            image_to_png_bytes(pair.blended_visualization)
        )
        (run_dir / "panorama" / f"pair_{index:02d}_intermediate.png").write_bytes(
            image_to_png_bytes(pair.panorama)
        )


def _save_final_panorama(run_dir: Path, result: PanoramaResult) -> None:
    panorama_dir = run_dir / "panorama"
    panorama_dir.mkdir(parents=True, exist_ok=True)
    (panorama_dir / "panorama_result.jpg").write_bytes(panorama_download_bytes(result))


def _save_metadata(run_dir: Path, result: PanoramaResult) -> None:
    metadata = build_metadata(result)
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def _safe_filename(filename: str) -> str:
    name = Path(filename).name.strip()
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name.strip("._") or "image"


def _safe_stem(filename: str) -> str:
    return Path(_safe_filename(filename)).stem or "image"


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _unique_path(directory: Path, filename: str) -> Path:
    candidate = directory / filename
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    for index in range(1, 1000):
        numbered = directory / f"{stem}_{index:03d}{suffix}"
        if not numbered.exists():
            return numbered

    raise FileExistsError(f"Could not create a unique path for {candidate}")
