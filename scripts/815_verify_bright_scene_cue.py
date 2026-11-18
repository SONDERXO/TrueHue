"""Independent scalar sixth-moment replay on the fixed44 cached inputs."""
from pathlib import Path
import json,hashlib,math,statistics
import numpy as np
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/bright_scene_cue_readiness_v1';P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    dest=O/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    assert all(sha(p)==h for p,h in read(O/'input_sha256_PRIVATE.json').items())
    rows={r['case_id']:r for r in read(P/'rows_PRIVATE.json')};records=read(O/'records_PRIVATE.json');idx={r['case_id']:r for r in records};pairs=read(O/'pairs_PRIVATE.json');summary=read(O/'summary_PRIVATE.json')
    for r in records:
        old=rows[r['case_id']]
        with np.load(old['pixels_file'],allow_pickle=False) as pack:
            image=pack['input_rgb8'];means=[(math.fsum((int(v)/255.)**6 for v in image[:,:,c].flat)/65536)**(1/6)*255 for c in range(3)]
        assert all(math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-11) for a,b in zip(means,r['p6_channel_means_codes']))
        vals=[math.log((means[0]+1)/(means[1]+1)),math.log((means[2]+1)/(means[1]+1))]
        assert all(abs(a-b)<1e-11 for a,b in zip(vals,r['new_features'].values()))
        assert r['input_vector_float32_18'][:16]==old['input_vector_float32']
        np.testing.assert_array_equal(np.array(list(r['new_features'].values()),np.float32),r['input_vector_float32_18'][16:])
    group={(r['group'],r['role']):r for r in records}
    for p in pairs:
        a=group[p['group'],'identity'];b=group[p['group'],p['role']]
        assert p['new_delta']==[v-w for v,w in zip(b['new_features'].values(),a['new_features'].values())]
        assert p['old_delta']==[v-w for v,w in zip(b['first_moment_ratios'],a['first_moment_ratios'])]
    originals=[r for r in records if r['role']=='identity']
    for j,(name,m) in enumerate(summary['original_dispersion'].items()):
        assert math.isclose(m['original_sd'],statistics.pstdev(r['new_features'][name] for r in originals),abs_tol=1e-12)
        assert math.isclose(m['old_original_sd'],statistics.pstdev(r['first_moment_ratios'][j] for r in originals),abs_tol=1e-12)
    assert len(records)==44 and len(pairs)==33 and summary['cool_red_decreases']==11 and summary['cool_blue_unchanged']==11
    dest.write_text(json.dumps(dict(passed=True,scalar_channel_moment_checks=132,new_feature_checks=88,preserved_parent_values=704,paired_comparisons=33,new_fits=0,original_photo_reads=0,holdout_reads=0,summary_sha256=sha(O/'summary_PRIVATE.json'),verifier_sha256=sha(__file__)),indent=2)+'\n')
    print(dest.read_text())
if __name__=='__main__':main()
