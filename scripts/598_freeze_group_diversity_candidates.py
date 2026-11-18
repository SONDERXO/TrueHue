"""Metadata-only 32-development/8-closed-holdout roster; no source image reads."""
from pathlib import Path
from decimal import Decimal
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/group_diversity_candidates_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve frozen candidate roster')
    bound={}
    def read(p):p=Path(p);bound[str(p)]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    receipt=ROOT/'outputs/stellenbosch_received_data_v1';subjects=read(receipt/'subjects_PRIVATE.json');files=read(receipt/'files_PRIVATE.json');release=read(receipt/'protocol.json')
    excluded=set()
    for name in ('stellenbosch_bounded_preparation_v1','stellenbosch_new_subjects_v1','frozen_split_subject_check_v1'):
        plan=read(ROOT/'outputs'/name/'plan_PRIVATE.json');excluded.update(r['subject_key'] for r in plan['selection'])
        excluded.update(plan.get('excluded_exposed_keys_PRIVATE',[]))
    filemap={r['path']:r for r in files};groups=[];selection=[]
    seed='TrueHue-group-diversity-expansion-v1:'
    conditions=('F_cool_600','H_warm_600','L_warm_600')
    for low,high in ((1,3),(3,5),(5,7),(7,9)):
        eligible=[r for r in subjects if r['subject_key'] not in excluded and Decimal(low)<=Decimal(r['exact_decimal'])<Decimal(high)]
        ordered=sorted(eligible,key=lambda r:hashlib.sha256((seed+r['subject_key']).encode()).hexdigest())
        assert len(ordered)>=10
        for i,r in enumerate(ordered[:10]):
            role='development_candidate' if i<8 else 'closed_holdout_candidate'
            groups.append(dict(subject_key=r['subject_key'],role=role,score_interval=f'[{low},{high})',source_score=r['exact_decimal']))
            for condition in conditions:
                rel=r['publisher_folder']+'/front-facing/'+condition+'.jpeg';f=filemap[rel]
                selection.append(dict(subject_key=r['subject_key'],role=role,condition=condition,
                    source_path=str(Path(release['dataset_location'])/rel),source_sha256=f['sha256'],
                    source_score=r['exact_decimal'],score_interval=f'[{low},{high})',training_admitted=False,calibration_admitted=False))
    assert len(groups)==40 and len(selection)==120 and len({r['subject_key'] for r in groups})==40
    assert not excluded&{r['subject_key'] for r in groups}
    bound[str(Path(__file__))]=sha(Path(__file__));p=ROOT/'docs/group-diversity-expansion-protocol-2026-11-08.md';bound[str(p)]=sha(p)
    result=dict(status='metadata_candidate_roles_frozen_pending_exposure_duplicate_audit',selection=selection,groups=groups,
        seed=seed,excluded_keys=sorted(excluded),source_hash_origin='Existing release inventory; actual source bytes must be checked before future preparation',
        highest_interval_fresh_groups=0,new_image_byte_reads=0,new_fits=0,scientific_admissions=0,
        limitation='Candidate groups absent from three known pixel plans; not universal exposure/identity/final-test certification')
    assert all(sha(p)==h for p,h in bound.items());OUT.mkdir()
    (OUT/'plan_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print('Frozen40candidate groups:32development/8closedholdout,120source metadata rows. Zero image reads/fits/admissions.')

if __name__=='__main__':main()
