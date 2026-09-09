"""
Hello-world script – verifies the Python environment and project structure.

Run from the project root:
    python scripts/run_hello_world.py
You can also run it as a module:  python -m scripts.run_hello_world
"""

import os
import sys

# Allow `python scripts/run_hello_world.py` to import the `src` package when
# invoked from the project root (running a script directly puts the script's
# own directory, not the root, at the front of sys.path).
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from src.utilities.config import get_config
from src.ita_estimation.compute_ita import compute_ita


def main() -> None:
    cfg = get_config()

    print(f"Project : {cfg.PROJECT_NAME}")
    print(f"Data    : {cfg.DATA_ROOT}")
    print(f"Models  : {cfg.MODELS_ROOT}")
    print(f"Outputs : {cfg.OUTPUTS_ROOT}")
    print()

    # Quick ITA sanity check
    ita = compute_ita(70.0, 20.0)
    print(f"ITA(L=70, b=20) = {ita:.2f}°")
    print()
    print("Python environment and folder structure initialised successfully.")


if __name__ == "__main__":
    main()
