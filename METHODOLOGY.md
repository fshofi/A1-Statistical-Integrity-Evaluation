# Methodology

## Design

A1 uses 24 deliberately selected cases organized as 12 matched contrasts. Each contrast changes a material statistical condition, claim, or decision rule. The cases are not iid draws and do not represent a population of statistical tasks.

## Run protocol

Run 1 used OpenAI `gpt-5.6-luna` with reasoning `low`. The collector created one fresh agent-created projectless task per public case. The visible model input contained a neutral run instruction plus only the public case ID, scenario, data, and task. Original traces record no browser, tool, memory, or retrieval invocation during the definitive turns.

The strongest defensible isolation statement is:

> The collector used fresh projectless tasks, one public case per task, with no recorded browser/tool/memory/retrieval invocations. Hidden platform context was not exposed and therefore cannot be independently ruled out.

## Three distinct evaluation layers

1. **Frozen deterministic parser/scorer.** Amendment 1.1 preserves requested/supplemental separation, six-decimal tolerance, exact-integer handling, unit status, parser status, and explicit denominators. The narrow parser evaluated 0/20 applicable responses because the prose responses were outside its accepted whole-response formats.
2. **Independent manual/analytical recomputation.** Abacus recomputed requested quantitative values from public case data. This layer supports 19/20 correct requested-field results, with Q195 as the sole failure.
3. **Semantic/statistical judgment.** Abacus supplied an attributed reviewer-declared three-level assessment; Astra supplied an independent hostile methodological review. These are AI-assisted judgments, not blinded human expert scoring or validated psychometrics.

Disagreement is retained rather than averaged. Final adjudication is recorded in `evidence/FINAL_ADJUDICATION.md`.
