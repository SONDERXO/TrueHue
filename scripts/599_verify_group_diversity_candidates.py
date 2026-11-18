"""Reconstruct roster and inspect existing hash metadata, without image reads."""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/group_diversity_candidates_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'plan_PRIVATE.json');bound=read(OUT/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bound.items())
    receipt=ROOT/'outputs/stellenbosch_received_data_v1';subjects=read(receipt/'subjects_PRIVATE.json');files=read(receipt/'files_PRIVATE.json')
    expected=[]
    for lo,hi in ((1,3),(3,5),(5,7),(7,9)):
        pool=[r for r in reversed(subjects) if r['subject_key'] not in d['excluded_keys'] and Decimal(lo)<=Decimal(r['exact_decimal'])<Decimal(hi)]
        ranked=sorted(pool,key=lambda r:hashlib.sha256((d['seed']+r['subject_key']).encode()).hexdigest())
        expected.extend(r['subject_key'] for r in ranked[:10])
    assert expected==[r['subject_key'] for r in d['groups']]
    hashes=defaultdict(set)
    for f in files:
        if f['path'].endswith('.jpeg'):hashes[f['sha256']].add(f['subject_key'])
    cross_duplicates=[dict(source_sha256=r['source_sha256'],candidate_key=r['subject_key'],matching_keys=sorted(hashes[r['source_sha256']])) for r in d['selection'] if hashes[r['source_sha256']]!={r['subject_key']}]
    assert not cross_duplicates
    # Inspect direct source-bearing records in canonical existing top-level metadata.
    # Dependency hashes, subject inventories and mere filename mentions are not pixel exposure.
    candidate={r['source_sha256'] for r in d['selection']};hits=[];checked=0;checked_hashes={}
    for package in (ROOT/'outputs').iterdir():
        if not package.is_dir() or package==OUT:continue
        for name in ('results_PRIVATE.json','preparation_PRIVATE.json','manifest.json'):
            p=package/name
            if not p.exists():continue
            try:value=read(p)
            except (ValueError,UnicodeError):continue
            if not isinstance(value,dict):continue
            checked+=1;checked_hashes[str(p)]=sha(p)
            for field in ('records','rows'):
                for row in value.get(field,[]) if isinstance(value.get(field),list) else []:
                    if isinstance(row,dict) and row.get('source_sha256') in candidate:
                        hits.append(dict(package=package.name,file=name,case_id=row.get('case_id'),source_sha256=row['source_sha256']))
    assert not hits
    counts=Counter(r['role'] for r in d['groups']);assert counts=={'development_candidate':32,'closed_holdout_candidate':8}
    assert Counter(r['role'] for r in d['selection'])=={'development_candidate':96,'closed_holdout_candidate':24}
    result=dict(passed=True,groups=40,source_metadata_rows=120,role_counts=dict(counts),
        cross_publisher_exact_hash_duplicates=cross_duplicates,canonical_source_record_matches=hits,
        canonical_metadata_files_checked=checked,canonical_metadata_sha256=checked_hashes,
        source_hashes=len(bound),plan_sha256=sha(OUT/'plan_PRIVATE.json'),verifier_sha256=sha(Path(__file__)),
        new_image_reads=0,new_fits=0,scientific_admissions=0,
        limitation='Exact-hash and canonical direct-record audit, not perceptual duplicate, universal exposure or identity certification.')
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('PASS deterministic40groups/120metadata rows,32/8roles,0cross-publisher exact-hash duplicates;',checked,'canonical metadata files,0direct source matches; no image reads.')

if __name__=='__main__':main()
