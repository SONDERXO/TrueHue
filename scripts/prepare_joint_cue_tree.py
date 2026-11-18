"""Exact cached feature join only: no portraits, encoder or predictor fits."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from wb_feature_direct_workflow import SETTINGS,read,write,sha


def main():
    out=ROOT/'outputs/joint_cue_tree_design_v1'
    if out.exists():raise FileExistsError(out)
    wb=ROOT/'outputs/wb_feature_direct_prediction_v1'
    receipt=read(wb/'verification.json');assert receipt['passed']
    known={p.replace('\\','/'):h for p,h in receipt['artifacts'].items()}
    bound={str((wb/'verification.json').relative_to(ROOT)):sha(wb/'verification.json')}
    for p in ['rows.json','plan.json','records.json','summary.json','held_controls_sealed.json']:
        assert sha(wb/p)==known[p];bound[str((wb/p).relative_to(ROOT))]=known[p]
    neural=ROOT/'outputs/camera_halfstop_neural_v1';done=read(neural/'completion_PRIVATE.json')
    data=ROOT/'outputs/camera_halfstop_data_v1';data_done=read(data/'completion_PRIVATE.json')
    proof=read(ROOT/'outputs/camera_halfstop_prediction_v1/verification_PRIVATE.json')
    assert proof['passed'] and proof['identity4096_exact']==11 and proof['scalar_feature_values']==18546
    assert done['passed'] and done['encoder_unchanged'] and done['vectors']==66
    assert sha(neural/'features.npz')==done['feature_sha256']
    assert sha(data/'plan_PRIVATE.json')==done['data_plan_sha256']==data_done['plan_sha256']
    assert sha(data/'rows281_PRIVATE.json')==data_done['rows281_sha256']
    base={r['case_id']:r for r in read(data/'rows281_PRIVATE.json')}
    parent_rows=read(wb/'rows.json');parent_plan=read(wb/'plan.json');rows=[]
    with np.load(neural/'features.npz',allow_pickle=False) as pack:
        assert set(pack.files)==set(base)=={r['case_id'] for r in parent_rows}
        for r in parent_rows:
            b=base[r['case_id']];n=pack[r['case_id']]
            assert all(r[k]==b[k] for k in ['case_id','source_id','role','y','generated_fixture'])
            assert r['generated_fixture'] is False and r['x314'][:281]==b['x']
            assert n.shape==(4096,) and n.dtype==np.float32 and np.isfinite(n).all()
            x=np.asarray(r['x314']+n.astype(float).tolist(),np.float32).astype(float).tolist()
            assert len(x)==4410 and x[:314]==r['x314'] and x[314:]==n.astype(float).tolist()
            rows.append({k:r[k] for k in ['case_id','source_id','role','generated_fixture','y']}|dict(x=x))
            e='evaluation/'+r['case_id']+'.npz';assert sha(wb/e)==known[e]
            bound[str((wb/e).relative_to(ROOT))]=known[e]
    for p in [neural/'features.npz',neural/'completion_PRIVATE.json',data/'plan_PRIVATE.json',data/'rows281_PRIVATE.json',data/'completion_PRIVATE.json',ROOT/'outputs/camera_halfstop_prediction_v1/verification_PRIVATE.json',Path(__file__),ROOT/'docs/joint-cue-tree-protocol-2026-11-16.md']:
        bound[str(p.relative_to(ROOT))]=sha(p)
    plan=dict(folds=parent_plan['folds'],generated_fixture=False,dimensions=4410,settings=SETTINGS,
              target_names=parent_plan['target_names'],model_ready=False)
    out.mkdir();write(out/'rows.json',rows);write(out/'plan.json',plan);write(out/'bindings.json',bound)
    # Independent complete scalar source joins, not a second feature extraction.
    with np.load(neural/'features.npz',allow_pickle=False) as p:
        for a,r in zip(rows,parent_rows):
            assert a['case_id']==r['case_id']
            for j in range(314):assert a['x'][j]==r['x314'][j]
            for j in range(4096):assert a['x'][314+j]==float(p[a['case_id']][j])
    for p,h in bound.items():assert sha(ROOT/p)==h
    write(out/'verification.json',dict(passed=True,rows=66,dimensions=4410,scalar_join_values=291060,
            real_fits=0,portrait_arrays=0,encoder_runs=0,rows_sha256=sha(out/'rows.json'),plan_sha256=sha(out/'plan.json')))
    print('PASS66x4410 exact cached joins,291060 scalar checks;0fits/portrait reads/encoder runs.')


if __name__=='__main__':main()
