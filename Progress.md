# PhishGuard Progress Dashboard

> A single-glance team reference for the verified Phase 1 backend, its deliberate boundaries, and the work that remains before Phase 2 research.
>
> **Frontend rule:** React + JavaScript + JSX only. TypeScript and TSX are not part of this project convention.

## Current position

| Phase | Status | What it means |
| --- | --- | --- |
| **Phase 1 — Backend baseline** | ✅ **Complete** | The Django REST + MongoEngine URL-analysis backend is implemented, tested, and documented for the current single-URL workflow. |
| **Phase 1.1 — Quality and reproducibility** | 🟡 **Next work** | Strengthen evidence with a licensed fixture, deterministic evaluation, artifact provenance, and a clean-environment run. |
| **Final Phase 2 — Measured model research** | ⬜ **Planned** | Train and evaluate a documented model against the Phase 1 heuristic baseline. |
| **Phase 3 — Product workflows** | ⬜ **Later** | Consider accounts, batch workflows, filtering, exports, and richer UI only after measurement. |
| **Phase 4 — Additional evidence sources** | 🔬 **Research only** | Investigate live or external evidence cautiously; this would change the current network-free safety boundary. |
| **Phase 5 — Deployment hardening** | ⏸️ **Not scheduled** | Define a target environment first; do not describe the project as production-ready yet. |

A numeric overall percentage is intentionally not used: Phase 2 depends on licensed data, reproducible experiments, and evidence—not only on the number of files or screens completed.

## What is complete in the Phase 1 backend

The following work is implemented in the current repository and covered by the current automated checks:

### API and configuration

- [x] Django REST Framework exposes `/`, `/api/health/`, `/api/capabilities/`, `/api/scan/`, and `/api/history/`.
- [x] JSON scan input is validated through a shared URL-validation module.
- [x] URLs are trimmed, length-limited, restricted to HTTP/HTTPS semantics, and rejected when malformed, internally spaced, backslash-containing, or missing a usable hostname.
- [x] `MAX_URL_LENGTH`, `MAX_BATCH_SIZE`, and `HISTORY_LIMIT` are read from settings and rejected at startup when non-positive.
- [x] Health and capabilities responses expose the Phase 1 boundary, limits, model state, database state, and unavailable future features.

### Analysis and prediction

- [x] Twenty deterministic URL and hostname features are extracted locally in the stable `url-features-v1` order.
- [x] Analysis remains network-free: submitted websites are never visited, fetched, resolved, or remotely inspected.
- [x] The baseline returns `legitimate`, `suspicious`, or `phishing` with human-readable reasons and confidence bounded to `[0, 1]`.
- [x] An optional `joblib` model hook validates the feature count/order and prediction shape before inference.
- [x] Missing, incompatible, or failing optional-model artifacts fall back to the heuristic predictor.
- [x] Responses include analyzer metadata, explicitly report `network_accessed: false`, and expose the separate local brand-confusion advisory metadata.
- [x] The local brand rules cover a small, documented set of simple hostname look-alike patterns without changing the stable 20-feature model contract.

### Persistence and diagnostics

- [x] Normal `runserver` startup performs a bounded MongoDB reachability check.
- [x] `--force` / `FORCE=1` provides an explicit diagnostic bypass when MongoDB is unavailable.
- [x] MongoEngine scan persistence is best-effort after startup; analysis remains usable when a probe or save fails.
- [x] MongoDB retry suppression, bounded probes, safe database diagnostics, and logged save/history failures are implemented.
- [x] History requests are capped by the configured `HISTORY_LIMIT`.
- [x] Scan documents carry bounded confidence, feature/explanation defaults, and analyzer-version metadata.

### Verification and documentation

- [x] Focused API tests cover feature ordering/version, malformed input, strict IPv4 handling, configurable limits, model fallback/compatibility, local brand-confusion behavior, health/capabilities, force handling, history limits, and persistence-failure tolerance.
- [x] Root `make ci` passed: Django checks, the API pytest suite (`29` tests), and the Vite production build.
- [x] Root `python3 -m compileall -q api` and `git diff --check` passed.
- [x] API and architecture references document the current routes, feature contract, validation, limits, persistence boundary, and Phase 1 non-goals.

> **Verification boundary:** the automated suite uses fallback/mocked database paths where necessary. A live MongoDB persistence run, a compatible trained model inference run, browser behavior, and model-quality metrics remain unverified until explicitly executed.

### Deliberately not claimed as complete

- No bundled compatible trained model, reproducible training pipeline, or licensed evaluation dataset.
- No accuracy, precision, recall, F1-score, calibration, or latency claim.
- No batch-scanning endpoint, authentication, user accounts, dashboard, browser extension, or email scanner.
- No SHAP integration or advanced explainer.
- No HTML, DOM, redirect, certificate, DNS, WHOIS, reputation, or live website inspection.
- No comprehensive brand, typosquatting, domain-ownership, or threat-intelligence coverage; the local rules are advisory and incomplete.
- No production security-gateway or safe-browsing guarantee.

## Remaining Phase 1.1 work

**Objective:** make the current backend easier to reproduce, evaluate, review, and extend without overstating its capabilities.

| Priority | Remaining job | Suggested owner | Definition of done |
| --- | --- | --- | --- |
| P0 | Add a small, licensed, versioned fixture or evaluation dataset. | ML / Research | Source, license, schema, version, and permitted academic use are documented. |
| P0 | Add a deterministic evaluation command and report format. | ML / Research | A clean setup produces results tied to the dataset and `url-features-v1`. |
| P0 | Add model-artifact metadata and provenance. | ML + Backend | Feature order, label mapping, training reference, artifact version, and provenance are recorded. |
| P1 | Perform a clean-environment installation and verification run. | QA + Docs | A new team member reproduces the checks without relying on this machine's generated state. |
| P1 | Run a deliberate MongoDB-backed smoke test. | Backend + QA | Startup, save, history, and failure behavior are recorded with a reachable local MongoDB instance. |
| P1 | Test a compatible model artifact end to end. | ML + Backend | Model loading, prediction, metadata, and fallback behavior are evidenced with a documented artifact. |
| P1 | Keep examples synchronized with observed behavior. | Docs + Project lead | Route tables, feature contract, limits, setup commands, and limitations remain accurate. |

### Phase 1.1 exit gate

Phase 1.1 is complete when a new team member can reproduce the baseline from a clean setup, understand the feature and model contract, run the documented checks, see meaningful edge-case coverage, and distinguish measured evidence from heuristic output.

## Final Phase 2: Measured model research

**Status: planned — do not implement or describe these outcomes as current capabilities.**

### What Phase 2 will achieve

1. **Licensed data foundation** — adopt or collect datasets whose terms permit the intended academic use.
2. **Reproducible preparation** — clean, normalize, deduplicate, label, and split the data through documented commands.
3. **Baseline comparison** — report the current heuristic results separately from any trained model results.
4. **Model experiments** — compare one or more documented models with the heuristic baseline rather than assuming an ensemble is better.
5. **Measured evaluation** — report a confusion matrix, precision, recall, F1-score, calibration where appropriate, and error categories.
6. **Error analysis** — inspect false positives and false negatives across relevant URL families instead of presenting one unexplained number.
7. **Artifact traceability** — record the feature version, label mapping, training environment, dataset reference, model version, and provenance.
8. **Application integration** — expose model metadata appropriate to the selected artifact while preserving a safe fallback when no compatible artifact is available.

### Phase 2 completion gate

Phase 2 is complete only when:

- Results can be reproduced from a documented command and versioned data reference.
- Heuristic-baseline and trained-model results are reported separately.
- Every metric identifies its dataset, split, feature version, artifact, and execution context.
- The model artifact is checked against the application feature contract.
- Error categories and limitations are documented honestly.
- No result is generalized beyond the data and conditions that were actually evaluated.

## Team work board

Replace `Unassigned` with names when work is distributed. A status applies to the workstream’s current baseline, not to every future feature listed in its row.

| Workstream | Current status | Owner | Immediate responsibility |
| --- | --- | --- | --- |
| Backend, API, and MongoDB | ✅ Baseline complete | Unassigned | Finish Phase 1.1 edge-case tests, persistence tests, and diagnostics. |
| URL analysis and ML research | 🟡 Phase 1.1 next | Unassigned | Define the fixture/evaluation path and the model-artifact contract before Phase 2 training. |
| React + JavaScript + JSX frontend | ✅ Baseline complete | Unassigned | Preserve the JSX-only architecture, verify the API workflow, and collect UI evidence. |
| QA and verification | 🟡 Ongoing | Unassigned | Re-run checks from a clean setup and record reproducible evidence. |
| Documentation and academic reporting | 🟡 Ongoing | Unassigned | Keep current behavior, limitations, roadmap, and examples synchronized. |
| Project integration / review | 🟡 Required | Unassigned | Assign owners, review exit gates, and prevent planned features from being presented as implemented. |

## Recommended order of work

1. Assign owners for the Phase 1.1 rows.
2. Freeze the verified Phase 1 baseline and record the current verification output.
3. Complete the licensed fixture, deterministic evaluation command, and artifact contract.
4. Add the edge-case and persistence tests, then repeat the clean-setup verification.
5. Begin Phase 2 only after Phase 1.1’s exit gate is satisfied.
6. Compare the measured Phase 2 model with the heuristic baseline and document errors.
7. Consider Phase 3 product features only after the model evidence and project scope are reviewed.

## Source documents

- [README](./README.md) — quick start, architecture, limitations, and documentation map.
- [Project plan](./docs/project-plan.md) — detailed Phase 1 workstreams and acceptance criteria.
- [Roadmap](./docs/ROADMAP.md) — staged Phase 1.1, Phase 2, and later research planning.
- [Project synopsis](./docs/project-synopsis.md) — academic scope, methodology, and ethical boundary.
- [Development guide](./docs/DEVELOPMENT_GUIDE.md) — setup, commands, configuration, and troubleshooting.
- [Testing guide](./docs/TESTING_GUIDE.md) — verification workflow and current test coverage.
