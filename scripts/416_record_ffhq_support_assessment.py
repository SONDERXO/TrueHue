"""Record assistant observations and independently check saved support arithmetic."""
import csv
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics

PARENT = ROOT/'outputs/ffhq_mask_support_v1'
OUT = ROOT/'outputs/ffhq_mask_support_assessment_v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
NOTES = {
 '54632': ('Face support includes the beard by design; lower support reaches crop edge.',
           'White beard/moustache remain visibly selected; not certified skin.',
           'Lower neck partly obscured/cropped; daylight and head covering.'),
 '39568': ('Broad face and some neck support visible; support reaches lower crop.',
           'No obvious large object inclusion on board; hair-edge and shadow uncertainty remain.',
           'Directional sunlight/shadow; lower neck cropped.'),
 '29617': ('Sunglasses and part of hand inside outline are corrected as designed; does not prove anatomical boundary accuracy.',
           'Most glasses and hand excluded on board; thin occlusion boundaries remain uncertain.',
           'Hand over cheek/jaw and sunglasses; side pose and neck/crop limitations.'),
 '29863': ('Clear spill onto white head covering above forehead; correction support not acceptable as facial extent.',
           'FaceOcc removes much upper contamination but beard/moustache remain selected.',
           'Dim uneven appearance and head covering; neck reaches lower crop.'),
 '16061': ('Glasses inside face are corrected; fringe creates irregular upper outline.',
           'Lens/eye region largely excluded; fringe and glasses-rim boundaries uncertain.',
           'Glasses/reflections; neck is limited by collar/crop.'),
 '52445': ('Face support available; associated neck is absent, not a complete face-and-neck success.',
           'No obvious large occluder inclusion on board; fine skin boundaries not established.',
           'Chin close to clothing/foreground object; no visible neck support recovered.'),
 '32685': ('Small lateral neck fragments beside jaw; possible collar inclusion, not reliable complete neck coverage.',
           'Fringe boundary irregular; no obvious large non-skin patch on board.',
           'Downward pose, collar and reduced visible neck; lighting not calibrated.'),
 '53146': ('Face support broad with narrow lateral neck; reaches crop edge.',
           'No obvious large object inclusion on board; shadow and cap-adjacent boundary uncertain.',
           'Hard sun/shadow, squint and head covering; lower crop limits neck.'),
 '48879': ('Correction includes a broad hair-covered area beside face; whole-outline inclusion policy does not establish correct outer extent.',
           'A diagonal strip of blond hair near temple/outer cheek appears selected; skin/hair separation concern.',
           'Oblique pose and hair across face; scarf/crop restrict neck.'),
 '49131': ('Broad face and associated neck visible; lower neck reaches crop edge.',
           'No obvious large occluder on board; stubble and fine boundaries remain unverified.',
           'More frontal example; reference lighting/skin and full neck still not admitted.'),
 '59807': ('Glasses and microphone inside outline corrected by design; neck association also needs scrutiny near necklace/clothing.',
           'Most microphone and lens region excluded; glasses rims, forehead fringe and lower occlusion boundaries uncertain.',
           'Glasses, microphone, fringe, jewellery and collar/crop; not a clean skin reference.'),
 '46795': ('Broad face support; only79 predicted associated neck pixels, not proof of usable neck coverage.',
           'No obvious large object inclusion on board; fringe/eye boundaries and shadow remain uncertain.',
           'Strong outdoor light/shadow, pose and high collar; neck largely unavailable.')}


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    manifest = read(PARENT/'sha256.json')
    assert all(sha(PARENT/k) == v for k, v in manifest.items())
    inputs = read(PARENT/'inference_plan.json')['input_sha256']
    assert all(sha(p) == h for p, h in inputs.items())
    result = read(PARENT/'results.json'); rows = []
    assert {r['id'] for r in result['records']} == set(NOTES)
    for r in result['records']:
        folder = PARENT/r['id']
        image = cv2.imread(str(folder/'input.png'))
        baseline = cv2.imread(str(folder/'baseline_mask.png'), 0)
        candidate = cv2.imread(str(folder/'candidate_mask.png'), 0)
        correction = cv2.imread(str(folder/'correction_mask.png'), 0)
        neck = cv2.imread(str(folder/'neck_mask.png'), 0)
        alpha = np.load(folder/'alpha.npy', allow_pickle=False)
        assert not candidate[baseline == 0].any()
        assert set(np.unique(candidate)) <= {0,255}
        assert not neck[correction == 0].any()
        assert np.array_equal(compute_masked_lab_statistics(image,candidate,1000),
                              r['candidate_report']['statistics'])
        assert int((candidate>0).sum())/int((baseline>0).sum()) == r['candidate_report']['retained_fraction']
        # Recompute the declared alpha equation directly, rather than invoking the renderer.
        _, x = np.nonzero(baseline); width = max(2,int(np.ceil((x.max()-x.min()+1)*.03)))
        distance = cv2.distanceTransform((correction>0).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
        t = np.clip(distance/width,0,1).astype(float)
        expected = t*t*(3-2*t); expected[correction == 0] = 0
        assert np.array_equal(alpha,expected)
        assert np.isfinite(alpha).all() and alpha.min()>=0 and alpha.max()<=1
        demo = cv2.imread(str(folder/'operator_demo.png'))
        assert np.array_equal(demo[correction == 0],image[correction == 0])
        rgb = image[:,:,::-1].astype(float)/255
        transformed = np.clip(rgb**.85*np.array([1.05,1.,.95]),0,1)
        expected_demo = np.rint((rgb*(1-alpha[:,:,None])+transformed*alpha[:,:,None])*255).astype(np.uint8)[:,:,::-1]
        assert np.array_equal(demo,expected_demo)
        a,b,c = NOTES[r['id']]
        rows.append(dict(id=r['id'], correction_status=r['correction_status'],
             measurement_status=r['measurement_status'], correction_pixels=r['correction_pixels'],
             neck_pixels=r['neck_pixels'], measured_pixels=int((candidate>0).sum()),
             parent_retained_fraction=r['candidate_report']['retained_fraction'],
             correction_observation=a, measurement_observation=b, source_limitation=c,
             observer='assistant', evidence='all12 saved256px boards; qualitative, no dense ground truth',
             disposition='retain_not_admitted', actual_skin_admitted=False,
             correction_admitted=False, reference_admitted=False, training_admitted=False, MST=None))
    OUT.mkdir()
    data = dict(records=rows, training_admissions=0, mask_admissions=0,
        original_cases_retained=12, parent_manifest_sha256=sha(PARENT/'sha256.json'),
        observation_script_sha256=sha(Path(__file__)), no_new_inference=True,
        verification=dict(saved_statistics_checks=12, independent_alpha_checks=12,
             independent_RGB8_demo_checks=12, parent_subset_checks=12,
             parent_manifest_and_input_hashes_unchanged=True,
             focused_tests='31 passed in4.34s; not full suite'))
    (OUT/'assessment.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    with (OUT/'assessment.csv').open('w',newline='',encoding='utf-8') as stream:
        writer = csv.DictWriter(stream,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    body = []
    import html
    for r in rows:
        body.append('<h2>'+r['id']+'</h2><p>'+html.escape(r['correction_observation'])+'</p><p>'+html.escape(r['measurement_observation'])+
            '</p><p>'+html.escape(r['source_limitation'])+'</p><img style="width:100%" src="../ffhq_mask_support_v1/'+r['id']+'/board.png">')
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>FFHQ support findings</title>'+
        '<body style="font:18px system-ui;max-width:1450px;margin:auto;padding:20px"><h1>FFHQ mask/support findings</h1>'+
        '<p>All12 retained. Technical processing succeeded; zero images admitted. Assistant observations only, no annotation task. '+
        'Panels: working input; correction green/cyan neck; measurement green; selected pixels; illustrative operator.</p>'+
        '<p><a href="../ffhq_source_visual_assessment_v1/review.html">Source attribution and limitations</a></p>'+''.join(body),encoding='utf-8')
    assert all(sha(PARENT/k) == v for k, v in manifest.items())
    assert all(sha(p) == h for p, h in inputs.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2))
    print(json.dumps(data['verification'],indent=2))


if __name__ == '__main__':
    main()
