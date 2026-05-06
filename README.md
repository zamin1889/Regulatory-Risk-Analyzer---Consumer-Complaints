# 🚀 AI-Powered Regulatory Risk Analyzer

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-orange.svg)
![LLM](https://img.shields.io/badge/AI-Gemini%20%2F%20Llama%203-brightgreen.svg)

An enterprise-grade, end-to-end data engineering pipeline and interactive executive dashboard designed to automate the ingestion, processing, and risk-scoring of unstructured consumer financial complaints. 

---

## 🛑 The Problem
Financial institutions receive thousands of unstructured consumer complaints daily via the CFPB and internal channels. Manual review of these narratives for regulatory risk, severity, and root-cause analysis is:
1. **Unscalable:** Requires hundreds of human hours per week.
2. **Inconsistent:** Human analysts often categorize identical complaints differently.
3. **Reactive:** Delays in processing mean critical compliance risks are caught weeks after they occur.

## 💡 The Solution
This project introduces an automated AI-driven ETL (Extract, Transform, Load) pipeline that reads raw CSV complaints, runs them through an LLM inference engine to extract structured JSON data, and visualizes the results on a high-speed, cached Streamlit dashboard.

### 🔑 Key Features
*   **Intelligent ETL Pipeline:** Automatically cleans and samples massive datasets, dropping nulls and standardizing date formats using Pandas.
*   **LLM Data Extraction:** Utilizes LLM inference (Gemini/Llama 3) to read complaint narratives and extract specific business intelligence: `root_cause_category`, `severity_score` (1-5), and `regulatory_risk_flag` (True/False).
*   **High-Cardinality Resolution:** Features a custom Pandas mapping layer to dynamically group LLM-hallucinated long-tail categories into clean, standardized executive taxonomy (e.g., grouping "Credit Error" and "Report Dispute" into "Credit Reporting").
*   **Fault-Tolerant Batch Processing:** Includes API rate-limit handling (`time.sleep` constraints) and automated fallback mechanisms to ensure the pipeline survives server spikes.
*   **Enterprise Dashboard:** A fast, `@st.cache_data` optimized Streamlit UI featuring interactive Plotly visualizations (dynamic Donut and Bar charts) and raw data export capabilities.

---

## 🏗️ Technical Architecture
1. **Data Layer:** Unstructured CFPB Consumer Complaint CSVs.
2. **Compute Node (Optional Cloud GPU):** Google Colab with T4 GPU running 4-bit quantized `Llama-3-8B-Instruct` via `vLLM`/HuggingFace for massive batch processing without rate limits.
3. **Application & Processing Layer:** Python, Pandas, JSON parsing, API integration.
4. **Presentation Layer:** Streamlit, Plotly Express (styled with custom CSS and a corporate Amex-branded color palette).

---

## 💻 How to Run Locally

### Prerequisites
*   Python 3.11 or higher
*   Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone [https://github.com/YourUsername/regulatory-risk-analyzer.git](https://github.com/YourUsername/regulatory-risk-analyzer.git)
   cd regulatory-risk-analyzer

2. **Create a virtual environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt

4. **Set up Environment Variables**
    : Create a .env file in the root directory and add your API key (if running the LLM engine locally):
    ```
    GEMINI_API_KEY=your_api_key_here

5. **Run the Dashboard**
   ```bash
   streamlit run app.py

   The application will be available at http://localhost:8501

