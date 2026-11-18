"""One stopped-input diagnostic; never resumes cue extraction or chooses a fix."""
import json
import numpy as np
from wb_cue_adapter import ROOT, ASSETS, load_model, sha


def main():
    out=ROOT/'outputs/wb_cue_cutoff_tie_diagnosis_v1'
    if out.exists():raise RuntimeError('Refuse overwrite')
    stopped=ROOT/'outputs/wb_cue_portrait_assessment_v1'
    access=json.loads((stopped/'array_access.json').read_text())
    failure=json.loads((stopped/'failure.json').read_text())
    assert failure=={'error':'UNAVAILABLE_BOUNDARY_TIE','extracted_cases':1}
    row=access[-1]
    assert row['case_id']=='camera_halfstop_ffhq_16061__colour_only'
    bindings=json.loads((stopped/'bindings.json').read_text())
    for path,h in bindings.items():assert sha(ROOT/path)==h
    model,normalize,receipt=load_model()
    with np.load(ROOT/row['path'],allow_pickle=False) as pack:rgb=pack['input'].copy()
    query=model.encode(model.rgb_uv_hist(normalize(rgb)))
    d=np.einsum('ij,ij->i',model.features,model.features)[:,None]+np.einsum('ij,ij->i',query,query)-2*model.features.dot(query.T)
    values=np.sort(d[:,0]);assert values[24]==values[25]
    cutoff=float(values[24]);below=np.flatnonzero(d[:,0]<cutoff);tied=np.flatnonzero(d[:,0]==cutoff)
    maps=model.mappingFuncs[tied]
    span=np.max(maps,axis=0).astype(float)-np.min(maps,axis=0).astype(float)
    identical=bool(np.all(maps==maps[0]))
    for path,h in bindings.items():assert sha(ROOT/path)==h
    out.mkdir()
    np.savez(out/'failure_witness.npz',query=query,distances=d,below_indices=below,tied_indices=tied,tied_mappings=maps)
    result={'status':'CUTOFF_TIE_CONFIRMED_NO_RETRY','case_id':row['case_id'],'input_sha256':sha(ROOT/row['path']),
            'cutoff':cutoff,'strictly_below':len(below),'tied_at_cutoff':len(tied),'remaining_slots':25-len(below),
            'tied_mapping_identical':identical,'max_coefficient_span':float(np.max(span)),
            'coefficient_span':span.tolist(),'continued_roster':False,'scored_cases':0,'predictor_fits':0,'correction_renders':0}
    (out/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
