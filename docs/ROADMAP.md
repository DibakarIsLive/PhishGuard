# PhishGuard Roadmap

## Roadmap policy

This roadmap separates implemented Phase 1 behavior from research and engineering work that remains. An item becomes a current capability only after code, tests, documentation, and evidence are available.

PhishGuard remains an academic and research-oriented tool throughout this roadmap. Future work must not be presented as a guarantee of website safety or as a production security gateway without a separately defined operational scope.

## Phase 1 — Verified baseline

**Status: implemented**

The current repository provides:

- Django REST Framework API.
- One-URL JSON scan endpoint.
- Configurable input limit (`MAX_URL_LENGTH`, 2,048 characters by default).
- Network-free extraction of 20 URL and hostname features.
- Heuristic verdicts: `legitimate`, `suspicious`, and `phishing`.
- Human-readable fallback reasons.
- Optional compatible joblib model boundary.
- MongoEngine/MongoDB scan history after the required normal-startup reachability check; forced diagnostics may run without persistence.
- React/Vite JavaScript and JSX interface.
- Focused API tests and local build/check commands.
- Explicit limitations and safety documentation.

## Phase 1.1 — Baseline quality and reproducibility

**Status: next**

### Candidate work

- Add a small, licensed, versioned evaluation dataset or a documented fixture set.
- Define deterministic evaluation commands without claiming results before they are measured.
- Add model-artifact metadata: feature order, training version, label mapping, and provenance.
- Add a compatible model artifact and evaluate it against a documented fixture or licensed dataset.
- Add a clean-environment reproduction run and deliberate MongoDB-backed smoke evidence.
- Keep configuration examples, route references, and capability descriptions synchronized with observed behavior.

### Acceptance criteria

- A fresh developer can reproduce the documented checks from a clean setup.
- Any reported metric includes dataset, split, feature version, model artifact, and command.
- Optional model loading cannot silently use an incompatible feature contract.
- Documentation examples match observed responses.

## Phase 2 — Measured model research

**Status: planned**

### Candidate work

- Collect or adopt datasets under terms that permit the intended academic use.
- Create a reproducible data-cleaning and split process.
- Compare the heuristic baseline with one or more documented models.
- Measure confusion matrix, precision, recall, F1-score, calibration, and error categories.
- Record training environment and artifact version.
- Analyze false positives and false negatives by URL family.

### Acceptance criteria

- Results are reproducible from a documented command and versioned data reference.
- Baseline and model results are reported separately.
- No metric is generalized beyond the evaluated data.
- The application exposes model metadata appropriate to the selected artifact.

## Phase 3 — Product workflow improvements

**Status: planned**

Possible work includes:

- History filtering and pagination.
- User accounts and authenticated history.
- Batch scanning with explicit resource and abuse controls.
- Export of authorized analysis records.
- Better user-facing explanation presentation.
- Frontend component and integration tests.

These features should not be added merely because configuration placeholders exist. Each requires a defined API contract, tests, privacy considerations, and documentation.

## Phase 4 — Additional evidence sources

**Status: research only**

Possible investigations include:

- Carefully isolated domain or reputation sources.
- Optional certificate, DNS, or redirect metadata.
- Controlled HTML or content analysis.
- Additional explanation methods.
- Browser or email integrations.

Any feature that contacts a submitted destination changes the current network-free safety boundary. It would require explicit consent and documentation for privacy, SSRF prevention, sandboxing, rate limits, logging, data retention, and failure behavior.

## Phase 5 — Deployment hardening

**Status: not scheduled**

Only pursue deployment work after the target environment is known. Potential topics include:

- Secret management.
- TLS and reverse-proxy configuration.
- Authentication and authorization.
- Observability and alerting.
- Dependency and artifact scanning.
- Data retention and deletion policies.
- Abuse prevention and rate-limit design.
- Backup and recovery procedures.

The presence of `production.py` provides configuration guardrails; it does not by itself make the system production-ready.

## Deferred or explicitly excluded until justified

- Unsupported accuracy targets.
- Claims of sub-200 ms latency.
- Unverified 30+ feature descriptions.
- Ensemble claims without implemented and evaluated ensembles.
- SHAP claims without an integrated explainer.
- Batch endpoint claims without a batch implementation.
- Production-readiness claims without an operational review.
- Commercial-use licensing without a deliberate license change.

## Related documents

- [Project plan](./project-plan.md)
- [Project synopsis](./project-synopsis.md)
- [Architecture](./ARCHITECTURE.md)
- [API reference](./API_REFERENCE.md)
- [Development guide](./DEVELOPMENT_GUIDE.md)
- [Testing guide](./TESTING_GUIDE.md)
