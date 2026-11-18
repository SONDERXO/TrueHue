"""Artificial eleven-source cases. No file IO, real source or tone label."""
import numpy as np
from src.distortion_generation.directional_exposure_recipe import render_rgb

ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']
VARIANTS=[('clean','none'),('color','none'),('exposure','under'),('exposure','over'),('combined','under'),('combined','over')]


def build(names,settings,*,side=256):
    mapping=dict(schema_version='truehue_shared_core_development_mst_v1',status='development_unvalidated_transfer',
        measurement_core_sha256='generated_core',feature_control_contract_sha256='generated_contract',
        ita_knots=[-90.,90.],mst_score_knots=[9.,2.],calibration_admitted=False,runtime_adopted=False,
        generated_fixture=True)
    ids=[f'generated_{i:02}' for i in range(11)];cases=[]
    for i,source_id in enumerate(ids):
        reference=np.random.default_rng(1500+i).integers(35,225,(side,side,3),dtype=np.uint8)
        measurement=np.ones((side,side),np.uint8)*255
        protected=np.zeros((side,side),bool);protected[side//2,side//2]=True
        measurement[protected]=0
        alpha=np.ones((side,side),float);alpha[[0,-1],:]=0;alpha[:,[0,-1]]=0
        alpha[1,1:-1]=.5;alpha[protected]=0
        targets=[[1.,1.,1.,1.,0.],[1.,1.04,.96,1.,0.],
            [.7,1.,1.,1/1.08,(.08+35/255)/1.08],[1/.7,1.,1.,1/1.08,-35/255/1.08],
            [.7,1.03,.97,1/1.08,(.08+35/255)/1.08],[1/.7,1.03,.97,1/1.08,-35/255/1.08]]
        # Six deliberately bound-valued synthetic targets, not copied real targets.
        if i<4:targets[3]=[3.1,1.02,1.,.62,.3]
        if i<2:targets[5]=[3.2,1.04,.96,.62,.3]
        for role,(variant,direction),y in zip(ROLES,VARIANTS,targets):
            image,_=render_rgb(reference,np.ones((side,side),float),'medium',variant,direction)
            cases.append(dict(case_id=source_id+'__'+role,source_id=source_id,role=role,
                generated_fixture=True,image=image,reference=reference.copy(),measurement=measurement.copy(),
                alpha=alpha.copy(),protected=protected.copy(),y=y))
    folds=[dict(held_source_id=s,fitting_cases=[c['case_id'] for c in cases if c['source_id']!=s],
        evaluation_cases=[c['case_id'] for c in cases if c['source_id']==s]) for s in ids]
    return dict(generated_fixture=True,feature_names=names,settings=settings,folds=folds),cases,mapping
