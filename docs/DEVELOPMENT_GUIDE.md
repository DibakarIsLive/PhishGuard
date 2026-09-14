# PhishGuard Development Guide

## Development principles

- Keep Phase 1 behavior aligned with the code and tests.
- Treat the analyzer as a network-free academic tool.
- Treat MongoDB as required for normal backend development startup; use the explicit force bypass only for diagnostics.
- Use Python `snake_case` for Python modules, functions, and variables.
- Keep the frontend in React, JavaScript, and JSX; do not introduce TypeScript or TSX.
- Do not commit secrets, local environments, generated builds, logs, datasets, or model artifacts.
- Document future work as future work until it is implemented and verified.

## Prerequisites

- Python 3.9 or newer.
- Node.js 18 or newer.
- npm.
- Git.
- MongoDB running and reachable for normal backend development-server startup.

The URL scan computation remains network-free, but `manage.py runserver` performs a bounded MongoDB reachability check before starting. Use `python3 manage.py runserver --force` or `make dev FORCE=1` only when intentionally running diagnostics without MongoDB.

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

The root target opens the API and web development servers in separate Terminal sessions. The web target automatically opens its configured Vite URL in the default browser; the API target does not open a browser tab.

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

Normal API startup requires reachable MongoDB. To intentionally run a diagnostic session without MongoDB, use `python3 manage.py runserver --force` or `make dev FORCE=1`.

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
| `MONGODB_URI` | `mongodb://127.0.0.1:27017` | MongoDB server URI used by the startup check and persistence |
| `MONGODB_DATABASE` | `phishguard` | MongoDB database used for scan history |
| `API_ANON_RATE` | `60/min` | Anonymous API throttle |
| `MAX_URL_LENGTH` | `2048` | Maximum URL length enforced by request validation and the analysis service |
| `MAX_BATCH_SIZE` | `25` | Reserved for future batch work; no batch route exists |
| `HISTORY_LIMIT` | `20` | Maximum number of records returned by the history service |
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

For a different local API address, use the web Makefile; it still opens the configured frontend URL automatically:

```bash
cd web
VITE_API_BASE_URL=http://127.0.0.1:8000/api make dev
```

Set `PORT` to change the Vite port and the URL opened by `make dev`, for example `make dev PORT=5174`. The client calls `/scan/`, `/history/`, and `/health/` relative to the API base URL.

## Command reference

### Root commands

| Command | Purpose |
| --- | --- |
| `make install` | Install API and web dependencies |
| `make setup-env` | Create `api/.env` from the template when absent |
| `make dev` | Start API and web in separate macOS Terminal sessions; the web target opens the frontend URL |
| `make dev-single` | Start both services in one terminal; the web target opens the frontend URL |
| `make api-only` | Start only the API; no browser tab is opened |
| `make web-only` | Start only the web client and open its configured frontend URL |
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
# If MongoDB is intentionally unavailable for diagnostics:
make dev FORCE=1
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

## MongoDB startup and history

Start a local MongoDB instance and keep the development values in `api/.env`, or point `MONGODB_URI` and `MONGODB_DATABASE` to an authorized instance. Normal `manage.py runserver` startup performs a bounded reachability check and exits with an error when MongoDB cannot be reached.

The explicit diagnostic bypasses are:

```bash
cd api
python3 manage.py runserver --force
make dev FORCE=1
```

A forced session may still perform best-effort persistence: successful scans can be saved when MongoDB becomes reachable, while a failed save does not invalidate the lexical analysis result and history may be empty. MongoDB is not used for Django migrations; Django is configured with a dummy relational database backend.

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

### The backend refuses to start because MongoDB is unavailable

This is expected for normal startup. Start the MongoDB server configured by `MONGODB_URI`, verify the bounded timeout settings in `api/.env`, and retry. Use `python3 manage.py runserver --force` or `make dev FORCE=1` only for an intentional diagnostic session; the bypass is explicit and MongoDB persistence remains best-effort.

### Scan input is rejected

Ensure the request contains one JSON string field named `url`, is no longer than the configured `MAX_URL_LENGTH` (2,048 characters by default), and contains a usable domain. The service does not need a scheme, but it does need a parseable network location. Internal whitespace, backslashes, unsupported schemes, invalid ports, and missing hostnames are rejected.

### The result is unexpected

The current baseline evaluates URL and hostname structure and applies a small local brand-confusion ruleset for selected look-alike labels. It does not know whether a page is live, whether a domain is registered, or whether a URL appears in a reputation database. Review the returned features, advisory metadata, and reasons, then treat the verdict as a preliminary signal; a brand match is not proof of phishing or domain ownership.

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
