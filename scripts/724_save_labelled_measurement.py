"""One local research annotation worker; never runs a predictor."""
from pathlib import Path
import argparse
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.demo.labelled_measurement import save_annotation


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--task', type=Path, required=True)
    cli.add_argument('--payload', type=Path, required=True)
    cli.add_argument('--output-parent', type=Path, default=ROOT / 'outputs/labelled_measurement_annotations_v1')
    args = cli.parse_args()
    folder = save_annotation(args.task, json.loads(args.payload.read_text(encoding='utf-8')),
                             args.output_parent)
    with args.payload.with_suffix('.result.json').open('x', encoding='utf-8') as stream:
        json.dump(dict(annotation=str(folder.resolve())), stream)


if __name__ == '__main__':
    main()
