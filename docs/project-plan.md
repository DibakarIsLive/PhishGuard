# PhishGuard Project Plan

## 1. Document purpose

This plan defines the academic implementation scope, work sequence, and acceptance criteria for PhishGuard. It describes the repository as it exists today and separates verified Phase 1 work from research that is intentionally deferred.

PhishGuard is an academic and research tool for inspecting URL-level phishing signals. It is not a production security gateway, a threat-intelligence service, or a guarantee that a website is safe.

## 2. Problem statement

Phishing URLs often use structural tricks—such as excessive length, deceptive hostnames, suspicious top-level domains, encoded characters, or account-related wording—to make a destination appear trustworthy. A small, inspectable application can help students study these signals through a repeatable API and a user-facing interface.

The Phase 1 problem is deliberately narrow:

> Given one user-submitted URL, extract deterministic lexical and hostname features, produce an interpretable baseline verdict, and optionally save the result for later review without fetching the target website.

This boundary keeps the first implementation understandable and prevents unsupported claims about live crawling, threat intelligence, or model accuracy.

## 3. Phase 1 objectives

### 3.1 Required objectives

- [x] Establish a repository layout with `api/`, `web/`, `public/`, and `docs/`.
- [x] Provide Django 4.2 and Django REST Framework configuration under `api/config/`.
- [x] Provide a single-URL `POST /api/scan/` endpoint.
- [x] Validate one trimmed URL string with a maximum length of 2,048 characters.
- [x] Extract a stable set of 20 URL and hostname features.
- [x] Produce `legitimate`, `suspicious`, or `phishing` verdicts.
- [x] Return human-readable reasons for the baseline prediction.
- [x] Keep the analysis path network-free: submitted websites are not visited or fetched.
- [x] Support an optional compatible `api/ml-models/phishguard_model.joblib` artifact.
- [x] Fall back to the heuristic predictor when the optional model is absent or cannot be used.
- [x] Persist scan records through MongoEngine when MongoDB is available.
- [x] Continue analysis when MongoDB is unavailable.
- [x] Provide a React/Vite frontend using JavaScript and JSX only.
- [x] Provide local development, check, test, and build commands.

### 3.2 Explicit non-goals for Phase 1

The following are not current deliverables:

- A measured accuracy, precision, recall, F1-score, or latency target.
- A bundled trained model or a reproducible training pipeline.
- HTML, DOM, form, certificate, DNS, WHOIS, reputation, or redirect inspection.
- SHAP or other advanced explainability integrations.
- Ensemble learning or a collection of third-party ML frameworks.
- Batch scanning, authentication, dashboards, browser extensions, or email scanning.
- A production security gateway or a guarantee of safe browsing.

## 4. Verified system scope

### 4.1 API layer

The Django application exposes:

- `/` — service information and endpoint links.
- `/api/health/` — API availability and the optional MongoDB boundary.
- `/api/scan/` — analysis of one URL.
- `/api/history/` — recent persisted scans.

The REST layer uses JSON parsing, permissive Phase 1 access, anonymous throttling, and explicit CORS origins for local Vite development. Authentication is intentionally deferred.

### 4.2 Analysis layer

`api/url_analysis/feature_extractor.py` returns these 20 feature keys in a stable order:

1. `url_length`
2. `hostname_length`
3. `dot_count`
4. `hyphen_count`
5. `at_count`
6. `question_count`
7. `equals_count`
8. `slash_count`
9. `digit_ratio`
10. `has_ip_address`
11. `has_https`
12. `has_suspicious_tld`
13. `has_punycode`
14. `subdomain_count`
15. `path_length`
16. `query_length`
17. `entropy`
18. `has_login_keyword`
19. `has_redirect_symbol`
20. `has_encoded_character`

The extractor parses the URL string locally. It does not make DNS, HTTP, TLS, page-content, or third-party service requests.

### 4.3 Predictor layer

The predictor first looks for the optional joblib artifact. When no compatible result is available, it evaluates a transparent weighted heuristic using indicators such as:

- IP-address hostnames.
- Commonly abused top-level domains.
- Login or account keywords.
- The `@` symbol.
- Punycode.
- Encoded characters.
- Unusually long URLs.
- Several subdomains.

The heuristic maps its score to one of three verdicts and returns a bounded confidence value plus reasons. The confidence value is a predictor output, not a validated probability or accuracy measurement.

### 4.4 Persistence layer

The MongoEngine `Scan` document stores:

- Submitted URL.
- Verdict.
- Confidence value.
- Feature dictionary.
- Explanation dictionary.
- UTC creation timestamp.

MongoDB is optional for analysis. If connection or save operations fail, the scan response remains available while the history endpoint returns no persisted results.

### 4.5 Web layer

The React interface provides:

- One URL input form.
- Loading and error states.
- A result card with verdict, displayed confidence, URL, and reasons.
- A recent-history list when MongoDB has saved records.
- A visible notice that analysis does not visit the submitted website.

The frontend uses JavaScript, JSX, React, React DOM, Vite, and the browser Fetch API. TypeScript and TSX are outside the project convention.

## 5. Work breakdown

### Workstream A — Repository and configuration

**Outcome:** A reproducible local project structure.

Tasks:

- Maintain the `api/`, `web/`, `public/`, and `docs/` boundaries.
- Keep environment-specific settings in `api/config/settings/`.
- Keep secrets and local generated data out of version control.
- Keep Python modules and variables in `snake_case`.
- Keep frontend source in JavaScript and JSX.

Acceptance criteria:

- `make doctor` identifies local prerequisites.
- `make setup-env` creates `api/.env` from the example when needed.
- `make check` passes from the repository root.

### Workstream B — URL analysis baseline

**Outcome:** A deterministic, network-free analysis service.

Tasks:

- Maintain stable feature names and order.
- Keep feature extraction free of outbound requests.
- Keep heuristic reasons understandable to a reviewer.
- Preserve the optional model fallback boundary.

Acceptance criteria:

- The feature extractor returns all 20 documented keys.
- Representative HTTPS and IP-host tests pass.
- A valid URL returns a supported verdict and confidence in the inclusive range 0–1.

### Workstream C — REST API

**Outcome:** A small HTTP contract suitable for the Phase 1 web client.

Tasks:

- Validate JSON input through the serializer.
- Map invalid URL structure to a client error.
- Return scan data as JSON.
- Keep health and history endpoints available independently of a live model artifact.

Acceptance criteria:

- The root endpoint identifies `phishguard-api`.
- Health returns HTTP 200.
- A valid scan returns HTTP 200.
- Invalid or missing input is rejected by serializer or service validation.
- History returns `{ "results": [...] }`.

### Workstream D — Optional MongoDB persistence

**Outcome:** Persistence that does not make local analysis fragile.

Tasks:

- Configure MongoEngine through environment variables.
- Bound server-selection, connect, and socket timeouts.
- Suppress repeated connection attempts for the configured retry interval after an unavailable database.
- Keep persistence failures from changing the analysis contract.

Acceptance criteria:

- The API can analyze a URL without MongoDB.
- When MongoDB is reachable, successful scans can appear in history.
- The documentation clearly distinguishes analysis from persistence.

### Workstream E — React interface

**Outcome:** A focused browser workflow for the API contract.

Tasks:

- Submit one trimmed URL.
- Display loading and error states.
- Display the returned verdict and reasons.
- Refresh history after a scan.
- Keep the network-free analysis notice visible.

Acceptance criteria:

- `npm run build` succeeds in `web/`.
- The default API base URL is documented.
- A non-default API URL can be supplied with `VITE_API_BASE_URL`.

### Workstream F — Verification and documentation

**Outcome:** A reviewer can understand, run, and verify the baseline.

Tasks:

- Maintain focused API tests.
- Compile-check Python sources.
- Build the frontend.
- Keep endpoint and feature documentation synchronized with code.
- Record limitations instead of converting future work into present claims.

Acceptance criteria:

```bash
make check
make test
make build
python3 -m compileall -q api
git diff --check
```

## 6. Suggested academic execution sequence

1. Confirm the repository structure and local prerequisites.
2. Create `api/.env` from `.env.example` and review local values.
3. Install API and web dependencies.
4. Run the API checks and focused tests.
5. Start the API and verify `/api/health/`.
6. Start the web client and submit representative URLs.
7. Run with MongoDB stopped to verify analysis independence.
8. Run with MongoDB available to verify history persistence.
9. Add a compatible model artifact only after its feature contract is documented.
10. Run the full verification commands before presenting the project.

## 7. Completion checklist

### Phase 1 implementation

- [x] API and web directories use the current naming convention.
- [x] Lowercase branding assets are used by the current documentation.
- [x] URL analysis is network-free.
- [x] Feature extraction and heuristic prediction are implemented.
- [x] Optional model loading is isolated from the default fallback.
- [x] MongoDB persistence is optional and bounded.
- [x] The web client uses React JavaScript and JSX.
- [x] Local commands and environment variables are documented.

### Evidence to collect for an academic submission

- A short test run showing the current passing suite.
- Screenshots of the scan form, result card, and history state.
- Example requests and responses from the API reference.
- A description of the 20 features and heuristic indicators.
- A limitations section that distinguishes lexical analysis from live website inspection.
- Any future model evaluation report, clearly dated and tied to a reproducible dataset and training command.

## 8. Phase 2 planning boundary

Phase 2 may investigate dataset preparation, reproducible training, model metadata, calibrated evaluation, improved persistence diagnostics, batch workflows, authentication, history filters, and richer explanations. Each item requires implementation, tests, documentation, and evidence before it can be described as a capability.

Additional ML libraries, SHAP, live content inspection, threat-intelligence integrations, and deployment hardening should be introduced only through separately reviewed work. They are not implied by the current Phase 1 codebase.

## 9. Related documents

- [Project synopsis](./project-synopsis.md)
- [Architecture](./ARCHITECTURE.md)
- [API reference](./API_REFERENCE.md)
- [Development guide](./DEVELOPMENT_GUIDE.md)
- [Testing guide](./TESTING_GUIDE.md)
- [Roadmap](./ROADMAP.md)
- [Contributing guide](./CONTRIBUTING.md)
