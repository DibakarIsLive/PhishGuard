# PhishGuard — ML Training Guide

This document is designed for a project demonstration/viva. It explains where the data comes from, how it is cleaned, how features are generated, how the model is trained, and how the trained model is used by the Django API.

## 1. Dataset

The project uses the public 21,000-row mirror/subset at:

`KaushiGihan/phishing-site-url` on Hugging Face

The dataset page identifies the source as the Tarun Tiwari Kaggle **Phishing Site URLs** dataset.

The data contains URL text and a binary phishing label:

- `0` = legitimate / benign
- `1` = phishing / malicious

No Kaggle login is required by the project because the training script downloads the public mirror directly from Hugging Face.

## 2. Important safety rule

The training code **never opens the URLs**. URLs are handled only as strings. This is important because the dataset contains malicious URLs.

## 3. Data-cleaning pipeline

Before training, PhishGuard:

1. Detects the URL and label columns (`url`/`label` or `text`/`labels`).
2. Removes empty URLs.
3. Removes missing or unknown labels.
4. Converts labels into `0` and `1`.
5. Normalizes whitespace.
6. Detects duplicate URLs.
7. Removes URLs that appear with conflicting labels rather than training on contradictory examples.
8. Shuffles the cleaned dataset with a fixed random seed for reproducibility.
9. Saves `backend/data/processed/cleaned_dataset.csv` so the cleaning result can be inspected.

## 4. Feature engineering

Each URL is converted into numerical features before the ML model sees it. The current extractor uses 20 URL-structure features, including:

- URL length
- domain length
- path length
- dot count
- hyphen count
- digit count
- special-character count
- subdomain count
- `@` symbol
- raw IP address
- HTTPS usage
- Punycode
- URL shortener
- suspicious TLD
- suspicious keyword count
- URL entropy
- encoded characters
- double slash in path
- explicit port
- query parameter count

These are the same features used during live prediction, which prevents a training/inference feature mismatch.

## 5. Data split

After cleaning, the data is split using stratification:

- 70% training
- 15% validation
- 15% testing

Stratification keeps the legitimate/phishing class distribution approximately consistent across the three splits.

## 6. ML model

PhishGuard trains a soft-voting ensemble containing:

1. **Random Forest Classifier** — captures non-linear relationships between URL features.
2. **Logistic Regression** — provides a strong linear baseline and is scaled before training.

The ensemble combines their probability outputs using soft voting, with a higher weight on Random Forest.

## 7. Evaluation

The training script reports:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion matrix

Validation and test results are saved to:

`backend/ml_models/training_metadata.json`

## 8. Run the training

From the `backend` directory:

```bash
pip install -r requirements.txt
python scripts/train_model.py
```

The first run downloads the three public Parquet files automatically.

The script creates:

```text
backend/data/raw/
    train-00000-of-00001.parquet
    validation-00000-of-00001.parquet
    test-00000-of-00001.parquet

backend/data/processed/
    cleaned_dataset.csv

backend/ml_models/
    ensemble.joblib
    training_metadata.json
```

## 9. Train from another CSV

The trainer also accepts a local CSV:

```bash
python scripts/train_model.py --csv path/to/dataset.csv
```

Supported schemas:

```text
url,label
```

or

```text
text,labels
```

The label can be `0/1`, `good/bad`, or common equivalent names such as `legitimate/phishing`.

## 10. How prediction works after training

```text
User enters URL
      ↓
feature_extractor.py
      ↓
20 numerical URL features
      ↓
ensemble.joblib
      ↓
phishing probability
      ↓
Django API response
      ↓
Frontend ResultCard
```

If no model has been trained yet, the application keeps its transparent heuristic fallback. Once `ensemble.joblib` exists, the API automatically uses the trained ensemble.

## 11. What to show the teacher

A good demonstration sequence is:

1. Show the dataset source and explain `0 = legitimate`, `1 = phishing`.
2. Open `backend/scripts/train_model.py` and show the cleaning section.
3. Show the 70/15/15 stratified split.
4. Show the 20 URL features in `feature_extractor.py`.
5. Run `python scripts/train_model.py`.
6. Show the accuracy/precision/recall/F1/ROC-AUC and confusion matrix printed by the script.
7. Show `training_metadata.json`.
8. Start Django and scan a URL through the PhishGuard UI.
9. Point out that the API response says `model_used: trained ensemble model`.

## 12. Honest limitation

This is a research/academic phishing URL classifier, not a production security gateway. Dataset age, class balance, label quality, and changes in modern phishing campaigns can affect real-world performance. The project should not claim that a single static dataset makes detection 100% accurate.
