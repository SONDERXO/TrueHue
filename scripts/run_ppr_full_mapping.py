"""Apply the one qualified frozen PPR mapping, sealing all outputs before scoring."""
from pathlib import Path
import sys
import zipfile
import numpy as np
import torch
from ppr_full_pipeline_assessment import (ROOT, ASSETS, QA, OUT, WB, FEATURES, PROTOCOL,
                                         read, write, sha, array_sha, runtime, native, quantize, composite)


def main():
    if OUT.exists():
        raise FileExistsError('Preserve prior or partial mapping attempt')
    qa = read(QA / 'verification.json')
    assert qa['passed'] and qa['actual_image_calls'] == 0
    for path, digest in qa['bindings'].items():
        assert sha(ROOT / path) == digest
    feature_verification = read(FEATURES / 'verification.json')
    assert feature_verification['passed'] and feature_verification['cases'] == 66
    assert sha(FEATURES / 'records.json') == feature_verification['records_sha256']
    assessment = read(ROOT / 'outputs/technical_plan_reassessment_2026_11_17/assessment.json')
    for name in ['verification.json', 'records.json']:
        path = FEATURES / name
        assert sha(path) == assessment['bindings'][path.relative_to(ROOT).as_posix()]
    coefficients = read(FEATURES / 'records.json')
    rows = read(WB / 'rows.json')
    assert len(coefficients) == len(rows) == 66
    assert [r['case_id'] for r in rows] == [r['case_id'] for r in coefficients]
    assert len({r['source_id'] for r in rows}) == 11
    parent = read(WB / 'verification.json')
    assert parent['passed']
    known = {p.replace('\\', '/'): h for p, h in parent['artifacts'].items()}
    bound = dict(qa['bindings'])
    extra = [Path(__file__), QA / 'verification.json', FEATURES / 'verification.json', FEATURES / 'records.json',
             WB / 'verification.json', WB / 'rows.json', WB / 'records.json', WB / 'summary.json']
    for path in extra:
        bound[path.relative_to(ROOT).as_posix()] = sha(path)
    for row, record in zip(rows, coefficients):
        assert all(row[k] == record[k] for k in ['case_id', 'source_id', 'role', 'generated_fixture'])
        assert record['generated_fixture'] is False
        c = np.asarray(record['coefficients'], np.float32)
        assert c.shape == (5,) and np.isfinite(c).all() and c.astype(float).tolist() == record['coefficients']
        path = WB / 'evaluation' / (record['case_id'] + '.npz')
        assert sha(path) == known['evaluation/' + path.name]
        with zipfile.ZipFile(path) as archive:
            assert {'input.npy', 'reference.npy', 'alpha.npy', 'protected.npy', '314.npy', 'constant.npy'} <= set(archive.namelist())
        bound[path.relative_to(ROOT).as_posix()] = sha(path)
    module, luts = runtime()
    before = [array_sha(t.numpy()) for t in luts]
    OUT.mkdir()
    (OUT / 'predictions').mkdir()
    write(OUT / 'bindings.json', bound)
    write(OUT / 'execution_plan.json', dict(cases=66, predictor_calls=0, training_fits=0,
          native_mappings=66, reference_access='Only after all 66 predictions are sealed',
          coefficients='Unmodified five cached float32 values', role_or_target_used_for_mapping=False,
          argv=sys.argv, python=sys.executable, numpy=np.__version__, torch=torch.__version__))
    records = []
    try:
        for record in coefficients:
            path = WB / 'evaluation' / (record['case_id'] + '.npz')
            with np.load(path, allow_pickle=False) as pack:
                image, alpha, protected = [pack[k] for k in ['input', 'alpha', 'protected']]
            assert image.dtype == np.uint8 and array_sha(image) == record['input_rgb_sha256']
            original_hashes = [array_sha(x) for x in [image, alpha, protected]]
            x = torch.from_numpy(np.ascontiguousarray(image.transpose(2, 0, 1)[None])).float() / 255
            x_hash = array_sha(x.numpy())
            raw = native(module, luts, x, np.asarray(record['coefficients'], np.float32))
            rgb = quantize(raw)
            candidate = composite(image, rgb, alpha, protected)
            assert x_hash == array_sha(x.numpy())
            assert original_hashes == [array_sha(x) for x in [image, alpha, protected]]
            assert np.array_equal(candidate[protected], image[protected])
            assert np.array_equal(candidate[alpha == 0], image[alpha == 0])
            dest = OUT / 'predictions' / (record['case_id'] + '.npz')
            np.savez(dest, candidate=candidate, native_rgb=rgb)
            records.append({k: record[k] for k in ['case_id', 'source_id', 'role', 'coefficients', 'input_rgb_sha256']} |
                           dict(npz_sha256=sha(dest), candidate_RGB8_sha256=array_sha(candidate),
                                native_RGB8_sha256=array_sha(rgb), raw_min=float(raw.min()), raw_max=float(raw.max()),
                                below_zero_channels=int((raw < 0).sum()), above_one_channels=int((raw > 1).sum()),
                                changed_pixels=int(np.any(candidate != image, axis=2).sum()),
                                read_keys_before_seal=['input', 'alpha', 'protected']))
            if len(records) % 11 == 0:
                print('PPR mappings saved ' + str(len(records)) + '/66; no reference reads.', flush=True)
        assert before == [array_sha(t.numpy()) for t in luts]
        for path, digest in bound.items():
            assert sha(ROOT / path) == digest
        write(OUT / 'predictions_sealed.json', dict(passed=True, cases=66, records=records,
              LUTs_input_immutable=True, no_reference_access=True, predictor_calls=0, training_fits=0,
              bindings_sha256=sha(OUT / 'bindings.json')))
        print('SEALED 66 PPR outputs before any reference scoring.', flush=True)
    except Exception as error:
        write(OUT / 'mapping_failure.json', dict(error=repr(error), completed=len(records),
              further_attempts_allowed=False))
        raise


if __name__ == '__main__':
    main()
