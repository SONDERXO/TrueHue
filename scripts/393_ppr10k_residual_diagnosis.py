"""Analyse saved oracle residuals without refitting or changing any controls."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from skimage.color import rgb2lab

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.utilities.config import get_config

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/get_config().OUTPUTS_ROOT
SAVED=BASE/'ppr10k_operator_diagnostic_v1'
OUT=BASE/'ppr10k_residual_diagnosis_v1'


def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'results.json').exists(): raise FileExistsError('Diagnosis already frozen')
    manifest=json.loads((SAVED/'sha256.json').read_text())
    for name,sha in manifest.items():
        assert hashlib.sha256((SAVED/name).read_bytes()).hexdigest()==sha
    rules=dict(input_results_sha256=hashlib.sha256((SAVED/'results.json').read_bytes()).hexdigest(),
        support='Exact saved check blocks and approximate face polygons; no new mask or exclusions.',
        measures='Mean signed Lab oracle-minus-target; RGB signed errors; source-green quartile residuals; required per-pixel red/blue gains with existing gamma held fixed.',
        strata='Source green quantiles 0,.25,.5,.75,1 within check blocks; descriptive only.',
        caution='Required-gain variation can include registration, quantisation and mixed facial features. No fitted alternative, causal proof or acceptable-error cutoff.',
        fits=0,new_photos=0,inference=0,tree_training=False,runtime_change=False)
    (OUT/'protocol.json').write_text(json.dumps(rules,indent=2),encoding='utf8')
    rows=[]
    for frame in json.loads((SAVED/'results.json').read_text())['results']:
        name=frame['frame'];z=np.load(SAVED/f'{name}_replay.npz')
        a,b,out,c=z['source'],z['target'],z['output'],z['check_mask']
        delta=(rgb2lab(out)-rgb2lab(b))[c]
        rgb=(out-b)[c]*255
        green=a[...,1][c];cuts=np.quantile(green,[0,.25,.5,.75,1])
        bins=[]
        for i in range(4):
            take=(green>=cuts[i]) & ((green<cuts[i+1]) if i<3 else (green<=cuts[i+1]))
            bins.append(dict(quartile=i+1,pixels=int(take.sum()),
                mean_signed_Lab=delta[take].mean(axis=0).tolist(),
                mean_signed_RGB_255=rgb[take].mean(axis=0).tolist()))
        power=a[c]**(1/z['parameters'][0]);gains={}
        for idx,label in [(0,'red'),(2,'blue')]:
            valid=(power[:,idx]>.02)&(b[c][:,idx]>.02)&(b[c][:,idx]<.98)
            required=b[c][valid,idx]/power[valid,idx]
            gains[label]=dict(pixels=int(valid.sum()),required_gain_p10_p50_p90=np.quantile(required,[.1,.5,.9]).tolist(),
                saved_gain=float(z['parameters'][1 if idx==0 else 2]))
        rows.append(dict(frame=name,check_pixels=int(c.sum()),mean_signed_Lab=delta.mean(axis=0).tolist(),
            mean_signed_RGB_255=rgb.mean(axis=0).tolist(),green_quartiles=bins,required_gains=gains,
            clipped_oracle_channel_samples=int(((out[c]<=0)|(out[c]>=1)).sum())))
    (OUT/'results.json').write_text(json.dumps(dict(protocol=rules,results=rows),indent=2),encoding='utf8')
    print(json.dumps(rows,indent=2))


if __name__=='__main__': main()
