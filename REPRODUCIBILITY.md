# Reproducibility

## Reproducible

- Stored source and evidence archives by SHA-256
- Frozen cases, references, scoring policy, parser, schemas, and tests
- Exact visible prompts and preserved model responses
- Run manifests and case-level prompt/response hashes
- Original trace inventory and privately retained rollout evidence
- Frozen checker/replay execution against the stored Run 1 responses
- Publication package contents through `SHA256_MANIFEST.txt`

The Amendment 1.1 processor was replayed against the stored Run 1 inputs during final adjudication. The generated summary and derived scoring JSONL were byte-identical to the packaged Run 1 outputs.

## Not exactly reproducible

- Future model generations
- Hidden provider system/developer instructions
- Unexposed sampling parameters
- Backend model build identity behind the unpinned alias
- Cryptographic proof of context isolation or absence of all hidden platform context

Strongest truthful statement:

> A1 provides replayable stored evidence and a hash-verifiable frozen processing environment. Its historical prompts, responses, provenance records, and derived outputs can be verified; identical future model generations cannot be guaranteed because provider-managed context, sampling controls, and backend build identity were not fully exposed.

The V1.2.1 separated review adds model-assisted challenge evidence, not an independent reproducibility guarantee. The later Abacus reviewer reproduced the packaged checks in its environment, but the underlying model identity was undisclosed and the received report did not match its printed self-hash. The Gemini lane did not execute repository code.

## Replay

From the repository root, with Python 3.11+:

```text
python scripts/verify_hashes.py
python scripts/verify_test_inventory.py
python -m unittest discover -s tests -p "test_*.py"
python scripts/run_v1_2_hardening.py
python scripts/run_benchmark.py runs/run1/raw_model_responses.jsonl --run-manifest runs/run1/run_manifest.json --output-dir replay-output
python scripts/publication_gate.py
```

## Public-release note

Public-release note: this repository is a publication-safe derivative of the frozen evidence package. Compiled Python caches and local filesystem identifiers were excluded/redacted for privacy and security. V1.2.1 adds reconciliation evidence and claim refinements; the underlying benchmark evidence, statistical results, adjudication and source logic were not altered. Historical freeze hashes are retained in the provenance record.
