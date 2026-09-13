# PhishGuard API Reference

## Base URLs

Local development uses:

- API root: `http://127.0.0.1:8000`
- API namespace: `http://127.0.0.1:8000/api`

The web client calls the API namespace. Set `VITE_API_BASE_URL` when the API is hosted elsewhere.

## Response conventions

- Responses use JSON.
- The API currently allows unauthenticated access as a Phase 1 boundary.
- Anonymous requests are throttled using `API_ANON_RATE`, which defaults to `60/min`.
- A scan analyzes the submitted URL string locally; it does not visit the destination.
- History is optional and depends on MongoDB persistence.

## `GET /`

Returns service metadata and the primary endpoint links.

Example:

```bash
curl http://127.0.0.1:8000/
```

Example response:

```json
{
  "service": "phishguard-api",
  "status": "ok",
  "message": "The PhishGuard API is running.",
  "frontend": "http://127.0.0.1:5173/",
  "endpoints": {
    "health": "/api/health/",
    "scan": "/api/scan/",
    "history": "/api/history/"
  }
}
```

## `GET /api/health/`

Reports that the API is available and identifies MongoDB as an optional dependency.

```bash
curl http://127.0.0.1:8000/api/health/
```

Example response:

```json
{
  "status": "ok",
  "service": "phishguard-api",
  "database": "optional MongoDB"
}
```

A successful health response does not mean that MongoDB is connected or that a model artifact is present.

## `POST /api/scan/`

Analyzes one URL and returns the baseline result.

### Request

Header:

```text
Content-Type: application/json
```

Body:

```json
{
  "url": "https://example.com/login"
}
```

Rules:

- `url` is required.
- It must be a string.
- Surrounding whitespace is trimmed.
- The serializer accepts at most 2,048 characters.
- A usable domain/network location is required by the analysis service.
- A scheme is not required in the input; values such as `example.com` are parsed as `http://example.com` for analysis.
- The target website is not requested, crawled, or resolved.

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/scan/ \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/login"}'
```

Example response without successful MongoDB persistence:

```json
{
  "url": "https://example.com/login",
  "verdict": "legitimate",
  "confidence": 0.92,
  "features": {
    "url_length": 24,
    "hostname_length": 11,
    "dot_count": 1,
    "hyphen_count": 0,
    "at_count": 0,
    "question_count": 0,
    "equals_count": 0,
    "slash_count": 3,
    "digit_ratio": 0.0,
    "has_ip_address": 0,
    "has_https": 1,
    "has_suspicious_tld": 0,
    "has_punycode": 0,
    "subdomain_count": 0,
    "path_length": 6,
    "query_length": 0,
    "entropy": 3.93,
    "has_login_keyword": 1,
    "has_redirect_symbol": 0,
    "has_encoded_character": 0
  },
  "explanations": {
    "reasons": [
      "No strong phishing indicators were found"
    ]
  }
}
```

The numerical feature values and heuristic result depend on the exact submitted URL. The example is illustrative; it is not an evaluation claim.

When persistence succeeds, the response may also contain:

```json
{
  "id": "665f2f1a2d4e9e4f12345678",
  "created_at": "2026-01-01T12:00:00+00:00"
}
```

### Verdicts

| Value | UI interpretation | Meaning |
| --- | --- | --- |
| `phishing` | High risk | Strong baseline indicators were present, or an optional model returned a positive label |
| `suspicious` | Needs review | Some baseline indicators were present |
| `legitimate` | Likely safe | No strong baseline indicators were found, or an optional model returned a negative label |

The verdict is an informational classifier output. It is not a safety guarantee, a block decision, or a threat-intelligence verdict.

### Explanation shape

The current response uses:

```json
{
  "explanations": {
    "reasons": ["...", "..."]
  }
}
```

The heuristic reasons can refer to the following signals:

- IP-address hostname.
- Commonly abused top-level domain.
- Account or login keyword.
- `@` symbol that can obscure a destination.
- Punycode.
- Encoded characters.
- Unusually long URL.
- Several subdomains.

When the optional model path is used, the current implementation returns `Optional trained model prediction` rather than feature-level model attribution.

### Error responses

Serializer validation errors return HTTP `400` with field details. For example, an overlong or missing field may return a structure similar to:

```json
{
  "url": [
    "This field is required."
  ]
}
```

Service-level URL validation returns HTTP `400`:

```json
{
  "detail": "Enter a valid URL with a domain name."
}
```

The exact serializer wording is supplied by Django REST Framework and may vary with dependency versions.

## `GET /api/history/`

Returns recent persisted scans. The service requests up to 20 records by default and orders MongoEngine records newest first.

```bash
curl http://127.0.0.1:8000/api/history/
```

Example with records:

```json
{
  "results": [
    {
      "id": "665f2f1a2d4e9e4f12345678",
      "url": "https://example.com/login",
      "verdict": "legitimate",
      "confidence": 0.92,
      "created_at": "2026-01-01T12:00:00+00:00"
    }
  ]
}
```

If MongoDB is unavailable or no records have been saved:

```json
{
  "results": []
}
```

The history response intentionally omits the stored feature and explanation dictionaries in the current Phase 1 endpoint.

## Feature contract

The scan response includes the 20 keys listed in [ARCHITECTURE.md](./ARCHITECTURE.md). Optional model artifacts must consume the same order defined by `FEATURE_NAMES` in `api/url_analysis/feature_extractor.py`.

## Limits and environment variables

| Variable | Default | Effect |
| --- | --- | --- |
| `MAX_URL_LENGTH` | `2048` | Shared documented URL limit; serializer currently enforces 2,048 directly |
| `MAX_BATCH_SIZE` | `25` | Reserved configuration; no batch endpoint exists in Phase 1 |
| `HISTORY_LIMIT` | `20` | Configuration for intended history sizing; current service default is 20 |
| `API_ANON_RATE` | `60/min` | Anonymous request throttle |
| `MONGODB_SERVER_SELECTION_TIMEOUT_MS` | `1000` | MongoDB server selection timeout |
| `MONGODB_CONNECT_TIMEOUT_MS` | `1000` | MongoDB connection timeout |
| `MONGODB_SOCKET_TIMEOUT_MS` | `1000` | MongoDB socket timeout |
| `MONGODB_RETRY_INTERVAL_SECONDS` | `30` | Delay before retrying an unavailable connection |

`MAX_BATCH_SIZE` does not imply batch support. It is retained as configuration for future work and must not be documented as an available endpoint.

## Current API non-goals

The API does not currently provide:

- Batch URL submission.
- Authentication or user accounts.
- URL reputation lookups.
- HTML or browser inspection.
- Certificate, DNS, WHOIS, or redirect analysis.
- SHAP attribution or feature-contribution percentages.
- A documented performance or accuracy guarantee.
