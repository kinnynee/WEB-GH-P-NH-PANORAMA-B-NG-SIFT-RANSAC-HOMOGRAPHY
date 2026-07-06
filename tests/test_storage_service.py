from __future__ import annotations

import json
from pathlib import Path

from models.result_models import StitchSettings
from services.processing_service import build_image_inputs, run_panorama_pipeline
from services.storage_service import save_run_artifacts, save_uploaded_file


def test_save_uploaded_file_writes_to_data_uploads(tmp_path: Path) -> None:
    saved_path = save_uploaded_file("../bad name.png", b"image-bytes", root=tmp_path)

    assert saved_path.parent == tmp_path / "uploads"
    assert saved_path.name.endswith("_bad_name.png")
    assert saved_path.read_bytes() == b"image-bytes"


def test_save_run_artifacts_writes_inputs_results_and_metadata(sample_paths: list[Path], tmp_path: Path) -> None:
    settings = StitchSettings(max_image_size=1000)
    original_files = [
        {"name": path.name, "data": path.read_bytes()}
        for path in sample_paths[:2]
    ]
    images = build_image_inputs([(item["name"], item["data"]) for item in original_files], settings)
    result = run_panorama_pipeline(images, settings)

    run_dir = save_run_artifacts(result, original_files, root=tmp_path)

    assert run_dir.parent == tmp_path / "results"
    assert (run_dir / "input" / f"01_{sample_paths[0].name}").exists()
    assert (run_dir / "processed_input" / "01_sample_01_left.png").exists()
    assert (run_dir / "keypoints" / "pair_01_base_keypoints.png").exists()
    assert (run_dir / "matches" / "good_matches" / "pair_01_good_matches.png").exists()
    assert (run_dir / "panorama" / "panorama_result.jpg").exists()

    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["image_count"] == 2
    assert metadata["status"] == "success"
