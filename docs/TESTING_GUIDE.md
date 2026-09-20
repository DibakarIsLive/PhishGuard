# PhishGuard Testing Guide

## Verification philosophy

PhishGuard is a Phase 1 academic baseline. Tests should verify deterministic behavior, API boundaries, and the network-free scope. They should not imply model quality that has not been measured with a reproducible dataset.

## Current automated tests

The API test suite is located in `api/tests/` and runs with pytest. Startup-gate tests also verify that normal `runserver` refuses an unavailable MongoDB and that `--force` removes only PhishGuard's guard argument before Django parses the command.

### Feature extractor tests

`api/tests/test_feature_extractor.py` verifies representative behavior including:

- Stable feature ordering through `FEATURE_NAMES`.
- Expected HTTPS detection.
- Expected IP-address-host detection.

The extractor currently returns 20 feature keys. Any feature-contract change should update the implementation, tests, optional-model documentation, and architecture reference together.

### Scan service and API tests

`api/tests/test_scan_service.py` verifies representative service behavior including:

- API root metadata.
- Supported verdict values.
- Confidence values bounded between 0 and 1.

The tests intentionally do not claim accuracy, recall, precision, F1-score, or latency.

## Run the tests

From the repository root:

```bash
make test
```

Focused targets:

```bash
make test-features
make test-api
```

Equivalent commands from `api/`:

```bash
make test
make test-features
make test-api
```

The API Makefile runs the suite with the project virtual environment:

```bash
.venv/bin/python -m pytest -q
```

## Full verification

Run all current checks before a documentation or implementation milestone:

```bash
make check
make test
make build
python3 -m compileall -q api
git diff --check
```

What each command covers:

| Command | Coverage |
| --- | --- |
| `make check` | Django configuration and system checks |
| `make test` | API pytest suite |
| `make build` | React/Vite production compilation |
| `python3 -m compileall -q api` | Python syntax compilation |
| `git diff --check` | Whitespace errors in changed text files |

## Manual endpoint smoke tests

Start the API first:

```bash
make api-only
```

In another terminal:

```bash
curl --fail --silent http://127.0.0.1:8000/ | python3 -m json.tool
curl --fail --silent http://127.0.0.1:8000/api/health/ | python3 -m json.tool
curl --fail --silent http://127.0.0.1:8000/api/history/ | python3 -m json.tool
curl --fail --silent -X POST http://127.0.0.1:8000/api/scan/ \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/login"}' | python3 -m json.tool
```

The scan request should return HTTP 200 for a valid URL when the API was started normally with MongoDB reachable or intentionally with the diagnostic force bypass. The history result may be empty during a forced session when MongoDB persistence is unavailable.

Test validation behavior:

```bash
curl --silent --show-error -i -X POST http://127.0.0.1:8000/api/scan/ \
  -H 'Content-Type: application/json' \
  -d '{}'
```

This should return a client-side validation error rather than a successful analysis.

## MongoDB startup-gate and network-free scope checks

The scan computation uses URL parsing and local feature extraction only, while backend startup separately checks MongoDB reachability. A useful review procedure is:

1. Stop MongoDB.
2. Start the API normally and confirm it exits with the MongoDB-required startup error.
3. Start the API with `python3 manage.py runserver --force` or `make dev FORCE=1`.
4. Submit a harmless, valid synthetic URL and confirm the lexical scan response can still return.
5. Confirm that history may return an empty result during the forced session.
6. Start MongoDB and verify that normal startup succeeds and successful scans can appear in history.
7. Review the code path to ensure the analyzer adds no HTTP, DNS, TLS, or browser fetch for the submitted URL.

Do not use a live malicious destination as a test target. A syntactically representative string is sufficient for the current analyzer.

## Persistence checks

When MongoDB is available:

1. Start MongoDB in an authorized local or test environment.
2. Run a valid scan.
3. Confirm the response includes `id` and `created_at`.
4. Call `/api/history/`.
5. Confirm the saved URL, verdict, confidence, and timestamp appear.

Persistence is best-effort after startup. A failed save should not be treated as a failed lexical analysis response, particularly during an explicit forced diagnostic session.

## UI checks

The current UI has no separate unit-test script. Use the build and manual workflow:

```bash
cd ui
npm install
npm run build
make dev
```

`make dev` passes the configured port to Vite and opens `http://localhost:5173/` automatically by default. Use `make dev PORT=5174` to test an override; the backend URL is never opened automatically.

Review:

- The scan form accepts one URL.
- The interface states that the website is not visited.
- Loading and error states are understandable.
- The result card displays verdict, confidence, URL, and reasons.
- History displays saved records or the no-persisted-records/MongoDB-unavailable message during a forced diagnostic session.
- The browser can call the API from the configured CORS origin.

## Test data guidance

Use harmless, synthetic, or authorized examples. The current tests can exercise structural signals such as:

- `https://example.com/login`
- `http://192.0.2.10/verify`
- A URL containing an `@` symbol in a controlled string.

The documentation address block `192.0.2.0/24` is reserved for examples, but no external request should be made to any test URL.

Avoid putting real credentials, private tokens, personal data, or unapproved malicious URLs into test fixtures, logs, screenshots, or MongoDB history.

## Adding tests

When changing the API or analyzer:

1. Add a focused test near the affected behavior.
2. Prefer deterministic inputs and exact boundary assertions.
3. Keep unit tests independent of a live MongoDB service; test the startup reachability gate and persistence behavior with bounded mocks or controlled integration fixtures.
4. Keep external network calls out of unit tests.
5. Update API examples and documentation when the response contract changes.
6. Run the full verification sequence.

For a feature-contract change, update at minimum:

- `api/url_analysis/feature_extractor.py`.
- `api/tests/test_feature_extractor.py`.
- `api/url_analysis/predictor.py` if the predictor consumes the feature.
- `docs/ARCHITECTURE.md`.
- `docs/API_REFERENCE.md`.
- Optional model metadata and evaluation notes, if an artifact is involved.

## Future testing scope

Future phases may add integration tests with a controlled MongoDB service, UI component tests, model evaluation tests, property-based URL inputs, load tests, and security tests. Those should be introduced with explicit fixtures, boundaries, and evidence rather than implied by the current baseline suite.
