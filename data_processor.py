"""Data loading and cleaning utilities for CFPB complaint data."""

from typing import List

import pandas as pd

REQUIRED_COLUMNS: List[str] = [
    "Date received",
    "Product",
    "Company",
    "State",
    "Company response to consumer",
    "Consumer complaint narrative",
]
OPTIONAL_COLUMNS: List[str] = ["Date sent to company"]


def load_and_clean_data(filepath: str) -> pd.DataFrame:
    """Load CFPB complaint data from CSV and return a cleaned DataFrame.

    Args:
        filepath: Path to the raw CFPB CSV file.

    Returns:
        A cleaned DataFrame with essential columns and optional Resolution_Time_Days.
    """
    try:
        header = pd.read_csv(filepath, nrows=0)
    except Exception as exc:  # pragma: no cover - IO/parse error handling
        raise RuntimeError(f"Failed to read CSV header from {filepath}") from exc

    available_columns = list(header.columns)
    missing_required = [col for col in REQUIRED_COLUMNS if col not in available_columns]
    if missing_required:
        missing_list = ", ".join(missing_required)
        raise ValueError(f"Missing required columns: {missing_list}")

    usecols = REQUIRED_COLUMNS + [col for col in OPTIONAL_COLUMNS if col in available_columns]

    try:
        df = pd.read_csv(filepath, usecols=usecols)
    except Exception as exc:  # pragma: no cover - IO/parse error handling
        raise RuntimeError(f"Failed to read CSV data from {filepath}") from exc

    narratives = df["Consumer complaint narrative"].fillna("").astype("string")
    narrative_mask = narratives.str.strip().ne("")
    df = df.loc[narrative_mask].copy()

    # Normalize date fields for downstream time-series analysis.
    df["Date received"] = pd.to_datetime(df["Date received"], format='mixed', errors="coerce")

    if "Date sent to company" in df.columns:
        df["Date sent to company"] = pd.to_datetime(
            df["Date sent to company"], format='mixed', errors="coerce"
        )
        df["Resolution_Time_Days"] = (
            df["Date sent to company"] - df["Date received"]
        ).dt.days
        df = df.drop(columns=["Date sent to company"])

    return df