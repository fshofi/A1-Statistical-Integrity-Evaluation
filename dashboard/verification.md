# Current verification — 13 November 2026

60 tests executed: 59 pass; 1 ERROR because the public checkout lacks frozen reviewer receipts. The receipt check has not been disabled or relabelled as a pass. This also affects the ability to substantiate the historical release review. All 5 new parsing tests pass. Derived parser evaluates 17/20 numeric cases, with 16 pass and Q195 fail. Source responses and historical scores unchanged. Do not advertise an all-green current suite.

Raw test output: `../evidence/client_readiness/unit_tests.txt`.

Test log checkout prefixes are normalised for public sharing. Browser checks: A1 numeric error → REPAIR REQUIRED; A2 leakage → DATA_QUALITY_FAILURE; A3 contradiction → SAFE_STOP and paraphrase → INSUFFICIENT_EVIDENCE, publication false. Desktop rendering inspected; narrow-screen behaviour not interactively tested.
