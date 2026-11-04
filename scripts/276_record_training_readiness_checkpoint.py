"""Metadata-only checkpoint: distinguish approved stress pairs from primary data."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/correction_readiness_checkpoint_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    candidate=ROOT/'outputs/endpoint_feature_tree_v1'
    verification=read(candidate/'verification.json');assert verification['status']=='pass'
    plan=read(candidate/'plan.json');rows=plan['rows']
    distorted=[r for r in rows if r['variant']!='identity'];clean=[r for r in rows if r['variant']=='identity']
    clipping=[dict(pair_id=r['pair_id'],fraction=r.get('clipped_pixel_fraction',r.get('clipping_fraction'))) for r in distorted]
    assert len(clean)==26 and len(distorted)==21 and all(r['fraction'] is not None and r['fraction']>0 for r in clipping)
    variants=ROOT/'outputs/three_variant_training_candidates_v1'
    summary=read(variants/'summary.json')
    unreviewed={name:r['unclipped_screen_passing_target_candidates'] for name,r in summary['variants'].items()}
    assert sum(unreviewed.values())==6
    report=dict(status='data_readiness_incomplete_not_another_model_experiment',approved_clean_rows=26,
        approved_distorted_rows=21,approved_distorted_with_any_generation_clipping=21,
        approved_unclipped_distorted_rows=0,approved_source_groups=len({r['duplicate_group_id'] for r in rows}),
        current_candidate='endpoint_feature_tree_v1',current_candidate_clean_failures=read(candidate/'summary.json')['gates']['paired_endpoint11']['harmed_clean_ids'],
        unreviewed_unclipped_screen_passing_variants=unreviewed,unreviewed_variants_automatically_admitted=0,
        scope='Current 47-row candidate plan only; not a claim about all raw data or all historical recipes.',
        limitations=['Any clipping does not make every pixel unusable or prove a pair cannot aid learning.',
            'Zero generation clipping does not establish mask quality, exact invertibility, calibrated color or dataset adequacy.',
            'Clipped experimental fitting remains authorized and preserved; it is not silently forbidden or removed.',
            'Unclipped selection can bias source/tone/severity coverage and requires separate reporting.'],
        new_models_fitted=0,images_opened=0,active_demo_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),candidate/'plan.json',candidate/'summary.json',candidate/'verification.json',variants/'summary.json']})
    out.mkdir();(out/'readiness.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Checkpoint: 26 clean + 21 clipped distorted approvals; 0 unclipped distorted approvals; 6 unreviewed screened variants, not admitted.')


if __name__=='__main__':main()
