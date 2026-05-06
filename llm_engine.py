"""Gemini LLM integration for CFPB complaint narratives."""

from typing import Any, Dict, Optional
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

MODEL_NAME = "gemini-3.1-flash-lite-preview"

DEFAULT_RESPONSE: Dict[str, Any] = {
    "root_cause_category": "Unknown",
    "severity_score": 1,
    "regulatory_risk_flag": False,
}

SYSTEM_PROMPT = (
    "You are a Risk Analyst specializing in consumer credit card complaints. "
    "Extract structured business intelligence from each complaint narrative. "
    "Return ONLY a JSON object with these exact keys: "
    "root_cause_category (string), severity_score (integer 1-5), "
    "regulatory_risk_flag (boolean). "
    "Do not include any extra keys, markdown, or commentary."
)

_CLIENT: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    """Create or reuse the Gemini client instance.

    Returns:
        A configured Gemini client.
    """
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT

    load_dotenv()
    _CLIENT = genai.Client()
    return _CLIENT


def _build_prompt(text_narrative: str) -> str:
    """Build the user prompt for the complaint narrative.

    Args:
        text_narrative: The complaint narrative text.

    Returns:
        A prompt string to send to the model.
    """
    cleaned_text = text_narrative.strip()
    return (
        "Complaint narrative:\n"
        f"{cleaned_text}\n\n"
        "Return the JSON object only."
    )


def _normalize_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and validate the model response payload.

    Args:
        payload: Parsed JSON payload from the model.

    Returns:
        A normalized dictionary that matches the required schema.
    """
    if not isinstance(payload, dict):
        return DEFAULT_RESPONSE.copy()

    root_cause = str(payload.get("root_cause_category", "Unknown")).strip() or "Unknown"

    severity_raw = payload.get("severity_score", 1)
    try:
        severity = int(severity_raw)
    except (TypeError, ValueError):
        severity = 1
    severity = max(1, min(severity, 5))

    risk_raw = payload.get("regulatory_risk_flag", False)
    if isinstance(risk_raw, bool):
        risk_flag = risk_raw
    elif isinstance(risk_raw, str):
        risk_flag = risk_raw.strip().lower() in {"true", "1", "yes", "y"}
    elif isinstance(risk_raw, (int, float)):
        risk_flag = bool(risk_raw)
    else:
        risk_flag = False

    return {
        "root_cause_category": root_cause,
        "severity_score": severity,
        "regulatory_risk_flag": risk_flag,
    }


def analyze_complaint(text_narrative: str) -> Dict[str, Any]:
    """Analyze a complaint narrative using Gemini and return structured data.

    Args:
        text_narrative: The raw complaint narrative text.

    Returns:
        A dictionary with root cause category, severity score, and risk flag.
    """
    if not text_narrative or not str(text_narrative).strip():
        return DEFAULT_RESPONSE.copy()

    try:
        client = _get_client()
        prompt = _build_prompt(str(text_narrative))
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
                max_output_tokens=256,
            ),
        )
        response_text = getattr(response, "text", None)
        if not response_text:
            return DEFAULT_RESPONSE.copy()
        parsed = json.loads(response_text)
        return _normalize_response(parsed)
    except Exception as exc:
        print(f"Gemini API error: {exc}")
        return DEFAULT_RESPONSE.copy()
