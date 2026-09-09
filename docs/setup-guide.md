# Setup Guide

Step-by-step instructions to get the TrueHue Python pipeline running.

## Prerequisites

| Tool | Minimum version | Check command |
|------|----------------|---------------|
| Python | 3.10 | `python --version` |
| pip | 22+ | `pip --version` |
| Git | 2.x | `git --version` |

## 1. Clone the repository

```bash
git clone https://github.com/<your-org>/skin-tone-correction.git
cd skin-tone-correction
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

> You should see `(venv)` at the start of your prompt after activation.

## 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Verify the installation

```bash
python -c "import cv2, numpy, sklearn, skimage; print('All core imports OK')"
```

## 5. Run the hello-world script

```bash
python scripts/run_hello_world.py
```

Expected output:

```
Project : TrueHue
Data    : data
Models  : models
Outputs : outputs

ITA(L=70, b=20) = 45.00°

Python environment and folder structure initialised successfully.
```

## 6. Run the test suite

```bash
pytest tests/ -v
```

You should see all tests passing (the skin-mask tests validate placeholder behaviour).

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'cv2'` | Run `pip install opencv-python` inside the venv. |
| `error: Microsoft Visual C++ 14.0 is required` | Install [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/). |
| `pip` command not found | Make sure the venv is activated; try `python -m pip install ...`. |
| Permission errors on Windows | Run the terminal as Administrator, or use `--user` flag. |
