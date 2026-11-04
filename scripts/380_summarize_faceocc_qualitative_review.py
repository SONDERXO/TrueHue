"""Bind actual user judgments to full-cycle qualitative findings; no adoption."""
from collections import Counter
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/faceocc_light_conclusion_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def read(relative):
        raw=(ROOT/relative).read_bytes();hashes[relative]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    decisions=read('outputs/faceocc_four_review_import_v1/decisions.json')
    imported=read('outputs/faceocc_four_review_import_v1/summary.json')
    full=read('outputs/faceocc_light_comparison_v1/summary.json')
    verification=read('outputs/faceocc_light_comparison_v1/verification.json')
    observations=read('outputs/faceocc_light_comparison_v1/assistant_observations.json')
    plan=read('outputs/faceocc_light_comparison_v1/plan.json')
    assert len(decisions)==4 and {r['image_id'] for r in decisions}==set(plan['user_review_ids'])
    assert len(full['records'])==len(observations)==24 and verification['paired_outputs']==18
    result=dict(status='qualitative_cycle_complete_promising_not_adopted',
        user_reviewed=4,preference_counts=dict(Counter(r['decisions']['preference'] for r in decisions)),
        old_unwanted_counts=dict(Counter(r['decisions']['old_unwanted'] for r in decisions)),
        new_unwanted_counts=dict(Counter(r['decisions']['new_unwanted'] for r in decisions)),
        useful_skin_lost_counts=dict(Counter(r['decisions']['useful_skin_lost'] for r in decisions)),
        user_decisions=decisions,full_attempts=24,paired_outputs=18,retained_failures=6,
        assistant_observations=observations,original_user_export_sha256=imported['export_sha256'],
        conclusion='User preferred FaceOcc in2fixed challenge cases and rated2similar; no reported skin loss in these4. Wider assistant skin-loss/occluder concerns remain.',
        adopted=False,pixel_accuracy_claim=False,independent_validation=False,fits=0,
        historical_scope_note='New four judgments do not erase earlier file/scope-bound source rejections or contamination observations.')
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    out.mkdir();(out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (out/'input_sha256.json').write_text(json.dumps(hashes,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ['user_decisions','assistant_observations']},indent=2))


if __name__=='__main__':main()
