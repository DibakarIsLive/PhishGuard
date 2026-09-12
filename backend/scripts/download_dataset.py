
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
BASE = "https://huggingface.co/datasets/KaushiGihan/phishing-site-url/resolve/main/data"
FILES = [
    "train-00000-of-00001.parquet",
    "validation-00000-of-00001.parquet",
    "test-00000-of-00001.parquet",
]
RAW.mkdir(parents=True, exist_ok=True)
for name in FILES:
    target = RAW / name
    print(f"Downloading {name} ...")
    urllib.request.urlretrieve(f"{BASE}/{name}", target)
    print(f"Saved {target} ({target.stat().st_size:,} bytes)")
print("Done. The training script can now read these files.")
