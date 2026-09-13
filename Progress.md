# PhishGuard Progress Dashboard

> A single-glance reference for the team. This tracker separates verified implementation from remaining engineering work and planned research.
>
> **Frontend rule:** React + JavaScript + JSX only. TypeScript and TSX are not part of this project convention.

## Current position

| Phase | Status | What it means |
| --- | --- | --- |
| **Phase 1 — Verified baseline** | ✅ **Complete** | The core URL-analysis application is implemented and the documented baseline checks have passed. |
| **Phase 1.1 — Quality and reproducibility** | 🟡 **Next work** | The baseline exists; it still needs stronger fixtures, artifact validation, edge-case coverage, and reproducibility evidence. |
| **Final Phase 2 — Measured model research** | ⬜ **Planned** | Build and evaluate a documented model workflow against the current heuristic baseline. |
| **Phase 3 — Product workflows** | ⬜ **Later** | Consider accounts, batch workflows, filtering, exports, and richer UI only after measurement. |
| **Phase 4 — Additional evidence sources** | 🔬 **Research only** | Investigate live or external evidence cautiously; this would change the current network-free safety boundary. |
| **Phase 5 — Deployment hardening** | ⏸️ **Not scheduled** | Define a target environment first; do not describe the project as production-ready yet. |

A numeric overall percentage is intentionally not used: Phase 2 is research work whose completion depends on licensed data, reproducible experiments, and evidence—not only on the number of files or screens completed.

## What is complete in Phase 1

The following work is implemented and verified in the current repository:

- [x] Repository boundaries are established with `api/`, `web/`, `public/`, and `docs/`.
- [x] Django REST Framework exposes the root, health, single-URL scan, and history endpoints.
- [x] One URL is validated, normalized, and limited to 2,048 characters.
- [x] Twenty deterministic URL and hostname features are extracted locally.
- [x] Analysis remains network-free: submitted websites are not visited or fetched.
- [x] The baseline returns `legitimate`, `suspicious`, or `phishing` with human-readable reasons.
- [x] An optional compatible `joblib` model hook exists, with heuristic fallback when the artifact is absent or unusable.
- [x] Normal backend startup performs a bounded MongoDB reachability check.
- [x] `--force` / `FORCE=1` provides an explicit diagnostic bypass when MongoDB is unavailable.
- [x] Scan persistence uses MongoEngine/MongoDB when available; a forced diagnostic session can still return lexical analysis if persistence fails.
- [x] The frontend is React/Vite with JavaScript and JSX pages and components.
- [x] Local setup, check, test, compile, build, and development commands are documented.
- [x] API tests, Django checks, Python compilation, frontend build, documentation-link checks, and whitespace checks have been run successfully.

### Deliberately not claimed as complete

These are not hidden unfinished promises inside Phase 1; they are explicitly outside the verified baseline:

- No bundled trained model or reproducible training pipeline.
- No licensed evaluation dataset or reported accuracy, precision, recall, F1-score, calibration, or latency result.
- No batch-scanning endpoint.
- No authentication, user accounts, dashboard, browser extension, or email scanner.
- No SHAP integration or other advanced explainer.
- No HTML, DOM, redirect, certificate, DNS, WHOIS, reputation, or live website inspection.
- No production security-gateway or safe-browsing guarantee.

## Remaining Phase 1 work: Phase 1.1

**Objective:** make the current baseline easier to reproduce, test, review, and extend without overstating its capabilities.

| Priority | Remaining job | Suggested owner | Definition of done |
| --- | --- | --- | --- |
| P0 | Add a small, licensed, versioned fixture or evaluation dataset. | ML / Research | The source, license, schema, version, and permitted academic use are documented. |
| P0 | Add a deterministic evaluation command and report format. | ML / Research | A clean setup can run the command and produce results tied to the dataset and feature version. |
| P0 | Add model-artifact metadata and feature-contract validation. | ML + Backend | The application checks feature order, label mapping, provenance, and artifact version before inference. |
| P1 | Expand edge-case tests for malformed URLs, whitespace normalization, verdict boundaries, and confidence bounds. | Backend + QA | Tests cover expected validation and prediction behavior and pass from the repository root. |
| P1 | Test best-effort persistence and forced diagnostic sessions explicitly. | Backend + QA | MongoDB failure behavior is tested and documented without changing the scan response contract. |
| P1 | Improve structured diagnostics for MongoDB connection and save failures. | Backend | Logs identify the failure stage while keeping timeouts bounded and useful. |
| P1 | Clarify or remove configuration values that are reserved or only partially consumed. | Backend + Docs | `.env.example`, settings, documentation, and runtime behavior agree. |
| P1 | Run a clean setup and collect academic evidence. | QA + Docs | A fresh environment reproduces the checks; screenshots and representative API responses are recorded. |
| P1 | Keep all documentation and examples synchronized with observed behavior. | Docs + Project lead | No future capability is described as current, and links/examples pass review. |

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
