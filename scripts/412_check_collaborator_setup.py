"""Read-only clone readiness report; optional local assets never imply failure."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import platform

ROOT=Path(__file__).resolve().parents[1]
PACKAGES=['numpy','scipy','opencv-contrib-python','Pillow','mediapipe','scikit-learn',
          'scikit-image','pandas','requests','pytest']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json',action='store_true')
    parser.add_argument('--require-python-deps',action='store_true',
                        help='Fail if the checked Python dependencies are missing')
    args=parser.parse_args()
    required=['README.md','docs/README.md','docs/collaborator-setup.md',
        'src/__init__.py','scripts/run_hello_world.py','tests/test_paper_gamma.py',
        'android-app/app/src/main/AndroidManifest.xml']
    missing=[name for name in required if not (ROOT/name).is_file()]
    versions={}
    for name in PACKAGES:
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]=None
    assets=['Thesis Proposal Document.pdf',
        'models/face_detector/face_detection_yunet_2023mar.onnx',
        'models/face_landmarker/face_landmarker.task',
        'models/face_parser_experimental_v1/resnet18.onnx',
        'android-app/app/src/main/assets/development_pipeline/manifest.json',
        'outputs/ffhq_source_visual_assessment_v1/review.html',
        'data/raw/ffhq_source_preparation_v1/ffhq-dataset-v2.json']
    report=dict(python=platform.python_version(),source_checkout_ready=not missing,
        missing_source_files=missing,checked_packages=versions,
        missing_packages=[name for name,value in versions.items() if value is None],
        optional_local_assets={name:(ROOT/name).is_file() for name in assets},
        local_assets_required_for_source_only_checks=False,
        scientific_validation=False,model_training_ready=False)
    if args.json:print(json.dumps(report,indent=2))
    else:
        print('Source checkout: '+('ready' if not missing else 'missing required source files'))
        print('Python: '+report['python'])
        print('Missing checked packages: '+(', '.join(report['missing_packages']) or 'none'))
        print('Optional local artifacts present: '+str(sum(report['optional_local_assets'].values()))+'/'+str(len(assets)))
        print('Missing photos/models/galleries are expected after cloning. See docs/collaborator-setup.md.')
        print('This checks setup only; it does not validate MST or correction quality.')
    if missing or (args.require_python_deps and report['missing_packages']):raise SystemExit(1)


if __name__=='__main__':main()
