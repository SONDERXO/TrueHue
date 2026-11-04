"""Verify blinded local assets, blank-form JS validation and Python import guards."""
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]


def main():
    package=ROOT/'outputs/photographer_reference_review_v1';target=package/'verification.json'
    if target.exists():raise FileExistsError(target)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    manifest=json.loads((package/'manifest.json').read_text(encoding='utf-8'));identity=digest(package/'manifest.json')
    key=json.loads((package/'researcher_key.json').read_text(encoding='utf-8'))
    assert len(manifest['cases'])==10 and len(key['case_sources'])==10
    assert manifest['reviewer_orders']['P1']!=manifest['reviewer_orders']['P2']
    for c in manifest['cases']:
        assert digest(package/c['image_path'])==c['image_sha256']
        r=next(r for r in key['case_sources'] if r['case_id']==c['case_id'])
        assert digest(ROOT/r['reference_path'])==c['image_sha256']
    validator=importlib.import_module('185_import_photographer_reference_reviews').validate_response
    fixtures=[]
    for reviewer in ['P1','P2']:
        html=(package/(reviewer+'.html')).read_text(encoding='utf-8')
        assert 'researcher_key' not in html and 'http://' not in html and 'https://' not in html
        assert all(r['source_image_id'] not in html for r in key['case_sources'])
        # Synthetic in-memory validation fixtures, never exported as collected ratings.
        good=dict(schema_version=manifest['schema_version'],manifest_sha256=identity,reviewer_code=reviewer,
            photographer_self_declaration=True,session_notes='SYNTHETIC VALIDATION FIXTURE',
            ratings=[dict(case_id=code,detail='adequate',illumination='usable',occlusion='low',decision='suitable',notes='SYNTHETIC FIXTURE') for code in manifest['reviewer_orders'][reviewer]])
        assert validator(good,manifest,identity)==reviewer
        bad=[]
        v=deepcopy(good);v['photographer_self_declaration']=False;bad.append(v)
        v=deepcopy(good);v['ratings']=v['ratings'][:-1];bad.append(v)
        v=deepcopy(good);v['ratings'][0]=v['ratings'][1];bad.append(v)
        v=deepcopy(good);v['ratings'][0]['decision']='uncertain';v['ratings'][0]['notes']='';bad.append(v)
        v=deepcopy(good);v['manifest_sha256']='wrong';bad.append(v)
        v=deepcopy(good);v['ratings'][0]['detail']='';bad.append(v)
        for value in bad:
            try:validator(value,manifest,identity)
            except ValueError:pass
            else:raise AssertionError('Invalid review accepted')
        fixtures.append(dict(reviewer=reviewer,good=good,bad=bad))
    # Run the same browser validator in Node without document/DOM initialization.
    testjs='const fs=require("fs"),vm=require("vm"),assert=require("assert");\n'
    testjs+='const manifest='+json.dumps(manifest)+';const manifestHash='+json.dumps(identity)+';\n'
    testjs+='const source=fs.readFileSync(__dirname+"/review.js","utf8");const fixtures='+json.dumps(fixtures)+';\n'
    testjs+='for(const f of fixtures){const c=vm.createContext({});vm.runInContext("const manifest="+JSON.stringify(manifest)+";const manifestHash="+JSON.stringify(manifestHash)+";const reviewer="+JSON.stringify(f.reviewer)+";const order=manifest.reviewer_orders[reviewer];"+source,c);c.fixture=f.good;assert.equal(vm.runInContext("validateReview(fixture).length",c),0);for(const bad of f.bad){c.fixture=bad;assert(vm.runInContext("validateReview(fixture).length",c)>0);}}console.log("PASS: browser validator accepts complete synthetic fixtures and rejects12invalid fixtures");'
    (package/'validate_review_test.js').write_text(testjs,encoding='utf-8')
    result=subprocess.run(['node',str(package/'validate_review_test.js')],capture_output=True,text=True,check=True)
    assert 'PASS' in result.stdout
    evidence={str(p.relative_to(package)):digest(p) for p in package.rglob('*') if p.is_file()}
    target.write_text(json.dumps(dict(status='pass',verified_local_images=10,reviewer_pages=2,manifest_sha256=identity,
        blank_forms_no_collected_ratings=True,python_validation_fixtures=14,browser_validation_fixtures=14,
        no_source_ids_in_reviewer_pages=True,presentation_blinding_only=True,actual_photographer_responses=0,
        note='Synthetic validation fixtures are code-test data only; not ratings or MOS',evidence_sha256=evidence),indent=2),encoding='utf-8')
    print(result.stdout.strip())


if __name__=='__main__':main()
