"""Independent scalar recount/hash audit; no network, torch, photos or fits."""
from pathlib import Path
import json,hashlib,math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/face_underexposure_pilot_v1';DESIGN=ROOT/'outputs/face_underexposure_pilot_design_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dest=OUT/'independent_audit.json'
    if dest.exists():raise FileExistsError(dest)
    proof=read(OUT/'verification.json');assert proof['passed'] and proof['portrait_calls']==66 and proof['training_fits']==0
    for p,h in proof['artifacts'].items():assert sha(OUT/p)==h
    for p,h in read(OUT/'bindings.json').items():assert sha(ROOT/p)==h
    seal=read(OUT/'score_seal.json');assert seal['cases']==66 and sha(OUT/'records.json')==seal['records_sha256']
    roster=read(DESIGN/'roster.json');records=read(OUT/'records.json');rows={r['case_id']:r for r in records}
    assert len(records)==len(rows)==len(roster)==66 and set(rows)=={r['case_id'] for r in roster}
    errors=[]
    for r in roster:
        q=rows[r['case_id']]
        assert all(q[k]==r[k] for k in ['case_id','source_id','role','generated_fixture','input_rgb_sha256'])
        a,b=q['logits'];m=max(a,b);ea,eb=math.exp(a-m),math.exp(b-m)
        p=[ea/(ea+eb),eb/(ea+eb)]
        assert q['scalar_softmax']==p
        errors.append(max(abs(x-y) for x,y in zip(q['probabilities'],p)))
        assert errors[-1]<=2e-7 and q['under_probability']==q['probabilities'][1]
        assert q['predicted_class']==int(b>a) and q['logit_margin']==b-a
    summary=read(OUT/'summary.json');roles=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']
    counts={}
    for role in roles:
        rr=[r for r in records if r['role']==role];assert len(rr)==11
        counts[role]=sum(r['logits'][1]>r['logits'][0] for r in rr)
        s=summary['by_role'][role]
        assert s['count']==11 and s['flagged_under']==counts[role]
        assert s['mean_under_probability']==math.fsum(r['probabilities'][1] for r in rr)/11
        assert s['min_under_probability']==min(r['probabilities'][1] for r in rr)
        assert s['max_under_probability']==max(r['probabilities'][1] for r in rr)
    pairing={};sources=sorted({r['source_id'] for r in records});assert len(sources)==11
    for family,base,under in [('pure','identity','exposure_under'),('combined','colour_only','combined_under')]:
        expected=[]
        for source in sources:
            a=next(r for r in records if r['source_id']==source and r['role']==base)
            b=next(r for r in records if r['source_id']==source and r['role']==under)
            expected.append(dict(source_id=source,reference_case=a['case_id'],under_case=b['case_id'],
                       probability_margin=b['probabilities'][1]-a['probabilities'][1],
                       logit_margin_change=b['logit_margin']-a['logit_margin']))
        p=summary['pairs'][family];assert p['records']==expected
        w=sum(x['probability_margin']>0 for x in expected);t=sum(x['probability_margin']==0 for x in expected)
        assert p['wins']==w and p['ties']==t and p['losses']==11-w-t
        pairing[family]=dict(wins=w,ties=t,losses=11-w-t)
    gates=dict(original_false_flags_zero=counts['identity']==0,colour_false_flags_zero=counts['colour_only']==0,
       pure_under_majority=counts['exposure_under']>=6,combined_under_majority=counts['combined_under']>=6,
       pure_ordering_majority=pairing['pure']['wins']>=6,combined_ordering_majority=pairing['combined']['wins']>=6)
    assert gates==summary['gates'] and all(gates.values())==summary['narrow_pilot_pass']==proof['narrow_pilot_pass']
    access=read(OUT/'access.json');assert len(access)==66 and all(r['keys']==['input'] for r in access)
    assert [r['case_id'] for r in access]==[r['case_id'] for r in records]
    misses=[r for r in records if (r['source_id'],r['role']) in [('16061','exposure_under'),('48879','exposure_under'),('48879','combined_under')]]
    result=dict(passed=True,records=66,independent_softmax_checks=66,softmax_max_error=max(errors),
       original_artifact_hashes=len(proof['artifacts']),source_bindings=len(read(OUT/'bindings.json')),
       role_counts=counts,pair_counts=pairing,gates=gates,narrow_pilot_pass=all(gates.values()),
       prior_three_misses=[{k:r[k] for k in ['case_id','under_probability','predicted_class']} for r in misses],
       new_inference=0,new_fits=0,pixel_decodes=0,model_ready=False)
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
    print(result)
if __name__=='__main__':main()
