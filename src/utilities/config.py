"""
Global project configuration.

Central place for paths, constants, and default parameters.
Import with:  from src.utilities.config import get_config
"""

from pathlib import Path
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    """Immutable project configuration."""

    PROJECT_NAME: str = "TrueHue"

    # Directory roots (relative to project root)
    DATA_ROOT: str = "data"
    MODELS_ROOT: str = "models"
    OUTPUTS_ROOT: str = "outputs"

    # Dataset sub-directories
    DATA_RAW: str = "data/raw"
    DATA_PROCESSED: str = "data/processed"
    DATA_TRAIN: str = "data/train"
    DATA_VAL: str = "data/validation"
    DATA_TEST: str = "data/test"

    # Face detector (YuNet ONNX model)
    FACE_MODEL_PATH: str = "models/face_detector/face_detection_yunet_2023mar.onnx"
    FACE_MODEL_URL: str = (
        "https://github.com/opencv/opencv_zoo/raw/main/"
        "models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
    )
    FACE_CONFIDENCE: float = 0.9

    # Face Landmarker (MediaPipe task model, used for anatomical feature
    # exclusion in the skin-mask stage)
    FACE_LANDMARKER_MODEL_PATH: str = "models/face_landmarker/face_landmarker.task"
    FACE_LANDMARKER_MODEL_URL: str = (
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
        "face_landmarker/float16/latest/face_landmarker.task"
    )
    FACE_LANDMARKER_MIN_DETECTION_CONFIDENCE: float = 0.5

    # Image defaults
    IMAGE_SIZE: int = 256

    # ITA / MST constants
    MST_LABELS: dict = field(default_factory=lambda: {
        0: "Very Light",
        1: "Light",
        2: "Medium Light",
        3: "Medium",
        4: "Medium Dark",
        5: "Dark",
        6: "Very Dark",
        7: "Deep",
        8: "Deep Plus",
        9: "Deepest",
    })


def get_config() -> Config:
    """Return the default project configuration."""
    return Config()
