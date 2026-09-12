# Reproduce the controlled design and verify this package

1. Verify the frozen Amendment 1.1 ZIP SHA-256 is `01e7092db82c1d3750ecc88fcb3fb12cc89436ef31584322987f35e878602d75`.
2. Verify `SHA256_MANIFEST.txt` against every packaged file except the manifest itself.
3. Confirm all 24 prompts use `user_prompt_template.txt` and match the exact public cases embedded in `run_manifest.json`.
4. Confirm every prompt and response hash against `definitive_task_provenance.json` and `run_manifest.json`.
5. Use OpenAI `gpt-5.6-luna`, reasoning `low`, with one fresh independent projectless task per case and no inherited prior-case turns.
6. Supply no benchmark material other than the neutral instruction and one public case ID/scenario/data/task.
7. Preserve each response verbatim before parsing. Do not retry weak or incorrect content; retry only transport/runtime failure and record it.
8. Validate `run_manifest.json` with the frozen Amendment 1.1 validator, then run the frozen `scripts/run_benchmark.py` against `raw_model_responses.jsonl`.
9. Keep raw response, parsing, deterministic scoring, semantic review, adjudication, and publication claims separate.

Exact generated wording is not guaranteed to repeat because sampling controls and exact platform prompts were `UNAVAILABLE / NOT EXPOSED`. This procedure reproduces the controlled design; the packaged hashes verify the recovered historical execution.
