"""Record explicit user rejection and trace already saved pixels; no correction changes."""
from pathlib import Path
import json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.reiqa_frozen_features import sha
OUT=ROOT/'outputs/frozen_neighbour_exposure_rejection_v1'
RUN=ROOT/'outputs/frozen_block_neighbour_prediction_v1'
REVIEW=ROOT/'outputs/frozen_neighbour_exposure_review_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    if OUT.exists():raise FileExistsError(OUT)
    manifest=read(REVIEW/'manifest_PRIVATE.json');proof=read(RUN/'verification_PRIVATE.json')
    hashes={Path(k).as_posix():v for k,v in proof['artifact_sha256'].items()}
    controls={r['case_id']:r for r in read(RUN/'models/held_controls_sealed.json')}
    traces=[]
    for number,points in [(0,[(110,95),(110,175),(160,110)]),(2,[(145,140),(180,140)])]:
        row=manifest['cases'][number];relative='evaluation/'+row['case_id']+'.npz'
        assert sha(RUN/relative)==hashes[relative]
        with np.load(RUN/relative,allow_pickle=False) as pack:
            data={k:pack[k].copy() for k in ['input','reference','alpha','protected','tree']}
        parameter=controls[row['case_id']]['controls'];q,r,b,a,d=parameter
        pixels=[dict(y=y,x=x,input=data['input'][y,x].tolist(),candidate=data['tree'][y,x].tolist(),
            reference=data['reference'][y,x].tolist(),alpha=float(data['alpha'][y,x]),protected=bool(data['protected'][y,x])) for y,x in points]
        if number==0:
            # Post-view diagnostic window, NOT new skin measurement or model support.
            window=np.zeros(data['alpha'].shape,bool);window[95:135,60:180]=True
            witness=window&(data['alpha']==1)&np.all(data['input']==0,axis=2)
            black=np.rint(np.clip(max(0.,d)**q*np.array([r,1,b]),0,1)*255).astype(np.uint8)
            detail=dict(diagnostic_window_yx=[95,135,60,180],clipped_black_core_pixels=int(witness.sum()),
                predicted_zero_input_RGB=black.tolist(),candidate_unique_RGB=np.unique(data['tree'][witness],axis=0).tolist(),
                reference_unique_RGB_count=len(np.unique(data['reference'][witness],axis=0)))
            if witness.any():assert np.all(data['tree'][witness]==black)
        else:
            window=np.zeros(data['alpha'].shape,bool);window[100:210,80:200]=True
            witness=window&(data['alpha']==1)&(data['input'][:,:,0]==255)
            red=int(round(255*min(1.,max(0.,a+d)**q*r)))
            detail=dict(diagnostic_window_yx=[100,210,80,200],red_saturated_core_pixels=int(witness.sum()),
                predicted_saturated_red=red,candidate_unique_red=np.unique(data['tree'][:,:,0][witness]).tolist(),
                reference_red_range=[int(data['reference'][:,:,0][witness].min()),int(data['reference'][:,:,0][witness].max())])
            assert np.all(data['tree'][:,:,0][witness]==red)
        traces.append(dict(case_id=row['case_id'],controls=parameter,selected_neighbour=controls[row['case_id']]['neighbour_case_id'],
            pixels=pixels,diagnostic=detail,cached_pack_sha256=hashes[relative]))
        assert sha(RUN/relative)==hashes[relative]
    OUT.mkdir()
    feedback=dict(source='explicit_user_message',exact_user_message='These changes are too unrealistic and unacceptable.',
        context='current eight-case exposure/combined review',review_manifest_sha256=sha(REVIEW/'manifest_PRIVATE.json'),
        run_verification_sha256=sha(RUN/'verification_PRIVATE.json'),
        scope='overall rejection of currently presented exposure changes; not fabricated eight casewise answers',
        disposition='REJECTED_FOR_COMBINED_MODEL_ADOPTION_STOP_REVIEW',model_ready=False,
        previous_identity_and_colour_ratings_preserved=True,new_casewise_ratings=0,new_fits=0,new_correction_renders=0,
        no_automatic_retry_or_colour_only_adoption=True)
    for name,value in [('user_feedback_PRIVATE.json',feedback),('saved_pixel_traces_PRIVATE.json',traces)]:
        (OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    print(json.dumps(feedback,indent=2));print(json.dumps([r['diagnostic'] for r in traces],indent=2))
if __name__=='__main__':main()
