from unittest.mock import patch

from csorchestrator.context.context_os_architecture import ContextOsArchitecture, detect_arm64_variant

# =========================================================
# NVIDIA JETSON VARIANTS
# =========================================================


def test_detect_arm64_variant_orin():
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "pathlib.Path.read_text",
            return_value="NVIDIA Jetson Orin Nano",
        ),
    ):
        result = detect_arm64_variant()

    assert result == "orin"


def test_detect_arm64_variant_xavier():
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "pathlib.Path.read_text",
            return_value="NVIDIA Jetson Xavier NX",
        ),
    ):
        result = detect_arm64_variant()

    assert result == "xavier"


def test_detect_arm64_variant_nano():
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "pathlib.Path.read_text",
            return_value="NVIDIA Jetson Nano",
        ),
    ):
        result = detect_arm64_variant()

    assert result == "nano"


# =========================================================
# GENERIC
# =========================================================


def test_detect_arm64_variant_generic_when_file_missing():
    with patch("pathlib.Path.exists", return_value=False):
        result = detect_arm64_variant()

    assert result == ContextOsArchitecture.ARCHITECTURE_VARIANT_GENERIC


def test_detect_arm64_variant_generic_unknown_model():
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "pathlib.Path.read_text",
            return_value="Some Random ARM Board",
        ),
    ):
        result = detect_arm64_variant()

    assert result == ContextOsArchitecture.ARCHITECTURE_VARIANT_GENERIC


def test_detect_arm64_variant_generic_on_exception():
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.read_text", side_effect=Exception("boom")),
    ):
        result = detect_arm64_variant()

    assert result == ContextOsArchitecture.ARCHITECTURE_VARIANT_GENERIC
