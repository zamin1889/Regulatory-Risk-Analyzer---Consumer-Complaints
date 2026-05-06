import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Regulatory Risk Analyzer - Consumer Complaints",
    layout="wide"
)

PROCESSED_DATA_PATH = "data/processed_complaints.csv"


@st.cache_data(show_spinner=False)
def load_processed_data(filepath: str = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Load the processed complaints dataset for the dashboard.

    Args:
        filepath: Path to the processed CSV file.

    Returns:
        A DataFrame of processed complaints or an empty DataFrame on failure.
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as exc:
        print(f"Failed to load processed data: {exc}")
        return pd.DataFrame()

    if "Date received" in df.columns:
        df["Date received"] = pd.to_datetime(df["Date received"], errors="coerce")

    return df


st.title("Regulatory Risk Analyzer - Consumer Complaints")
st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; }
    </style>
    """,
    unsafe_allow_html=True
)