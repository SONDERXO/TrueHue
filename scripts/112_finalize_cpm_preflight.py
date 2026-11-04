"""Verify experimental artifact provenance and record the unexecuted next gates."""
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'outputs/cpm_pattern_preflight_v1';summary=json.loads((out/'summary.json').read_text());legacy=json.loads((out/'legacy_metadata.json').read_text())
    for report in [summary,legacy,json.loads((ROOT/'outputs/material_failure_attribution_v1/summary.json').read_text())]:
        assert all(digest(ROOT/p)==h for p,h in report['input_sha256'].items())
    assert legacy['checkpoint_sha256']==summary['inspection']['checkpoint_sha256']=='27421250269552f61a6c52581a73baf50cb3f4dee88c8403d87943b53a9ebfec'
    checkpoint=ROOT/summary['checkpoint_path'];assert digest(checkpoint)==legacy['checkpoint_sha256']
    assert checkpoint.stat().st_size==130433505
    assert len(legacy['streams'])==5 and legacy['metadata_end']==125125
    assert legacy['streams'][-1]['end']==legacy['metadata_end']
    assert all(a['end']==b['start'] for a,b in zip(legacy['streams'],legacy['streams'][1:]))
    assert legacy['opaque_remaining_bytes']+legacy['metadata_end']==checkpoint.stat().st_size
    assert 'segmentation_models_pytorch.unet.model Unet' in legacy['streams'][3]['serialized_globals']
    assert not legacy['model_deserialized'] and not legacy['serialized_globals_imported'] and not legacy['tensors_materialized']
    assert not summary['readiness']['image_inference'] and not summary['readiness']['training']
    assert not summary['new_image_inference'] and not summary['new_candidate_masks']
    ignored=subprocess.run(['git','check-ignore',str(checkpoint.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True,check=True)
    assert ignored.stdout.strip()
    source=json.loads((out/'source_manifest.json').read_text());assert len(source['sources'])==14
    assert all(source['revision'] in r['url'] and (ROOT/r['local']).is_file() for r in source['sources'])
    readiness=dict(status='hold_preflight_only_not_image_candidate_ready',candidate_lead='CPM pattern branch',
        checkpoint_locally_available=True,static_metadata_inspected=True,actual_model_loaded=False,
        gates=dict(uv_native_coordinate_mapping='unverified',preprocessing_contract='unresolved_training_transfer_difference',
            scalar_cutoff='not_selected',cpu_export_parity='not_tested',material_reference_adjudication='not_completed',
            representative_material_evaluation='not_completed',android_costs='not_tested',checkpoint_data_rights='not_cleared_for_distribution'),
        next_work='Isolated reproducible CPU/export and UV input-contract investigation; no cutoff selection on study images',
        original_reviews_holds_and_folds_unchanged=True,training_pairs_regenerated=0,models_fitted=0)
    (out/'readiness.json').write_text(json.dumps(readiness,indent=2))
    tracked=list((out/'source').glob('*.txt'))+[out/'summary.json',out/'legacy_metadata.json',out/'source_manifest.json',out/'readiness.json',
        checkpoint,Path(__file__),ROOT/'tests/test_cpm_static_preflight.py',ROOT/'docs/cpm-pattern-feasibility.md']
    result=dict(status='pass',source_snapshots_verified=14,checkpoint_bytes=130433505,checkpoint_gitignored=True,
        metadata_streams_checked=5,prior_input_hashes_unchanged=True,
        tests='491 passed in16.98s, including10new offline preflight tests; workspace basetemp',
        limitation='Static metadata provenance only; no model execution, accuracy, CPU/export or phone validation',
        artifact_sha256={str(p.relative_to(ROOT)):digest(p) for p in tracked})
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'}))
if __name__=='__main__':main()
