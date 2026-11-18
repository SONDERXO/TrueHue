"""Verify immutable prefixes, group roles, descriptor moments and fold binding."""
from pathlib import Path
import json
import hashlib
import math
import struct

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/spatial_input_preparation_v1'
BASE = ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    dest = OUT/'verification_PRIVATE.json'
    if dest.exists():
        raise FileExistsError('Preserve verification')
    for p, h in read(OUT/'input_sha256_PRIVATE.json').items():
        assert hashlib.sha256(Path(p).read_bytes()).hexdigest() == h
    source = {r['case_id']:r for r in read(BASE/'rows_PRIVATE.json')}
    rows = read(OUT/'rows_PRIVATE.json')
    assert len(rows) == len(source) == 44
    assert len({r['case_id'] for r in rows}) == 44
    names = read(OUT/'feature_names_PRIVATE.json')
    assert len(names) == len(set(names)) == 52
    for r in rows:
        old = source[r['case_id']]
        assert not r['generated_fixture'] and not r['training_admitted']
        assert r['input_vector_float32'][:16] == old['input_vector_float32']
        assert r['old_input_vector_float32'] == old['input_vector_float32']
        for field in ['publisher_group', 'experimental_role', 'nominal_controls']:
            assert r[field] == old[field]
        assert list(r['spatial_features']) == names[16:]
        for i, v in enumerate(r['spatial_features'].values()):
            expected = struct.unpack('f', struct.pack('f', v))[0]
            assert r['input_vector_float32'][16+i] == expected
            assert math.isfinite(v)
        for scale in [1, 2]:
            f = r['spatial_features']
            for direction in ['h', 'v', 'd1', 'd2']:
                prefix = f'spatial_nss_s{scale}_{direction}_'
                alpha = f[prefix+'shape']
                lv, rv = f[prefix+'left_variance'], f[prefix+'right_variance']
                mean = (math.sqrt(rv)-math.sqrt(lv))*math.exp(
                    math.lgamma(2/alpha)-.5*(math.lgamma(1/alpha)+math.lgamma(3/alpha)))
                assert math.isclose(mean, f[prefix+'mean'], rel_tol=1e-11, abs_tol=1e-12)
    for fold in read(BASE/'folds_PRIVATE.json'):
        fit = [source[c] for c in fold['fitting_cases']]
        held = [source[c] for c in fold['evaluation_cases']]
        assert len(fit) == 40 and len(held) == 4
        assert {r['publisher_group'] for r in fit}.isdisjoint({r['publisher_group'] for r in held})
    assert all(r['changed_float32_coordinates'] > 0 for r in read(OUT/'responses_PRIVATE.json'))
    dest.write_text(json.dumps(dict(passed=True, prefixes_targets_group_checks=44,
        float32_append_checks=1584, aggd_mean_checks=352, source_disjoint_folds=11,
        photo_reads=0, fits=0, summary_sha256=hashlib.sha256((OUT/'summary_PRIVATE.json').read_bytes()).hexdigest(),
        verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
    print(dest.read_text())


if __name__ == '__main__':
    main()
