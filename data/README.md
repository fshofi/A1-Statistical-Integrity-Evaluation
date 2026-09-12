# Public cases

`cases.jsonl` is a byte-identical publication copy of the 24 public cases in
`baseline/a1_revision_bundle/a1_blind_check/cases.jsonl`.

Only `scenario`, `data`, and `task` may be supplied to a model during response
generation. Reference answers, checker source, revision notes, and evaluation
labels must remain outside the model context. `tests/test_cases.py` prevents the
public copy from drifting away from the frozen source.
