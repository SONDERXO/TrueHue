"""
Shared configuration and path helpers for the TrueHue pipeline.

Usage:
    from src.utilities.config import get_config
    cfg = get_config()
    print(cfg.PROJECT_NAME)  # "TrueHue"
"""

from src.utilities.config import get_config, Config  # noqa: F401
