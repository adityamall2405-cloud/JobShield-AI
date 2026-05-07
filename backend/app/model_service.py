from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from .schemas import JobPostingInput


MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "jobshield_model.joblib"


def parse_salary_max(value: str) -> float:
    if not isinstance(value, str) or not value.strip():
        return 0.0
    cleaned = value.replace("$", "").replace(",", "").strip()
    if "-" in cleaned:
        parts = [p.strip() for p in cleaned.split("-") if p.strip()]
        nums = []
        for p in parts:
            try:
                nums.append(float(p))
            except ValueError:
                continue
        return max(nums) if nums else 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


class ModelService:
    def __init__(self) -> None:
        self.artifact = None
        self.model = None

    def load(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run training before starting the API."
            )
        self.artifact = joblib.load(MODEL_PATH)
        self.model = self.artifact["model"]

    def _prepare_input(self, payload: JobPostingInput) -> pd.DataFrame:
        data = payload.model_dump()
        combined_text = " ".join(
            [
                data.get("title", ""),
                data.get("location", ""),
                data.get("department", ""),
                data.get("company_profile", ""),
                data.get("description", ""),
                data.get("requirements", ""),
                data.get("benefits", ""),
                data.get("employment_type", ""),
                data.get("required_experience", ""),
                data.get("required_education", ""),
                data.get("industry", ""),
                data.get("function", ""),
            ]
        ).strip()
        row = {
            "combined_text": combined_text,
            "telecommuting": int(data.get("telecommuting", 0) or 0),
            "has_company_logo": int(data.get("has_company_logo", 0) or 0),
            "has_questions": int(data.get("has_questions", 0) or 0),
            "salary_max": parse_salary_max(data.get("salary_range", "")),
        }
        return pd.DataFrame([row])

    def _risk_level(self, fake_prob: float) -> str:
        if fake_prob >= 0.75:
            return "high"
        if fake_prob >= 0.4:
            return "medium"
        return "low"

    def _indicators(self, payload: JobPostingInput, fake_prob: float) -> list[str]:
        indicators = []
        if not payload.company_profile.strip():
            indicators.append("Missing company profile")
        if parse_salary_max(payload.salary_range) >= 250000:
            indicators.append("Unrealistic salary range")
        text = f"{payload.description} {payload.requirements}".lower()
        phishing_terms = ["wire transfer", "bank details", "processing fee", "urgent hiring"]
        if any(term in text for term in phishing_terms):
            indicators.append("Potential phishing language")
        if payload.has_company_logo == 0:
            indicators.append("No company logo")
        if payload.has_questions == 0:
            indicators.append("No screening questions")
        if fake_prob >= 0.75:
            indicators.append("High fraud probability by ML model")
        return indicators

    def predict(self, payload: JobPostingInput) -> dict:
        if self.model is None:
            self.load()
        X = self._prepare_input(payload)
        fake_prob = float(self.model.predict_proba(X)[0][1])
        trust_score = float(1.0 - fake_prob)
        return {
            "is_fake": fake_prob >= 0.5,
            "fake_probability": round(fake_prob, 4),
            "trust_score": round(trust_score, 4),
            "risk_level": self._risk_level(fake_prob),
            "indicators": self._indicators(payload, fake_prob),
        }
