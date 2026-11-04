"""Bundle the existing Python-demo baseline and its dependencies, without fitting."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config
from src.skin_masking.landmark_exclusion import FEATURE_INDICES
from src.skin_masking.mouth_exclusion import OUTER_LIPS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    config=get_config();out=ROOT/'android-app/app/src/main/assets/development_pipeline'
    sources={'face_detection_yunet.onnx':ROOT/config.FACE_MODEL_PATH,'face_landmarker.task':ROOT/config.FACE_LANDMARKER_MODEL_PATH,
        'baseline5.json':ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1/fold_1/decision_tree.json',
        'mst_lookup.json':ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'}
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    if args.verify:
        manifest=json.loads((out/'manifest.json').read_text())
        assert manifest['experiment']=='baseline5' and manifest['fold_id']==1
        for name,path in sources.items():assert sha(path)==sha(out/name)==manifest['assets_sha256'][name]
        assert manifest['landmark_regions']==list(FEATURE_INDICES.values())+[list(OUTER_LIPS)]
        print('PASS: same existing baseline5/fold1, lookup, detector and landmark assets; no model fit or parser switch.')
        return
    if out.exists():raise FileExistsError(out)
    for path in sources.values():assert path.is_file(),path
    out.mkdir(parents=True)
    for name,path in sources.items():shutil.copyfile(path,out/name)
    lookup=json.loads(sources['mst_lookup.json'].read_text())
    plan=json.loads((ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1/fit_plan.json').read_text())
    manifest=dict(schema_version='truehue_android_development_v1',experiment='baseline5',fold_id=1,experimental=True,quality_gate_passed=False,
        python_measurement_contract_sha256=lookup['measurement_contract_sha256'],android_measurement_contract='android_square256_port_v1_parity_pending',
        platform_pixel_parity_verified=False,gamma_convention='reciprocal_exponent',features=plan['features'],
        landmark_regions=list(FEATURE_INDICES.values())+[list(OUTER_LIPS)],assets_sha256={name:sha(path) for name,path in sources.items()})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Prepared experimental local assets. They remain gitignored; a fresh clone needs the original local models.')


if __name__=='__main__':main()
