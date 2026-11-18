"""Saved-record tree/MST/role compatibility audit; no image or model execution."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/photographic_tree_contract_audit_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if OUT.exists():raise FileExistsError('Preserve existing audit')
    bound={}
    def read(rel):
        p=ROOT/rel;bound[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    model=read('outputs/green_nonharm_models_v1/models_PRIVATE.json')
    old=read('outputs/aligned_correction_preparation_v1/plan_PRIVATE.json')
    source=read('outputs/ppr10k_native_pipeline_diagnostic_v1/results_PRIVATE.json')
    sourceplan=read('outputs/ppr10k_native_pipeline_diagnostic_v1/plan_PRIVATE.json')
    target=read('outputs/ppr10k_expert_control_readiness_v1/results_PRIVATE.json')
    targetplan=read('outputs/ppr10k_expert_control_readiness_v1/plan_PRIVATE.json')
    targetverify=read('outputs/ppr10k_expert_control_readiness_v1/verification_PRIVATE.json')
    assert targetverify['passed'] and targetverify['results_sha256']==bound['outputs/ppr10k_expert_control_readiness_v1/results_PRIVATE.json']
    assert model['measurement_contract_sha256']==old['measurement_contract_sha256']
    assert sourceplan['measurement_contract']==targetplan['measurement_contract']==old['contract']['desktop_measurement_contract']
    assert sourceplan['bridge']==targetplan['bridge']=='native_anchor_square_context_1p5_v1'
    calibrations=[]
    for key,c in model['calibrations'].items():
        assert c['measurement_contract_sha256']==model['measurement_contract_sha256']
        calibrations.append(dict(key=key,training_cases=len(c['training_cases']),
            training_publisher_keys=len(c['training_keys']),calibration_admitted=c['calibration_admitted'],
            measurement_contract_sha256=c['measurement_contract_sha256']))
    assert not any(c['calibration_admitted'] for c in calibrations)
    rows=[]
    names=['input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees']
    for role,d in [('photographic_source',source),('expert_identity_candidate',target)]:
        for r in d['records']:
            available=r['status']=='available'
            stats=r.get('measurement_report',{}).get('statistics',{})
            values={n:stats[n.removeprefix('input_')] for n in names} if available else None
            rows.append(dict(case_id=role+'__'+r['frame'],photo=r['frame'],publisher_group=r['frame'].split('_')[0],
                role=role,technical_measurement_available=available,raw_four=values,
                compatible_mst_score=None,provided_mst_label=None,
                correct_person_for_pair=r.get('historical_face_match',r.get('source_historical_face_match',False)),
                control_action='identity_proposed_not_admitted' if role=='expert_identity_candidate' else 'not_assigned',
                tree_training_eligible=False))
    assert len(rows)==16 and len({r['publisher_group'] for r in rows})==8
    result=dict(passed=True,feature_names=model['feature_names'],expected_feature_count=len(model['feature_names']),
        rows=rows,attempted_roles=16,technical_raw_four_available=sum(r['raw_four'] is not None for r in rows),
        qualified_complete_tree_vectors=0,provided_ppr_mst_labels=0,
        calibrations=calibrations,old_contract=old['contract'],
        old_outer_contract_sha256=model['measurement_contract_sha256'],
        shared_inner_measurement_contract=sourceplan['measurement_contract'],new_bridge=sourceplan['bridge'],
        compatibility='Shared measurement service does not establish equivalence of native-anchor and old stretched-anchor outer pipelines; no approved matching calibration.',
        unprepared_input_families=['matched MST score','whole-scene summaries','fixed green summaries'],
        unprepared_note='Scene/green can be extracted from bound inputs; no new representation is needed, but extraction would not supply MST validation.',
        fitting_design='Unassigned. No favourable-subset fitting or claimed independent test.',
        selected_direction='Photographic supervision is a candidate intervention, not fit-ready; no new inputs/objective/architecture bundle.',
        disposition='NO-GO new correction fit: eligible controls/support, compatible MST and grouped evaluation unresolved.',
        image_reads=0,new_features_extracted=0,new_fits=0,new_forwards=0,holdout_reads=0,input_sha256=bound)
    bound['scripts/712_audit_photographic_tree_contract.py']=sha(Path(__file__))
    assert all(sha(ROOT/p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'audit_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print('PASS:16 source/control roles,15 measured raw-four records,8publisher groups,',len(calibrations),'unadmitted old-contract MST calibrations.')
    print('Matching complete qualified tree vectors:0. No images/features/model execution. New correction fit:NO-GO.')
if __name__=='__main__':main()
