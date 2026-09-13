# PhishGuard Project Synopsis

## Title

**PhishGuard: An Explainable, Network-Free Baseline for Phishing URL Analysis**

## Abstract

Phishing remains a practical cybersecurity problem because malicious links can imitate trusted services while using small structural changes to redirect or deceive users. PhishGuard is an academic and research-oriented full-stack application that studies this problem at the URL level. Its current Phase 1 implementation accepts one URL, extracts a stable set of 20 lexical and hostname features locally, produces an interpretable baseline verdict, and records the result in MongoDB when the configured database is reachable. Normal backend startup validates MongoDB reachability first. A Django REST API exposes the analysis service and a React interface provides the user workflow.

The application deliberately does not visit or crawl submitted websites. It therefore demonstrates a safe and inspectable baseline rather than complete website classification. The current predictor is heuristic by default, with an optional compatible `joblib` model artifact boundary. No accuracy or production-security claim is made without a reproducible dataset, training process, evaluation report, and operational evidence.

**Keywords:** phishing URLs, cybersecurity education, lexical features, hostname analysis, explainable baseline, Django REST Framework, React, MongoDB.

## 1. Introduction

Phishing attacks commonly depend on social engineering and deceptive destinations. A link may use a misleading hostname, an IP address, unusual punctuation, encoded characters, an abused top-level domain, or account-related wording. These properties can be studied without loading the target website.

PhishGuard provides a small system in which those signals are visible from input to output. The project is intended for academic exploration of feature engineering, API design, frontend integration, best-effort persistence, and responsible documentation. It should be read as a baseline research application, not as a replacement for browser security controls or professional incident analysis.

## 2. Problem definition

The Phase 1 research problem is:

> How can a compact, network-free service extract transparent URL and hostname signals and return a useful preliminary phishing-oriented verdict for one submitted URL?

The project does not attempt to answer whether a live website is safe in every context. It does not inspect page content, follow redirects, validate certificates, query reputation providers, or infer the intent of a website from behavior that is unavailable in the URL string.

## 3. Aim and objectives

### 3.1 Aim

To implement and document a reproducible baseline workflow for URL-level phishing analysis that is understandable to students and easy to verify locally.

### 3.2 Objectives

1. Build a Django REST API for one-URL analysis.
2. Validate and normalize the submitted URL input.
3. Extract 20 deterministic lexical and hostname features.
4. Produce one of three baseline verdicts: `legitimate`, `suspicious`, or `phishing`.
5. Return human-readable explanation reasons alongside the verdict.
6. Keep the analysis path independent of live website access.
7. Require MongoDB for normal backend startup and provide an explicit force bypass for diagnostics.
8. Provide MongoDB history through MongoEngine with best-effort persistence after startup.
9. Provide a React/Vite frontend using JavaScript and JSX, with automatic browser opening for the configured Vite URL during `make dev`.
10. Add focused tests and local commands for verification.
11. Document limitations and future research without presenting them as implemented capabilities.

## 4. Scope

### 4.1 Included in Phase 1

- URL string validation through the DRF serializer.
- Maximum submitted URL length of 2,048 characters.
- Local parsing of URL and hostname components.
- Stable extraction of 20 features.
- Transparent heuristic prediction.
- Optional loading of a compatible `api/ml-models/phishguard_model.joblib` artifact.
- JSON endpoints for root information, health, scanning, and history.
- MongoDB-backed persistence for saved scans, with a required normal-startup reachability check and an explicit diagnostic bypass.
- React components for input, results, errors, and recent history.
- Development and production-oriented Django settings separation.
- Documentation, tests, Python compilation, and frontend build verification.

### 4.2 Excluded from Phase 1

- Live HTTP requests or website crawling.
- HTML, DOM, form, JavaScript, redirect, certificate, DNS, WHOIS, or reputation analysis.
- Claimed accuracy, recall, precision, F1-score, or latency targets.
- A bundled model, dataset, training command, or evaluation report.
- SHAP, ensemble voting, or multiple advanced model frameworks.
- Batch scanning, authentication, user accounts, dashboards, browser extensions, and email integrations.
- Production deployment as a security gateway.

## 5. Methodology

### 5.1 Input validation

The API accepts a JSON object containing one `url` string. The serializer trims surrounding whitespace and rejects empty or overlong values. The service then parses the value and requires a usable URL structure before analysis.

### 5.2 Feature extraction

The feature extractor evaluates the input string and its parsed hostname without contacting external services. The current feature contract contains:

- URL, hostname, path, and query lengths.
- Counts of dots, hyphens, `@`, question marks, equals signs, and slashes.
- Ratio of digits to URL characters.
- IP-address-host detection.
- HTTPS detection.
- Suspicious top-level-domain detection.
- Punycode detection.
- Subdomain count.
- Character entropy.
- Login-keyword detection.
- Redirect-symbol detection.
- Encoded-character detection.

The order and names of these features are treated as an interface because an optional model artifact may depend on them.

### 5.3 Prediction

The predictor has two paths:

1. **Optional model path:** If a compatible joblib artifact exists and can produce a valid result, the predictor may use it.
2. **Heuristic path:** Otherwise, transparent indicators contribute to a bounded score that maps to `legitimate`, `suspicious`, or `phishing`.

The fallback reasons are returned in plain language so that a reviewer can connect the verdict to observable URL properties. Confidence is an application output used for presentation; it is not evidence of validated statistical calibration.

### 5.4 Persistence

After startup validation, the service can save a `Scan` document through MongoEngine. The document contains the URL, verdict, confidence, feature dictionary, explanation dictionary, and UTC creation time. Normal startup requires reachable MongoDB; `--force` (or `FORCE=1` through the API Makefile) is an explicit diagnostic bypass. In a forced session, a database failure leaves the lexical analysis response useful and the history collection may be empty.

### 5.5 User interface

The React/Vite frontend submits one URL to the API and displays the returned verdict, confidence, URL, and explanation reasons. It also requests recent history and shows a clear message when no saved records are available. The interface explicitly states that the submitted website is not visited during analysis.

## 6. System architecture

```text
User
  │
  ▼
React + Vite + JSX (`web/`)
  │ JSON over HTTP
  ▼
Django REST Framework (`api/web_api/`)
  │
  ▼
Scan service (`api/url_analysis/scan_service.py`)
  ├── URL parser and 20-feature extractor
  ├── optional joblib predictor
  ├── heuristic fallback and reasons
  └── optional MongoEngine persistence
```

The architecture has a deliberate boundary between startup validation, analysis, and persistence. URL inspection is local and does not fetch the submitted website. Normal backend startup requires MongoDB; an explicit `--force` bypass supports diagnostics, while persistence after startup remains best-effort and is observable through the history endpoint.

## 7. Expected outputs

A successful scan response contains the submitted URL, a supported verdict, a confidence value bounded between 0 and 1, an explanation object, and the extracted feature values. The exact JSON shape is documented in [API_REFERENCE.md](./API_REFERENCE.md).

The system should be evaluated by behavior and reproducibility rather than by an invented performance number. A future evaluation must identify its dataset, split strategy, feature version, model artifact, metrics, and execution environment.

## 8. Educational value

The project gives students practical experience with:

- Translating a security problem into measurable input signals.
- Designing a stable feature contract.
- Separating HTTP transport from domain logic.
- Handling a required startup dependency and best-effort persistence without hiding failures.
- Connecting a React client to a Django REST API.
- Writing tests for feature order and prediction boundaries.
- Communicating system limitations responsibly.

## 9. Limitations and ethical considerations

URL structure alone is incomplete evidence. Benign services can use long or complex URLs, while malicious services can use simple URLs. A heuristic can therefore produce both false positives and false negatives. The result must not be used as the sole basis for blocking, allowing, reporting, or investigating a website.

The application should be tested only with URLs and datasets that the user is authorized to handle. The current analyzer does not fetch websites, but any future live-inspection feature would require explicit controls for privacy, abuse prevention, rate limiting, logging, and safe handling of potentially malicious content.

The project must not claim that it prevents phishing, guarantees safety, or replaces established security products. Future model metrics must be reported with enough detail for another researcher to reproduce them.

## 10. Future research directions

Future work may investigate:

- Licensed datasets and reproducible training/evaluation scripts.
- Model artifact versioning and feature-contract validation.
- Calibration and threshold analysis.
- Error analysis across URL families and languages.
- Batch workflows and authenticated history.
- Additional explanation methods.
- Carefully isolated reputation or live-content integrations.
- Deployment and observability for a clearly defined environment.

Each direction is a separate research increment. It becomes part of the system description only after implementation, testing, documentation, and evidence are complete.

## 11. Conclusion

PhishGuard establishes a focused Phase 1 foundation for academic phishing URL analysis. It combines deterministic local feature extraction, an inspectable predictor, a small REST contract, MongoDB-backed history with an explicit diagnostic startup bypass, and a JavaScript/JSX frontend. Its strongest design property is the explicit safety and scope boundary: it analyzes the submitted URL string without visiting the destination and presents its result as an informational signal.

This foundation can support measured future research while remaining honest about what the current implementation does—and does not—demonstrate.
