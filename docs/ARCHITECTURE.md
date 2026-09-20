# PhishGuard Architecture

## Purpose

This document describes the current Phase 1 implementation. It is intentionally narrower than a future production architecture: PhishGuard analyzes one URL string locally, returns an explainable baseline result, and persists that result in MongoDB when the configured database is reachable. Normal backend startup requires a successful bounded MongoDB reachability check.

## System boundary

```text
┌──────────────────────────────────────────────────────────────┐
│ Browser                                                      │
│ React + Vite + JavaScript/JSX (`ui/`)                      │
│ ScanForm · ResultCard · HistoryList                         │
└──────────────────────────────┬───────────────────────────────┘
                               │ JSON over HTTP
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ Django REST API (`api/`)                                    │
│ config/ · web_api/                                          │
│ root · health · capabilities · scan · history              │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ URL analysis (`api/url_analysis/`)                          │
│ scan_service → feature_extractor → predictor                │
│                              └──────────────┬────────────────┘
│                                             ▼
│ MongoEngine persistence                 │
└──────────────────────────────────────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
┌───────────────────────────┐   ┌────────────────────────────┐
│ Optional joblib artifact  │   │ MongoDB database           │
│ ml-models/phishguard_     │   │ collection: `scans`         │
│ model.joblib              │   └────────────────────────────┘
└───────────────────────────┘
```

The analyzer does not fetch the submitted website. No HTTP client, DNS lookup, certificate inspection, HTML parser, or third-party reputation call is part of the current scan path.

## Repository boundaries

```text
PhishGuard/
├── api/
│   ├── config/
│   │   ├── settings/base.py         Shared settings and environment helpers
│   │   ├── settings/development.py  Local defaults
│   │   ├── settings/production.py   Explicit deployment requirements
│   │   └── urls.py                  Root and `/api/` routing
│   ├── url_analysis/
│   │   ├── feature_extractor.py     Versioned 20-feature URL contract
│   │   ├── brand_confusion.py       Small local advisory hostname rules
│   │   ├── predictor.py              Validated optional model + fallback
│   │   ├── scan_service.py           Analysis and best-effort persistence
│   │   ├── url_validation.py          Shared local URL validation
│   │   ├── models.py                 MongoEngine `Scan` document
│   │   └── database.py               Bounded MongoDB diagnostics/setup
│   ├── web_api/
│   │   ├── serializers.py            Request validation
│   │   ├── views.py                  HTTP views
│   │   └── urls.py                   API endpoint routes
│   ├── tests/                        Focused API and feature tests
│   ├── data/                         Local dataset placeholders
│   ├── ml-models/                    Optional local model artifacts
│   ├── logs/                         Runtime logs
│   ├── manage.py
│   └── requirements.txt
├── ui/
│   ├── src/components/              UI components
│   ├── src/hooks/                   Scan state hook
│   ├── src/services/                Fetch API client
│   ├── src/App.jsx                  Main page composition
│   ├── src/main.jsx                 React entry point
│   └── package.json
├── public/                          Lowercase branding assets
├── docs/                            Project and developer documentation
├── LICENSE
└── Makefile
```

## Request lifecycle

### 1. Browser request

`ScanForm.jsx` submits one URL through `scanUrl()` in `ui/src/services/api-client.js`. The client sends JSON to `${VITE_API_BASE_URL}/scan/`. The default base URL is `http://localhost:8000/api`.

### 2. Serializer validation

`ScanView` passes request data to `ScanSerializer`. The serializer requires a character field named `url`, trims surrounding whitespace, applies the configured `MAX_URL_LENGTH`, and uses the shared validator for supported schemes, hostnames, whitespace, backslashes, and ports.

### 3. Service validation and parsing

`analyze_url()` normalizes the value and uses `urllib.parse.urlsplit`. If the input has no scheme, `http://` is used for parsing purposes. A usable network location is required; invalid input produces a client error.

This normalization does not contact the hostname. It only makes parsing consistent for inputs such as `example.com`.

### 4. Feature extraction

`extract_features()` analyzes the raw URL and parsed hostname. It returns a dictionary containing the stable feature contract documented below. The extractor performs no outbound I/O. A separate `brand_confusion.py` check examines a small, explicit local ruleset and does not add a feature to this model vector.

### 5. Prediction

`predict()` checks for `api/ml-models/phishguard_model.joblib`. Before using it, the predictor validates the feature count/order when metadata is exposed, the prediction shape and label, and the confidence range. If any compatibility check fails, the predictor logs a warning and evaluates the transparent heuristic rules instead.

When the URL is available, the predictor also receives an advisory result from the small local brand-confusion ruleset. This signal can add a human-readable reason and heuristic weight, but it is separate from the 20-feature vector and does not override a compatible model's label. It covers only explicitly configured brands and simple ASCII look-alike patterns; it is not a complete typosquatting, ownership, reputation, or threat-intelligence service.

### 6. Response construction

The service returns:

- `url`
- `verdict`
- `confidence`
- `features`
- `explanations.reasons`
- `explanations.analyzer_version`
- `explanations.network_accessed` (`false`)
- `explanations.brand_rules_version`
- `explanations.brand_confusion` (`null` or an advisory local-rule object)

When MongoDB persistence succeeds, it also returns `id` and `created_at`.

### 7. Startup gate and persistence

Before normal `runserver` startup, `manage.py` performs a bounded MongoDB reachability check against the configured server and refuses to start when the check fails. The explicit `--force` flag is a diagnostic bypass; the API Makefile exposes the equivalent `FORCE=1` setting.

After startup, the service attempts bounded MongoDB persistence. A successful scan is saved as a `Scan` document. Connection failure or save failure—especially during a forced diagnostic session—does not invalidate the lexical analysis result, and the history endpoint returns recent saved records only when they are available.

## Feature contract

The current extractor returns exactly these keys:

| Key | Meaning |
| --- | --- |
| `url_length` | Length of the trimmed URL string |
| `hostname_length` | Length of the parsed hostname |
| `dot_count` | Number of `.` characters in the raw URL |
| `hyphen_count` | Number of `-` characters in the raw URL |
| `at_count` | Number of `@` characters |
| `question_count` | Number of `?` characters |
| `equals_count` | Number of `=` characters |
| `slash_count` | Number of `/` characters |
| `digit_ratio` | Digits divided by URL length |
| `has_ip_address` | Whether the hostname matches an IPv4-shaped pattern |
| `has_https` | Whether the parsed scheme is HTTPS |
| `has_suspicious_tld` | Whether the hostname ends with a configured suspicious TLD |
| `has_punycode` | Whether the hostname contains `xn--` |
| `subdomain_count` | Parsed hostname dot count minus one, bounded at zero |
| `path_length` | Length of the parsed path |
| `query_length` | Length of the parsed query |
| `entropy` | Rounded character entropy of the raw URL |
| `has_login_keyword` | Whether account-related keywords appear in the raw URL |
| `has_redirect_symbol` | Whether the path contains `//` or the URL contains `@` |
| `has_encoded_character` | Whether `%` appears in the raw URL |

The feature order is held in `FEATURE_NAMES` and is relevant to optional model artifacts. Changing a feature name or order is a compatibility change.

## Predictor boundary

The heuristic currently assigns weighted indicators to:

- IPv4-shaped hostnames.
- Configured suspicious TLD endings.
- Login, verify, account, secure, update, signin, or password keywords.
- `@` symbols.
- Punycode.
- Percent-encoded characters.
- URLs longer than 100 characters.
- More than two subdomains.
- A configured brand-like hostname pattern outside its configured official domains.

The result categories are:

| Verdict | Meaning in the UI |
| --- | --- |
| `phishing` | High risk |
| `suspicious` | Needs review |
| `legitimate` | No obvious structural red flags |

These labels are preliminary signals. They do not establish that a website is malicious or safe.

## Persistence model

The MongoEngine `Scan` document uses the `scans` collection and newest-first ordering. Its fields are:

| Field | Type | Purpose |
| --- | --- | --- |
| `url` | string | Submitted URL |
| `verdict` | string | One supported verdict |
| `confidence` | float | Predictor output used in the response |
| `features` | dictionary | Extracted feature values |
| `explanations` | dictionary | Human-readable reasons |
| `created_at` | datetime | UTC creation timestamp |

MongoDB is required for normal backend startup in Phase 1. The Django relational database is deliberately configured as a dummy backend; history is handled through MongoEngine. Forced diagnostic startup can proceed without MongoDB, but persistence remains best-effort.

## Configuration modes

- `DJANGO_ENV=development` selects local settings and allows the documented local hosts/origins.
- `DJANGO_ENV=production` requires an explicit `SECRET_KEY`, `ALLOWED_HOSTS`, and `CORS_ALLOWED_ORIGINS`, and enables HTTPS-oriented settings.
- `MONGODB_*` values configure the startup reachability check, MongoEngine history persistence, and bounded timeouts.
- `VITE_API_BASE_URL` points the UI client at the API.

See [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) for setup and [API_REFERENCE.md](./API_REFERENCE.md) for the HTTP contract.

## Design decisions

1. **Network-free analysis:** A scan must not load the submitted destination as a side effect of analysis.
2. **Explicit startup dependency:** Normal backend startup requires MongoDB; `--force` is reserved for intentional diagnostics.
3. **Best-effort persistence:** After startup, a failed MongoDB save must not make the lexical analysis result unusable.
4. **Stable feature interface:** Feature names, order, and version are explicit because optional model artifacts depend on them.
5. **Visible capability boundary:** Health and capabilities responses describe the current implementation without pretending deferred features exist.
6. **Small HTTP surface:** Phase 1 exposes only scan/history plus diagnostics needed for coordination.
7. **Explicit uncertainty:** Confidence is displayed as an application output, not presented as a validated probability.
8. **JavaScript and JSX:** The UI layer follows the repository convention and does not introduce TypeScript or TSX.

## Related documents

- [Project plan](./project-plan.md)
- [Project synopsis](./project-synopsis.md)
- [API reference](./API_REFERENCE.md)
- [Development guide](./DEVELOPMENT_GUIDE.md)
- [Testing guide](./TESTING_GUIDE.md)
- [Roadmap](./ROADMAP.md)
- [Contributing guide](./CONTRIBUTING.md)
