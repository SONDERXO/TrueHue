"""Prospective review eligibility and exact carry-forward; no automatic answers."""
from copy import deepcopy
import math
from .acceptability_review import validate

EVIDENCE=['input_RGB8_sha256','output_RGB8_sha256','reference_RGB8_sha256','correction_sha256','measurement_sha256','protection_sha256','alpha_sha256','viewing_contract','question_semantics']

def carry_forward(old,new,rating,provenance,old_output,new_output,display):
    if any(k not in old or k not in new or not old[k] or old[k]!=new[k] for k in EVIDENCE):return None
    if old['viewing_contract']!=display:return None
    if not provenance.get('revision_sha256') or not provenance.get('case_id'):return None
    if old_output not in ['A','B'] or new_output not in ['A','B']:raise ValueError('Explicit panel mapping required')
    result=deepcopy(rating)
    if old_output!=new_output:
        for key in ['preference','artifact']:
            if result.get(key) in ['A','B']:result[key]='B' if result[key]=='A' else 'A'
    return dict(rating=result,provenance=deepcopy(provenance),exact_evidence=deepcopy(new))

def assess(public,saved,load_private):
    complete=validate(public,saved)
    for c in public['cases']:
        if c['kind']=='identity' and saved['ratings'].get(c['id'],{}).get('identity')=='unwanted_change':
            return dict(status='FAIL_CLOSED_NOT_ADOPTED',scores_unblinded=False)
    if not complete:raise ValueError('Complete initial judgments before unblinding')
    if any(r.get('identity')=='cannot_judge' or r.get('preference')=='cannot_judge' or r.get('artifact')=='cannot_judge' for r in saved['ratings'].values()):raise ValueError('Unresolved judgment; no unblinding')
    private=load_private();useful=set();concerns=[]
    for c in public['cases']:
        r=saved['ratings'][c['id']];p=private['mapping'][c['id']]
        if c['kind']=='identity':continue
        if r['preference']==p['output_panel']:useful.add(p['role'])
        if r['preference'] in ['both_unacceptable','A','B'] and r['preference']!=p['output_panel'] or r['artifact'] in [p['output_panel'],'both']:concerns.append(c['id'])
    families={'exposure_under','exposure_over','colour_cool','blue_decrease','blue_increase'}
    numeric=all(math.isfinite(private['benefits'][f]) and private['benefits'][f]>0 for f in families)
    return dict(status='DEVELOPMENT_ACCEPTABLE' if numeric and families<=useful and not concerns else 'NOT_READY',scores_unblinded=True,model_adopted=False,concerns=concerns)
