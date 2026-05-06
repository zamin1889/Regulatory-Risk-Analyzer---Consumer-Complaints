import pandas as pd
import plotly.express as px
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

    if "severity_score" in df.columns:
        df["severity_score"] = pd.to_numeric(df["severity_score"], errors="coerce")

    if "regulatory_risk_flag" in df.columns:
        df["regulatory_risk_flag"] = (
            df["regulatory_risk_flag"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(["true", "1", "yes"])
        )

    return df


def normalize_root_cause(raw_value: str) -> str:
    """Normalize root cause categories using keyword-based mapping.

    Args:
        raw_value: The raw category value from the dataset.

    Returns:
        A normalized category label.
    """
    if not isinstance(raw_value, str):
        return "Unknown"

    value = raw_value.strip()
    if not value:
        return "Unknown"

    lowered = value.lower()
    keyword_groups = [
        ("Identity Theft/Fraud", ("ident", "fraud", "theft")),
        ("Billing & Payments", ("bill", "payment", "fee")),
        ("Account Management", ("account", "close", "manage")),
        ("Credit Reporting", ("credit", "report", "score")),
    ]

    for label, keywords in keyword_groups:
        if any(keyword in lowered for keyword in keywords):
            return label

    return value


st.title("Regulatory Risk Analyzer - Consumer Complaints")
st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e3e6eb;
        border-radius: 12px;
        padding: 18px 16px;
        box-shadow: 0 2px 10px rgba(16, 24, 40, 0.08);
    }
    div[data-testid="stMetric"] label {
        color: #1f2937;
        font-weight: 600;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f172a;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #475569;
    }
    </style>
    """,
    unsafe_allow_html=True
)


df = load_processed_data()

with st.sidebar:
    st.header("Filters")

    date_series = df.get("Date received", pd.Series([], dtype="datetime64[ns]")).dropna()
    if not date_series.empty:
        min_date = date_series.min().date()
        max_date = date_series.max().date()
    else:
        today = pd.Timestamp.today().date()
        min_date = today
        max_date = today

    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    company_options = sorted(df.get("Company", pd.Series([], dtype=str)).dropna().unique())
    selected_companies = st.multiselect(
        "Company",
        options=company_options,
        default=company_options,
    )

    state_options = sorted(df.get("State", pd.Series([], dtype=str)).dropna().unique())
    selected_states = st.multiselect(
        "State",
        options=state_options,
        default=state_options,
    )

filtered_df = df.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range
    end_date = date_range

if "Date received" in filtered_df.columns:
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    filtered_df = filtered_df[
        filtered_df["Date received"].between(start_ts, end_ts, inclusive="both")
    ]

if selected_companies and "Company" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Company"].isin(selected_companies)]

if selected_states and "State" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["State"].isin(selected_states)]

total_complaints = int(filtered_df.shape[0])

severity_series = (
    filtered_df["severity_score"]
    if "severity_score" in filtered_df.columns
    else pd.Series([], dtype=float)
)
avg_severity = severity_series.mean()
avg_severity_display = f"{avg_severity:.2f}" if pd.notna(avg_severity) else "N/A"

risk_series = (
    filtered_df["regulatory_risk_flag"]
    if "regulatory_risk_flag" in filtered_df.columns
    else pd.Series([], dtype=bool)
)
risk_pct = risk_series.mean() * 100 if not risk_series.empty else float("nan")
risk_pct_display = f"{risk_pct:.1f}%" if pd.notna(risk_pct) else "N/A"

root_cause_series = (
    filtered_df["root_cause_category"]
    if "root_cause_category" in filtered_df.columns
    else pd.Series([], dtype=str)
)
top_root_cause = (
    root_cause_series.mode().iloc[0]
    if not root_cause_series.dropna().empty
    else "N/A"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Complaints Analyzed", f"{total_complaints:,}")
col2.metric("Average Severity Score", avg_severity_display)
col3.metric("Regulatory Risk Flagged", risk_pct_display)
col4.metric("Top Root Cause Category", top_root_cause)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if "root_cause_category" in filtered_df.columns and not filtered_df.empty:
        normalized_root_causes = (
            filtered_df["root_cause_category"]
            .fillna("Unknown")
            .astype(str)
            .apply(normalize_root_cause)
        )
        root_cause_counts = normalized_root_causes.value_counts()
        top_categories = root_cause_counts.head(7)
        other_count = root_cause_counts.iloc[7:].sum()
        if other_count > 0:
            top_categories = pd.concat(
                [
                    top_categories,
                    pd.Series({"Other": other_count}),
                ]
            )
        root_cause_counts = top_categories.reset_index()
        root_cause_counts.columns = ["root_cause_category", "count"]

        display_mode = st.radio(
            "Display",
            ["Percentage", "Actual Count"],
            horizontal=True,
            index=0,
        )
        textinfo_value = "percent" if display_mode == "Percentage" else "value"

        fig_root_cause = px.pie(
            root_cause_counts,
            names="root_cause_category",
            values="count",
            hole=0.5,
            title="Root Cause Category Distribution",
            labels={"root_cause_category": "Root Cause", "count": "Complaints"},
        )
        fig_root_cause.update_traces(
            textinfo=textinfo_value,
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Complaints: %{value}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            ),
        )
        fig_root_cause.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_root_cause, use_container_width=True)
    else:
        st.info("No root cause data available for the selected filters.")

with chart_col2:
    if "Company" in filtered_df.columns and "severity_score" in filtered_df.columns:
        severity_by_company = (
            filtered_df.dropna(subset=["Company", "severity_score"])
            .groupby("Company", as_index=False)["severity_score"]
            .mean()
            .sort_values("severity_score", ascending=False)
        )

        if not severity_by_company.empty:
            fig_severity = px.bar(
                severity_by_company,
                x="Company",
                y="severity_score",
                title="Average Severity Score by Company",
            )
            fig_severity.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_severity, use_container_width=True)
        else:
            st.info("No severity data available for the selected filters.")
    else:
        st.info("No company severity data available for the selected filters.")


@st.cache_data(show_spinner=False)
def dataframe_to_csv(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to CSV bytes for downloading.

    Args:
        df: DataFrame to convert.

    Returns:
        CSV data as UTF-8 encoded bytes.
    """
    return df.to_csv(index=False).encode("utf-8")


st.subheader("Raw Data & Export")
st.dataframe(filtered_df, use_container_width=True)

csv_data = dataframe_to_csv(filtered_df)
st.download_button(
    label="Download Data as CSV",
    data=csv_data,
    file_name="filtered_complaints.csv",
    mime="text/csv",
)