"""Experimental development orchestration; importing performs no dataset IO."""
from collections import defaultdict
from copy import deepcopy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000
from .portable_oblique_tree import PortableObliqueTree, from_axis_tree
from .portable_tree import PortableTree
from .oblique_regression_tao import train_oblique

def load_verifier(root):
    spec=importlib.util.spec_from_file_location('independent_oblique',root/'scripts/846_verify_oblique_training_feasibility.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def write(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def render(image,alpha,controls):
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3:
        raise ValueError('RGB8 input required')
    if alpha.shape!=image.shape[:2] or not np.isfinite(alpha).all() or np.any((alpha<0)|(alpha>1)):
        raise ValueError('Valid matching alpha required')
    if len(controls)!=3 or not all(math.isfinite(v) and v>0 for v in controls):raise ValueError('Invalid controls')
    u=image/255.
    return np.rint(255*(u*(1-alpha[:,:,None])+np.clip(u**controls[0]*[controls[1],1.,controls[2]],0,1)*alpha[:,:,None])).astype(np.uint8)

def measure(image,reference,mask):
    if mask.dtype!=bool or mask.shape!=image.shape[:2] or not mask.any():raise ValueError('Nonempty boolean scoring support required')
    return dict(RGB=float(np.abs(image[mask].astype(float)-reference[mask]).mean()),
        DE=float(deltaE_ciede2000(rgb2lab(image[mask]/255.),rgb2lab(reference[mask]/255.)).mean()))

def aggregate(predictions):
    result={}
    for role in sorted({p['role'] for p in predictions}):
        rows=[p for p in predictions if p['role']==role];groups=defaultdict(list)
        for p in rows:groups[p['source']].append(p['input']['DE']-p['output']['DE'])
        differences=[p['input']['DE']-p['output']['DE'] for p in rows]
        result[role]=dict(cases=len(rows),sources=len(groups),
            source_equal_DE_improvement=math.fsum(math.fsum(g)/len(g) for g in groups.values())/len(groups),
            DE_benefits=sum(d>1e-10 for d in differences),DE_harms=sum(d < -1e-10 for d in differences),
            numerical_equal=sum(abs(d)<=1e-10 for d in differences),worst_DE_improvement=min(differences),
            input_RGB=math.fsum(p['input']['RGB'] for p in rows)/len(rows),
            output_RGB=math.fsum(p['output']['RGB'] for p in rows)/len(rows))
    return result

def fit_all(out,folds,axes,records,reused,reused_report,verify,*,trainer=train_oblique):
    """No held inference here. Caller creates output once before calling."""
    models=[]
    for index,fold in enumerate(folds):
        group=fold['held_publisher_group'];axis=axes[index]['tree']
        assert axes[index]['definition']==fold
        train=[records[c] for c in fold['fitting_cases']]
        assert all(r['publisher_group']!=group for r in train)
        x=[r['input_vector_float32'] for r in train];y=[r['nominal_controls'] for r in train]
        roles=[r['experimental_role'] for r in train];initial=from_axis_tree(axis)
        assert PortableTree(axis).predict(x)==PortableObliqueTree(initial).predict(x)
        folder=out/group;folder.mkdir()
        write(folder/'initial_PRIVATE.json',initial)
        if index==0:candidate,report=deepcopy(reused),deepcopy(reused_report)
        else:candidate,report=trainer(initial,x,y,max_passes=20,max_proposals=300,max_seconds=60.)
        write(folder/'candidate_PRIVATE.json',candidate);write(folder/'optimization_PRIVATE.json',report)
        checked=verify(axis,initial,candidate,report,x,y,roles)
        write(folder/'fitting_verification_PRIVATE.json',checked)
        models.append(dict(definition=fold,tree=candidate,report=report,reused=index==0))
        write(out/'models_PRIVATE.json',models)
    write(out/'all_fits_verified_PRIVATE.json',dict(passed=True,models=len(models)))
    return models

def replay_render(image,alpha,controls):
    """Independent per-channel implementation, deliberately separate from render."""
    output=np.empty_like(image)
    for channel,gain in enumerate([controls[1],1.,controls[2]]):
        values=image[:,:,channel].astype(np.float64)/255.
        corrected=np.minimum(1.,np.maximum(0.,np.power(values,controls[0])*gain))
        output[:,:,channel]=np.round(255.*(values*(1.-alpha)+corrected*alpha)).astype(np.uint8)
    return output
