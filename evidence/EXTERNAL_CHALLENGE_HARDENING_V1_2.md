# A1 V1.2 — External-Challenge Hardening

## Trigger

A1 was reopened under its frozen-release policy because a public technical question from Nick Hart identified a genuine missing control: the release did not expose a named survivor/selection-bias audit. A public observation from Fábio Borges also sharpened the need to distinguish a correct answer from a reconstructable, observable evidence path.

These interventions are credited as external challenge inputs. They are **not** represented as independent validation, endorsement, co-authorship, or approval of this implementation.

## Implemented controls

1. **Definitive-run universe check** — expected cases, preserved responses and provenance records must match exactly and in order.
2. **Attempt preservation** — every declared attempt must remain recorded; retries cannot replace or erase earlier failures.
3. **Outcome-safe classification** — refusals, truncations, timeouts and provider errors cannot be relabelled as successful completions.
4. **No outcome-based exclusion** — removing an attempt because of observed performance fails closed.
5. **Hash-bound selection** — every selected attempt must bind to the preserved raw response hash.
6. **Population-claim barrier** — purposive designed contrasts cannot authorise representative or population-performance claims.
7. **Observable reasoning lineage** — cases, raw outputs, task provenance, run manifest, reference answers, derived results and final adjudication are hash-bound.
8. **Hidden-reasoning boundary** — A1 does not claim access to, reconstruction of, or verification of private chain-of-thought.
9. **Authority boundary** — evidence evaluation does not confer execution authority.

## Run 1 finding

The definitive Run 1 contains 24 expected cases, 24 preserved responses, 24 provenance records and 24 selected first attempts. No refusal, timeout, truncation, retry or provider error is recorded within that definitive universe. No execution attrition is observed there.

This does **not** establish the absence of survivor bias across the complete development history. Run 0 and earlier pilot/corrective activity are disclosed, but their complete artifact universe is not present in the public package. The hardening result is therefore **CONDITIONAL PASS**, not PASS.

## Residual limitations

- The 24 cases are purposive designed contrasts, not a probability sample.
- The complete earlier development-attempt universe cannot be cryptographically reconstructed from the public package.
- Run 1 did not systematically require every discarded alternative to be recorded.
- The 168-item structured semantic-review queue remains unscored; attributed narrative adjudication is separate.
- No independent human validation has been completed.

## Commercial boundary

A1 V1.2 may be shown as a reproducible, selected-case portfolio demonstration of evidence-governed evaluation. It must not be sold or described as a validated population benchmark, a universal measure of model competence, an independently validated system, or evidence of client-deployment performance.
