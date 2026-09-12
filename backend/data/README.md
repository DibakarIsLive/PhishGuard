# PhishGuard training data

The project uses the public 21,000-row mirror/subset `KaushiGihan/phishing-site-url` on Hugging Face, which identifies the Tarun Tiwari Kaggle **Phishing Site URLs** dataset as its source.

Labels used by the training pipeline:

- `0` = legitimate / benign
- `1` = phishing / malicious

The training script downloads the three public Parquet files automatically. No Kaggle account is required.

**Safety:** URLs are never opened or visited. They are processed only as text for URL-structure features.

`data/processed/cleaned_dataset.csv` is generated after training so the cleaned labels and URLs can be inspected during a project demonstration.
