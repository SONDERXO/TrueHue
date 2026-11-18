"""Independent seven-formula replay from cached RGB, no source-image rereads."""
from pathlib import Path
import hashlib,json,math
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/reviewed_scene_diagnostic_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    bound=read(OUT/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bound.items())
    records=read(OUT/'records_PRIVATE.json');summary=read(OUT/'summary_PRIVATE.json');pairs=read(OUT/'pairs_PRIVATE.json')
    assert len(records)==60 and len({r['source_sha256'] for r in records})==60
    names=list(summary['scene_ranges']);replayed={}
    for r in records:
        assert r['scene_status']=='available' and not r['calibration_admitted'] and not r['training_admitted']
        path=OUT/r['frame_file'];assert sha(path)==r['frame_sha256']
        rgb=np.load(path,allow_pickle=False);assert rgb.shape==(224,224,3) and rgb.dtype==np.uint8
        means=[float(rgb[:,:,i].astype(np.uint64).sum())/(224*224) for i in range(3)]
        encoded=cv2.cvtColor(rgb[:,:,::-1].copy(),cv2.COLOR_BGR2LAB)[:,:,0]
        histogram=np.bincount(encoded.ravel(),minlength=256)
        # Construct sorted float32 lightness levels and linearly interpolate by hand.
        levels=np.arange(256,dtype=np.float32)*(100/255)
        ordered=np.repeat(levels,histogram).tolist()
        quantiles=[]
        for q in (.1,.5,.9):
            at=(len(ordered)-1)*q;lo=math.floor(at);fraction=at-lo
            quantiles.append(ordered[lo]*(1-fraction)+ordered[min(lo+1,len(ordered)-1)]*fraction)
        zero=int(np.count_nonzero(np.min(rgb,axis=2)==0))/(224*224)
        full=int(np.count_nonzero(np.max(rgb,axis=2)==255))/(224*224)
        expected=dict(zip(names,[math.log((means[0]+1)/(means[1]+1)),math.log((means[2]+1)/(means[1]+1)),*quantiles,zero,full]))
        for f,v in expected.items():assert math.isclose(v,r['scene_features'][f],abs_tol=1e-10,rel_tol=1e-10),(r['case_id'],f,v,r['scene_features'][f])
        replayed[r['case_id']]=expected
    for pair in pairs:
        assert pair['available']
        a=next(r for r in records if r['subject_id']==pair['subject_id'] and r['condition']==pair['family']+'_600')
        b=next(r for r in records if r['subject_id']==pair['subject_id'] and r['condition']==pair['family']+'_1200')
        for f in names:assert math.isclose(pair['delta'][f],replayed[b['case_id']][f]-replayed[a['case_id']][f],abs_tol=1e-10,rel_tol=1e-10)
    for f in names:
        values=[r['scene_features'][f] for r in records];assert summary['scene_ranges'][f]==[min(values),max(values)]
        changes=[p['delta'][f] for p in pairs];m=summary['paired_changes'][f]
        assert m['positive']==sum(v>0 for v in changes) and m['negative']==sum(v<0 for v in changes) and m['zero']==sum(v==0 for v in changes)
        assert math.isclose(m['mean_delta'],sum(changes)/30,abs_tol=1e-10)
    photo=read(ROOT/'outputs/reviewed_feature_control_contract_v1/partial_features_and_targets_PRIVATE.json')
    for row,p in zip(summary['photographic_support'],photo):
        assert row['case_id']==p['case_id']
        assert row['outside_scene_marginals']==[f for f in names if not summary['scene_ranges'][f][0]<=p['features_partial'][f]<=summary['scene_ranges'][f][1]]
    assert summary['photographic_outside_any_scene_marginal']==sum(bool(r['outside_scene_marginals']) for r in summary['photographic_support'])==14
    report=dict(passed=True,cached_frames=60,scalar_feature_checks=420,paired_delta_checks=210,photographic_support_checks=14,
        original_source_rereads=0,model_calls=0,fits=0,predictions=0,holdout_reads=0,
        results_sha256=sha(OUT/'records_PRIVATE.json'),summary_sha256=sha(OUT/'summary_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(report,indent=2)+'\n');print('PASS:60 cachedframes/420 independent scalar checks/210 paired deltas/14 photographic support checks;no source rereads.')


if __name__=='__main__':main()
