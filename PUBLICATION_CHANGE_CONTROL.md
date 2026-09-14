# Publication change control

## A1 V1.2.1 controlled reconciliation release

V1.2.1 preserves V1.2 unchanged and adds separated reviewer evidence, actual received-file hashes, controlled reconciliation and tightened public wording. It does not alter a benchmark case, prompt, raw response, reference answer, score, adjudication or hardening control.

Added:

- `reviews/gemini_lane_a/` raw blind-review evidence and received-file hash;
- `reviews/abacus_lane_b/` raw technical-review evidence, declaration and received-file hashes;
- `evidence/CROSS_MODEL_REVIEW_RECONCILIATION_V1_2_1.md`;
- `evidence/CLAIM_LEDGER_V1_2_1.csv`; and
- `PUBLICATION_FREEZE_V1_2_1.json`.

Revised only for claim precision and release identification:

- `README.md`, `RESULTS.md`, `LIMITATIONS.md`, `AI_ASSISTANCE_DISCLOSURE.md`;
- `REPRODUCIBILITY.md`, `CHANGELOG.md`, `evidence/EVIDENCE_CHAIN.md`;
- `evidence/PORTFOLIO_AND_RECRUITER_COPY.md`; and
- publication-gate version labels.

V1.2.1 is model-assisted and architect-reconciled. It is not independent human validation or institutional certification.

Six publication-reconciliation controls were added without changing the benchmark corpus, raw responses, reference answers, derived scoring evidence or final adjudication. The V1.2.1 total is 52: the preserved 46 benchmark/hardening tests plus six claim-and-receipt controls.

The Final freeze additionally preserves Claude's raw final-GO report and a separate reconciliation. It accepts the bounded disposition while declining five overstatements. This evidence-only addition does not change the test count or underlying benchmark evidence.

## A1 V1.2 external-challenge release

The frozen Amendment 1.1 baseline, prompts, responses, references, deterministic outputs and final adjudication remain unchanged. V1.2 adds a separate control layer and does not retroactively alter Run 1.

Added:

- `src/hardening.py`
- `scripts/run_v1_2_hardening.py`
- selection-design and observable-reasoning records and schemas
- machine-readable hardening results under `runs/run1/hardening_v1_2/`
- 14 external-challenge tests, bringing the reconciled total to 46
- external-challenge report, Codex adversarial review and V1.2 claim ledger
- `PUBLICATION_FREEZE_V1_2.json`

Revised only to describe or execute the new control layer:

- `README.md`, `RESULTS.md`, `LIMITATIONS.md`, `REPRODUCIBILITY.md`, `CHANGELOG.md`
- `evidence/EVIDENCE_CHAIN.md`
- test inventory, publication gate and package manifest tooling

The V1.2 review is architect-requested and AI-assisted. It is not independent validation.

Source package: `A1_Publication_Freeze_Package.zip`  
Source SHA-256: `ddd2f5dfab0f9ccbede0ff4493184fb590a6b122ae9579314a3091491def6c2e`

## EXCLUDED - COMPILED CACHE

- `scripts/__pycache__/clean_replay.cpython-312.pyc`
- `src/__pycache__/__init__.cpython-312.pyc`
- `src/__pycache__/checker.cpython-312.pyc`
- `src/__pycache__/parsing.cpython-312.pyc`
- `src/__pycache__/schemas.cpython-312.pyc`
- `src/__pycache__/scoring.cpython-312.pyc`
- `src/__pycache__/utils.cpython-312.pyc`
- `tests/__pycache__/test_amendment_h01_h06.cpython-312.pyc`
- `tests/__pycache__/test_cases.cpython-312.pyc`
- `tests/__pycache__/test_checker.cpython-312.pyc`
- `tests/__pycache__/test_model_run.cpython-312.pyc`
- `tests/__pycache__/test_reproducibility.cpython-312.pyc`
- `tests/__pycache__/test_scoring.cpython-312.pyc`

## REDACTED - LOCAL PATH

- `baseline/a1_revision_bundle/revision/checker_execution_log_rev2.txt` - two occurrences replaced with `[LOCAL_PATH_REDACTED]`.
- `evidence/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Public_Safe.zip` internal member `A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Freeze_Candidate/baseline/a1_revision_bundle/revision/checker_execution_log_rev2.txt` - two occurrences replaced with `[LOCAL_PATH_REDACTED]`.
- `evidence/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Public_Safe.zip` internal member `A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Freeze_Candidate/results/fresh_rev2_execution.log` - two occurrences replaced with `[LOCAL_PATH_REDACTED]`.

## DERIVED - PUBLIC-SAFE ARCHIVE

- Removed unsanitized `evidence/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Freeze_Candidate.zip` from the derivative.
- Added `evidence/A1_Statistical_Integrity_Benchmark_V1_Amendment_1.1_Public_Safe.zip` with SHA-256 `2a0f196125b5474f77e532bc5154ad6b288fc74220d0d2e6116accf01881e5b4`.
- Replaced the source package manifest with a new derivative `SHA256_MANIFEST.txt`.
- Updated only the sanitized execution-log hash in the derivative bundle-content manifest; the historical private manifest is retained under `evidence/historical_manifests/`.
- Added `evidence/historical_manifests/HISTORICAL_PRIVATE_BUNDLE_CONTENT_SHA256.txt` as the exact preserved pre-sanitization bundle manifest.
- Within the public-safe Amendment derivative: regenerated `PROJECT_SHA256.txt`; preserved the private project manifest as `baseline/HISTORICAL_PRIVATE_FREEZE_PROJECT_SHA256.txt`; preserved the private bundle manifest as `baseline/HISTORICAL_PRIVATE_BUNDLE_CONTENT_SHA256.txt`; added `PUBLICATION_DERIVATIVE_PROVENANCE.md`; updated only the sanitized log entry in `baseline/a1_revision_bundle/BUNDLE_CONTENT_SHA256.txt`.
- The package ZIP itself has an external `PUBLICATION_PACKAGE_SHA256.txt` sidecar to avoid circular self-hashing.

## ADDED - PUBLICATION DOCUMENTATION

- `.gitignore`
- `PUBLICATION_PROVENANCE.md`
- `PUBLICATION_SANITIZATION_LOG.md`
- `PUBLICATION_CHANGE_CONTROL.md`
- `PUBLICATION_PRIVACY_SCAN.json`
- `evidence/historical_manifests/HISTORICAL_PRIVATE_BUNDLE_CONTENT_SHA256.txt`
- Public-release notes appended to `README.md` and `REPRODUCIBILITY.md`
- Publication-safe derivative entry appended to `CHANGELOG.md`

## Prohibited change classes

- BENCHMARK LOGIC CHANGE: **NONE**
- REFERENCE CHANGE: **NONE**
- RESULT CHANGE: **NONE**
- ADJUDICATION CHANGE: **NONE**
- RAW RESPONSE CHANGE: **NONE**
