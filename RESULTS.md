# Results

## Publication-safe result block

For these 24 selected cases, this one recorded run, the `gpt-5.6-luna` alias, and reasoning `low`:

- 24/24 definitive responses are preserved and hash-bound in the Run 1 evidence archive.
- The frozen deterministic parser evaluated 0 of 20 numerically applicable cases; this is a parser-coverage result and must not be reported as 0% accuracy.
- **Independent manual/analytical recomputation** found that 19/20 numerically applicable cases returned every requested quantitative value correctly. Q195 was the sole requested-field numeric failure.
- Q361 returned all requested outputs correctly but included incorrect supplemental free-fit values.
- 23/24 final verdicts were statistically defensible under attributed independent AI-assisted review; Q195 was the exception.
- 11/12 selected designed contrasts showed defensible verdict-level discrimination in both arms. This is descriptive only: no iid assumption, confidence interval, population inference, or universal competence claim is made.
- Q195 contained a substantive Bayes-denominator error, producing an approximately 17.29-fold overestimate and reversing the verdict.
- Q976 correctly diagnosed future-information leakage and supplied a valid drop-feature repair, but its alternative suggestion to delay scoring until 10:05 changed the stated 10:00 requirement.
- The independent review observed no causal-overreach or unjustified-certainty defect across the 24 responses. This is an attributed semantic observation, not a validated universal score.

## Frozen deterministic result

- Numeric-applicable cases: 20
- Not applicable: 4
- Deterministically evaluated: 0
- Deterministic numeric accuracy: undefined because the evaluated denominator is zero
- Responses present: 24/24

## Final case adjudication summary

| Case | Final status | Credit |
|---|---|---|
| Q142 | PASS | Full |
| Q195 | MATERIAL DEFECT | Failing |
| Q216 | PASS | Full |
| Q361 | MINOR DEFECT | Partial |
| Q731 | AMBIGUOUS / RETAIN DISSENT | Full requested-field credit; semantic qualification retained |
| Q976 | MINOR DEFECT | Partial |

The detailed issue, consequence, repair, reference risk, and reviewer-dissent findings appear in `evidence/FINAL_ADJUDICATION.md`.
