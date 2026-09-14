# A1 V1.2 Controlled Reconciliation Report

## Status

- Candidate: `A1-Statistical-Integrity-Benchmark-V1.2.zip`
- Candidate SHA-256: `95057403b9d1ab8b1f8c26ebcc953195c7fe29396d6ccb12599ce4e74fc84703`
- Reconciliation date: 2026-09-14
- Publication disposition: **CONDITIONAL GO - bounded portfolio/research demonstration only**
- Independent-human-validation status: **ABSENT**

This reconciliation does not certify that A1 is defect-free. It determines whether the frozen candidate and its bounded claims are sufficiently controlled for publication as a portfolio demonstration.

## Preserved reviewer evidence

### Lane A - Gemini through OnlyPrompts

- Received raw PDF SHA-256: `4d45d1adf04b4350582ee3221612577f5590be730ff9acfb9ea2961b2eb93d61`
- Reviewer-declared disposition: `CONDITIONAL GO`
- Use in reconciliation: blinded methodological challenge evidence, **not a clean approval**.

### Lane B - Abacus AI Agent

- Received declaration SHA-256: `56ca9927ee5df42983b2d8977f960d2c273a1438297047a5cc066ff89723fd38`
- Received raw report SHA-256: `9b5ea9f3405580e2c2a1575532293b997aeb77f9594348f40e05ed3e8ea28236`
- Reviewer-declared disposition: `CONDITIONAL GO`
- Use in reconciliation: technical reproduction and hostile-claim evidence, qualified because the underlying model identity was not disclosed by the platform.

## Convergent findings

Both lanes support the following conclusions:

1. Q195 contains a material failure by the evaluated model. The correct value is `0.005509641873` (about 0.551%), so the claim that the probability is below 1% is true. The preserved model response reported `0.095238095` and rejected the claim.
2. The 24 cases are purposively selected and do not establish population-level model competence.
3. Absence of attrition is evidenced only within the declared definitive Run 1 universe; the complete earlier development-attempt universe is unavailable.
4. Publication must retain the distinction between observed outputs and inaccessible hidden model cognition.
5. The appropriate outcome is conditional rather than unconditional approval.

## Lane A nonconformities

The Gemini report is preserved as raw evidence but cannot be treated as a clean final validation report:

1. It recomputed Q195 as `0.0052356`; the correct value is `0.005509641873`.
2. It marked Q795's requested numeric values as incorrect even though `slope=0.6`, `intercept=2.2`, and `RSS=2.4` are correct.
3. It did not identify the incorrect supplemental free-intercept values in Q361. The evaluated response reported `0.4`, `2.8`, and `2.8`; the correct comparator is `0.6`, `2.2`, and `2.4`.
4. It did not identify its exact model/provider/version in the independence declaration.
5. Its printed report SHA-256 does not match the received PDF and cannot be verified as an end-to-end freeze hash.

Disposition: **QUALIFY**. The report demonstrates useful blinded challenge capability, but its aggregate `23/24` statement and clean-approval implication are not adopted.

## Lane B verification and qualifications

Lane B reports:

- frozen candidate hash verified;
- 46/46 tests passed;
- required verification, hardening, security and publication scripts exited successfully;
- all 24 preserved response hashes matched;
- all seven named evidence-chain artifacts matched;
- no hostile bypass succeeded;
- known Q195, Q361, Q731 and Q976 findings were independently reproduced; and
- all five residual limitations were confirmed.

An architect-controlled clean replay previously reproduced the same 46/46 candidate test result, conditional hardening result and security pass. No contradictory execution result was found.

Qualifications:

1. The declaration identifies an Abacus AI Agent/orchestration system but says the underlying model identity was not disclosed. The run must therefore not be publicly described as cryptographically verified Kimi K3 review.
2. The report's printed SHA-256 does not match the received Markdown file. The actual received-file hash is preserved above.
3. Some hostile findings were confirmed through existing tests or inspection; the report is not evidence that every attack was implemented as a wholly new executable exploit.

Disposition: **RETAIN WITH QUALIFICATION**.

## Candidate-level disposition

No new critical repository, integrity, security or claim-control defect was established by the two review lanes. The reviews instead confirmed that A1 preserves and discloses material failures by the evaluated model rather than repairing raw evidence after the fact.

The following known limitations remain mandatory:

1. population representativeness is not established;
2. the prior development-attempt universe is incomplete;
3. discarded alternatives were not systematically captured in Run 1;
4. the 168-record structured semantic-review queue remains unscored;
5. independent human validation is absent;
6. the evaluated model alias is not pinned to a recoverable backend build; and
7. context isolation is procedurally evidenced, not cryptographically proven.

## Publication conditions

Publication may proceed only if all of the following remain true:

1. The frozen candidate bytes and SHA-256 remain unchanged.
2. Q195 remains reported as a material evaluated-model failure; it is not silently corrected in the raw response.
3. Q361 remains reported as a supplemental-calculation defect despite its surviving verdict.
4. The five formal residual flags remain visible, with model pinning and procedural context isolation also disclosed where reproducibility is discussed.
5. Neither reviewer is described as independent human or institutional validation.
6. The Abacus lane is described as an Abacus AI Agent review with undisclosed underlying model identity unless verifiable platform provenance is later supplied.
7. Gemini's raw report is not presented as an error-free statistical certification.
8. Public claims remain limited to selected-case portfolio/research demonstration, evidence governance, reproducibility controls and hostile-test behavior.

## Permitted wording

> A1 is a bounded statistical-integrity portfolio demonstration. Its V1.2.1 release candidate passed 52 automated controls: 46 benchmark and hostile-hardening tests plus six publication-reconciliation controls. It underwent separated, blinded model-assisted methodological and technical challenge. The process preserved reviewer disagreement and known evaluated-model failures. It is not a population benchmark, deployment-performance claim, independent human validation or institutional certification.

## Prohibited wording

- defect-free;
- independently human validated;
- institutionally certified;
- representative model benchmark;
- proof of general statistical competence;
- client deployment performance evidence;
- cryptographically proven context isolation; or
- verified Kimi K3 review without recoverable model provenance.

## Final state

**CONDITIONAL GO** for controlled public portfolio publication after the reconciliation statement and exact claim boundary are incorporated into the publication package. **NO-GO** for operational deployment claims, population inference, independent-validation claims or removal of the disclosed limitations.
