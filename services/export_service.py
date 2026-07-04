from __future__ import annotations

import json
import zipfile
from dataclasses import asdict
from io import BytesIO

from models.result_models import PanoramaResult
from utils.image_utils import image_to_jpeg_bytes, image_to_png_bytes


def build_metadata(result: PanoramaResult) -> dict:
    return {
        "settings": asdict(result.settings),
        "image_count": len(result.input_images),
        "image_names": [image.name for image in result.input_images],
        "keypoint_counts": result.keypoint_counts,
        "raw_match_counts": result.raw_match_counts,
        "good_match_counts": result.good_match_counts,
        "inlier_counts": result.inlier_counts,
        "inlier_ratios": result.inlier_ratios,
        "processing_time": result.processing_time,
        "status": result.status,
        "final_resolution": {
            "width": int(result.final_panorama.shape[1]),
            "height": int(result.final_panorama.shape[0]),
        },
    }


def panorama_download_bytes(result: PanoramaResult) -> bytes:
    return image_to_jpeg_bytes(result.final_panorama)


def results_zip_bytes(result: PanoramaResult) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index, image in enumerate(result.input_images, start=1):
            archive.writestr(f"output/input/{index:02d}_{image.name}.png", image_to_png_bytes(image.image))

        for index, pair in enumerate(result.pair_results, start=1):
            archive.writestr(
                f"output/keypoints/pair_{index:02d}_base_keypoints.png",
                image_to_png_bytes(pair.base_features.visualization),
            )
            archive.writestr(
                f"output/keypoints/pair_{index:02d}_next_keypoints.png",
                image_to_png_bytes(pair.next_features.visualization),
            )
            archive.writestr(
                f"output/matches/raw_matches/pair_{index:02d}_raw_matches.png",
                image_to_png_bytes(pair.matches.raw_visualization),
            )
            archive.writestr(
                f"output/matches/ransac_inliers/pair_{index:02d}_ransac_inliers.png",
                image_to_png_bytes(pair.ransac_visualization),
            )
            archive.writestr(
                f"output/panorama/pair_{index:02d}_intermediate.png",
                image_to_png_bytes(pair.panorama),
            )

        archive.writestr("output/panorama/panorama_result.jpg", panorama_download_bytes(result))
        archive.writestr("output/metadata.json", json.dumps(build_metadata(result), indent=2))
    return buffer.getvalue()
