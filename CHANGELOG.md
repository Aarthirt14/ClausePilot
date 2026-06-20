# Improvements Changelog

Summary of changes made to harden ClausePilot for production use and
portfolio presentation. Organized by category; see git history (once
this is in a repo) for line-level detail.

## Performance
- **Fixed model reloading on every request.** `src/inference.py` and
  `src/explainability.py` previously reloaded the BERT checkpoint,
  rebuilt the tokenizer, and (for `/explain`) rebuilt the SHAP explainer
  from scratch on every single call. Both are now cached per-process
  behind a thread-safe lazy singleton, so the expensive load happens
  once instead of once-per-upload / once-per-explanation.
- `app.py` now warms the model cache at startup (best-effort) instead of
  paying that cost on the first user's request.

## Security & production readiness
- `app.run(debug=True)` is gone — debug mode is now off by default and
  controlled via `FLASK_DEBUG` (the Werkzeug debugger allows arbitrary
  code execution if a debug-mode app is ever exposed to a network).
- Added `MAX_CONTENT_LENGTH` (default 20MB, configurable) with a proper
  413 error page instead of letting an unbounded upload hang a worker.
- Added a `SECRET_KEY` config (was unset).
- Added structured logging (`logging` module) — exceptions in the
  broad `except Exception` blocks are now logged server-side instead of
  only being shown to the user as a bare string.
- Added time-based cleanup of uploaded PDFs (`UPLOAD_RETENTION_HOURS`,
  default 24h) since uploaded contracts can be sensitive documents.
- Added a `/healthz` endpoint for container orchestrators / uptime checks.
- Centralized all of the above into `src/config.py`, driven by
  environment variables (see `.env.example`).

## Bug fixes
- `mitigation_summary` was computed in `analyze_contract()` but never
  passed to `results.html` — the entire mitigation-strategy feature
  (`src/scoring/mitigation_strategies.py`) was built but invisible in
  the UI. Now wired into both an executive-level "Recommended
  Mitigations" card and a per-clause mitigation section.
- The error-fallback render context in `app.py`'s `/result` route was
  missing `risk_score_breakdown.high_risk_count` and
  `risk_score_breakdown.calibrated_clauses`, which `results.html`
  references — this would have raised a Jinja `UndefinedError` on any
  failure path (e.g. missing model). Fixed.
- Fixed a subtle cache-identity bug in both `inference.py` and
  `explainability.py`: the first call returned a freshly-constructed
  tuple instead of the cached one, so `load_bert_model(...) is
  load_bert_model(...)` was `False` even though no reload happened.
  Functionally harmless (no extra disk reads) but now fixed for
  correctness and testability.
- Fixed a broken import in `src/pdf_analyzer.py` (`from predict import
  ...` instead of `from src.predict import ...`) that would fail
  whenever the script was run from the repo root.
- Removed dead code: an unused `attach_risk_scores` import in `app.py`,
  and two unused functions in `dashboard_utils.py`
  (`calculate_overall_risk_score`, `build_risk_score_breakdown`) that
  were superseded by `attach_advanced_risk_scores` but never removed.
- Removed unused imports across several modules (`train_bert.py`,
  `evaluate_models.py`, `train_baseline.py`, `category_mapper.py`,
  `modeling/baseline.py`, `calibration/reliability.py`).
- Moved a buried `import os` to the top of `pdf_extractor.py`.

## Code quality
- `segmentation.py` and `data_processing/cleaning.py` each had their
  own copy of the OCR-noise/multi-dot regex patterns. `segmentation.py`
  now imports the shared patterns from `cleaning.py` instead of
  duplicating them.

## Testing
- Added a full `pytest` suite under `tests/` (previously: one manual
  script and no CI). Covers segmentation, text cleaning, category
  mapping, both risk-scoring modules, mitigation strategies, evaluation
  metrics, error analysis, calibration, dashboard utilities (including
  PDF report generation), the evaluation API, the model/explainer
  caches, and Flask routes (mocking the inference/explainability layer
  so tests don't need a trained checkpoint).
- Added `requirements-dev.txt`, `pytest.ini`, and a `pyproject.toml`
  `[tool.ruff]` config.

## Dependencies
- Pinned `requirements.txt` with compatible-release ranges instead of
  no version constraints at all (a real reproducibility risk for an ML
  project where `torch`/`transformers` upgrades can change behavior).
- Added `joblib`, which was imported by `train_baseline.py` and
  `predict.py` but missing from `requirements.txt` (it happened to work
  anyway since scikit-learn pulls it in transitively, but it should be
  declared directly since the project imports it directly).

## Deployment
- Added `Dockerfile` (Gunicorn-based, not the Flask dev server) and
  `docker-compose.yml` with the model/uploads/evaluation directories
  mounted as volumes rather than baked into the image.
- Added `.github/workflows/ci.yml`: lint (`ruff`) + test (`pytest`) on
  every push/PR to `main`.

## Documentation
- README: fixed an inaccurate "Labels" list (IP Risk was missing — it's
  added via rule-based text detection rather than being a direct model
  output, which is now called out explicitly), added Testing/Docker
  sections, a "Known Limitations" section, updated the route list,
  added cross-platform setup instructions, and removed a stray
  unfinished sentence at the end of the file.
