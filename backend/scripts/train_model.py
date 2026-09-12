
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = ROOT / "ml_models"

HF_BASE = "https://huggingface.co/datasets/KaushiGihan/phishing-site-url/resolve/main/data"
FILES = {
    "train": "train-00000-of-00001.parquet",
    "validation": "validation-00000-of-00001.parquet",
    "test": "test-00000-of-00001.parquet",
}

sys.path.insert(0, str(ROOT))
from vision.feature_extractor import extract_features  # noqa: E402


def download_dataset() -> list[Path]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename in FILES.values():
        target = RAW_DIR / filename
        if not target.exists() or target.stat().st_size < 1000:
            url = f"{HF_BASE}/{filename}"
            print(f"Downloading {filename} ...")
            urllib.request.urlretrieve(url, target)
        paths.append(target)
    return paths


def normalize_url(value: object) -> str:
    url = str(value).strip()
    url = re.sub(r"\s+", "", url)
    return url


def normalize_label(value: object) -> int | None:
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return int(value)
    text = str(value).strip().lower()
    if text in {"1", "bad", "phishing", "malicious", "phish", "yes", "true"}:
        return 1
    if text in {"0", "good", "legitimate", "benign", "safe", "no", "false"}:
        return 0
    try:
        number = int(float(text))
        return number if number in {0, 1} else None
    except ValueError:
        return None


def load_source(csv_path: str | None) -> pd.DataFrame:
    if csv_path:
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")
        return pd.read_csv(path)

    paths = download_dataset()
    frames = [pd.read_parquet(path) for path in paths]
    return pd.concat(frames, ignore_index=True)


def clean_dataset(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    # Accept both the Hugging Face schema (text/labels) and common CSV schemas.
    url_col = next((c for c in ["url", "URL", "text", "Text"] if c in raw.columns), None)
    label_col = next((c for c in ["label", "Label", "labels", "class"] if c in raw.columns), None)
    if not url_col or not label_col:
        raise ValueError(
            f"Could not find URL/label columns. Found: {list(raw.columns)}. "
            "Expected url+label or text+labels."
        )

    df = raw[[url_col, label_col]].copy()
    df.columns = ["url", "label_raw"]
    before = len(df)
    df["url"] = df["url"].map(normalize_url)
    df["label"] = df["label_raw"].map(normalize_label)

    empty_removed = int((df["url"] == "").sum())
    unknown_labels = int(df["label"].isna().sum())
    df = df[(df["url"] != "") & df["label"].notna()].copy()
    df["label"] = df["label"].astype(int)

    # Deduplicate by normalized URL. If the same URL has conflicting labels,
    # remove it instead of allowing noisy labels into the model.
    df["url_key"] = df["url"].str.lower().str.rstrip("/")
    conflicts = df.groupby("url_key")["label"].nunique()
    conflicting_keys = set(conflicts[conflicts > 1].index)
    conflict_rows = int(df["url_key"].isin(conflicting_keys).sum())
    df = df[~df["url_key"].isin(conflicting_keys)].copy()
    duplicate_rows = int(df.duplicated("url_key").sum())
    df = df.drop_duplicates("url_key").drop(columns=["url_key", "label_raw"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Keep the cleaned CSV easy for a teacher to inspect.
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / "cleaned_dataset.csv", index=False)

    cleaning = {
        "rows_before_cleaning": before,
        "empty_urls_removed": empty_removed,
        "unknown_or_missing_labels_removed": unknown_labels,
        "conflicting_label_rows_removed": conflict_rows,
        "duplicate_urls_removed": duplicate_rows,
        "rows_after_cleaning": len(df),
        "legitimate_0": int((df["label"] == 0).sum()),
        "phishing_1": int((df["label"] == 1).sum()),
    }
    return df, cleaning


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame([extract_features(url) for url in df["url"]])
    # Freeze the exact feature order used by the deployed predictor.
    return features.sort_index(axis=1)


def build_model() -> VotingClassifier:
    forest = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    logistic = Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=42)),
        ]
    )
    return VotingClassifier(
        estimators=[("forest", forest), ("logistic", logistic)],
        voting="soft",
        weights=[2, 1],
    )


def evaluate(model, X, y, split_name: str) -> dict:
    pred = model.predict(X)
    prob = model.predict_proba(X)[:, 1]
    metrics = {
        "split": split_name,
        "accuracy": round(accuracy_score(y, pred), 4),
        "precision": round(precision_score(y, pred, zero_division=0), 4),
        "recall": round(recall_score(y, pred, zero_division=0), 4),
        "f1": round(f1_score(y, pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y, prob), 4),
        "confusion_matrix": confusion_matrix(y, pred).tolist(),
    }
    print(f"\n{split_name.upper()} RESULTS")
    print(json.dumps(metrics, indent=2))
    print(classification_report(y, pred, target_names=["legitimate (0)", "phishing (1)"], zero_division=0))
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train PhishGuard on labeled phishing/legitimate URLs.")
    parser.add_argument("--csv", help="Optional local CSV. Supports url,label or text,labels.")
    parser.add_argument("--test-size", type=float, default=0.15)
    parser.add_argument("--validation-size", type=float, default=0.15)
    args = parser.parse_args()

    if not 0 < args.test_size < 0.5 or not 0 < args.validation_size < 0.5 or args.test_size + args.validation_size >= 0.8:
        raise ValueError("test-size and validation-size must each be between 0 and 0.5 and leave enough training data.")

    print("PhishGuard training pipeline")
    print("IMPORTANT: URLs are treated as strings; the program never visits them.")
    raw = load_source(args.csv)
    print(f"Raw rows loaded: {len(raw):,}")

    df, cleaning = clean_dataset(raw)
    print("\nDATA CLEANING")
    print(json.dumps(cleaning, indent=2))

    # Stratified split: 70% train, 15% validation, 15% test by default.
    train_df, temp_df = train_test_split(
        df,
        test_size=args.test_size + args.validation_size,
        stratify=df["label"],
        random_state=42,
    )
    relative_test = args.test_size / (args.test_size + args.validation_size)
    validation_df, test_df = train_test_split(
        temp_df,
        test_size=relative_test,
        stratify=temp_df["label"],
        random_state=42,
    )

    X_train, X_val, X_test = map(make_features, [train_df, validation_df, test_df])
    y_train, y_val, y_test = train_df["label"], validation_df["label"], test_df["label"]

    print("\nDATA SPLIT")
    print(f"Train:      {len(train_df):,} ({len(train_df)/len(df):.1%})")
    print(f"Validation: {len(validation_df):,} ({len(validation_df)/len(df):.1%})")
    print(f"Test:       {len(test_df):,} ({len(test_df)/len(df):.1%})")
    print(f"Features:   {X_train.shape[1]}")
    print(f"Feature names: {', '.join(X_train.columns)}")

    model = build_model()
    print("\nTRAINING Random Forest + Logistic Regression soft-voting ensemble ...")
    model.fit(X_train, y_train)

    val_metrics = evaluate(model, X_val, y_val, "validation")
    test_metrics = evaluate(model, X_test, y_test, "test")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_DIR / "ensemble.joblib", compress=3)

    metadata = {
        "dataset": "KaushiGihan/phishing-site-url",
        "dataset_reference": "https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls",
        "dataset_note": "Public 21,000-row mirror/subset of the referenced Kaggle dataset.",
        "label_mapping": {"0": "legitimate", "1": "phishing"},
        "algorithm": "Soft Voting Ensemble: Random Forest + Logistic Regression",
        "feature_count": int(X_train.shape[1]),
        "features": list(X_train.columns),
        "cleaning": cleaning,
        "split_sizes": {"train": len(train_df), "validation": len(validation_df), "test": len(test_df)},
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
    }
    (MODEL_DIR / "training_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"\nSaved model: {MODEL_DIR / 'ensemble.joblib'}")
    print(f"Saved metrics: {MODEL_DIR / 'training_metadata.json'}")
    print(f"Saved cleaned data: {PROCESSED_DIR / 'cleaned_dataset.csv'}")


if __name__ == "__main__":
    main()
