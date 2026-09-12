# A1 Statistical-Integrity Benchmark

<p align="center">
  <a href="assets/plates/a1-cvdna-atlas-plate.jpg">
    <img src="assets/plates/a1-cvdna-atlas-plate.jpg" alt="CVDNA Atlas II Technical Plate — A1 Statistical Integrity Evaluation for LLMs" width="100%">
  </a>
</p>

<p align="center"><em>CVDNA Atlas II | Technical Plate — A1 Statistical Integrity Evaluation for LLMs</em></p>

## Publication status

**CONDITIONAL PUBLICATION GO** - bounded portfolio/research artifact, frozen after final adjudication.

A1 is a compact, AI-assisted evaluation artifact comprising 24 selected statistical-integrity cases arranged as 12 designed matched contrasts. It combines preserved prompt/response provenance, frozen scoring and run-protocol governance, independent replay, failure localization, AI-assisted statistical review, hostile publication review, and explicit claim controls.

This release does **not** establish representative model accuracy, universal statistical competence, contamination-free execution, psychometric validity, enterprise deployment performance, or superiority to other benchmarks.

## Recorded run

- Model alias: OpenAI `gpt-5.6-luna`
- Reasoning setting: `low`
- Responses preserved: 24/24
- Collection: one reported fresh projectless task per case, in two blocks
- Frozen deterministic parser: 0/20 numeric-applicable cases evaluated; this is parser coverage, **not 0% accuracy**
- Independent manual/analytical recomputation: 19/20 applicable cases returned all requested numeric values correctly
- Descriptive matched contrasts: 11/12 had defensible verdict-level discrimination in both arms

See `RESULTS.md`, `LIMITATIONS.md`, and `evidence/FINAL_ADJUDICATION.md` before quoting any result.

## Repository map

- `data/`, `src/`, `tests/`, `config/`, `schemas/`, `scripts/`: unchanged Amendment 1.1 processor materials
- `baseline/`: preserved blind, Rev-1, and Rev-2 reference provenance
- `runs/run1/`: complete post-Amendment Run 1 evidence package contents
- `reviews/abacus/`: attributed independent AI-assisted statistical review
- `reviews/astra/`: attributed hostile methodological/publication review
- `evidence/`: evidence chain, hashes, replay results, adjudication, and publication-scope controls

## Citation boundary

Describe A1 as a selected-case evaluation framework and portfolio artifact. Do not describe it as a validated population benchmark or a measure of general model competence.

## Public-release note

Public-release note: this repository is a publication-safe derivative of the frozen evidence package. Compiled Python caches and local filesystem identifiers were excluded/redacted for privacy and security. The underlying benchmark evidence, statistical results, adjudication, and source logic were not altered. Historical freeze hashes are retained in the provenance record.

