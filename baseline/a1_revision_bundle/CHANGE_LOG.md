# A1 Checker — Revision 1 Change Log

**Stage**: Unblinded targeted correction following `ABACUS_TARGETED_REVISION.txt`.  
**Originals preserved**: `checker_code.py`, `checker_answers.jsonl`, `checker_execution_log.txt`  
**Revised outputs**: `checker_code_rev1.py`, `checker_answers_rev1.jsonl`, `checker_execution_log_rev1.txt`  
**Numeric values altered**: 0 of 40 (all original numeric quantities preserved exactly).  
**New computed quantity added**: `coverage_narrow` for Q731 (2Φ(z/6)−1, EXECUTED).  
**Cases changed**: Q142, Q187, Q216, Q731, Q842, Q854, Q903, Q976.  
**Cases unchanged**: Q195, Q251, Q268, Q317, Q361, Q423, Q459, Q473, Q542, Q586, Q624,
Q639, Q694, Q768, Q795, Q928.

---

## SC-01 — Q187, Q976: directional performance-distortion claim

**Finding**: Leakage establishes an invalid evaluation boundary, but the stated facts do
not establish that performance distortion is optimistic or that performance is inflated.

**Decision: ACCEPT**

**Reasoning**:

For **Q187** (column-mean imputation fitted on all rows): the severity of the leakage
depends on how much the held-out column means differ from the training column means.
If they are close, the imputed values are almost identical to what training-only fitting
would produce, and the distortion of the evaluation metric is small and of indeterminate
sign. "Will in general be optimistically biased" is an overstatement of what can be derived
from the design description alone.

For **Q976** (look-ahead snapshot at 10:05): "inflating estimated performance" assumes
the snapshot is predictive of the scored outcome. If the feature has zero predictive power
relative to the model's other inputs, there is no performance distortion at all. The direction
is not established from the stated facts.

In both cases, leakage is real and the evaluation boundary is invalid; the direction and
magnitude of distortion are data-dependent and unquantified.

**Changes made**:

- **Q187 derivation**: removed "will in general be optimistically biased"; replaced with
  "The direction and magnitude of performance distortion are not established from the stated
  facts: they depend on the specific data and how much the held-out feature means differ from
  training means."
- **Q976 derivation**: removed "inflating estimated performance"; replaced with "The direction
  and magnitude of performance distortion are not established from the stated facts: they depend
  on whether and how predictively the snapshot contributes (a non-predictive feature would cause
  no distortion)."

---

## SC-02 — Q976: 10:05 deadline as a repair option

**Finding**: Moving the required 10:00 prediction deadline to 10:05 changes the task;
operational constraints are explicitly stated.

**Decision: ACCEPT**

**Reasoning**: The case states that the model "must score an order at 10:00". This is an
explicit operational constraint. Proposing to move the deadline to 10:05 substitutes a different
task for the stated one. A valid repair must work within the stated 10:00 constraint: drop the
unavailable feature or substitute one with first-available time ≤ 10:00 and rerun evaluation.

**Changes made**:

- **Q976 minimum_repair**: removed "alternatively move the scoring time to 10:05 or later";
  replaced with a note that moving the deadline changes the task and requires separate operational
  approval. Repair now specifies only drop/substitute options within the 10:00 constraint.

---

## SC-03 — Q903: outcome-driven procedure selection

**Finding**: The minimum_repair language "if rejection is scientifically required, prespecify
a less conservative FWER/FDR procedure and justify it" frames procedure choice as a means to
achieve a desired rejection (outcome-driven). FDR is not interchangeable with FWER.

**Decision: ACCEPT**

**Reasoning**: The phrase "if rejection is scientifically required" logically selects a
procedure to obtain a desired result, which reverses the correct order of inference: procedures
must be selected and justified prospectively, independently of and before examining the results.
Additionally, Bonferroni controls the familywise error rate (FWER); switching to an FDR
procedure changes the error-rate objective and requires separate scientific justification, not
merely a desire to reject.

The conclusion itself is unchanged and correct: under Bonferroni with adjusted p = 0.24 > 0.05,
do not reject.

**Changes made**:

- **Q903 minimum_repair**: removed "if rejection is scientifically required, prespecify a less
  conservative FWER/FDR procedure and justify it rather than rejecting with adjusted p = 0.24";
  replaced with: procedure selection must be prospective and independent of the desired outcome;
  FDR and FWER are distinct objectives; switching error-rate frameworks requires independent
  justification.

---

## SC-04 — Q216, Q854: study-population estimand; SE/CI assumptions

**Finding**: Random assignment does not alone establish superpopulation generalisation.
Equal observed counts do not establish equal sampling uncertainty across randomised and
self-selected designs.

**Decision: ACCEPT (with qualification on Q216 SE/CI)**

### Q216 (random assignment)

**Reasoning**: The assumptions field stated "the same point estimate targets the superpopulation
ATE." This is an additional claim beyond what the case design supports: random assignment within
a fixed study population justifies the finite-sample (study-population) ATE. Extending to the
superpopulation requires treating the study participants as a random sample from a larger
population — an assumption not stated in the case.

The Wald SE/CI figures (SE = 0.089443, CI = (0.024695, 0.375305)) are not implied by random
assignment alone; they require an additional iid Bernoulli outcome model. We keep these figures
as explicitly labelled model-based illustrations, per the instruction "state their additional
modelling assumptions explicitly."

**Changes made**:

- **Q216 assumptions**: removed "the same point estimate targets the superpopulation ATE".
  Estimand is now stated as strictly "finite-sample average treatment effect in the study
  population." Added assumption: "Wald SE/CI additionally require iid Bernoulli outcome model
  (model-based, not design-based)."
- **Q216 derivation**: Wald SE/CI sentences now labelled "model-based illustrations under iid
  Bernoulli assumptions."
- **Q216 uncertainty**: SE/CI now labelled explicitly as model-based.
- **Q216 minimum_repair**: updated to state that any uncertainty statement must specify whether
  it is design-based or model-based, and to restrict the estimand to the study population.

### Q854 (participant choice)

**Reasoning**: The original uncertainty field equated the Wald SE to that of the randomised case
("Same sampling uncertainty as the randomised case…"), which is incorrect. Under participant
choice, the sampling distribution of the unadjusted proportion difference is not equivalent to
that under random assignment. Reporting the same SE formula alongside a note about confounding
bias could mislead: it implies that sampling and confounding uncertainty can simply be added,
which is not the case, and that the Wald formula correctly characterises sampling variability
under the observational design. We remove the SE from the uncertainty field.

**Changes made**:

- **Q854 uncertainty**: removed Wald SE and CI figures; replaced with: "Unquantified confounding
  bias of unknown direction and size. The sampling uncertainty of the unadjusted proportion
  difference cannot be equated to the randomised-case SE: the observational design does not
  support the iid sampling model needed for the Wald formula to represent the relevant source
  of uncertainty, and confounding is not captured by any SE."

---

## SC-05 — Q731: coverage of narrow interval not unknown

**Finding**: Coverage is described as "unknown (much below 95%)" while the derivation assumes
one random draw from a known normal population, under which coverage is analytically computable.

**Decision: ACCEPT**

**Reasoning**: Under the stated model — one unit drawn from N(μ, σ²=36), measured 36 times with
perfect correlation — the drawn value is X = μ + 6Z, Z ~ N(0,1), and x̄ = X. The narrow interval
[X − z·1, X + z·1] covers μ if and only if |X − μ| ≤ z·1, i.e., |6Z| ≤ z, i.e., |Z| ≤ z/6.

Coverage = P(|Z| ≤ z/6) = 2Φ(z/6) − 1 = erf(z/(6√2))  [EXECUTED]

```
z  = 1.959963984540054
z/6 = 0.326660664090009
coverage_narrow = erf(z/(6*sqrt(2))) = 0.256075445069137   (~25.6075%)
reference value = 0.25607544506913693   ✓ (match to 15 d.p.)
```

The wider proposed repair interval [X ± z·σ] has coverage = 2Φ(z) − 1 = 0.95 under the same model.

If the random-draw model is not assumed, coverage of both intervals is formally unspecified;
we now state this assumption explicitly.

**Changes made**:

- **Q731 numeric dict**: added `coverage_narrow` = 0.256075445069137 (proportion), EXECUTED.
- **Q731 derivation**: coverage computation now explicitly stated and executed; random-draw
  model assumption stated for both narrow and wide intervals.
- **Q731 assumptions**: added "Random-draw model assumed: one unit drawn from N(mu, sigma^2=36);
  required for coverage computation of both intervals."
- **Q731 uncertainty**: replaced "unknown (much below 95%)" with computed value
  (~25.6075%) conditional on the random-draw model; noted that coverage is formally
  unspecified without that assumption.
- **Q731 conclusion**: updated to state the computed coverage value.
- **Q731 ambiguities**: added note that the random-draw assumption was not explicitly stated
  in the original case and should be added before model collection.

---

## SC-06 — Q142: 'no uncertainty statement possible' too broad

**Finding**: "No uncertainty statement is possible for the x=8 prediction without additional
distributional assumptions" is too broad; qualitative uncertainty can be described.

**Decision: ACCEPT**

**Reasoning**: The original claim is correct that a *calibrated numerical prediction interval*
is not identified without a distributional assumption (noise model). However, qualitative
uncertainty statements are possible and informative: extrapolation amplifies model-form risk,
the fitted value is a conditional mean estimate subject to irreducible noise, and risk increases
outside the observed predictor range. Saying "no uncertainty statement is possible" forecloses
useful communication that does not require a distributional assumption.

**Changes made**:

- **Q142 uncertainty**: replaced "No uncertainty statement is possible for the x=8 prediction
  without additional distributional assumptions; none were given" with "A calibrated numerical
  prediction interval is not identified by the supplied assumptions (no noise model, no
  distributional form given); qualitative uncertainty can still be described: extrapolation
  amplifies model-form risk and noise uncertainty relative to the observed data range."
- **Q142 minimum_repair**: updated to say the fitted value should be presented as a
  model-based conditional mean estimate "with unidentified prediction uncertainty (no
  distributional assumptions supplied)."

---

## SC-07 — Q842: 'holds only at FPR=0.01' overstates the comparison

**Finding**: The minimum_repair says the 'more likely defective' claim "holds only at the lower
false-positive rate (0.01)". In fact FPR=0.01 is not the unique rate at which PPV > 0.5.

**Decision: ACCEPT**

**Reasoning**: With the other parameters fixed (prevalence = 0.03, sensitivity = 0.8), PPV > 0.5
whenever Se·prev > FPR·(1−prev), i.e., whenever FPR < Se·prev/(1−prev). Computing:

```
FPR_thresh = 0.8 * 0.03 / 0.97 = 0.024742268041...   [EXECUTED]
```

Any FPR below ~0.02474 gives PPV > 0.5 under these parameters; FPR=0.01 is one such value
but is not the unique threshold. The correct framing is "holds in the lower-FPR paired case
(FPR=0.01 vs FPR=0.10)."

**Changes made**:

- **Q842 derivation**: added FPR threshold computation and explanation that PPV > 0.5 whenever
  FPR < Se·prev/(1−prev) ≈ 0.02474.
- **Q842 minimum_repair**: replaced "holds only at the lower false-positive rate (0.01)" with
  "holds in the lower-FPR paired case (FPR=0.01). With these other parameters fixed, PPV > 0.5
  for any FPR < Se·prev/(1−prev) = 0.02474...; FPR=0.01 is not the unique rate giving PPV > 0.5."

---

## Summary table

| Finding | Cases    | Decision | Numeric values changed |
|---------|----------|----------|------------------------|
| SC-01   | Q187, Q976 | ACCEPT | None |
| SC-02   | Q976     | ACCEPT   | None |
| SC-03   | Q903     | ACCEPT   | None |
| SC-04   | Q216, Q854 | ACCEPT | None |
| SC-05   | Q731     | ACCEPT   | coverage_narrow added (new, not a revision of existing) |
| SC-06   | Q142     | ACCEPT   | None |
| SC-07   | Q842     | ACCEPT   | None |

All 40 requested numeric values from the original blind run are preserved exactly.
`coverage_narrow` (Q731, value 0.256075445069137) is a new quantity required by the revision,
not a change to an existing value.

---

# REVISION 2 — TARGETED FINAL REPAIR

Scope constraint: no benchmark redesign; no alteration of unaffected cases; no alteration of validated numerical results. Original blind provenance and all Revision-1 SC-01–SC-07 repairs are preserved.

## R2-01 — REPRODUCIBILITY / PACKAGING

**Decision: ACCEPT / REPAIRED**

The Revision-1 deliverable referenced `a1_blind_check/cases.jsonl` and `a1_blind_check/manifest.json` but did not include them, so a clean extraction could not execute without undeclared external files.

**Changes made**:

- Added the exact original blind `a1_blind_check/cases.jsonl` and `a1_blind_check/manifest.json` to the bundle.
- Verified `cases.jsonl` SHA-256 against the preserved manifest: `79b4feb88561c0d3d46ba0f8f660f21bb997383652ea99a70651bfda6907a2ca` (match = true).
- Changed only path resolution in `revision/checker_code_rev1.py` so inputs and output are resolved relative to the script/bundle location, not the caller's working directory.
- `revision/checker_code_rev2.py` uses the same self-contained repository-relative path structure.
- Revision-1 answers regenerated identically: SHA-256 remained `b94a752f45e7e7e8ab81145c5581f680cf8eee5a86d46fc440d4d9366e3d29a9`.

## R2-02 — Q854 UNCERTAINTY

**Decision: ACCEPT / REPAIRED**

Revision-1 wording was too categorical in implying that participant-choice/observational design itself prevents a conventional Wald standard error from quantifying sampling variability of the observed associational proportion difference.

**Replacement distinction**:

1. A conventional Wald SE may quantify sampling variability of the observed associational proportion difference under additional independent-sampling/Bernoulli assumptions.
2. Those assumptions are not established merely by the participant-choice observational design.
3. Such an SE does not quantify confounding bias; the direction and magnitude of that bias remain unquantified here.
4. Such an SE does not justify causal interpretation.

No Q854 numeric value was changed or added.

## Regression confirmation

- 24 cases compared Revision-1 vs Revision-2.
- Only changed answer field: `Q854.uncertainty`.
- All numeric dictionaries across all 24 cases are identical between Revision-1 and Revision-2.
- All other Revision-1 semantic repairs (SC-01–SC-07) are unchanged.
- All unaffected cases are unchanged.
