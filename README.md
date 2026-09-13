<div align="center">

# 🛡️ PhishGuard

### A Phase 1 explainable phishing URL analysis application

[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-JSX-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![MongoEngine](https://img.shields.io/badge/MongoDB-MongoEngine-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://docs.mongoengine.org/)

![PhishGuard Banner](./public/phishguard-banner.png)

**Inspect the URL → explain the signals → optionally record the result**

</div>

## Overview

PhishGuard is an academic and research-oriented full-stack application for inspecting suspicious URLs. The current Phase 1 implementation combines a network-free URL feature extractor, a transparent heuristic predictor, an optional `joblib` model hook, a Django REST API, optional MongoDB history, and a React interface written with JavaScript and JSX.

The analyzer does **not** visit, crawl, resolve, or fetch submitted websites. Its output is an informational signal for study and review. It is not a guarantee that a website is safe, and it must not replace browser warnings, endpoint protection, email security controls, or professional security analysis.

> **Scope note:** Phase 1 deliberately favors a small, inspectable baseline over unsupported accuracy, latency, or production-readiness claims. The repository does not currently include a reproducible training pipeline or a bundled trained model.

## Current capabilities

- Extracts 20 deterministic URL and hostname features without making outbound requests.
- Reports one of three verdicts: `legitimate`, `suspicious`, or `phishing`.
- Returns human-readable reasons for the heuristic result.
- Uses the heuristic predictor by default.
- Loads `api/ml-models/phishguard_model.joblib` when a compatible optional model artifact is present; a load or prediction failure falls back to the heuristic path.
- Accepts one URL per scan request, with a 2,048-character serializer limit.
- Stores scan history in MongoDB when MongoDB is configured and persistence succeeds.
- Continues URL analysis when MongoDB is unavailable; history then returns an empty result set.
- Provides a focused React/Vite interface for scanning, viewing explanations, and viewing saved history.

## Architecture

```text
┌──────────────────────────────┐
│ React + Vite + JSX (`web/`)  │
│ Scan form · result · history │
└──────────────┬───────────────┘
               │ JSON over HTTP
               ▼
┌──────────────────────────────┐
│ Django REST API (`api/`)     │
│ serializers · views · routes │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ URL analysis service         │
│ features → predictor → notes │
└──────────────┬───────────────┘
               ├───────────────┐
               ▼               ▼
┌────────────────────┐  ┌─────────────────────┐
│ Optional joblib    │  │ Optional MongoDB    │
│ model artifact     │  │ scan history        │
└────────────────────┘  └─────────────────────┘
```

The analysis path is intentionally independent of webpage content and MongoDB availability. The service extracts features, produces a verdict and reasons, then attempts optional persistence.

## Quick start

### Prerequisites

- Python 3.9 or newer
- Node.js 18 or newer
- npm
- MongoDB for persistent history only

### Recommended: root Makefile

From the repository root:

```bash
make install       # create the API environment and install API/web dependencies
make setup-env     # create api/.env when it does not exist
make dev           # launch API and web in separate Terminal windows on macOS
```

The services use these local addresses:

- API: `http://127.0.0.1:8000`
- Web: `http://localhost:5173`

Useful commands:

```bash
make doctor        # inspect local prerequisites
make check         # run Django system checks
make test          # run the API test suite
make build         # create the Vite production build
make ci            # check, test, and build
make dev-single    # run API and web from one terminal
```

`make dev` uses macOS Terminal tabs/windows. On other platforms, use `make dev-single` or start the API and web manually.

### Manual setup

API:

```bash
cd api
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py runserver 127.0.0.1:8000
```

Web, in a second terminal:

```bash
cd web
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

The web client defaults to `http://localhost:8000/api`. Set `VITE_API_BASE_URL` when the API is hosted elsewhere, for example:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api npm run dev
```

### MongoDB

MongoDB is optional for analysis and required only for saved history. The development defaults use:

- URI: `mongodb://127.0.0.1:27017`
- Database: `phishguard`
- Collection: `scans`

Override `MONGODB_URI` and `MONGODB_DATABASE` in `api/.env` when needed. Connection and socket timeouts are bounded so an unavailable local MongoDB instance does not block the analysis path indefinitely.

## API endpoints

| Method | Endpoint        | Purpose                                                    |
| ------ | --------------- | ---------------------------------------------------------- |
| `GET`  | `/`             | Return service information and endpoint links              |
| `GET`  | `/api/health/`  | Report API availability and the optional database boundary |
| `POST` | `/api/scan/`    | Analyze one URL                                            |
| `GET`  | `/api/history/` | Return recent persisted scans                              |

Example scan request:

```bash
curl -X POST http://127.0.0.1:8000/api/scan/ \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/login"}'
```

See [docs/API_REFERENCE.md](./docs/API_REFERENCE.md) for request validation, response fields, and examples.

## Documentation map

- [Project plan](./docs/project-plan.md) — verified Phase 1 workstreams, completion criteria, and future phases.
- [Project synopsis](./docs/project-synopsis.md) — academic description of the problem, method, scope, and limitations.
- [Architecture](./docs/ARCHITECTURE.md) — module responsibilities and end-to-end data flow.
- [API reference](./docs/API_REFERENCE.md) — HTTP contract and response examples.
- [Development guide](./docs/DEVELOPMENT_GUIDE.md) — setup, configuration, commands, and troubleshooting.
- [Testing guide](./docs/TESTING_GUIDE.md) — current test coverage and verification workflow.
- [Roadmap](./docs/ROADMAP.md) — staged future work without presenting it as implemented functionality.
- [Contributing guide](./docs/CONTRIBUTING.md) — repository conventions and change checklist.

## Project structure

```text
PhishGuard/
├── api/
│   ├── config/                 Django settings and URL configuration
│   ├── data/{raw,processed}/  Local data placeholders; contents are ignored
│   ├── logs/                  Runtime logs; contents are ignored
│   ├── ml-models/             Optional model artifacts; contents are ignored
│   ├── tests/                 API and analysis tests
│   ├── url_analysis/          Feature extraction, prediction, persistence
│   ├── web_api/               REST serializers, views, and routes
│   ├── manage.py
│   └── requirements.txt
├── web/
│   ├── src/components/        Scan, result, and history components
│   ├── src/hooks/             React state hooks
│   ├── src/services/          Fetch-based API client
│   ├── src/App.jsx
│   ├── src/main.jsx
│   └── package.json
├── public/                    Lowercase project branding assets
├── docs/                      Project, architecture, API, and workflow docs
├── LICENSE                    PhishGuard source-available license
├── Makefile                   Root development shortcuts
└── README.md
```

## Verification

Run the repository-level checks from the project root:

```bash
make check
make test
make build
python3 -m compileall -q api
```

`git diff --check` is also recommended before committing. The API test suite currently covers stable feature ordering, representative feature flags, API-root details, verdict values, and confidence bounds. The web project currently provides a Vite production build rather than a separate frontend test suite.

## Limitations and safety boundary

- URL analysis is lexical and hostname-based; it does not inspect HTML, forms, redirects, certificates, DNS, WHOIS data, page reputation, or live network behavior.
- A heuristic verdict is not a threat-intelligence lookup and can produce false positives or false negatives.
- No accuracy, recall, precision, latency, or coverage target is asserted by the current repository.
- The optional model artifact is not included, and the repository does not yet provide the dataset, training script, evaluation report, or artifact metadata needed to make model-quality claims.
- There is no authentication, batch endpoint, browser extension, email scanner, dashboard, or SHAP integration in Phase 1.
- The custom license permits academic and evaluation use but does not grant commercial rights. Third-party dependencies, datasets, and model artifacts may have separate terms.

## Roadmap

1. Add licensed dataset ingestion and a reproducible training/evaluation pipeline.
2. Record model metadata and validate optional artifacts against the 20-feature contract.
3. Improve persistence diagnostics and make configurable limits consistently effective.
4. Consider batch scanning, history filtering, authentication, and richer UI only after the baseline is measured.
5. Evaluate additional explainability methods and model families as research work, not as assumed capabilities.
6. Add deployment, observability, and security hardening only when a concrete target environment exists.

See [docs/ROADMAP.md](./docs/ROADMAP.md) for staged acceptance criteria.

## License

PhishGuard is distributed under the [PhishGuard Source-Available Academic and Evaluation License](./LICENSE). It is not an OSI-approved open-source license and does not grant commercial-use rights.

<div align="center">

Built with ❤️ by Dibakar

</div>
