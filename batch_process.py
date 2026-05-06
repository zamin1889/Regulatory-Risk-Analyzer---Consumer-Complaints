"""Batch process CFPB complaints with Gemini and save a cached dataset."""

from pathlib import Path
from typing import Any, Dict, List
import time

import pandas as pd

from data_processor import load_and_clean_data
from llm_engine import analyze_complaint

RAW_DATA_PATH = "CFPB_complaint_data_2025.csv"
OUTPUT_DATA_PATH = "data/processed_complaints.csv"
SAMPLE_SIZE = 300
NARRATIVE_COLUMN = "Consumer complaint narrative"


def _run_llm_batch(df: pd.DataFrame, narrative_column: str) -> pd.DataFrame:
    """Run Gemini analysis on each complaint narrative.

    Args:
        df: Cleaned CFPB DataFrame.
        narrative_column: Column name containing complaint narratives.

    Returns:
        The input DataFrame with LLM-derived columns appended.
    """
    results: List[Dict[str, Any]] = []
    narratives = df[narrative_column].fillna("").astype(str)

    for index, text in enumerate(narratives, start=1):
        result = analyze_complaint(text)
        results.append(result)
        print(f"Processed {index}/{len(df)} complaints")
        time.sleep(4.5)

    results_df = pd.DataFrame(results)
    return pd.concat([df.reset_index(drop=True), results_df], axis=1)


def process_sample(raw_csv_path: str, output_path: str, sample_size: int = SAMPLE_SIZE) -> pd.DataFrame:
    """Load, clean, sample, and enrich complaints with Gemini analysis.

    Args:
        raw_csv_path: Path to the raw CFPB CSV file.
        output_path: Destination path for the processed CSV.
        sample_size: Number of rows to process for the test batch.

    Returns:
        The processed DataFrame containing LLM output fields.
    """
    cleaned_df = load_and_clean_data(raw_csv_path)
    sample_df = cleaned_df.sample(n=sample_size, random_state=42).copy()

    enriched_df = _run_llm_batch(sample_df, NARRATIVE_COLUMN)

    # Ensure output directory exists before writing the CSV.
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    enriched_df.to_csv(output_path, index=False)
    return enriched_df


def main() -> None:
    """Run the batch processing pipeline for a small test sample."""
    try:
        process_sample(RAW_DATA_PATH, OUTPUT_DATA_PATH, SAMPLE_SIZE)
        print(f"Saved processed complaints to {OUTPUT_DATA_PATH}")
    except Exception as exc:
        print(f"Batch processing failed: {exc}")


if __name__ == "__main__":
    main()
