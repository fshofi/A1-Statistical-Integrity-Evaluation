# A1 sample findings memo
Illustrative portfolio work; author: Shofi Ahmed Uddin.

## Decision
Q195 has a material numerical error. Preserve the response and correct the calculation before reusing its conclusion.

## Reproducible calculation
Sensitivity 0.90, specificity 0.95, prevalence 0.05:
P(fault | negative) = (0.10 × 0.05) / ((0.10 × 0.05) + (0.95 × 0.95)) = 0.005509641873.
The recorded answer is 0.095238095. Numerical agreement fails. Causal/semantic judgments are a separate review.

## Coverage and limits
The new derived labelled parser evaluates 17/20 numeric-applicable cases: 16 pass, Q195 fails, 3 abstain. It does not infer units or parse arbitrary equations. Historical Run 1 files and frozen parser remain unchanged.
