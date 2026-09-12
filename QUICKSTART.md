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

## 3. Train the ML model

The default training command downloads the public 21,000-row mirror of the referenced phishing URL dataset automatically. No Kaggle login is required.

```powershell
cd backend
python scripts/train_model.py
```

The pipeline cleans the data, removes duplicates/conflicting labels, extracts URL features, performs a stratified 70/15/15 train-validation-test split, trains the Random Forest + Logistic Regression soft-voting ensemble, evaluates it, and saves `ml_models/ensemble.joblib` plus training metrics.

You can also train on your own CSV:

```powershell
python scripts/train_model.py --csv data/raw/urls.csv
```

The CSV can use `url,label` or `text,labels`. Labels may be `good/bad` or `0/1`; the script normalizes them automatically.

## 4. Frontend ↔ backend connection

Keep both terminals running:

- Django: `http://127.0.0.1:8000`
- Vite: normally `http://localhost:5173`

The frontend uses `/api` by default, and Vite proxies `/api/*` to Django during development. This makes the connection reliable without hard-coding the backend address into the browser. For another deployment, set `VITE_API_URL` to the backend API base URL.

Test the backend directly with:

```powershell
curl http://127.0.0.1:8000/api/health/
```

Then open the frontend and use **Analyze URL**. The result is returned from Django, saved to SQLite history, and displayed by React.

The app deliberately keeps the URL-pattern baseline as a fallback. Once `backend/ml_models/ensemble.joblib` exists, predictions automatically use the trained ensemble.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health/` | Server health check |
| POST | `/api/check-url/` | Check one URL: `{ "url": "https://example.com" }` |
| POST | `/api/batch-check/` | Check up to 100 URLs: `{ "urls": ["..."] }` |
| GET | `/api/predictions/` | Recent scan history |
| GET | `/api/stats/` | Scanner statistics |
