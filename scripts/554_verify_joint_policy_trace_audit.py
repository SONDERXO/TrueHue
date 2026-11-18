"""Independent saved-row categories, affine gates and manual leaf verification."""
from pathlib import Path
from collections import Counter
import json,hashlib,struct
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/joint_policy_trace_audit_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def route(tree,features):
    x=[struct.unpack('!f',struct.pack('!f',v))[0] for v in features];node=0
    while tree['nodes'][node]['kind']=='split':
        n=tree['nodes'][node];node=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
    return node

def main():
    audit=read(OUT/'results_PRIVATE.json');bindings=read(OUT/'input_sha256_PRIVATE.json')
    assert all(sha(p)==h for p,h in bindings.items())
    records=read(ROOT/'outputs/joint_neutral_support_v1/results_PRIVATE.json')['records']
    originals={(r['suite'],r['case_id']):r for r in records}
    chosen=[r for r in records if r['suite'] in ('fold_working256','fallback_native224')]
    full=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json')
    gates={f['held_key']:f['model'] for f in read(ROOT/'outputs/benefit_aware_gate_v1/results_PRIVATE.json')['folds']}
    counts=Counter();verified=[]
    for r in chosen:
        if r['features'] is not None:
            g=full['gate'] if r['suite']=='fallback_native224' else gates[r['subject_id']]
            assert r['subject_id'] not in g['training_keys']
            raw=np.asarray(g['coefficient'],dtype=np.longdouble)/np.asarray(g['scale'],dtype=np.longdouble)
            bias=np.longdouble(g['intercept'])-np.dot(raw,np.asarray(g['mean'],dtype=np.longdouble))
            value=float(np.dot(raw,np.asarray(r['features'],dtype=np.longdouble))+bias)
            assert abs(value-r['gate']['logit'])<1e-10 and (value>0)==r['gate']['apply_correction'];counts['gates']+=1
        if not r['reference_available']:continue
        inp=r['input_reference_metrics']['rgb8_mae_codes'];p=r['paths']
        rejected=p['policy_ungated']['reference_metrics']['rgb8_mae_codes']<inp and p['policy_gated']['changed_channels']==0
        lost=p['retained']['reference_metrics']['rgb8_mae_codes']<inp and p['policy_gated']['changed_channels']==0
        item=next(x for x in audit['classifications'] if (x['suite'],x['case_id'])==(r['suite'],r['case_id']))
        assert item['modified_benefit_rejected_by_gate']==rejected and item['retained_benefit_lost']==lost
        reason=('outside_leaf_ranges' if not r['policy']['supported'] else 'neutral_leaf_controls') if lost else None
        assert item['lost_reason']==reason
        if rejected:assert not r['gate']['apply_correction']
        if lost:assert r['gate']['apply_correction'] and p['policy_ungated']['changed_channels']==0
        counts['classifications']+=1;verified.append(item)
    for suite,layers in audit['summary'].items():
        for layer,s in layers.items():
            rr=[x for x in verified if x['suite']==suite and x['layer']==layer];assert len(rr)==s['scored']
            for name,flag,metric in [('modified_benefit_rejected','modified_benefit_rejected_by_gate','policy_ungated_gain'),('retained_benefit_lost','retained_benefit_lost','retained_gain')]:
                group=[x for x in rr if x[flag]];summary=s[name]
                assert len(group)==summary['rows']
                assert len({x['case_id'].split('__')[0] for x in group})==summary['original_photos']
                assert len({x['subject_id'] for x in group})==summary['publisher_keys']
                assert dict(Counter(x['recipe'] for x in group))==summary['recipes']
                assert dict(Counter(x['lost_reason'] for x in group if x['lost_reason']))==summary['lost_reasons']
                if group:assert abs(sum(x[metric] for x in group)/len(group)-summary['mean_modified_gain' if metric=='policy_ungated_gain' else 'mean_retained_gain'])<1e-10
                if layer!='clean' and group:
                    target=sorted(group,key=lambda x:(-x[metric],x['case_id']))[0]
                    category='gate_rejected_benefit' if flag=='modified_benefit_rejected_by_gate' else 'policy_lost_benefit'
                    assert any(b['case_id']==target['case_id'] and b['suite']==suite and b['reason']==category for b in audit['selected_boards'])
    table={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json')}
    f=audit['focal'];q=originals['fallback_native224',f['case_id']];tree=full['split']['heads']['gamma']['tree'];leaf=route(tree,q['features'])
    members=[c for c,x in zip(full['training_cases'],full['training_features']) if route(tree,x)==leaf]
    assert members==f['members'] and leaf==f['leaf']
    assert q['subject_id'] not in full['training_keys']
    mean=sum(table[c]['target'][0] for c in members)/len(members)
    assert abs(mean-f['raw_gamma'])<1e-12
    assert dict(Counter(table[c]['case']['id'] for c in members))==f['recipes'] and f['recipes'].get('clean',0)==0
    for row in f['clean_counterparts']:
        i=full['training_cases'].index(row['case_id']);assert route(tree,full['training_features'][i])==row['gamma_leaf']!=leaf
        assert table[row['case_id']]['target']==[1.,1.,1.]
    assert len(chosen)==audit['attempts']==756 and counts['gates']==audit['gate_checks']==688
    assert all(sha(p)==h for p,h in bindings.items())
    result=dict(passed=True,attempts=756,gate_replays=counts['gates'],classification_checks=counts['classifications'],
        focal_leaf_members=len(members),paired_clean_checks=len(f['clean_counterparts']),source_hashes=len(bindings),verifier_sha256=sha(Path(__file__)),new_fits=0,new_correction_renders=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
