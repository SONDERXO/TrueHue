"""Verify writing provenance and links; no images, models, tests or experiments."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/thesis_progress_update_20261103_v1'
DRAFTS = ['docs/thesis-methods-results-draft-2026-11-03.md',
          'docs/thesis-discussion-limitations-conclusion-draft-2026-11-03.md']
HISTORICAL = ['docs/thesis-methods-results-draft.md',
              'docs/thesis-discussion-limitations-conclusion-draft.md',
              'docs/thesis-results-addendum-2026-11-01.md',
              'Thesis Proposal Document.pdf']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    linked = set()
    link_count = 0
    for name in DRAFTS:
        path = ROOT/name
        text = path.read_text(encoding='utf-8')
        assert '\ufffd' not in text
        assert 'Development is' in text
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in target or target.startswith('#'):
                continue
            resolved = (path.parent/target.split('#',1)[0]).resolve()
            assert resolved.is_relative_to(ROOT.resolve()) and resolved.is_file(), target
            linked.add(resolved.relative_to(ROOT.resolve()).as_posix())
            link_count += 1
    proposal_hash='1426f3769ba771daadf9b6e0e0b1e347729c8f04919c214e6fedc3df272e7b8a'
    assert sha(ROOT/'Thesis Proposal Document.pdf') == proposal_hash
    frozen = ROOT/'outputs/integrated_correction_plan_v1'
    source_hashes = json.loads((frozen/'source_hashes.json').read_text())
    manifests = json.loads((frozen/'parent_manifest_hashes.json').read_text())
    assert all(sha(ROOT/k)==v for k,v in source_hashes.items())
    assert all(sha(ROOT/'outputs'/k/'sha256.json')==v for k,v in manifests.items())
    claims = [
        dict(id='historical_models', evidence=['endpoint-feature-tree-results.md',
            'reviewed-primary-training-results.md','broader-source-comparison-results.md'],
            meaning='historical automatic-model experiments, not revised-mask scores'),
        dict(id='mask_continuity', evidence=['adopted-masking-design-2026-11-01.md',
            'reference-r1-and-continuity-results-2026-11-01.md'],
            meaning='adopted development design; six of16 changed,588pixels; no new trained predictions'),
        dict(id='nostril_MST', evidence=['nostril-mst-calibration-results-2026-11-01.md'],
            values=dict(attempts=418,measured=393,subjects=15,failures=25,
                ordinal_MAE=2.125,exact_percent=12.98,median_baseline_exact_percent=13.99),
            meaning='exposed subject-held development, mapping unadopted'),
        dict(id='FaceOcc',evidence=['faceocc-comparison-evidence-2026-11-01.md',
            'faceocc-qualitative-conclusion-2026-11-01.md',
            'faceocc-development-service-results-2026-11-01.md'],
            meaning='sparse/qualitative and software evidence, not dense accuracy or deployment'),
        dict(id='skin_study',evidence=['mst-subject-skin-study-results-2026-11-02.md'],
            values=dict(fixed_subjects=19,favourable=11,concern_or_uncertain=7,failure=1),
            meaning='structured answers, not objective skin or cohort admission'),
        dict(id='PPR',evidence=['ppr10k-operator-diagnostic-results-2026-11-02.md',
            'ppr10k-contrast-diagnostic-results-2026-11-02.md',
            'ppr10k-new-group-comparison-results-2026-11-02.md',
            'ppr10k-clipping-detail-results-2026-11-02.md',
            'ppr10k-smooth-boundary-results-2026-11-02.md'],
            meaning='target-aware fits; mixed-region caveat retained; later revised-region rendering not refitting'),
        dict(id='generated_checks',evidence=['blended-recovery-target-results-2026-11-03.md',
            'directional-exposure-revision-results-2026-11-03.md',
            'synthetic-development-role-results-2026-11-03.md','core-colour-recipe-results-2026-11-03.md'],
            meaning='RGB8-code residuals on generated arrays, not predictions or tone coverage'),
        dict(id='scope_and_next_gates',evidence=['proposal-scope-validation-2026-11-03.md',
            'integrated-correction-development-plan-2026-11-03.md','panel-change-register.md'],
            meaning='photographic restoration already proposal scope; development/final evaluation unfinished'),
        dict(id='Android',evidence=['delivery-checkpoint-2026-11-01.md'],
            meaning='six native/18JVM/one-example emulator parity; old baseline, not physical-device/newmask validation')]
    for row in claims:
        row['evidence_sha256']={name:sha(ROOT/'docs'/name) for name in row['evidence']}
    OUT.mkdir()
    payloads = dict(claim_evidence=claims,
        draft_sha256={name:sha(ROOT/name) for name in DRAFTS},
        historical_sha256={name:sha(ROOT/name) for name in HISTORICAL},
        linked_source_sha256={name:sha(ROOT/name) for name in sorted(linked)},
        verification=dict(drafts=2,local_links_checked=link_count,distinct_link_targets=len(linked),
            proposal_hash_unchanged=True, integrated_plan_sources_unchanged=len(source_hashes),
            integrated_parent_manifests_unchanged=len(manifests),
            writing_only=True,new_experiments=0,new_fits=0,new_photos=0,new_tests=0,
            panel_approval_claimed=False,final_completion_claimed=False))
    for name,value in payloads.items():
        path=OUT/(name+'.json')
        path.write_text(json.dumps(value,indent=2),encoding='utf-8')
        assert json.loads(path.read_text(encoding='utf-8'))==value
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()
        if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(payloads['verification'],indent=2))


if __name__=='__main__':
    main()
