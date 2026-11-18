"""Build read-only paper/prototype milestone from saved text/JSON evidence only."""
from pathlib import Path
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/research_prototype_paper_milestone_v1'
DATE = '2026-11-12'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve milestone')
    bound = {}
    def bind(name):
        p = ROOT/name
        assert p.suffix in ['.json', '.md', '.py', '.cmd']
        b = p.read_bytes();bound[name] = hashlib.sha256(b).hexdigest()
        return b.decode('utf-8-sig')
    def read(name):
        return json.loads(bind(name))
    baseline = read('outputs/reviewed_ffhq_restoration_comparison_v1/summary_PRIVATE.json')
    search = read('outputs/bounded_training_comparison_v1/summary_PRIVATE.json')
    spatial = read('outputs/spatial_input_correction_comparison_v1/summary_PRIVATE.json')
    broad = read('outputs/expanded_correction_comparison_v1/results_PRIVATE.json')['summary']
    assessment = read('outputs/expanded_correction_comparison_v1/assessment_PRIVATE.json')
    lineage = read('outputs/consolidated_training_design_decision_v1/summary_PRIVATE.json')
    audit = read('outputs/reviewed_ffhq_support_audit_v1/audit_PRIVATE.json')
    for p in ['outputs/reviewed_ffhq_restoration_comparison_v1/verification_PRIVATE.json',
              'outputs/bounded_training_comparison_v1/verification_PRIVATE.json',
              'outputs/spatial_input_correction_comparison_v1/verification_PRIVATE.json',
              'outputs/expanded_correction_comparison_v1/verification_PRIVATE.json']:
        assert read(p)['passed']
    for p in ['docs/consolidated-training-design-decision-2026-11-12.md',
        'docs/correction-model-and-paper-realignment-2026-11-11.md',
        'docs/completed-ffhq-support-results-2026-11-11.md',
        'docs/correction-training-target-audit-results-2026-11-11.md',
        'docs/expanded-correction-training-results-2026-11-08.md',
        'docs/green-feature-correction-results-2026-11-09.md',
        'docs/gray-pixel-selector-results-2026-11-12.md',
        'docs/traditional-feature-scope-decision-2026-11-11.md',
        'docs/reviewed-ffhq-restoration-results-2026-11-11.md',
        'docs/bounded-training-comparison-results-2026-11-11.md',
        'docs/spatial-input-correction-results-2026-11-11.md',
        'src/demo/current_masking.py', 'src/demo/desktop.py', 'run_truehue_demo.cmd',
        'review_ffhq_support.cmd', 'scripts/842_build_prototype_paper_milestone.py']:
        bind(p)
    assert audit['passed'] and audit['summary']['saved_revisions'] == 11
    assert not assessment['all_requirements_pass']
    assert all(not x['development_checks_passed'] for x in [baseline, search, spatial])
    attempt_counts = {k:sum(v['attempts'] for v in records.values()) for k,records in broad.items()}
    available_counts = {k:sum(v['available'] for v in records.values()) for k,records in broad.items()}
    scored_counts = {k:sum(v['scored'] for v in records.values()) for k,records in broad.items()}
    assert sum(attempt_counts.values()) == 756
    assert sum(available_counts.values()) == 451
    assert sum(scored_counts.values()) == 560
    assert lineage['expanded_originals'] == 102 and lineage['later_originals'] == 82
    ffhq_table = '| Input role | Input RGB | Baseline RGB | Search RGB | Spatial RGB | Input DE | Baseline DE | Search DE | Spatial DE |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n'
    labels = dict(identity='Unchanged reference', exposure_under='Underexposure',
                  exposure_over='Overexposure', colour_cool='Mild cool cast')
    numeric_rows = []
    for role,label in labels.items():
        b,s,n = [d['by_role'][role] for d in [baseline, search, spatial]]
        values = [b['input_RGB'], b['output_RGB'], s['output_RGB'], n['output_RGB'],
                  b['input_DE'], b['output_DE'], s['output_DE'], n['output_DE']]
        ffhq_table += '| '+label+' | '+' | '.join(f'{v:.4f}' for v in values)+' |\n'
        numeric_rows.append(dict(role=role, values=values))
    broad_table = '| Exposed cohort/layer | Uncorrected RGB | Aligned comparator RGB | Expanded candidate RGB | Uncorrected DE | Aligned comparator DE | Expanded candidate DE |\n|---|---:|---:|---:|---:|---:|---:|\n'
    coverage_table = '| Cohort/layer | Attempted | Model input available | Regional score available |\n|---|---:|---:|---:|\n'
    for cohort, layers in broad.items():
        for layer,record in layers.items():
            coverage_table += f"| {cohort}/{layer} | {record['attempts']} | {record['available']} | {record['scored']} |\n"
            if layer != 'clean':
                raw = assessment['input_baselines'][cohort+'_'+layer]
                parent,candidate = [record['methods'][k] for k in ['parent','candidate']]
                values = [raw['input_RGB'],parent['region_MAE'],candidate['region_MAE'],
                          raw['input_DE'],parent['region_CIEDE2000'],candidate['region_CIEDE2000']]
                broad_table += '| '+cohort+'/'+layer+' | '+' | '.join(f'{v:.4f}' for v in values)+' |\n'
    draft = '''# TrueHue: research-prototype methods and developmental results

12 November 2026. Working paper insert prepared from preserved records. This is an interim research milestone, not a replacement for the submitted proposal or a claim of a finished correction model. Numerical tables reproduce saved developmental results; no experiment was rerun for this draft.

## Suggested abstract text

This study investigates single-photo photographic restoration using facial colour measurements, the Individual Typology Angle (ITA), an experimental Monk Skin Tone (MST) estimate, and decision-tree prediction of gamma and red/blue adjustment parameters. A local research prototype supports inspection and optional manual refinement of separate measurement and correction regions. Developmental comparisons showed useful average exposure restoration, but gains were inconsistent across correction types and source photographs. A broader training-data comparison preserved usable unchanged references and improved mean reconstruction relative to uncorrected distorted inputs, while losing recovery relative to its frozen comparator. In a separate eleven-source controlled diagnostic, ordinary and revised tree designs continued to alter unchanged references and harm mild colour-cast inputs. Implementation and metric replay confirmed reproducibility of these outcomes but did not establish model validity. The present work therefore demonstrates a functioning experimental pipeline and documents unresolved correction generalization; independent final evaluation, expert appraisal, tone-stratified conclusions and qualified Android delivery remain incomplete.

## 1. Study objective and scope

The primary task is restoration of synthetically altered photographs toward their original photographic references. The uncorrected distorted photograph is the required baseline. Original images are photographic targets, not calibrated measurements of intrinsic skin reflectance; these experiments cannot prove recovery of a person's actual skin colour or correction of real smartphone camera bias. The intended final correction predictor remains one decision tree using ITA/MST and input-derived traditional colour statistics. Local single-photo operation is retained.

The proposed paper originally described facial correction. The developed research workflow includes visible-neck correction and optional manual support refinement as explicit extensions. Manual intervention is reported separately from automatic support estimation. Learned segmentation components already used in the support workflow do not make the correction predictor a neural model; the proposed additional neural correction-feature route was not selected.

## 2. Measurement, support and correction method

Measurement and correction masks have different purposes. Facial measurement excludes non-skin structures and estimates CIELAB statistics and ITA. Correction support may include the visible neck and uses its own protection and soft boundary blend. User-reviewed selections retain uncertainty around beard, hair, glasses, microphones and fine boundaries; review is not a guarantee of dense physical skin labels. Derivative masks in the eleven-source diagnostic were propagated through geometry-preserving photometric transformations, not newly predicted or individually reviewed for every derivative.

ITA is computed from measured mean L* and b*. Its mapped MST value is an experimental input estimate whose provenance and lighting sensitivity must be retained. Different historical mask, crop and mapping contracts are not interchangeable. The FFHQ working-frame application uses an existing fixed map under explicitly unvalidated transfer; it is not evidence of calibrated MST accuracy or underlying tone diversity. Reference information is used to construct supervision and scores, not supplied to single-photo inference.

For the controlled working-frame diagnostic, encoded RGB8 is converted to [0,1]. Direct correction raises each channel to a shared positive gamma, multiplies red and blue by their predicted gains, clips to [0,1], blends with the actual input using its saved alpha, and rounds to RGB8. Identity controls are [1,1,1]. The forward recipes use gamma 1/0.7 for darkening, gamma 0.7 for brightening, or red gain 245/255 for a mild cool cast. Nominal inverse controls follow the audited power/gain inverse. Quantization and boundary blending mean that nominal inverse controls do not imply exact final-pixel restoration.

The paper's Table 2 also includes brightness/contrast/channel-slider settings. Earlier work gave an explicit composite implementation and approximate bounded three-control targets, with clipping and residual reports. The simple diagnostic is a declared engineering subset, not completion of the full tone-dependent Table 2 experiment. Approximate composite recovery targets are not exact physical inverse parameters or proven global optima.

## 3. Data, allocation and evaluation

Experiments are reported as separate cohorts and contracts rather than pooled as a single benchmark. In the broad source-expansion comparison, the full fit used 1,117 conditions from 102 originals. A later reserved-clean design removed 227 conditions from twenty usable originals, leaving 890 fitting rows from 82 originals. Those reserved-clean roles are different from the untouched final holdout. Publisher/source groups are not verified person identities; synthetic variants and repeated fold appearances are not additional independent participants.

The later reviewed FFHQ diagnostic uses eleven accepted original references, eleven identities and thirty-three controlled derivatives: forty-four available cases from forty-eight planned roles. Four roles from one user-rejected underexposed reference remain excluded in the ledger. All eleven actual support reviews were saved and audited; three contained painted edits and eight explicit unchanged selections. These are complete historical reviews, not pending annotation tasks. The four roles of each source were held together, producing eleven folds with forty fitting and four held cases each.

The ordinary baseline used a depth-four DecisionTreeRegressor, seed 42, minimum leaf size one, unweighted squared-error fitting and sixteen fixed input features. The bounded-search and spatial-feature comparisons were separately specified modifications with the same source folds and correction operator; neither was adopted. The spatial comparison added all thirty-six fixed descriptors, rather than selecting features using held outcomes. No final all-data model was trained from these comparisons.

RGB mean absolute error and CIEDE2000 are computed against the same photographic reference and scoring support for each matched comparison. For the working-frame FFHQ experiment, every actual-input alpha-positive pixel/channel contributes. Unchanged references, underexposure, overexposure and colour casts are reported separately, together with individual harms and protected/zero-alpha equality. Lower reconstruction error does not by itself establish perceptual naturalness, physical accuracy or fairness. Parameter error is interpreted against the declared control targets, not as MST-label accuracy.

The broad experiment's coverage accounting is:

''' + coverage_table + '''
The full attempt denominator is 756; model input is available for 451 attempts and regional scoring for 560. These denominators are deliberately different. A row can retain a reference-scoring region and receive an unchanged failure-policy output despite unavailable actual-input measurement. Such scored fallback rows are not successful model predictions. Rows without reference support remain in the attempt ledger but lack a regional score. Fourteen unchanged-reference measurement failures are not learned clean preservation. The 24-photo final holdout and older locked allocations have not been opened for this milestone.

## 4. Developmental results

### 4.1 Broader training-data comparison

''' + broad_table + '''
The expanded candidate preserved all forty usable unchanged references across the two exposed cohorts, compared with two unwanted edits in each cohort for the aligned comparator. Core reconstruction improved relative to uncorrected inputs, but worsened relative to that comparator. Core beneficial RGB outcomes decreased from 106 to 62 of 176 scored development conditions and from 84 to 51 of 144 later conditions. Core RGB harms decreased from one and five to zero. Stress results retained trade-offs, including worse later CIEDE2000 and fewer beneficial outcomes. The fixed comparison required preservation and retained recovery together, so the candidate failed and was not promoted.

These results supply positive exposed-development restoration evidence. They do not turn a failed adoption comparison into an accepted model or establish independent final performance. The earlier comparator likewise remains an experimental reference, not a validated fallback for deployment.

### 4.2 Separate reviewed working-frame diagnostic

Each row below contains eleven held-photo outputs. The three candidate columns are preserved comparisons, not a selection of a deployable winner. RGB values use code units; DE denotes CIEDE2000.

''' + ffhq_table + '''
All three designs edited all eleven unchanged references. Each improved both mean exposure directions relative to the corresponding distorted inputs, but substantially worsened mean mild-cast reconstruction. The ordinary baseline harmed ten of eleven colour cases in RGB and eight in CIEDE2000. The spatial candidate harmed ten in RGB and nine in CIEDE2000. The complete case ledgers retain individual exposure harms rather than treating mean improvement as universal benefit. Protected and zero-alpha pixel invariants passed.

The bounded search reduced summed fitting control SSE by approximately 84%, but improved fitting did not produce reliable held-photo decisions. This distinguishes numerical training success from the paper's restoration question. The current sample has a constant blue-control target of one; zero blue parameter error is not evidence that blue correction was learned.

### 4.3 Measurement and representation findings

Known inverse controls in the saved target audit produced far smaller errors than learned controls on the same simple recipes, confirming a substantial prediction gap without proving a global rendering optimum. All forty-four input feature vectors were distinct; this excludes exact conflicting full-vector targets in those saved records but does not prove generalization. All eleven original references received the same MST estimate. Changes in two distorted variants do not constitute independent tone labels or demonstrated tone conditioning.

A separate gray-pixel engineering study used twelve generated conditions only. It found false material selections and numerical near-tie sensitivity and stopped before any photo screen or tree fit. Those fixtures are not portrait data or correction accuracy results. The neural-feature feasibility review was not selected. Neither route changed the app or contributes a new successful restoration result.

## 5. Discussion and limitations

The evidence shows that ITA/MST-informed tree-based correction can improve selected developmental restoration averages, while the tested models remain unreliable across correction types and source content. Improving masks, adding identity rows, expanding sources, reducing fitting loss and adding summaries did not by themselves establish the required transfer. This does not prove that every decision tree or traditional representation must fail.

The failure of a comparison's frozen engineering checks must be distinguished from the paper's primary uncorrected-baseline question. Exact unchanged-output preservation and nonregression versus a particular comparator were prospective criteria of particular comparisons; they are not silently rewritten as verbatim proposal requirements. Conversely, mean colour error worse than the uncorrected baseline directly limits restoration claims independently of the identity criterion. No failed criterion has been relaxed after observing results.

Coverage is limited by exposed development reuse, uncertain person independence, small source counts, incomplete blue/combined/severity coverage in the eleven-source diagnostic, lighting-sensitive MST estimates, differing historical processing contracts and uncertain support boundaries. The present results cannot support a complete tone-group fairness conclusion. A future primary protocol must explicitly resolve the proposal's MST-E evaluation-versus-calibration wording, executable Table 2 interpretation and disparity formula before the corresponding evaluation. None requires inventing skin-tone labels or physically measured intrinsic colour.

## 6. Prototype status and interim conclusion

The current desktop workflow demonstrates local processing, separate support inspection, optional manual refinement and saved exports. Source inspection confirms that current displayed-mask measurements and historical model controls can have different provenance. Refining the displayed mask does not retrain the correction tree or recompute those historical controls. Therefore successful editing and saving must not be described as correction-model validation. The desktop demo does not run the rejected candidates reported above.

The milestone is a functioning research prototype with reproducible developmental evidence and unresolved correction quality. No trained candidate is promoted by this draft. A validated final model, compatible frozen end-to-end evaluation, genuine photographer MOS and measured Android correction delivery remain incomplete. No expert scores, significance claims, final fairness conclusion or completion date are supplied. The working-model objective remains open; preparing this milestone does not automatically redefine the study as a limitations-only thesis.

## Evidence for insertion and review

All exact table values are linked to their saved JSON sources in the milestone's metrics and provenance files. Narrative evidence: [consolidated training decision](consolidated-training-design-decision-2026-11-12.md), [broad expansion results](expanded-correction-training-results-2026-11-08.md), [reviewed FFHQ baseline](reviewed-ffhq-restoration-results-2026-11-11.md), [bounded search](bounded-training-comparison-results-2026-11-11.md), [spatial comparison](spatial-input-correction-results-2026-11-11.md), [support audit](completed-ffhq-support-results-2026-11-11.md), [target audit](correction-training-target-audit-results-2026-11-11.md), and [scope realignment](correction-model-and-paper-realignment-2026-11-11.md). These internal records support this insert; the final manuscript must retain its original bibliography and cite adopted published methods rather than substitute internal filenames for literature citations.
'''
    guide = '''# Research-prototype demonstration guide

12 November 2026. This guide presents existing software and preserved results. It does not request another photo, mask review, training run or expert rating. No live application or new photo inference was executed when preparing this milestone.

## Opening statement

"TrueHue is a local research prototype for single-photo skin-region measurement and decision-tree correction. Mask inspection, optional manual refinement and exports work. The tested correction models are not validated for reliable use, and the current demonstration retains historical controls. I will show both restoration benefits and failures."

## A five-minute walkthrough

1. Open the [milestone report](../outputs/research_prototype_paper_milestone_v1/index.html). Show the status statement before any examples. This read-only report does not run a model or write annotations.
2. Explain the two supports: facial measurement for Lab/ITA and a separate face/visible-neck correction area with protection. Explain optional manual refinement as a supported interaction, not a new request to edit the completed review queue.
3. Open all four linked saved spatial-comparison sheets. Within each case, panels are **input / held-model output / original reference**. Together they show all 44 cases from eleven source photos. They are a failed developmental candidate, not the current app, an independent final test or a best-result gallery. Include the identity and mild-cast failures as well as exposure improvements.
4. Show the matched table in the report. Explain that useful average exposure restoration coexists with unwanted edits and colour harms. The larger experiment is a separate cohort and cannot be pooled into the 44-case averages.
5. Close with what remains unresolved: source transfer, honest tone-group evidence, an end-to-end compatible frozen model, final evaluation, expert MOS and Android measurements. Keep the working-model objective explicit.

## Existing desktop software, if already demonstrating it

The current launcher is `run_truehue_demo.cmd`. Its UI has **Choose photo**, **Run demo**, **Save result / report**, and **Refine mask**. This guide does not run it or select any new image. Use an existing permitted development example only when a live demonstration is separately intended; never browse to locked images. Do not imply that the saved experimental report is a live application run.

The UI itself labels the workflow as current masks with older experimental controls. Source inspection of `src/demo/current_masking.py` confirms separate historical feature/MST/control provenance and `combined_pipeline_validated=False`. The refinement callback updates displayed measurement and reloads the refined run; it does not retrain the tree or recalculate the historical controls. Save applies to the export, not scientific model admission. A better painted beard exclusion may improve measurement while leaving an overly bright correction unresolved.

The root `review_ffhq_support.cmd` is a completed data-review queue, not the presentation launcher. Its eleven saves were audited; do not use it to redo the reviews. Earlier labelled, brightness and photographic reviews likewise need no repetition. Do not run numbered training/acquisition scripts as a demonstration setup step, especially script 665.

## Accurate wording

| Say | Avoid claiming |
|---|---|
| "The prototype supports manual mask refinement and export." | "Manual refinement fixed the learned correction model." |
| "This preserved developmental comparison improved exposure means." | "These examples prove correction works on unfamiliar photos." |
| "The correction predictor is a decision tree using ITA/MST features." | "The experiment demonstrated fair correction across MST groups." |
| "The broad model preserved 40 usable clean references." | "All 54 clean photos were successfully analyzed and preserved." |
| "The current app uses historical controls and is unvalidated." | "The new experimental model is already integrated." |
| "Final evaluation and expert MOS are pending." | "Visual inspection here is an expert MOS or final test." |

No screenshots, new visual assessments, user reviews, app execution or phone benchmarks are claimed by this guide. The linked boards were inspected in their recorded experiment; this milestone only links them. No photos are embedded in the paper draft or copied into a distributable package. Keep source licences and permission requirements in mind before sharing images externally; no sharing is performed here.
'''
    remaining = '''# Remaining work after this milestone

12 November 2026. The user selected a prototype/paper milestone while retaining the working correction-model goal. The following statuses are distinct; a completed draft does not convert pending experiments into results.

| Deliverable | Milestone status | Still needed for the corresponding final claim |
|---|---|---|
| Interim methods/results/discussion text | Prepared from saved evidence | Researcher review and integration with the actual manuscript/template; proposal is unchanged |
| Demonstration material | Read-only report and guide prepared | A real presentation if desired; no fresh live GUI or photo inference has been performed |
| Optional manual refinement | Existing function and eleven audited FFHQ saves documented | No new review is requested; this is not model training |
| Reliable correction model | Unfinished; no candidate adopted | A genuinely justified intervention and prospective evidence, not another automatic feature/data sweep |
| Compatible measurement-to-controls pipeline | Unqualified | One matching mask/geometry/measurement/MST/features/tree/render contract; current demo has historical controls |
| Complete primary synthetic experiment | Incomplete | Explicit adopted recipe/target/role protocol consistent with the paper; no failed experiment reopened |
| Tone-stratified/fairness conclusion | Unsupported by the current diagnostic | Eligible group evidence and a prospectively defined analysis; no fabricated labels or exposure-severity-as-tone claim |
| Independent final evaluation | Not started | Qualifying frozen method and a specific later final-access decision; no holdout opened now |
| Genuine expert MOS | No ratings supplied in this milestone | Actual appraisals of an explicitly identified system, reported with their real sample counts; no outreach or scores fabricated |
| Android correction delivery | Not qualified for the reviewed models | Matching assets, actual protection/output parity and phone measurements after model readiness |

The next user-facing action is reviewing the milestone text and deciding what belongs in the manuscript or presentation. A Word/PDF template or required chapter structure would determine formatting if that becomes the next requested task. No new model search is required to review this draft, and no adviser approval is a prerequisite. Do not call this a final submission, validated correction model, negative-results-only thesis decision or completed study.

Retained choices: one final tree, ITA/MST, lightweight traditional correction features, single photo, face/visible neck, optional manual refinement, existing datasets, no neural feature extraction or new captures. PPR remains optional and paused. All old failures/gates/reviews remain preserved; final24 and older locks remain byte-unread. No deadline beyond the preference for "soon" has been asserted.
'''
    paper_name = 'prototype-paper-methods-results-draft-2026-11-12.md'
    guide_name = 'prototype-demonstration-guide-2026-11-12.md'
    remaining_name = 'prototype-milestone-remaining-work-2026-11-12.md'
    index_name = 'prototype-paper-milestone-2026-11-12.md'
    index = f'''# TrueHue prototype/paper milestone

12 November 2026. User-selected interim milestone; the working correction-model objective remains open.

**Prepared:**

- [Read-only presentation report](../outputs/research_prototype_paper_milestone_v1/index.html)
- [Paper methods, results, discussion and interim conclusion draft]({paper_name})
- [Demonstration walkthrough and accurate claims]({guide_name})
- [Remaining work and final-claim limits]({remaining_name})

The report reproduces saved numbers and links the complete 44-case comparison. It does not run the application or a correction model. The draft separates the broad and small cohorts, reports failures and does not promote a candidate. Current manual refinement remains available, but displayed-mask edits do not recompute the historical correction controls.

No submitted proposal, existing scientific artifact, runtime, model, source photo, user review or locked allocation was changed. No new fits, expert MOS, final evaluation or Android result is claimed. Numeric provenance and verification receipts are local under `outputs/research_prototype_paper_milestone_v1/`. Do not distribute private photographs or artifacts merely because this local report links them.
'''
    docs = {paper_name:draft, guide_name:guide, remaining_name:remaining, index_name:index}
    for name in docs:
        if (ROOT/'docs'/name).exists():
            raise FileExistsError(name)
    OUT.mkdir()
    for name,body in docs.items():
        (ROOT/'docs'/name).write_text(body,encoding='utf-8')
    # A local read-only report. Existing PNGs are linked, never opened or copied.
    def html_table():
        head = ['Role','Input RGB','Baseline RGB','Search RGB','Spatial RGB']
        return '<table><thead><tr>'+''.join('<th>'+h+'</th>' for h in head)+'</tr></thead><tbody>'+''.join(
            '<tr><th>'+html.escape(labels[r['role']])+'</th>'+''.join(f'<td>{v:.4f}</td>' for v in r['values'][:4])+'</tr>'
            for r in numeric_rows)+'</tbody></table>'
    sheets = [ROOT/'outputs/spatial_input_correction_comparison_v1'/f'visual_sheet_{n}.png' for n in range(1,5)]
    assert all(p.is_file() for p in sheets)  # metadata only, no PNG bytes read
    links = ''.join(f'<li><a href="../spatial_input_correction_comparison_v1/visual_sheet_{n}.png">Sheet {n}: saved input / output / reference panels</a></li>' for n in range(1,5))
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>TrueHue research milestone — 12 November 2026</title>
<style>body{font:17px/1.65 system-ui,sans-serif;color:#233044;background:#f5f7fa;margin:0}main{max-width:1050px;margin:auto;padding:40px 24px}h1{line-height:1.2;font-size:2.3rem}h2{margin-top:2.2em}.notice{border-left:5px solid #975615;background:#fff4df;padding:18px 24px}section{background:white;padding:18px 26px;border-radius:8px;margin:24px 0}table{border-collapse:collapse;width:100%;font-size:15px}th,td{padding:12px;text-align:right;border-bottom:1px solid #d9e0ea}th:first-child{text-align:left}a{color:#155dc0}.scroll{overflow:auto}footer{color:#58677b;font-size:14px}@media print{body{background:white}main{padding:0}section{break-inside:avoid}}</style><main>
<p>12 November 2026 · Local research-prototype milestone</p><h1>TrueHue: implemented workflow, unresolved correction quality</h1>
<div class="notice"><strong>The correction model is unfinished.</strong> This milestone documents existing software and saved developmental evidence. No candidate is adopted, no final test is reported, and no new model runs when you open this page.</div>
<section><h2>What the prototype demonstrates</h2><p>Separate measurement and correction supports, ITA display, optional manual refinement and exports. The current desktop demonstration retains historical MST/control measurements: editing a displayed mask does not retrain the tree or recompute those controls.</p></section>
<section><h2>What the preserved experiments show</h2><p>The broader 102-original training comparison improved average exposure restoration versus uncorrected inputs and preserved 40 usable unchanged references, but failed its frozen adoption criteria. It is a different cohort from the eleven-source results below.</p><p>In the separate 44-case diagnostic, mean exposure error improves while mild colour casts become worse. All 11 unchanged references are edited by each listed candidate. Lower RGB error is better.</p><div class="scroll">'''+html_table()+'''</div><p>These are exposed-development results, not independent final accuracy or fairness. No columns represent the current deployed app or a selected winner.</p></section>
<section><h2>View the complete saved comparison</h2><p>Four sheets cover all 44 spatial-candidate cases, including failures. Every case shows input, held output and original reference. Images remain in their existing local folders; opening these links does not run inference.</p><ol>'''+links+'''</ol><p>Manual reviews are complete. No new annotation or ratings are requested.</p></section>
<section><h2>Paper and demonstration material</h2><ul>'''+''.join(f'<li><a href="../../docs/{name}">{label}</a></li>' for name,label in [(paper_name,'Methods/results/discussion draft'),(guide_name,'Demonstration guide'),(remaining_name,'Remaining work and limits')])+'''</ul><p>The submitted proposal is unchanged. Final evaluation, expert MOS, supported tone-group claims and qualified Android correction delivery remain pending.</p></section>
<footer>No source/holdout photographs were read to build this report. Tables come from saved JSON; links refer to existing boards. This local file contains no scripts or external assets and does not publish or upload data.</footer></main></html>'''
    (OUT/'index.html').write_text(page,encoding='utf-8')
    metrics = dict(ffhq_table_rows=numeric_rows, broad_summary=broad,
        broad_input_baselines=assessment['input_baselines'],
        coverage=dict(attempts=attempt_counts, available=available_counts, scored=scored_counts),
        interpretations=dict(all_comparisons_unadopted=True, final_accuracy_claim=False,
            MOS_supplied=False, fairness_claim=False, model_finished=False))
    (OUT/'metrics_PRIVATE.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2)+'\n',encoding='utf-8')
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in bound.items())
    print(json.dumps(dict(paper_draft=str(ROOT/'docs'/paper_name), entry=str(ROOT/'docs'/index_name),
        report=str(OUT/'index.html'), fits=0, photo_reads=0, holdout_reads=0),indent=2))


if __name__ == '__main__':
    main()
