"""New derived run only; keeps historical Run 1 evidence unchanged."""
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.parsing import load_policy, numeric_status
from src.labelled_parsing import parse_labelled
from src.checker import load_references

policy = load_policy()
references = {r['case_id']: r for r in load_references()}
rows = []
for record in map(json.loads, (ROOT/'runs/run1/raw_model_responses.jsonl').read_text().splitlines()):
    cid = record['case_id']; cp = policy['cases'][cid]; required = cp['required_numeric_fields']
    parsed = parse_labelled(record['raw_model_response'], required)
    reference = references[cid]
    scores = {f: numeric_status(parsed.values[f]['value'], reference['numeric'][f]['value'], cp['fields'][f]['acceptance'], policy) for f in required if f in parsed.values}
    complete = bool(required) and all(f in scores for f in required)
    status = 'NOT_APPLICABLE' if not required else 'NOT_EVALUATED' if not complete else 'PASS' if all(s['status']=='PASS' for s in scores.values()) else 'FAIL'
    rows.append({'case_id':cid, 'status':status, 'required':required, 'parsed':parsed.values, 'field_scores':scores, 'units':'NOT_INFERRED', 'raw_response_sha256':hashlib.sha256(record['raw_model_response'].encode()).hexdigest()})
summary = {'case_count':len(rows), 'numeric_applicable':sum(bool(r['required']) for r in rows), 'evaluated':sum(r['status'] in ('PASS','FAIL') for r in rows), 'passed':sum(r['status']=='PASS' for r in rows), 'failed':[r['case_id'] for r in rows if r['status']=='FAIL'], 'abstained':[r['case_id'] for r in rows if r['status']=='NOT_EVALUATED'], 'scope':'Derived exact-label parser; no semantic or unit correctness claim; not independent validation'}
out=ROOT/'evidence/client_readiness';out.mkdir(exist_ok=True)
(out/'labelled_replay.json').write_text(json.dumps({'summary':summary,'rows':rows},indent=2))
print(json.dumps(summary,indent=2))
