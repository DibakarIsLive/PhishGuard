# PhishGuard quick start

## 1. Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/health/`.

## 2. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local address shown by Vite (normally `http://localhost:5173`).

## 3. Train a model (optional, after you have data)

Place a CSV in `backend/data/raw/` with two columns: `url` and `label`, where `label` is `0` for legitimate and `1` for phishing. Then run:

```powershell
cd backend
python scripts/train_model.py ..\phishing_site_urls.csv --max-samples 30000
```

This trains a soft-voting ensemble of Random Forest, XGBoost, SVM, LightGBM, and CatBoost. The resulting `backend/ml_models/ensemble.joblib` is loaded automatically by the API. `metrics.json` stores the evaluation result.

## 4. Scan a dataset from the browser

Use the **Dataset / CSV Scanner** area in the frontend. Upload a CSV containing a `URL` column (the included dataset uses `URL,Label`). The demo scans up to 500 URLs in one request, returns total/phishing/legitimate counts, and lists phishing URLs with the reason for each result.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health/` | Server health check |
| POST | `/api/check-url/` | Check one URL: `{ "url": "https://example.com" }` |
| POST | `/api/batch-check/` | Check up to 100 URLs: `{ "urls": ["..."] }` |
| GET | `/api/predictions/` | Recent scan history |
| GET | `/api/stats/` | Scanner statistics |
