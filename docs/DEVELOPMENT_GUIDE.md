# PhishGuard Development Guide

## Development principles

- Keep Phase 1 behavior aligned with the code and tests.
- Treat the analyzer as a network-free academic tool.
- Keep MongoDB optional for URL analysis.
- Use Python `snake_case` for Python modules, functions, and variables.
- Keep the frontend in React, JavaScript, and JSX; do not introduce TypeScript or TSX.
- Do not commit secrets, local environments, generated builds, logs, datasets, or model artifacts.
- Document future work as future work until it is implemented and verified.

## Prerequisites

- Python 3.9 or newer.
- Node.js 18 or newer.
- npm.
- Git.
- MongoDB only when saved scan history is required.

MongoDB is not required to run the local URL analysis path.

## Initial setup

From the repository root:

```bash
make install
make setup-env
```

The API install target creates `api/.venv`, installs `api/requirements.txt`, and creates `api/.env` from `api/.env.example` when it does not already exist. The web install target runs `npm install` in `web/`.

Inspect the local setup:

```bash
make doctor
make -C api doctor
make -C web doctor
```

## Start the application

### macOS

```bash
make dev
```

The root target opens the API and web development servers in separate Terminal sessions.

### One terminal or non-macOS

```bash
make dev-single
```

Or start each service manually.

API:

```bash
cd api
make dev
```

Web:

```bash
cd web
make dev
```

Local addresses:

- API root: `http://127.0.0.1:8000/`
- API namespace: `http://127.0.0.1:8000/api/`
- Web client: `http://localhost:5173/`

## Environment configuration

Copy the template manually when needed:

```bash
cp api/.env.example api/.env
```

### Common variables

| Variable | Development default | Description |
| --- | --- | --- |
| `DJANGO_ENV` | `development` | Selects development or production settings |
| `SECRET_KEY` | Development placeholder | Django signing key; replace outside local development |
| `DEBUG` | `True` in the template | Enables Django debug behavior in development |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma-separated allowed hostnames |
| `CORS_ALLOWED_ORIGINS` | Local Vite origins | Comma-separated browser origins allowed to call the API |
| `CORS_ALLOW_CREDENTIALS` | `False` | Credentialed cross-origin request setting |
| `MONGODB_URI` | `mongodb://127.0.0.1:27017` | Optional MongoDB server URI |
| `MONGODB_DATABASE` | `phishguard` | Optional history database |
| `API_ANON_RATE` | `60/min` | Anonymous API throttle |
| `MAX_URL_LENGTH` | `2048` | Documented URL length setting |
| `MAX_BATCH_SIZE` | `25` | Reserved for future batch work; no batch route exists |
| `HISTORY_LIMIT` | `20` | Intended recent-history limit |
| `LOG_LEVEL` | `DEBUG` in the template | Console and file logging level |

MongoDB timeout variables are also available in `.env.example`. Keep them bounded for local development so a stopped database does not cause long waits.

### Production settings boundary

Set `DJANGO_ENV=production` only when the deployment environment provides:

- A non-placeholder `SECRET_KEY`.
- At least one explicit `ALLOWED_HOSTS` value.
- At least one explicit `CORS_ALLOWED_ORIGINS` value.
- A TLS-terminating deployment path appropriate for the configured secure-cookie and redirect settings.

The production settings file is configuration hardening, not evidence that the application is production-ready as a security product.

## Frontend API configuration

The web client reads:

```text
VITE_API_BASE_URL
```

When omitted, it uses:

```text
http://localhost:8000/api
```

For a different local API address:

```bash
cd web
VITE_API_BASE_URL=http://127.0.0.1:8000/api npm run dev -- --host 127.0.0.1 --port 5173
```

The client calls `/scan/`, `/history/`, and `/health/` relative to that base URL.

## Command reference

### Root commands

| Command | Purpose |
| --- | --- |
| `make install` | Install API and web dependencies |
| `make setup-env` | Create `api/.env` from the template when absent |
| `make dev` | Start API and web in separate macOS Terminal sessions |
| `make dev-single` | Start both services in one terminal |
| `make api-only` | Start only the API |
| `make web-only` | Start only the web client |
| `make doctor` | Inspect Python, Node, npm, MongoDB, and environment status |
| `make health` | Call the web Makefile health target, which checks the API |
| `make status` | Show API and web status |
| `make check` | Run Django checks |
| `make test` | Run the API test suite |
| `make build` | Build the Vite frontend |
| `make ci` | Run checks, tests, and the frontend build |
| `make clean-cache` | Remove generated caches |
| `make clean` | Remove local dependencies and generated files; inspect the target before use |

### API commands

Run from `api/`:

```bash
make install
make setup-env
make dev
make check
make test
make test-features
make test-api
make compile
make ping
make doctor
make status
```

The API Makefile uses `api/.venv/bin/python` after the virtual environment exists.

### Web commands

Run from `web/`:

```bash
make install
make dev
make build
make preview
make test-api
make health
make doctor
make bundle-size
```

The web package currently has `dev`, `build`, and `preview` npm scripts. It does not currently include a frontend unit-test or lint script.

## MongoDB history

To enable saved history, start a local MongoDB instance and keep the development values in `api/.env`, or point `MONGODB_URI` and `MONGODB_DATABASE` to an authorized instance.

The application:

1. Attempts a bounded MongoDB connection when a scan or history request needs it.
2. Saves successful scans to the `scans` collection.
3. Returns `id` and `created_at` when a scan is saved.
4. Continues returning scan results when MongoDB is unavailable.
5. Returns an empty history result when it cannot read MongoDB.

MongoDB is not used for Django migrations; Django is configured with a dummy relational database backend.

## Optional model artifact

The predictor looks for:

```text
api/ml-models/phishguard_model.joblib
```

The artifact must be compatible with the 20-feature order in `FEATURE_NAMES`. If it is missing or fails to load/predict, the application logs the issue and uses the heuristic fallback.

Do not commit a model artifact until its provenance, license, feature version, training process, and evaluation evidence are documented. Model files are ignored by the repository configuration.

## Troubleshooting

### The web page cannot reach the API

1. Confirm the API is running at `http://127.0.0.1:8000`.
2. Run `make health` or `make -C web test-api`.
3. Check `VITE_API_BASE_URL` and ensure it ends with `/api`.
4. Confirm the web origin is listed in `CORS_ALLOWED_ORIGINS`.
5. Restart Vite after changing a `VITE_` environment variable.

### MongoDB warnings appear

This is expected when MongoDB is not running. URL analysis should still complete. Start MongoDB only when history persistence is needed, or inspect the bounded timeout and retry settings in `api/.env`.

### Scan input is rejected

Ensure the request contains one JSON string field named `url`, is no longer than 2,048 characters, and contains a usable domain. The service does not need a scheme, but it does need a parseable network location.

### The result is unexpected

The current baseline only evaluates URL and hostname structure. It does not know whether a page is live, whether a domain is registered, or whether a URL appears in a reputation database. Review the returned features and reasons, then treat the verdict as a preliminary signal.

### The optional model is not used

Check that the artifact exists at the exact path, can be loaded by the installed `joblib` version, accepts the documented feature order, and exposes the required prediction method. The heuristic fallback is intentional.

## Change workflow

Before opening a pull request or sharing a milestone:

```bash
make check
make test
make build
python3 -m compileall -q api
git diff --check
```

Then review:

- `git status --short` for accidental generated files.
- Documentation links and paths.
- API response examples against current behavior.
- Any changed feature names or order.
- Whether a new claim is backed by implementation and evidence.
