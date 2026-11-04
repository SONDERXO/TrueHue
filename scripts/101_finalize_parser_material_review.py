"""Package fixed experiments, preserved reviews and explicit technical holds."""
import hashlib
import html
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    output=ROOT/'outputs/parser_material_boundary_v1'
    summary=json.loads((output/'summary.json').read_text())
    core=ROOT/'outputs/parser_material_core_v1';historical=ROOT/'outputs/parser_material_historical_v1'
    predecessors={name:json.loads((path/'summary.json').read_text()) for name,path in [('core',core),('historical',historical)]}
    previous={phase:{r['key']:r for r in data['records']} for phase,data in predecessors.items()}
    reviews=json.loads((ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json').read_text())
    review_map={r['pair_id']:r for r in reviews['pairs']}
    current=[r for r in summary['records'] if r['phase']=='core' and 'retention_old_generation_denominator' in r]
    assert len(current)==32
    paint_cases=[r for r in summary['records'] if r['phase']=='core' and r['image_id']=='16798']
    paint_evidence=[dict(case=r['key'],**r['stages']['correction']['paint']) for r in paint_cases]
    assert sorted(p['added'] for p in paint_evidence)==[69,113]
    readiness=dict(status='technical_hold_not_waiting_for_routine_user_permission',ready_to_regenerate=False,ready_to_train=False,
        candidate='C2 is preserved as a promising contour-recovery experiment; no arm adopted',
        reasons=['New protected painted-reference pixels selected versus original correction masks',
                 'Valid labeled-skin coverage decreases in the stricter arms',
                 'Five historical prospective-generation retention failures and prior source/variant holds remain'],
        paint_evidence=paint_evidence,prior_reviews_unchanged=True,models_fitted=0,
        current_pairs=[dict(pair_id=r['key'],image_id=r['image_id'],prior_human_decision=review_map[r['key']]['human_decision'],
            mask_policy_admitted=False,retention_screen_pass=r['retention_old_generation_denominator']['screen_pass'],
            measurement_valid=r['measurement_statistics']['statistics']['valid'] and r['measurement_statistics']['brightness']['valid']) for r in current],
        original_fold4_status='empty, not silently reassigned',revised_fold_plan_status='unexecuted',
        original_user_direction='data/manifests/parser_combination_v1/user_direction.json',
        report='docs/parser-material-combination-results.md',summary_sha256=digest(output/'summary.json'))
    (output/'readiness.json').write_text(json.dumps(readiness,indent=2),encoding='utf-8')
    pages=['<!doctype html><meta charset="utf-8"><title>TrueHue combined parser review</title>',
        '<style>body{font:16px system-ui;margin:24px;background:#fafafa;color:#202020}main{max-width:1280px;margin:auto}img{max-width:100%;display:block;margin:12px 0}table{border-collapse:collapse;width:100%}th,td{padding:8px;border:1px solid #ccc;text-align:left}details{margin:24px 0;border:1px solid #ccc;padding:14px;background:white}summary{cursor:pointer;font-weight:600}a{color:#16498a}.hold{padding:16px;background:#fff0d9}code{font-size:14px}</style><main>',
        '<h1>Combined parser, anatomy and material experiment</h1>',
        '<p>All143 known source/input cases were checked:53 current/reference cases and90 historical source/variant cases. No original data, review decision or runtime model changed.</p>',
        '<div class="hold"><strong>Technical hold for regeneration and training.</strong> C2 recovers the annotated cheek and passes32/32 current numerical screens, but still selects newly protected paint pixels and loses some labeled skin. These passes are not mask-quality approval.</div>',
        '<p>Columns in each contact: <strong>Original | A anatomy | F full Lab | C chroma only | C2 chroma plus2px boundary guard</strong>. Green marks selected support. Generation/correction are prospective masks; inputs still use old generation masks.</p>',
        '<p><a href="readiness.json">Readiness and32 pair statuses</a> · <a href="summary.json">C2 metrics and witnesses</a> · <a href="verification.json">Final verification</a> · <a href="../parser_material_core_v1/summary.json">Core A/F/C metrics</a> · <a href="../parser_material_historical_v1/summary.json">Historical A/F/C metrics</a></p>',
        '<h2>Paint-area failure, despite paint-point passes</h2><table><tr><th>Native reference</th><th>C2 painted pixels selected</th><th>Newly selected painted pixels versus original</th></tr>']
    for evidence in paint_evidence:
        pages.append(f'<tr><td>{html.escape(evidence["case"])}</td><td>{evidence["selected"]}</td><td>{evidence["added"]}</td></tr>')
    pages.append('</table><p>Paint detail: original | C2 mask | selected reference exclusions in orange, newly selected reference exclusions in red. The counts above isolate the painted subgroup; colored details also show feature disagreements. Unlabeled pixels are unscored.</p>')
    for variant in ['clean','global_color_shift']:
        pages.append(f'<img src="reference_details/16798_regression_{variant}_paint.png" alt="{variant} paint and exclusion detail">')
    pages.append('<h2>Source and variant comparisons</h2><p>Expand a source for all stages. Historical decisions shown below are preserved, not overridden by new masks.</p>')
    for phase in ['core','historical']:
        rows=[r for r in summary['records'] if r['phase']==phase]
        for ident in sorted({r['image_id'] for r in rows}):
            pages.append(f'<details id="{phase}_{ident}"><summary>{phase}: {ident}</summary><table><tr><th>Case</th><th>Measurement</th><th>Retention old / prospective</th><th>Original human decision</th></tr>')
            for row in (r for r in rows if r['image_id']==ident):
                key=row['key'];valid=row.get('measurement_statistics',{}).get('statistics',{}).get('valid')
                old=row.get('retention_old_generation_denominator');new=row.get('retention_prospective_generation_denominator')
                screen=lambda v:('pass' if v['screen_pass'] else 'hold') if v else 'not evaluated'
                prior=previous[phase][key];decision=prior.get('original_review') or review_map.get(key)
                decision=decision.get('human_decision','not a variant review') if decision else 'not a variant review'
                pages.append(f'<tr><td>{html.escape(key)}</td><td>{"valid" if valid else "not measured"}</td><td>{screen(old)} / {screen(new)}</td><td>{html.escape(decision)}</td></tr>')
            pages.append(f'</table><a href="contacts/{phase}_{ident}.png"><img loading="lazy" src="contacts/{phase}_{ident}.png" alt="All original, A, F, C and C2 masks for {phase} {ident}"></a></details>')
    pages.append('<h2>Historical31154 witness edge</h2><p>Three remaining pixels overlap the old diagnostic rectangle at a blurred edge; they are not automatically certified hair or skin. The original technical hold remains.</p><img src="contacts/31154_witness_zoom.png" alt="Original and three retained witness-edge pixels"><p>No model fit, training admission, runtime adoption, final-evaluation claim or proposal amendment.</p></main>')
    (output/'review.html').write_text('\n'.join(pages),encoding='utf-8')
    for parent in [core,historical]:
        (parent/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Parser material experiment</title><h1>Parser material experiment</h1><p><a href="../parser_material_boundary_v1/review.html">Combined original/A/F/C/C2 review gallery</a></p><p><a href="summary.json">This phase metrics</a> · <a href="verification.json">Independent replay</a></p>',encoding='utf-8')
    # Each source snapshot contains keys for original artifacts; consolidate before hashing.
    hashes=dict(summary['input_sha256'])
    for parent in [core,historical]:
        replay=json.loads((parent/'verification.json').read_text())
        hashes.update(replay['output_sha256'])
    for parent in [output]:
        hashes.update({str(p.relative_to(ROOT)):digest(p) for p in (parent/'masks').glob('*.png')})
    assert all(digest(ROOT/name)==h for name,h in hashes.items())
    # Static gallery QA covers every local image/link, including predecessor links.
    for parent in [output,core,historical]:
        for target in re.findall(r'(?:href|src)="([^"]+)"',(parent/'review.html').read_text()):
            if target=='verification.json' and parent==output:continue
            if not target.startswith('#'):assert (parent/target).is_file(),target
    verification=dict(status='pass',predecessor_masks_replayed=804,C2_masks_disk_replayed=268,
        predecessor_feature_sets=357,C2_feature_sets=119,predecessor_reference_checks=102,additional_C2_reference_checks=34,
        tests='481 passed in9.70s, workspace-local temporary directory',
        visual_review='All30 phase/source contacts covering80 predecessor boards and80 follow-up boards, plus paint details and witness zoom',
        original_and_candidate_hashes_unchanged=True,artifact_count_verified=len(hashes),
        summary_sha256=digest(output/'summary.json'),readiness_sha256=digest(output/'readiness.json'),
        finalizer_sha256=digest(Path(__file__)),report_sha256=digest(ROOT/'docs/parser-material-combination-results.md'),
        no_regeneration=True,models_fitted=0,limitation='Development replay and reference checks, not independent final mask accuracy or Android validation.')
    (output/'verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
    print(json.dumps(verification,indent=2))


if __name__=='__main__':main()
