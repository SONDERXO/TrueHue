"""Read-only matched clean/mild-cast control comparison, not a new fit."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'outputs/whole_scene_correction_v1'
OUT=ROOT/'outputs/scene_gate_mistake_diagnosis_v1/mild_cast_controls_PRIVATE.json'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    result=json.loads((SOURCE/'results_PRIVATE.json').read_text());preds={r['case_id']:r for r in result['records']}
    rows=json.loads((SOURCE/'prepared_rows_PRIVATE.json').read_text());records=[]
    for r in rows:
        if r['case']['id'] not in ['colour_cool','colour_warm'] or r['target'] is None:continue
        p=preds[r['case_id']]['methods']['face_plus_scene']['parameters'];clean=preds[r['source_case']+'__clean']['methods']['face_plus_scene']['parameters']
        assert p==clean
        records.append(dict(case_id=r['case_id'],target_gamma=r['target'][0],predicted_gamma=p[0],same_controls_as_clean=True))
    assert len(records)==58
    v=dict(records=records,matched_controls=len(records),target_gamma_range=[min(r['target_gamma'] for r in records),max(r['target_gamma'] for r in records)],
        predicted_gamma_range=[min(r['predicted_gamma'] for r in records),max(r['predicted_gamma'] for r in records)],new_fits=0,
        source_bindings={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE/'results_PRIVATE.json',SOURCE/'prepared_rows_PRIVATE.json']})
    OUT.write_text(json.dumps(v,indent=2),encoding='utf-8')
    print('All58mild casts receive same controls as paired clean source; zero fits.')


if __name__=='__main__':main()
