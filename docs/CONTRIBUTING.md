# Contributing to PhishGuard

## Project standard

PhishGuard is an academic and research-oriented URL analysis project. Contributions should improve a verifiable Phase 1 baseline or clearly identify future research. Do not describe planned behavior as implemented behavior.

## Before making a change

1. Read the relevant document in `docs/`.
2. Check the current implementation and tests.
3. Confirm that the change stays within the requested scope.
4. Keep the API, analyzer, UI, and documentation contracts synchronized.

## Repository conventions

- Use `api/` for Django and analysis code.
- Use `ui/` for React source.
- Use lowercase `public/` assets.
- Use Python `snake_case` for Python files, functions, and variables.
- Use JavaScript and JSX only in the UI.
- Keep generated files, local environments, logs, datasets, and model artifacts ignored.
- Preserve the network-free scan boundary unless a separately reviewed feature changes it.

## Documentation rules

Documentation must:

- Reflect verified code and commands.
- State whether MongoDB is optional or required for a workflow.
- Distinguish heuristic output from validated model performance.
- Avoid unsupported feature counts, model-family claims, accuracy claims, latency claims, and production-readiness claims.
- Explain future work as future work.
- Use relative links that resolve from the document location.
- Keep the safety disclaimer visible where users encounter scan results.

## Code and test changes

For a code change:

1. Add or update focused tests.
2. Avoid external network calls in tests.
3. Consider MongoDB-unavailable behavior when touching persistence.
4. Consider the stable 20-feature contract when touching extraction or prediction.
5. Run:

```bash
make check
make test
make build
python3 -m compileall -q api
git diff --check
```

For feature-contract changes, update the extractor tests, optional-model documentation, architecture table, API reference, and any artifact metadata together.

## Commit and review checklist

Before sharing a change, inspect:

```bash
git status --short
git diff --stat
git diff --check
```

Reviewers should be able to answer:

- What behavior changed?
- Which tests prove it?
- Does the API response contract remain compatible?
- Does the UI still use JavaScript and JSX?
- Does the change make any network request that was not previously made?
- Are claims in `README.md` and `docs/` supported by the repository?
- Are secrets or generated artifacts absent?

## Security and privacy

Do not commit credentials, private URLs, tokens, personal data, unlicensed datasets, or unverified model artifacts. Do not submit real malicious destinations to automated tests. Use harmless or authorized fixtures.

If a proposed feature would fetch, crawl, resolve, or otherwise contact a submitted URL, document the privacy and abuse-prevention design before implementation. The current Phase 1 analyzer intentionally does not perform those operations.

## License

Contributions and repository use are governed by the [PhishGuard Source-Available Academic and Evaluation License](../LICENSE). Third-party dependencies, datasets, and model artifacts may have separate terms.
