"""
Load and split datasets (FairFace, SCIN, MST-E).

This module provides helpers for locating image files,
reading metadata CSVs, and creating train/val/test splits.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pandas as pd


def list_images(directory: str, extensions: Tuple[str, ...] = (".jpg", ".jpeg", ".png")) -> List[Path]:
    """Return sorted image paths under *directory*."""
    root = Path(directory)
    files = [f for f in sorted(root.rglob("*")) if f.suffix.lower() in extensions]
    return files


def load_metadata(csv_path: str) -> pd.DataFrame:
    """Read a dataset CSV (FairFace / SCIN label file)."""
    return pd.read_csv(csv_path)


def train_val_split(df: pd.DataFrame, val_ratio: float = 0.15, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Randomly split a DataFrame into train and validation sets."""
    val_df = df.sample(frac=val_ratio, random_state=seed)
    train_df = df.drop(val_df.index)
    return train_df, val_df
