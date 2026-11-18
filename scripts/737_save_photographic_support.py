"""One explicit photographic support review; identity alpha only, zero models."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.demo.photographic_support import save_support


def main():
    p=argparse.ArgumentParser();p.add_argument('--export-folder',type=Path,required=True);p.add_argument('--payload',type=Path,required=True)
    p.add_argument('--output-parent',type=Path,default=ROOT/'outputs/photographic_support_annotations_v1');a=p.parse_args()
    folder=save_support(a.export_folder,json.loads(a.payload.read_text(encoding='utf-8')),a.output_parent)
    with a.payload.with_suffix('.result.json').open('x',encoding='utf-8') as f:json.dump(dict(export=str(folder.resolve())),f)


if __name__=='__main__':main()
