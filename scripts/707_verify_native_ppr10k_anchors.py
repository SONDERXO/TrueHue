"""Verify saved native detector records/coordinates and bind actual visual review."""
from pathlib import Path
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/ppr10k_native_anchor_comparison_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve completed verification')
    d=read(OUT/'results_PRIVATE.json');plan=read(OUT/'plan_PRIVATE.json')
    artifacts=read(OUT/'artifact_sha256_PRIVATE.json')
    assert all(sha(OUT/p)==h for p,h in artifacts.items())
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    assert d['detector_forwards']==8 and len(d['records'])==8
    assert [r['frame'] for r in d['records']]==plan['frames']
    prior=read(ROOT/'outputs/ppr10k_automatic_support_v1/results_PRIVATE.json')
    old={r['frame']:r for r in prior['records']}
    checks=[]
    # Explicit visual findings from all eight viewed source-only overlays.
    matches={frame:frame!='904_0' for frame in plan['frames']}
    observations={'787_0':'same hat-wearing painter', '330_0':'historical boat portrait face',
        '767_0':'same seated bridal face','1117_0':'same spotlit profile face',
        '1188_0':'historical image-right man in couple','990_0':'same seated hat-wearing face',
        '904_0':'child at image centre, not historical image-right adult man',
        '455_0':'historical face with rollers'}
    for r in d['records']:
        h,w,_=r['shape'];filtered=[]
        for f in r['raw_faces']:
            assert len(f)==15 and all(math.isfinite(v) for v in f)
            if f[14]<plan['threshold']:continue
            x=max(0,min(math.trunc(f[0]),w));y=max(0,min(math.trunc(f[1]),h))
            bw=max(1,min(math.trunc(f[2]),w-x));bh=max(1,min(math.trunc(f[3]),h-y))
            filtered.append(([x,y,bw,bh],f[14]))
        filtered.sort(key=lambda z:z[0][2]*z[0][3],reverse=True)
        assert [a for a,b in filtered]==r['candidate_boxes']
        assert [b for a,b in filtered]==r['candidate_scores']
        assert len(filtered)==r['candidate_face_count']==1
        for a,b in zip(r['previous_boxes_native_display'],old[r['frame']]['anchors_256']):
            expected=[b[0]/256*w,b[1]/256*h,b[2]/256*w,b[3]/256*h]
            assert all(abs(x-y)<1e-12 for x,y in zip(a,expected))
        checks.append(dict(frame=r['frame'],raw_filtering_and_coordinates=True,
            visual_match_to_historical_face=matches[r['frame']],observation=observations[r['frame']],
            overlay_sha256=sha(OUT/r['frame']/'overlay.png')))
    retained=sum(r['previous_available'] and matches[r['frame']] for r in d['records'])
    recovered=sum(not r['previous_available'] and matches[r['frame']] for r in d['records'])
    wrong=[r['frame'] for r in d['records'] if not matches[r['frame']]]
    result=dict(passed=True,verification_scope='Saved filtering, geometry, hashes and visual accounting; NO repeated inference.',
        checks=checks,reviewed_overlays=8,detector_outputs_with_one_face=8,
        correct_historical_face_matches=sum(matches.values()),prior_successes_retained=retained,
        previous_misses_recovered_as_correct_face=recovered,wrong_person_selections=wrong,
        predeclared_advance_criterion_pass=retained==4 and recovered>=1 and not wrong,
        disposition='FAIL advance criterion:904_0 selects child, not fixed historical adult. No adoption or rescue.',
        no_new_forwards=True,new_fits=0,holdout_reads=0,
        results_sha256=sha(OUT/'results_PRIVATE.json'),artifact_manifest_sha256=sha(OUT/'artifact_sha256_PRIVATE.json'),
        verifier_sha256=sha(Path(__file__)),
        limitation='Visual selected-face correspondence, not dense detector ground truth; the child is a real face, not a spurious detection.')
    assert all(sha(OUT/p)==h for p,h in artifacts.items())
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('Verification PASS; 8/8 one-face outputs, 7/8 historical-face matches; retained',retained,'recovered',recovered,'wrong',wrong)
    print('Predeclared advancement FAIL. Eight overlays viewed; zero verification forwards.')
if __name__=='__main__':main()
