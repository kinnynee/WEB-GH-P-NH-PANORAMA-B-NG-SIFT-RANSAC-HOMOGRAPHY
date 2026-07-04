from __future__ import annotations

import pytest

from models.result_models import UserFacingError
from utils.validation import validate_file_extension, validate_image_count


def test_validate_image_count_accepts_two_to_four() -> None:
    validate_image_count(2)
    validate_image_count(4)


@pytest.mark.parametrize("count", [0, 1, 5])
def test_validate_image_count_rejects_invalid_counts(count: int) -> None:
    with pytest.raises(UserFacingError):
        validate_image_count(count)


def test_validate_format_accepts_supported_images() -> None:
    validate_file_extension("frame.JPG")
    validate_file_extension("frame.jpeg")
    validate_file_extension("frame.png")


def test_validate_format_rejects_pdf() -> None:
    with pytest.raises(UserFacingError):
        validate_file_extension("notes.pdf")
