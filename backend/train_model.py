from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


TEXT_COLS = [
    "title",
    "location",
    "department",
    "company_profile",
    "description",
    "requirements",
    "benefits",
    "employment_type",
    "required_experience",
    "required_education",
    "industry",
    "function",
]

NUMERIC_COLS = ["telecommuting", "has_company_logo", "has_questions", "salary_max"]


def parse_salary_max(value: str) -> float:
    if not isinstance(value, str) or not value.strip():
        return 0.0
    cleaned = value.replace("$", "").replace(",", "").strip()
    if "-" in cleaned:
        parts = [p.strip() for p in cleaned.split("-") if p.strip()]
        try:
            nums = [float(p) for p in parts]
            return max(nums) if nums else 0.0
        except ValueError:
            return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    for col in TEXT_COLS:
        if col not in data.columns:
            data[col] = ""
        data[col] = data[col].fillna("").astype(str)

    data["salary_max"] = data.get("salary_range", "").apply(parse_salary_max)
    data["salary_max"] = data["salary_max"].fillna(0.0)

    for col in ["telecommuting", "has_company_logo", "has_questions"]:
        data[col] = pd.to_numeric(data.get(col, 0), errors="coerce").fillna(0)

    data["combined_text"] = data[TEXT_COLS].agg(" ".join, axis=1)
    return data


def train(data_path: Path, output_path: Path) -> None:
    raw_df = pd.read_csv(data_path)
    if "fraudulent" not in raw_df.columns:
        raise ValueError("Dataset must contain a 'fraudulent' label column.")

    df = build_feature_frame(raw_df)
    X = df[["combined_text", *NUMERIC_COLS]]
    y = df["fraudulent"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("text", TfidfVectorizer(max_features=12000, ngram_range=(1, 2)), "combined_text"),
            ("num", Pipeline([("scale", StandardScaler())]), NUMERIC_COLS),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    max_iter=400,
                    class_weight="balanced",
                    solver="liblinear",
                    random_state=42,
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    report = classification_report(y_test, preds, output_dict=True)
    auc = roc_auc_score(y_test, probs)

    artifact = {
        "model": model,
        "metrics": {"roc_auc": float(auc), "classification_report": report},
        "feature_columns": ["combined_text", *NUMERIC_COLS],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, output_path)

    print("Model trained successfully.")
    print(f"Saved model to: {output_path}")
    print(f"ROC AUC: {auc:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train fake job posting detector.")
    parser.add_argument("--data", type=str, required=True, help="Path to CSV dataset")
    parser.add_argument(
        "--output",
        type=str,
        default="models/jobshield_model.joblib",
        help="Output model path",
    )
    args = parser.parse_args()

    train(Path(args.data), Path(args.output))
