"""Freeze conditional32-source design and exact historical reuse; never fit."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    base=ROOT/'outputs';out=base/'broader_source_comparison_design_v1'
    if out.exists():raise FileExistsError(out)
    if (base/'additional_six_source_mask_import_v1').exists():
        raise RuntimeError('Mask decisions already imported; cannot claim this is pre-import design')
    hashes={}
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):
        hashes[p.relative_to(ROOT).as_posix()]=digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    parent=base/'reviewed_primary_comparison_v1';endpoint=base/'endpoint_feature_tree_v1'
    previous=read(parent/'plan.json');pv=read(parent/'verification.json')
    ep=read(endpoint/'plan.json');ev=read(endpoint/'verification.json')
    assert pv['status']==ev['status']=='pass'
    for folder,verification in [(parent,pv),(endpoint,ev)]:
        assert digest(folder/'plan.json')==verification['evidence_sha256']['plan.json']
    registry=read(base/'reviewed_source_evidence32_v1/registry.json')
    rv=read(base/'reviewed_source_evidence32_v1/verification.json')
    assert digest(base/'reviewed_source_evidence32_v1/registry.json')==rv['evidence_sha256']['registry.json']
    rows=registry['rows'];by_id={r['pair_id']:r for r in rows}
    assert len(rows)==len(by_id)==117
    pending_manifest=read(base/'additional_six_source_mask_review_v1/manifest.json')
    pending=read(base/'additional_six_source_pairs_v1/primary_review_queue.json')
    assert {r['pair_id'] for r in pending}=={r['pair_id'] for r in pending_manifest['rows']}
    assert len(pending)==15 and all(r['exact_input_mask_review']=='pending' for r in pending)
    assert registry['features']==previous['features']==ep['features']
    assert registry['measurement_contract_sha256']==previous['measurement_contract_sha256']==ep['measurement_contract_sha256']
    old_ids={r['pair_id'] for r in previous['rows']};old_sources={r['source_image_id'] for r in previous['rows']}
    a=[r['pair_id'] for r in ep['rows']]
    b=[r['pair_id'] for r in previous['rows'] if r['variant']=='identity' or r['cohort']=='primary']
    assert len(a)==47 and len(b)==84 and len(old_ids)==105 and len(old_sources)==26
    prior_features=read(parent/'features.json')
    assert digest(parent/'features.json')==pv['evidence_sha256']['features.json']
    for r in previous['rows']:
        assert by_id[r['pair_id']]['features']==prior_features[r['pair_id']]
        assert by_id[r['pair_id']]['target_direct_gamma_red_blue']==r['paper_target']
    extra_controls=[r for r in rows if r['stratum']=='original_control' and r['source_image_id'] not in old_sources]
    assert len(extra_controls)==6
    c_definite=b+[r['pair_id'] for r in extra_controls]
    c_conditional=[r['pair_id'] for r in pending]
    groups={r['duplicate_group_id'] for r in rows};assert len(groups)==32
    pending_group={r['pair_id']:r['duplicate_group_id'] for r in pending}
    pending_source={r['pair_id']:r['source_image_id'] for r in pending}
    group_source={}
    for r in rows:
        group_source.setdefault(r['duplicate_group_id'],set()).add(r['source_image_id'])
    assert all(len(s)==1 for s in group_source.values())
    folds=[];reused=[]
    for fold in previous['folds']:
        group=fold['held_group'];fid=fold['fold_id']
        a_train=[p for p in a if by_id[p]['duplicate_group_id']!=group]
        b_train=[p for p in b if by_id[p]['duplicate_group_id']!=group]
        for method,folder,verification,expected in [('A',endpoint,ev,a_train),('B',parent,pv,b_train)]:
            mp=folder/f'fold_{fid}/membership.json';tp=folder/f'fold_{fid}/candidate.json'
            membership=read(mp);tree=read(tp)
            assert membership['train_pair_ids']==expected
            assert tree['provenance']['held_group']==group
            assert tree['provenance']['gamma_convention']=='direct_exponent'
            assert tree['provenance']['leaf_policy']=='identity_if_any_fitting_control_v1'
            for p in [mp,tp]:assert digest(p)==verification['evidence_sha256'][p.relative_to(folder).as_posix()]
            reused.append(dict(method=method,held_group=group,tree_path=tp.relative_to(ROOT).as_posix(),
                tree_sha256=digest(tp),ordered_training_pair_ids=expected))
    predictions=read(parent/'predictions.json')
    assert digest(parent/'predictions.json')==pv['evidence_sha256']['predictions.json']
    assert len(predictions)==210 and len({(r['method'],r['pair_id']) for r in predictions})==210
    assert {r['pair_id'] for r in predictions}==old_ids
    assert {r['method'] for r in predictions}=={'frozen_endpoint_baseline','primary_candidate'}
    ordered_groups=[f['held_group'] for f in previous['folds']]+sorted(groups-{f['held_group'] for f in previous['folds']})
    for index,group in enumerate(ordered_groups,1):
        source=next(iter(group_source[group]))
        held=[r['pair_id'] for r in rows if r['duplicate_group_id']==group]
        conditional_held=[p for p in c_conditional if pending_group[p]==group]
        definite_train=[p for p in c_definite if by_id[p]['duplicate_group_id']!=group]
        conditional_train=[p for p in c_conditional if pending_group[p]!=group]
        assert not set(held)&set(definite_train) and not set(conditional_held)&set(conditional_train)
        assert all(by_id[p]['source_image_id']!=source for p in definite_train)
        assert all(pending_source[p]!=source for p in conditional_train)
        folds.append(dict(fold_id=index,held_group=group,held_source=source,
            definite_evaluation_pair_ids=held,conditional_evaluation_pair_ids=conditional_held,
            C_definite_training_pair_ids=definite_train,C_conditional_training_pair_ids=conditional_train,
            A_B_strategy='reuse_exact_historical_folds' if source in old_sources else 'reuse_two_shared_all_historical_fits'))
    hashes[Path(__file__).relative_to(ROOT).as_posix()]=digest(Path(__file__))
    protocol=ROOT/'docs/broader-source-comparison-predeclaration.md'
    hashes[protocol.relative_to(ROOT).as_posix()]=digest(protocol)
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
    result=dict(status='predeclared_awaiting_actual_mask_export',execution_authorized=False,
        features=registry['features'],settings=ep['settings'],sample_weight=None,
        leaf_policy='identity_if_any_fitting_control_v1',gamma_convention='direct_exponent',
        measurement_contract_sha256=registry['measurement_contract_sha256'],lookup_sha256=registry['lookup_sha256'],
        A_ordered_fit_candidates=a,B_ordered_fit_candidates=b,
        C_ordered_definite_fit_candidates=c_definite,C_ordered_conditional_fit_candidates=c_conditional,
        new_primary_admission_rule='Actual exact-mask accept plus verified source/target/feature/role provenance only',
        folds=folds,historical_reusable_trees=reused,
        historical_predictions_to_reuse=dict(path=(parent/'predictions.json').relative_to(ROOT).as_posix(),
            sha256=digest(parent/'predictions.json'),count=210),
        planned_new_tree_fits=dict(A_shared=1,B_shared=1,C_source_held=32,total=34),
        definite_evaluation_cases=117,maximum_evaluation_cases=132,source_groups=32,
        reserved_roles_locked=['development_validation','final_test'],
        stopping_rule='No adoption after any declared gate failure; no follow-up same-data parameter/recipe/source trials',
        automatic_demo_adoption=False,input_sha256=hashes)
    out.mkdir();(out/'design.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    verification=dict(status='pass',source_separated_conditional_folds=32,
        exact_historical_memberships_checked=52,historical_prediction_records_bound=210,
        conditional_masks_not_approved=15,model_fits=0,raw_image_decodes=0,reserved_pixel_access=0,
        design_sha256=digest(out/'design.json'),protocol_sha256=digest(protocol))
    (out/'verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
    print(json.dumps(verification,indent=2))


if __name__=='__main__':main()
