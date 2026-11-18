"""Local UI worker for one explicit mask-edit payload; never runs models."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.demo.manual_refinement import apply_refinement
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--export-folder',type=Path,required=True)
    cli.add_argument('--payload',type=Path,required=True);args=cli.parse_args()
    payload=json.loads(args.payload.read_text(encoding='utf-8'))
    folder=apply_refinement(args.export_folder,payload,ROOT/'outputs/manual_mask_refinement_v1')
    with args.payload.with_suffix('.result.json').open('x',encoding='utf-8') as f:json.dump(dict(export=str(folder.resolve())),f)
if __name__=='__main__':main()
