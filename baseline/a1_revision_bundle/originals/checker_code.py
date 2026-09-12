#!/usr/bin/env python3
"""
checker_code.py — A1 blind statistical check (24 synthetic cases).
All derivations computed from first principles (stdlib only; exact rational
arithmetic via fractions.Fraction where values are rational).
Reads : a1_blind_check/cases.jsonl, a1_blind_check/manifest.json
Writes: checker_answers.jsonl
Prints: full execution log to stdout.
"""
import json, hashlib, platform, sys, datetime, math
from fractions import Fraction as F

CASES_PATH    = "a1_blind_check/cases.jsonl"
MANIFEST_PATH = "a1_blind_check/manifest.json"
OUT_PATH      = "checker_answers.jsonl"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()

def f12(x):
    return f"{float(x):.12f}"

log = []
def emit(s=""):
    print(s)
    log.append(s)

# ---------------------------------------------------------------- header
emit("=" * 78)
emit("A1 BLIND STATISTICAL CHECK — EXECUTION LOG")
emit("=" * 78)
emit(f"timestamp_utc : {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
emit(f"python        : {sys.version.split()[0]} ({platform.python_implementation()})")
emit(f"platform      : {platform.platform()}")
emit(f"executable    : {sys.executable}")
emit(f"cases_sha256  : {sha256_file(CASES_PATH)}")
with open(MANIFEST_PATH) as fh:
    manifest = json.load(fh)
expected = manifest.get("public_cases_sha256")
actual   = sha256_file(CASES_PATH)
emit(f"manifest_sha256_expected : {expected}")
emit(f"manifest_sha256_match    : {expected == actual}")
emit(f"manifest_status          : {manifest.get('status')}")
emit(f"manifest_contains_answers: {manifest.get('contains_author_answers')}")

with open(CASES_PATH) as fh:
    cases = {json.loads(l)["id"]: json.loads(l) for l in fh.read().strip().split("\n")}
emit(f"case_count    : {len(cases)}")
emit("")

answers = []
def record(case_id, numeric, derivation, assumptions, uncertainty, conclusion,
           minimum_repair, execution_status, ambiguities):
    obj = {
        "case_id": case_id,
        "numeric": numeric,
        "derivation": derivation,
        "assumptions": assumptions,
        "uncertainty": uncertainty,
        "conclusion": conclusion,
        "minimum_repair": minimum_repair,
        "execution_status": execution_status,
        "ambiguities": ambiguities,
    }
    assert obj["derivation"] and obj["conclusion"], "nonempty derivation/conclusion required"
    answers.append(obj)
    emit("-" * 78)
    emit(f"[{case_id}] execution_status={execution_status}")
    for k, v in numeric.items():
        emit(f"    {k} = {v['value']}  ({v['unit']})")
    emit(f"    conclusion: {conclusion}")

# ---------------------------------------------------------------- OLS core
x  = [F(v) for v in [1, 2, 3, 4, 5]]
y  = [F(v) for v in [2, 4, 5, 4, 5]]
n  = F(5)
xbar = sum(x) / n            # 3
ybar = sum(y) / n            # 4
Sxy  = sum((xi - xbar) * (yi - ybar) for xi, yi in zip(x, y))   # 6
Sxx  = sum((xi - xbar) ** 2 for xi in x)                        # 10
slope_free     = Sxy / Sxx                                    # 3/5 = 0.6
intercept_free = ybar - slope_free * xbar                     # 11/5 = 2.2
rss_free = sum((yi - (intercept_free + slope_free * xi)) ** 2 for xi, yi in zip(x, y))  # 12/5
slope_c = sum(xi * yi for xi, yi in zip(x, y)) / sum(xi * xi for xi in x)               # 66/55 = 6/5
rss_c   = sum((yi - slope_c * xi) ** 2 for xi, yi in zip(x, y))                          # 34/5 = 6.8

# ---- Q142 : free OLS, evaluate at x = 8 (outside [1,5])
fit8 = intercept_free + slope_free * F(8)   # 7
record(
    "Q142",
    {"slope": {"value": float(slope_free), "unit": "y-units per x-unit"},
     "intercept": {"value": float(intercept_free), "unit": "y-units"},
     "fitted_value": {"value": float(fit8), "unit": "y-units"}},
    f"OLS with intercept: slope = Sxy/Sxx = 6/10 = {f12(slope_free)}; intercept = ybar - slope*xbar = 4 - 0.6*3 = {f12(intercept_free)}; "
    f"fitted(8) = 2.2 + 0.6*8 = {f12(fit8)}. Observed predictor range is [1, 5]; x = 8 lies outside it, so the evaluation is EXTRAPOLATION, not interpolation. "
    "A fitted value is a model-based conditional mean estimate at an unobserved point; it is not a guaranteed future observation (irreducible noise plus model-form risk, amplified outside the data range).",
    ["Linear conditional-mean model", "OLS with intercept as specified", "x-range [1,5] defines 'observed predictor range'"],
    "Arithmetic exact (rational). No uncertainty statement is possible for the x=8 prediction without additional distributional assumptions; none were given.",
    "Numerics correct under OLS (slope 0.6, intercept 2.2, fitted(8) = 7.0), but the analyst's description is wrong: x = 8 is extrapolation beyond the observed predictor range, and the fitted value carries no guarantee about any future observation.",
    "Relabel the evaluation as extrapolation and present the fitted value as a model prediction with unstated uncertainty, not as interpolation or a guaranteed outcome.",
    "EXECUTED",
    ["None material; the mislabel is unambiguous given target_x = 8 > 5."])

# ---- Q586 : free OLS, evaluate at x = 3 (inside [1,5])
fit3 = intercept_free + slope_free * F(3)   # 4
record(
    "Q586",
    {"slope": {"value": float(slope_free), "unit": "y-units per x-unit"},
     "intercept": {"value": float(intercept_free), "unit": "y-units"},
     "fitted_value": {"value": float(fit3), "unit": "y-units"}},
    f"Same OLS fit: slope = {f12(slope_free)}, intercept = {f12(intercept_free)}; fitted(3) = 2.2 + 0.6*3 = {f12(fit3)}. "
    "x = 3 lies inside the observed predictor range [1, 5] (it is an observed design point), so 'interpolation within the observed predictor range' is an accurate description. "
    "Even so, the fitted value is the estimated conditional mean, not a guaranteed observation: at x = 3 the observed y is 5 while the fit gives 4.0, a residual of 1.0.",
    ["Linear conditional-mean model", "OLS with intercept as specified"],
    "Arithmetic exact (rational). Prediction uncertainty for a new observation at x=3 is not quantified without a noise model.",
    "The interpolation description is correct for x = 3, and the fitted value is 4.0; however the fitted value must still be distinguished from a guaranteed future observation (the observed y at x = 3 was 5, not 4.0).",
    "None required for the interpolation label; only avoid presenting the fitted value as a guaranteed observation.",
    "EXECUTED",
    ["None material."])

# ---- Q361 : zero-intercept OLS; claim it also minimizes RSS over free-intercept lines
record(
    "Q361",
    {"selected_slope": {"value": float(slope_c), "unit": "y-units per x-unit"},
     "selected_intercept": {"value": 0, "unit": "y-units"},
     "selected_rss": {"value": float(rss_c), "unit": "squared y-units"}},
    f"Constrained fit (intercept fixed at 0): slope = sum(xy)/sum(x^2) = 66/55 = {f12(slope_c)}; RSS = sum((y - 1.2x)^2) = {f12(rss_c)}. "
    f"Unconstrained OLS gives slope = {f12(slope_free)}, intercept = {f12(intercept_free)}, RSS = {f12(rss_free)}. Since {f12(rss_c)} > {f12(rss_free)}, "
    "the constrained fit does NOT minimize RSS over the larger class of lines with a freely chosen intercept; the constrained class is a strict subset and the unconstrained minimizer (intercept 2.2 != 0) lies outside it.",
    ["RSS is the objective in both classes", "Free-intercept class strictly contains the zero-intercept class"],
    "Arithmetic exact (rational); no sampling uncertainty involved in an optimization fact.",
    "The claim is false: the zero-intercept fit (slope 1.2, RSS 6.8) is dominated by the free-intercept OLS fit (slope 0.6, intercept 2.2, RSS 2.4), so it is not the minimizer over all straight lines with a freely chosen intercept.",
    "If the goal is unconstrained RSS minimization, use the free-intercept OLS fit (slope 0.6, intercept 2.2, RSS 2.4); otherwise present the zero-intercept fit explicitly as a constrained optimum, not as the free-intercept minimizer.",
    "EXECUTED",
    ["None; the two optima differ strictly (2.4 < 6.8)."])

# ---- Q795 : free-intercept OLS; claim it minimizes RSS over all free-intercept lines
record(
    "Q795",
    {"selected_slope": {"value": float(slope_free), "unit": "y-units per x-unit"},
     "selected_intercept": {"value": float(intercept_free), "unit": "y-units"},
     "selected_rss": {"value": float(rss_free), "unit": "squared y-units"}},
    f"Free-intercept OLS: slope = Sxy/Sxx = {f12(slope_free)}, intercept = {f12(intercept_free)}, RSS = {f12(rss_free)}. "
    "RSS(b0, b1) is a strictly convex quadratic in (b0, b1) here (Sxx = 10 > 0), so the normal-equation solution is the unique global minimizer over all straight lines with a freely chosen intercept. The claim holds by construction of OLS.",
    ["RSS objective", "x has nonzero variance (Sxx = 10 > 0), giving a unique minimizer"],
    "Arithmetic exact (rational); optimization fact, no sampling uncertainty.",
    "The claim is correct: the free-intercept least-squares fit (slope 0.6, intercept 2.2, RSS 2.4) is by definition the unique RSS minimizer over the class of all straight lines with a freely chosen intercept.",
    "None required.",
    "EXECUTED",
    ["None."])

# ---------------------------------------------------------------- Bayes: fault given negative
def p_fault_neg(prev, sens, spec):
    num = (1 - sens) * prev
    den = num + spec * (1 - prev)
    return num / den

# ---- Q195 : prev 0.05
r195 = p_fault_neg(F(5, 100), F(9, 10), F(95, 100))   # 2/363
record(
    "Q195",
    {"fault_given_negative": {"value": float(r195), "unit": "proportion (0 to 1)"}},
    f"P(F|neg) = (1-Se)*prev / [(1-Se)*prev + Sp*(1-prev)] = (0.1*0.05)/(0.005 + 0.95*0.95) = 0.005/0.9075 = 2/363 = {f12(r195)} "
    f"(about 0.550964%). This is below 1%.",
    ["Sensitivity, specificity and prevalence are exact population parameters as stated", "Randomly selected unit"],
    "Exact rational value (2/363); no sampling uncertainty because parameters are stipulated exact.",
    f"The claim is supported: P(fault | negative) = {f12(r195)} = 0.550964% < 1%.",
    "None required.",
    "EXECUTED",
    ["None."])

# ---- Q624 : prev 0.60
r624 = p_fault_neg(F(60, 100), F(9, 10), F(95, 100))  # 3/22
record(
    "Q624",
    {"fault_given_negative": {"value": float(r624), "unit": "proportion (0 to 1)"}},
    f"P(F|neg) = (0.1*0.60)/(0.06 + 0.95*0.40) = 0.06/0.44 = 3/22 = {f12(r624)} (about 13.636364%). This is far above 1%.",
    ["Exact population parameters as stated", "Randomly selected unit"],
    "Exact rational value (3/22); no sampling uncertainty.",
    f"The claim is false: with prevalence 0.60, P(fault | negative) = {f12(r624)} = 13.636364%, roughly fourteen times the claimed 1% ceiling.",
    f"Correct the claim to P(fault | negative) = {f12(r624)} (3/22); the '<1%' statement holds only at low prevalence such as the 0.05 case.",
    "EXECUTED",
    ["None."])

# ---------------------------------------------------------------- PPV
def ppv(prev, sens, fpr):
    num = sens * prev
    den = num + fpr * (1 - prev)
    return num / den

# ---- Q317 : fpr 0.01
p317 = ppv(F(3, 100), F(8, 10), F(1, 100))            # 240/337
record(
    "Q317",
    {"ppv": {"value": float(p317), "unit": "proportion (0 to 1)"}},
    f"PPV = P(defective | positive) = Se*prev / [Se*prev + FPR*(1-prev)] = (0.8*0.03)/(0.024 + 0.01*0.97) = 0.024/0.0337 = 240/337 = {f12(p317)} "
    f"(about 71.216617%). Since {f12(p317)} > 0.5, a positively tested item is more likely defective than nondefective.",
    ["Exact population parameters as stated", "Randomly drawn item", "FPR = 1 - specificity = 0.01"],
    "Exact rational value (240/337); no sampling uncertainty.",
    f"The claim is supported: PPV = {f12(p317)} = 71.216617% > 50%, so a positive result is more likely defective than nondefective under these parameters.",
    "None required.",
    "EXECUTED",
    ["None."])

# ---- Q842 : fpr 0.10
p842 = ppv(F(3, 100), F(8, 10), F(1, 10))             # 24/121
record(
    "Q842",
    {"ppv": {"value": float(p842), "unit": "proportion (0 to 1)"}},
    f"PPV = (0.8*0.03)/(0.024 + 0.10*0.97) = 0.024/0.121 = 24/121 = {f12(p842)} (about 19.834711%). Since {f12(p842)} < 0.5, "
    "a positively tested item is more likely NONdefective (a false positive) than defective.",
    ["Exact population parameters as stated", "Randomly drawn item", "FPR = 0.10"],
    "Exact rational value (24/121); no sampling uncertainty.",
    f"The claim is false: with false-positive probability 0.10, PPV = {f12(p842)} = 19.834711% < 50%; a positive result is roughly four times as likely to be a false positive as a true defect.",
    f"Correct the claim: PPV = {f12(p842)}; the 'more likely defective' statement holds only at the lower false-positive rate (0.01).",
    "EXECUTED",
    ["None."])

# ---------------------------------------------------------------- causal risk difference
rd = F(36, 60) - F(24, 60)                            # 1/5 = 0.2
se_rd = math.sqrt(0.6 * 0.4 / 60 + 0.4 * 0.6 / 60)
ci_lo, ci_hi = 0.2 - 1.959963984540054 * se_rd, 0.2 + 1.959963984540054 * se_rd

# ---- Q216 : random assignment
record(
    "Q216",
    {"risk_difference": {"value": float(rd), "unit": "proportion (0 to 1)"}},
    f"RD = pA - pB = 36/60 - 24/60 = 0.6 - 0.4 = {f12(rd)}. Under fair random allocation with complete follow-up, consistent treatment "
    "definitions and no interference (SUTVA/consistency stipulated), the unadjusted difference in means is a design-justified unbiased "
    "estimate of the average treatment effect in the study population (randomization makes treatment independent of potential outcomes "
    "in expectation). This is an ESTIMATE, not proof of a nonzero effect: the Wald SE is "
    f"sqrt(0.6*0.4/60 + 0.4*0.6/60) = {se_rd:.12f}, giving an approximate 95% CI of ({ci_lo:.6f}, {ci_hi:.6f}).",
    ["Random assignment as stipulated", "SUTVA: no interference and consistent treatment definitions (stipulated)", "Complete follow-up (stipulated)",
     "'Average causal effect' read as the finite-population ATE; the same point estimate targets the superpopulation ATE"],
    f"Estimation uncertainty remains: SE = {se_rd:.6f}, approx. 95% Wald CI ({ci_lo:.6f}, {ci_hi:.6f}); a nonzero effect is not proven.",
    "The claim is supported as an estimation statement: with random assignment and the stipulated conditions, the unadjusted risk difference 0.2 is a design-justified estimate of the average causal effect; it is not proof that the true effect is nonzero.",
    "None for the design-justified estimation claim; add an uncertainty statement (SE/CI or randomization-based p-value) and keep 'estimate' rather than 'proof' language.",
    "EXECUTED",
    ["'Study population' may be read as finite-sample or superpopulation; the point estimate is the same either way."])

# ---- Q854 : participant choice
record(
    "Q854",
    {"risk_difference": {"value": float(rd), "unit": "proportion (0 to 1)"}},
    f"RD = 36/60 - 24/60 = {f12(rd)} numerically, but assignment was by participant choice, so treatment is plausibly confounded with "
    "self-selection (preferences, baseline prognosis). Randomization-based identification is absent and no adjustment set or "
    "identification strategy is stated; the stipulated complete follow-up/consistency/no-interference conditions do not remove "
    "confounding by indication. The unadjusted difference is therefore an associational contrast, not a design-justified causal estimate.",
    ["Participant-choice assignment as stipulated", "No stated adjustment set, instrument, or other identification strategy"],
    f"Same sampling uncertainty as the randomized case (SE = {se_rd:.6f}) PLUS unquantified confounding bias of unknown sign and size.",
    "The causal-estimation claim is not supported: the unadjusted risk difference 0.2 describes an association under self-selection; without randomization or a stated identification/adjustment strategy it cannot be used as a design-justified estimate of the average causal effect.",
    "Restrict the claim to a descriptive association, or obtain design-justified identification (randomize, or specify and defend an adjustment/identification strategy); report the estimand and assumptions explicitly.",
    "EXECUTED",
    ["The numeric RD is unaffected; only its interpretation changes."])

# ---------------------------------------------------------------- precision/recall
rec = F(0, 30)   # TP/(TP+FN) = 0/30
# ---- Q251 : analyst says precision undefined
record(
    "Q251",
    {"recall": {"value": float(rec), "unit": "proportion (0 to 1)"},
     "predicted_positive_count": {"value": 0, "unit": "count"}},
    "Confusion counts: TP=0, FP=0, FN=30, TN=170. Recall = TP/(TP+FN) = 0/30 = 0.000000000000. Predicted positives = TP+FP = 0. "
    "Precision = TP/(TP+FP) = 0/0, which is indeterminate; with no zero-division convention adopted, precision is undefined. "
    "The analyst's statement ('positive-class precision is undefined') is correct.",
    ["Precision definition TP/(TP+FP) as stated", "No zero-division policy (zero_division_policy = null)"],
    "Exact arithmetic; no sampling uncertainty in the confusion-matrix quantities as stipulated.",
    "Correct: with zero predicted positives, precision is 0/0 and therefore undefined under the stated definition and absent convention; recall is 0.0 and the predicted-positive count is 0.",
    "None required; the statement is accurate.",
    "EXECUTED",
    ["Some libraries impute 0.0 with a warning by convention; the case explicitly adopts no such convention, so 'undefined' stands."])

# ---- Q694 : analyst says precision zero
record(
    "Q694",
    {"recall": {"value": float(rec), "unit": "proportion (0 to 1)"},
     "predicted_positive_count": {"value": 0, "unit": "count"}},
    "Same counts: TP=0, FP=0, FN=30, TN=170. Recall = 0/30 = 0.000000000000; predicted positives = 0. Precision = 0/0 is "
    "indeterminate, not zero: 0/0 has no defined value, whereas zero would require TP = 0 with TP+FP > 0. With no zero-division "
    "convention adopted, reporting precision as zero is a category error that masks the fact that the classifier never predicted "
    "positive at all.",
    ["Precision definition TP/(TP+FP) as stated", "No zero-division policy (zero_division_policy = null)"],
    "Exact arithmetic; no sampling uncertainty.",
    "Incorrect: precision is undefined (0/0, no predicted positives), not zero; recall is 0.0 and the predicted-positive count is 0.",
    "Report precision as 'undefined (0/0; classifier predicted no positives)', or explicitly adopt and disclose a zero-division convention before assigning it a numeric value.",
    "EXECUTED",
    ["If an explicit convention (e.g., 0.0) were adopted and disclosed, a numeric report would be permissible; none was adopted here."])

# ---------------------------------------------------------------- Bonferroni
def bonf(p, m):
    return min(1.0, p * m)

# ---- Q268 : m = 1
a268 = bonf(F(12, 1000), 1)
record(
    "Q268",
    {"adjusted_p": {"value": float(a268), "unit": "proportion (0 to 1)"}},
    f"Bonferroni adjusted p = min(1, m * p_min) = min(1, 1 * 0.012) = {f12(a268)}. Comparison: {f12(a268)} <= alpha = 0.05, so the "
    "Bonferroni procedure rejects. With a single prespecified hypothesis, Bonferroni coincides with the ordinary level-0.05 test.",
    ["Valid p-value as stipulated", "Familywise alpha 0.05", "m = 1 hypothesis"],
    "Exact arithmetic; decision deterministic given the stated p-value.",
    "The proposal is valid: with one hypothesis the Bonferroni-adjusted p-value is 0.012 <= 0.05, so rejecting the null under Bonferroni at familywise alpha 0.05 is correct.",
    "None required.",
    "EXECUTED",
    ["None; m = 1 makes the adjustment vacuous."])

# ---- Q903 : m = 20
a903 = bonf(F(12, 1000), 20)
record(
    "Q903",
    {"adjusted_p": {"value": float(a903), "unit": "proportion (0 to 1)"}},
    f"Bonferroni adjusted p = min(1, 20 * 0.012) = {f12(a903)}. Comparison: {f12(a903)} > alpha = 0.05, so Bonferroni does NOT reject "
    "(equivalently, the per-comparison threshold is 0.05/20 = 0.0025 and 0.012 > 0.0025).",
    ["Valid p-values as stipulated", "Familywise alpha 0.05", "m = 20 prespecified hypotheses"],
    "Exact arithmetic; decision deterministic given the stated p-value.",
    "The proposal is invalid: the Bonferroni-adjusted p-value is 0.24 > 0.05, so the null with the smallest p-value cannot be rejected at familywise alpha 0.05 under Bonferroni.",
    "Do not reject under Bonferroni; if rejection is scientifically required, prespecify a less conservative FWER/FDR procedure and justify it rather than rejecting with adjusted p = 0.24.",
    "EXECUTED",
    ["None."])

# ---------------------------------------------------------------- cost/accuracy
def cost_acc(d, cfp, cfn):
    cost = d["fp"] * cfp + d["fn"] * cfn
    acc  = F(d["tp"] + d["tn"], d["tp"] + d["tn"] + d["fp"] + d["fn"])
    return cost, acc
A = {"tp": 18, "fp": 18, "fn": 2, "tn": 62}
B = {"tp": 12, "fp": 2, "fn": 8, "tn": 78}

# ---- Q423 : costs 1 / 1
ca, aa = cost_acc(A, 1, 1); cb, ab = cost_acc(B, 1, 1)
record(
    "Q423",
    {"cost_a": {"value": ca, "unit": "cost units"},
     "cost_b": {"value": cb, "unit": "cost units"},
     "accuracy_a": {"value": float(aa), "unit": "proportion (0 to 1)"},
     "accuracy_b": {"value": float(ab), "unit": "proportion (0 to 1)"}},
    f"Cost (FP=1, FN=1): A = 18*1 + 2*1 = {ca}; B = 2*1 + 8*1 = {cb}. Accuracy: A = (18+62)/100 = {f12(aa)}; B = (12+78)/100 = {f12(ab)}. "
    f"Under the stated equal-cost function, B has the lower total cost ({cb} < {ca}) and also the higher accuracy; the two criteria agree here.",
    ["Stated cost function (FP = 1, FN = 1; correct predictions free)", "Evaluation on the same 100 labeled cases"],
    "Exact arithmetic on stipulated counts; no sampling variability modeled.",
    "The recommendation is supported on this sample under the stated cost function: B costs 10 units versus A's 20, and B is also the more accurate model (0.9 vs 0.8).",
    "None required for the stated sample and cost function; note that the conclusion is sample- and cost-specific, not a general superiority claim.",
    "EXECUTED",
    ["Recommendation is conditional on the 100-case sample and unit costs; no generalization was requested."])

# ---- Q768 : costs 1 / 10
ca2, aa2 = cost_acc(A, 1, 10); cb2, ab2 = cost_acc(B, 1, 10)
record(
    "Q768",
    {"cost_a": {"value": ca2, "unit": "cost units"},
     "cost_b": {"value": cb2, "unit": "cost units"},
     "accuracy_a": {"value": float(aa2), "unit": "proportion (0 to 1)"},
     "accuracy_b": {"value": float(ab2), "unit": "proportion (0 to 1)"}},
    f"Cost (FP=1, FN=10): A = 18*1 + 2*10 = {ca2}; B = 2*1 + 8*10 = {cb2}. Accuracy: A = {f12(aa2)}; B = {f12(ab2)}. "
    f"B is more accurate but far costlier ({cb2} > {ca2}) because it misses 8 positives at 10 units each. The analyst's recommendation "
    "appears to follow accuracy rather than the stated cost function.",
    ["Stated cost function (FP = 1, FN = 10)", "Evaluation on the same 100 labeled cases"],
    "Exact arithmetic on stipulated counts; no sampling variability modeled.",
    f"The recommendation is incorrect under the stated cost function: B's total cost is {cb2} units versus A's {ca2}; A is the lower-total-cost model on this sample even though B has higher accuracy (0.9 vs 0.8).",
    f"Recommend model A under the stated costs ({ca2} < {cb2}), or restate the decision rule if accuracy rather than total cost was intended.",
    "EXECUTED",
    ["None material; accuracy and cost rank the models oppositely here."])

# ---------------------------------------------------------------- confidence intervals
z = 1.959963984540054
sigma, nrec, mean = 6.0, 36, 12.0
se36 = sigma / math.sqrt(nrec)
lo, hi = mean - z * se36, mean + z * se36

# ---- Q459 : independent units
record(
    "Q459",
    {"nominal_lower": {"value": lo, "unit": "measurement units"},
     "nominal_upper": {"value": hi, "unit": "measurement units"}},
    f"Stated formula: 12 +/- 1.959963984540054 * 6/sqrt(36) = 12 +/- {z*se36:.12f}, giving ({lo:.12f}, {hi:.12f}). "
    "The constant used is the exact 0.975 standard-normal quantile. Because the population is stipulated normal with KNOWN sigma = 6 "
    "and the 36 units are independently sampled (each measured once), the sample mean is exactly normal with SE = 6/6 = 1, so the "
    "z-interval is exactly valid at nominal 95% coverage for the population mean. No correction is required.",
    ["Normal population with known sigma = 6 (stipulated)", "36 independent units, one measurement each (stipulated)", "z taken as given (exact 0.975 quantile)"],
    "Nominal 95% coverage is exact under the stipulated design; the interval estimate itself is random across repeated samples.",
    f"The inference is valid as stated: ({lo:.12f}, {hi:.12f}) is an exactly calibrated 95% confidence interval for the population mean under a normal population with known sigma and 36 independent units.",
    "None required.",
    "EXECUTED",
    ["None material."])

# ---- Q731 : one unit measured 36 times, perfectly correlated
lo1, hi1 = mean - z * sigma, mean + z * sigma
record(
    "Q731",
    {"nominal_lower": {"value": lo, "unit": "measurement units"},
     "nominal_upper": {"value": hi, "unit": "measurement units"}},
    f"Nominal formula output is identical: ({lo:.12f}, {hi:.12f}), since 6/sqrt(36) = 1. However the 36 records are perfectly "
    "correlated repeats of ONE sampled unit, so they carry no independent information about between-unit variability; the effective "
    "sample size is n = 1, not 36, and the divisor sqrt(36) understates the standard error by a factor of 6. The nominal interval "
    "therefore has no valid 95% coverage claim for the population mean. Under this design the honest single-unit interval is "
    f"12 +/- 1.959963984540054 * 6/sqrt(1) = ({lo1:.12f}, {hi1:.12f}), and the proper repair is to sample multiple independent units.",
    ["Perfectly correlated repeats as stipulated", "sigma = 6 describes between-unit spread of unit values (population SD)", "The repeated measurements estimate only the single drawn unit's value"],
    "Nominal interval has unknown (much below 95%) coverage for the population mean; effective n = 1.",
    f"The inference is invalid: ({lo:.12f}, {hi:.12f}) treats 36 perfectly correlated repeats as independent draws; with effective n = 1 the design supports only the much wider interval ({lo1:.6f}, {hi1:.6f}) or, properly, a redesign with independent units.",
    f"Do not divide by sqrt(36); either report the single-unit interval 12 +/- 1.959963984540054*6 = ({lo1:.6f}, {hi1:.6f}) or, preferably, resample multiple independent units and recompute with the true number of independent units.",
    "EXECUTED",
    ["If measurement error of the repeats were nonzero and independent, repeats could reduce measurement error for that one unit's value; perfect correlation as stipulated removes even that benefit beyond the first reading."])

# ---------------------------------------------------------------- Simpson's paradox
a_easy = F(42, 50); a_hard = F(54, 90); b_easy = F(120, 150); b_hard = F(10, 20)
a_pool = F(42 + 54, 50 + 90); b_pool = F(120 + 10, 150 + 20)
strat_note = (f"Within-stratum proportions: A easy = 42/50 = {f12(a_easy)} vs B easy = 120/150 = {f12(b_easy)} (A higher); "
              f"A hard = 54/90 = {f12(a_hard)} vs B hard = 10/20 = {f12(b_hard)} (A higher). "
              f"Pooled: A = 96/140 = 24/35 = {f12(a_pool)}; B = 130/170 = 13/17 = {f12(b_pool)} (B higher). "
              "The reversal arises because B's cases are concentrated in the easy group (150/170) while A's skew hard (90/140) — a classic Simpson's reversal.")

# ---- Q473 : claim A higher pooled
record(
    "Q473",
    {"a_pooled": {"value": float(a_pool), "unit": "proportion (0 to 1)"},
     "b_pooled": {"value": float(b_pool), "unit": "proportion (0 to 1)"}},
    f"A pooled = (42+54)/(50+90) = 96/140 = {f12(a_pool)}; B pooled = (120+10)/(150+20) = 130/170 = {f12(b_pool)}. Since "
    f"{f12(a_pool)} < {f12(b_pool)}, the descriptive claim that A has the higher pooled completion proportion is false. {strat_note} "
    "Because assignment was observational, these observations alone cannot establish a causal advantage in either direction; case mix "
    "(difficulty) is associated with both group and outcome.",
    ["Counts as stipulated", "Observational assignment as stipulated", "Pooled proportion defined as total successes / total cases"],
    "Exact arithmetic on stipulated counts; no causal or sampling inference warranted from the description alone.",
    f"The descriptive claim is false: B's pooled proportion ({f12(b_pool)}) exceeds A's ({f12(a_pool)}), even though A is higher within each difficulty stratum; and as observational data they establish no causal advantage for either arm.",
    "Correct the pooled claim (B is higher); report stratified proportions alongside pooled ones, and avoid any causal reading without an identification strategy.",
    "EXECUTED",
    ["None material; the within-stratum ordering and the pooled ordering genuinely disagree (Simpson's reversal)."])

# ---- Q928 : claim A higher within each group
record(
    "Q928",
    {"a_pooled": {"value": float(a_pool), "unit": "proportion (0 to 1)"},
     "b_pooled": {"value": float(b_pool), "unit": "proportion (0 to 1)"}},
    f"Within-stratum check: A easy {f12(a_easy)} > B easy {f12(b_easy)}; A hard {f12(a_hard)} > B hard {f12(b_hard)}. The descriptive "
    f"claim is true for both difficulty groups. Pooled values (requested): A = {f12(a_pool)}, B = {f12(b_pool)} — note the pooled "
    "ordering reverses, because group B's cases concentrate in the easy stratum. Observational assignment means the within-group "
    "associations still do not establish a causal advantage (unmeasured confounding within strata remains possible).",
    ["Counts as stipulated", "Observational assignment as stipulated", "Within-group comparison defined on the stated difficulty strata"],
    "Exact arithmetic on stipulated counts; causal uncertainty is qualitative and unquantified.",
    f"The within-group descriptive claim is supported (A higher in both strata: {f12(a_easy)} > {f12(b_easy)} and {f12(a_hard)} > {f12(b_hard)}), but the observations alone do not establish a causal advantage, and the pooled comparison reverses (A {f12(a_pool)} < B {f12(b_pool)}).",
    "Keep the stratified claim but state the pooled reversal explicitly and refrain from causal language without an identification strategy.",
    "EXECUTED",
    ["If 'higher' were intended on the pooled sample, the claim would fail; the stratum-wise reading is the correct one."])

# ---------------------------------------------------------------- leakage / availability (analytical)
def t2min(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)

# ---- Q187 : imputer fit on all rows
record(
    "Q187",
    {},
    "Design facts: imputer_fit_scope = 'all_rows' (includes held-out rows); split_before_preprocessing = true; model_label_scope = "
    "'training_rows'. Fitting column means on all rows lets held-out feature values influence the fitted preprocessing parameters, "
    "so the transformation applied to the training data encodes test-set information. This is data leakage in the preprocessing "
    "stage; the held-out evaluation is not isolated and will in general be optimistically biased. The label-handling is clean; the "
    "defect is confined to imputer fitting. Verdict derived analytically from the stated design; no numerical result was requested.",
    ["Column-mean imputation is data-dependent as stated", "Held-out rows contributed to the fitted means as stated"],
    "Deterministic logical verdict given the stated design; bias magnitude is unquantified (depends on data).",
    "The isolation claim is false: the imputer was fitted on all rows including held-out rows, so data-dependent preprocessing is not isolated from test data (train/test leakage through the column means).",
    "Fit the imputer on training rows only, then apply the frozen transform to train and test (equivalently, place the imputer inside a pipeline fit exclusively on training folds).",
    "ANALYTICAL_ONLY",
    ["Effect size of the leakage is data-dependent and not computable from the stated facts."])

# ---- Q639 : imputer fit on training rows only
record(
    "Q639",
    {},
    "Design facts: imputer_fit_scope = 'training_rows'; model_label_scope = 'training_rows'; split_before_preprocessing = true. "
    "All data-dependent fitting (imputation parameters and model) uses training rows only; the frozen imputer merely transforms the "
    "held-out rows. No held-out information influences any fitted component, so the stated isolation claim holds as far as the "
    "described pipeline is concerned. Verdict derived analytically; no numerical result was requested.",
    ["No other data-dependent preprocessing steps exist beyond those stated", "Split itself does not leak (e.g., no duplicate or grouped rows spanning train/test — not stated but required for full isolation)"],
    "Deterministic logical verdict given the stated design.",
    "The isolation claim is supported on the stated facts: imputation and model fitting are confined to training rows, so data-dependent preprocessing is isolated from the held-out data; no material defect is present in the described pipeline.",
    "None required; as good practice, keep all preprocessing inside a training-only pipeline and verify split integrity (no duplicate/grouped records across the split).",
    "ANALYTICAL_ONLY",
    ["Other leakage channels (feature selection on all data, duplicates across the split, grouped/temporal structure) are outside the stated facts."])

# ---- Q542 : snapshot available 09:55, scoring 10:00
record(
    "Q542",
    {},
    f"Timeline check: snapshot first available at 09:55 ({t2min('09:55')} min), required scoring time 10:00 ({t2min('10:00')} min); "
    "09:55 <= 10:00, so the feature exists before scoring. The snapshot is immutable, so the stored historical value is identical to "
    "the value that was knowable at 09:55 on each historical date; using the stored value introduces no look-ahead. Every evaluation "
    "feature could therefore also be supplied at the live scoring time. Verdict derived analytically; no numerical result requested.",
    ["'First available 09:55' holds on every relevant date, including historical ones", "Immutability as stipulated", "All other predictors available by 10:00 as stipulated"],
    "Deterministic logical verdict given the stated timeline.",
    "The availability claim is supported: the immutable snapshot is first available at 09:55, five minutes before the 10:00 scoring time, and its stored historical value equals what was knowable then; no look-ahead or availability defect is present.",
    "None required; optionally enforce point-in-time (as-of) feature retrieval in the feature store to guarantee the property persists.",
    "ANALYTICAL_ONLY",
    ["If 'first available' varied by date or immutability were violated operationally, the conclusion would need re-checking."])

# ---- Q976 : snapshot available 10:05, scoring 10:00
record(
    "Q976",
    {},
    f"Timeline check: snapshot first available at 10:05 ({t2min('10:05')} min), required scoring time 10:00 ({t2min('10:00')} min); "
    "10:05 > 10:00, so the feature does not exist at scoring time. Historical evaluation nevertheless uses its stored value for every "
    "order, which is look-ahead leakage: the evaluation supplies information that would not have been available live, inflating "
    "estimated performance. Immutability does not cure the defect (the value is simply unknowable at 10:00). Verdict derived "
    "analytically; no numerical result requested.",
    ["First-available time of 10:05 applies to the dates being scored", "No earlier equivalent snapshot exists (none stated)"],
    "Deterministic logical verdict given the stated timeline.",
    "The availability claim is false: the snapshot first becomes available at 10:05, after the 10:00 scoring time, so it cannot be supplied live; the historical evaluation leaks future information through this feature.",
    "Smallest operationally valid repair: re-run evaluation using only features available by 10:00 (drop the snapshot or substitute the latest snapshot with first-available time <= 10:00, with documented as-of semantics); alternatively move the scoring time to 10:05 or later.",
    "ANALYTICAL_ONLY",
    ["Which minimal repair (drop/replace vs. delay scoring) is 'smallest' depends on operational constraints not stated."])

# ---------------------------------------------------------------- write + hash
with open(OUT_PATH, "w") as fh:
    for a in answers:
        fh.write(json.dumps(a) + "\n")

emit("=" * 78)
emit(f"wrote {OUT_PATH} with {len(answers)} answer objects")
emit(f"checker_answers_sha256 : {sha256_file(OUT_PATH)}")
emit("END OF LOG")
