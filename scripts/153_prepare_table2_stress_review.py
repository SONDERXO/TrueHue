"""Stage source-grouped candidates and an offline review; never admit or fit."""
import base64
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.ita_estimation.square_measurement import contract
from src.data_preparation.training_manifest import LABEL_TO_GROUP
from src.data_preparation.source_group_folds import source_group_folds


def main():
    out=ROOT/'outputs/table2_stress_review_v1'
    if out.exists():raise FileExistsError(out)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    folder=ROOT/'outputs/table2_known_source_feasibility_v1'
    path=folder/'summary.json';data=json.loads(path.read_text())
    assert digest(path)==json.loads((folder/'verification.json').read_text())['summary_sha256']
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    for p,h in data['evidence_sha256'].items():assert digest(folder/p)==h
    _,identity=contract(ROOT);assert identity==data['measurement_contract_sha256']
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert digest(artifact)==data['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(json.loads(artifact.read_text()),identity)
    old=json.loads((ROOT/'outputs/control_aware_model_build_v1/fit_manifest.json').read_text())
    provenance={r['source_path']:r for r in old['rows']}
    candidates=[];sections=[];sources=[]
    for ref in data['references']:
        source=ref['source_path'];name=Path(source).stem;p=provenance[source]
        if ref['report']['status']!='success':raise ValueError('Reference failure must be explicitly staged')
        label=lookup.label(ref['report']['features']['input_ita_degrees']);group=LABEL_TO_GROUP[label]
        selected=next(r for r in data['records'] if r['source_path']==source and r['severity_probe']==group)
        source_record=dict(source_image_id=p['source_image_id'],duplicate_group_id=p['duplicate_group_id'],
            source_path=source,reference_mst_estimate=label,assigned_severity=group,
            group_assignment_source='experimental_reference_ita_lookup',official_mst_label=None,
            mask_review_status='pending',scene_review_status='pending')
        sources.append(source_record)
        for variant,report in [('identity',ref['report']),('table2_'+group,selected['input_measurement'])]:
            candidates.append(dict(pair_id=name+'__'+variant,source_image_id=p['source_image_id'],
                duplicate_group_id=p['duplicate_group_id'],partition='train',table_use='train',
                planned_fold_only=True,training_eligible=False,variant=variant,
                input_processing_status=report['status'],measurement=report,
                experimental_input_features={**report['features'],'input_mst_index':lookup.label(report['features']['input_ita_degrees'])-1} if report['status']=='success' else None,
                target_fit=selected.get('target_fit') if variant!='identity' else None,
                identity_target=[1.,1.,1.] if variant=='identity' else None,
                evidence_prefix=str(folder.relative_to(ROOT)/name),
                clipping=selected['clipping'] if variant!='identity' else dict(clipped_pixels=0,clipped_channel_samples=0),
                reference_mst_estimate=label,assigned_severity=group,mask_review_status='pending'))
        image=base64.b64encode((folder/f'{name}_review.png').read_bytes()).decode()
        sections.append(f'<section><h2>{html.escape(name)} — estimated MST {label}; proposed {group} severity</h2>'
            f'<p>Reference and all three diagnostic severities are shown. The proposed pair uses {group} only, plus unchanged identity control. '
            'Check actual skin coverage, eyes/lips/hair/background exclusions, and whether the scene has only one person. '
            'Report accept, reject or uncertain for this source; mention any affected column.</p>'
            f'<img alt="Reference, light, medium and dark skin masks for {name}" src="data:image/png;base64,{image}"></section>')
    # Candidate fold planning only. The helper never confers admission; all rows
    # still carry training_eligible=False and pending review in the saved ledger.
    folds=source_group_folds(candidates)
    out.mkdir(parents=True)
    result=dict(status='awaiting_user_mask_and_scene_review',training_admitted=0,sources=sources,
        candidate_rows=candidates,provisional_folds=folds,measurement_contract_sha256=identity,
        lookup_sha256=digest(artifact),feasibility_summary_sha256=digest(path),
        policy='table2_clipping_stress_training_v1',
        identity_gate='zero fixed-reference-mask CIEDE2000 increase; conservative engineering gate, not a perceptual threshold',
        limitation='Estimated severity assignment and MST features use the weak experimental mapping. No official FairFace MST or independently verified person-disjoint split is claimed.')
    (out/'readiness.json').write_text(json.dumps(result,indent=2))
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Table 2 source review</title>'
        '<style>body{font:17px system-ui;max-width:1100px;margin:30px auto;padding:15px}img{width:100%}section{margin:40px 0;border-top:1px solid #aaa}</style>'
        '<h1>Table 2 experimental training: six sources needing review</h1>'
        '<p>Green indicates estimated skin. These are distorted inputs, not learned corrections. '
        'Severity assignment is an experimental estimate. All previous review decisions are preserved. '
        'Reply with source IDs to accept, reject or mark uncertain; acceptance concerns only the visible mask/scene, not MST accuracy.</p>'
        +''.join(sections),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',readiness_sha256=digest(out/'readiness.json'),
        review_sha256=digest(out/'review.html'),candidate_count=len(candidates),planned_fold_count=len(folds),
        all_candidates_unadmitted=all(r['training_eligible'] is False for r in candidates)),indent=2))
    print(json.dumps(dict(sources=sources,candidates=len(candidates),provisional_folds=len(folds),training_admitted=0),indent=2))


if __name__=='__main__':main()
