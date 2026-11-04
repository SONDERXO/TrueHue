"""Save Codex source-screen observations, verify audit coverage and plot features.

Observations are development notes, not human acceptance or training labels.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NOTES={
'64594':('hold','Facial hair and shading; selected mask includes beard/neck-like material, unsuitable for immediate reference/generation acceptance.'),
'707':('hold','Low contrast/softness and uncertain lighting/reference suitability; this is not rejection based on intrinsic skin tone.'),
'59443':('hold','Large sunglasses obscure eyes and selected support includes glasses/frame regions.'),
'61764':('hold','Downward pose, uneven lighting and strongly fragmented selected skin.'),
'36185':('hold','Turned/downward pose, softness and broad rectangular mask including uncertain outer regions.'),
'72162':('hold','Only small side/lower facial region selected; most facial coverage missed.'),
'41854':('hold','Strong rendering/lighting cast and fragmented side-face coverage; reference suitability uncertain.'),
'43269':('hold','Soft image, background/outer-region inclusion and uncertain source rendering.'),
'22905':('pipeline_hold','Landmarks unavailable; fallback candidate overlay is diagnostic only, not valid feature-excluded mask.'),
'35732':('hold','Eye-area artifacts/appearance and fragmented coverage; shadowed facial regions need closer review.'),
'20555':('promising_followup_only','Relatively frontal, broad facial coverage without obvious large occlusion; inspect source/mask at full size and run per-variant checks before eligibility.'),
'27122':('hold','Sunglasses and side pose; large eye region unavailable and frame boundaries uncertain.'),
'51205':('hold','Severe half-face coverage loss and outer hair/side-region inclusion despite hair cleanup.'),
'11236':('hold','Strong blur/softness and hair/outer-region inclusion; useful facial detail is limited.'),
'42643':('hold','Hand occludes mouth/face, selected as skin; not suitable as clean facial generation support.'),
'13529':('hold','Helmet/face paint or strong colored rendering, high exposure and fragmented coverage; not a clean reference candidate.'),
'49453':('hold','Microphone occlusion, strong lighting and fragmented skin coverage.'),
'70222':('hold','Glasses, turned face and substantial outer/background support inclusion.')}


def main():
    output=ROOT/'outputs/training_coverage_audit_v1';tables=ROOT/'data/manifests/training_coverage_audit_v1'
    destination=tables/'candidate_disposition.json'
    if destination.exists():raise FileExistsError(destination)
    summary=json.loads((output/'summary.json').read_text())
    selected=json.loads((tables/'selected_source_ids.json').read_text())
    assert len(selected)==len(summary['new_source_attempts'])==18
    assert {r['image_id'] for r in selected}=={r['image_id'] for r in summary['new_source_attempts']}
    observations=[]
    for record in summary['new_source_attempts']:
        stem=record['image_id'].replace('/','_');image=cv2.imread(str(output/'images'/(stem+'_input.png')))
        mask=cv2.imread(str(output/'images'/(stem+'_estimation.png')),0)
        clean=cv2.imread(str(output/'images'/(stem+'_hairclean.png')),0)
        assert image.shape==(256,256,3) and mask.shape==clean.shape==(256,256)
        assert not np.any((clean>0)&(mask==0))
        assert record['partition']=='train' and record['training_eligible'] is False
        if 'skin_pixels' in record:assert int(np.count_nonzero(mask))==record['skin_pixels']
        identifier=Path(record['source_path']).stem
        status,reason=NOTES[identifier]
        observations.append(dict(image_id=record['image_id'],status=status,reason=reason,
            assessor='Codex visual development inspection, not human/expert acceptance',
            original_human_decision=record['original_human_decision'],training_eligible=False))
    ledger=ROOT/'data/manifests/development_exposure_additions.jsonl'
    exposures=[json.loads(line) for line in ledger.read_text(encoding='utf-8').splitlines() if line]
    assert {r['image_id'] for r in selected}<={r['image_id'] for r in exposures}
    for name,expected in summary['input_sha256'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected
    report=dict(status='complete',sources_reviewed=18,source_boards_reviewed=6,
        promising_followup_only=1,held=17,admitted_to_training=0,observations=observations,
        limitation='Selected development batch, not population acceptance rate or MST-balanced cohort. No human labels changed.')
    destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
    with (ROOT/'data/manifests/correction_controls_sourcecv_v1/development_train.csv').open(encoding='utf-8',newline='') as f:current=list(csv.DictReader(f))
    identities=[r for r in current if r['variant']=='identity_control']
    valid=[r for r in summary['new_source_attempts'] if r['status']=='success']
    fig,axes=plt.subplots(1,2,figsize=(11,4.8),constrained_layout=True)
    for ax,key,label in [(axes[0],'mean_b_star','Measured b*'),(axes[1],'mean_a_star','Measured a*')]:
        ax.scatter([float(r['input_mean_l_star']) for r in identities],[float(r['input_'+key]) for r in identities],
                   c='#1d4ed8',marker='o',s=55,label='Current six source controls')
        ax.scatter([r['mean_l_star'] for r in valid],[r[key] for r in valid],c='#6b7280',marker='x',s=48,label='New processing successes (not accepted)')
        promising=next(r for r in valid if r['image_id']=='fairface__train/20555.jpg')
        ax.scatter([promising['mean_l_star']],[promising[key]],c='#d97706',marker='*',s=150,label='20555: follow-up only')
        for r in identities:
            identifier=Path(r['source_path']).stem
            if identifier in ['51739','75027','22454']:ax.annotate(identifier,(float(r['input_mean_l_star']),float(r['input_'+key])),xytext=(4,5),textcoords='offset points',fontsize=8)
        ax.set_xlabel('Measured L* at 256x256');ax.set_ylabel(label);ax.grid(alpha=.2)
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncols=1,fontsize=8)
    fig.suptitle('Development photo measurements: coverage is not skin-tone labeling',fontsize=12)
    fig.savefig(output/'feature_coverage.png',dpi=150);fig.savefig(output/'feature_coverage.svg');plt.close(fig)
    (output/'verification.json').write_text(json.dumps(dict(status='passed',selected_train_sources=18,
        all_reserved_sources_excluded=True,saved_mask_contracts_checked=18,exposure_ledger_checked=True,
        original_hashes_unchanged=True,promoted_sources=0),indent=2),encoding='utf-8')
    print(json.dumps(dict(promising_followup=1,held=17,training_additions=0,mask_checks=18)))


if __name__=='__main__':main()
