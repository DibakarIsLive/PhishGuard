"""Train PhishGuard's five-model soft-voting ensemble from a URL CSV dataset."""
import argparse
from pathlib import Path
import sys
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vision.feature_extractor import extract_features

parser = argparse.ArgumentParser()
parser.add_argument("csv", help="CSV file with URL and Label columns (bad/good or 1/0)")
parser.add_argument("--max-samples", type=int, default=30000, help="Use a balanced subset for faster demo training")
args = parser.parse_args()
data = pd.read_csv(args.csv)
columns = {column.strip().lower(): column for column in data.columns}
if "url" not in columns or "label" not in columns:
    raise ValueError("Dataset must contain URL and Label columns.")
data = data[[columns["url"], columns["label"]]].rename(columns={columns["url"]: "url", columns["label"]: "label"}).dropna()
data["label"] = data["label"].astype(str).str.strip().str.lower().map({"bad": 1, "phishing": 1, "malicious": 1, "1": 1, "good": 0, "legitimate": 0, "benign": 0, "0": 0})
data = data.dropna(subset=["label"]).drop_duplicates("url")
if len(data) > args.max_samples:
    data, _ = train_test_split(data, train_size=args.max_samples, stratify=data["label"], random_state=42)
features = pd.DataFrame([extract_features(url) for url in data["url"]])
X_train, X_test, y_train, y_test = train_test_split(features, data["label"].astype(int), test_size=0.2, stratify=data["label"], random_state=42)
model = VotingClassifier([
    ("random_forest", RandomForestClassifier(n_estimators=180, random_state=42, class_weight="balanced", n_jobs=-1)),
    ("xgboost", XGBClassifier(n_estimators=180, max_depth=6, learning_rate=0.08, subsample=0.85, colsample_bytree=0.85, random_state=42, n_jobs=-1, eval_metric="logloss")),
    ("svm", Pipeline([("scale", StandardScaler()), ("model", SVC(C=2.0, probability=True, class_weight="balanced", random_state=42))])),
    ("lightgbm", LGBMClassifier(n_estimators=180, learning_rate=0.08, num_leaves=31, random_state=42, n_jobs=-1, verbosity=-1)),
    ("catboost", CatBoostClassifier(iterations=180, depth=6, learning_rate=0.08, random_seed=42, verbose=False)),
], voting="soft", n_jobs=-1)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
target = Path(__file__).resolve().parent.parent / "ml_models"
target.mkdir(exist_ok=True)
joblib.dump(model, target / "ensemble.joblib")
metrics = {"models": ["Random Forest", "XGBoost", "SVM", "LightGBM", "CatBoost"], "training_samples": len(X_train), "test_samples": len(X_test), "accuracy": round(float(accuracy_score(y_test, predictions)), 4), "f1_score": round(float(f1_score(y_test, predictions)), 4), "report": classification_report(y_test, predictions, output_dict=True)}
(target / "metrics.json").write_text(__import__("json").dumps(metrics, indent=2), encoding="utf-8")
print(f"Saved five-model ensemble to {target / 'ensemble.joblib'}")
print(f"Accuracy: {metrics['accuracy']:.2%} | F1: {metrics['f1_score']:.2%}")
