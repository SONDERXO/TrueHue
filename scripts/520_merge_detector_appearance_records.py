"""Merge 48 new target records with 288 unchanged cached records; bind both."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'outputs/input_derived_mask_check_v1';NEW=ROOT/'outputs/detector_appearance_inference_v1';OUT=ROOT/'outputs/detector_appearance_merged_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if OUT.exists():raise FileExistsError(OUT)
    old=read(BASE/'results_PRIVATE.json')['records'];new={r['case_id']:r for r in read(NEW/'results_PRIVATE.json')['records']};assert len(new)==48
    for package in [BASE,NEW]:assert all(sha(package/n)==h for n,h in read(package/'sha256.json').items())
    records=[]
    for r in old:
        cid=r['case_id'];selected=cid in new;s=dict(new[cid] if selected else r);s['artifact_root']=str((NEW if selected else BASE)/cid);s['detector_fallback_target']=selected;records.append(s)
    assert len(records)==336
    bindings={str(package/n):h for package in [BASE,NEW] for n,h in read(package/'sha256.json').items()}
    OUT.mkdir();(OUT/'results_PRIVATE.json').write_text(json.dumps(dict(records=records,new_target_cases=48,reused_cases=288,new_fits=0),indent=2),encoding='utf-8')
    bindings[str(OUT/'results_PRIVATE.json')]=sha(OUT/'results_PRIVATE.json');bindings[str(Path(__file__))]=sha(Path(__file__))
    (OUT/'sha256.json').write_text(json.dumps(bindings,indent=2),encoding='utf-8');print('Bound 48 targeted attempts plus 288 unchanged cached records.')
if __name__=='__main__':main()
