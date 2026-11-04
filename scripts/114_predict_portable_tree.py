"""Run exported tree parameters with only the Python standard library."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree',type=Path,required=True)
    parser.add_argument('--features-file',type=Path,required=True,help='JSON object keyed by exact exported input feature names')
    args=parser.parse_args();payload=json.loads(args.tree.read_text());features=json.loads(args.features_file.read_text())
    if not isinstance(features,dict):raise ValueError('A named feature object is required')
    tree=PortableTree(payload)
    result=dict(parameters=dict(zip(tree.target_names,tree.predict_one(features))),leaf_id=tree.leaf_id(features),
        tree_sha256=hashlib.sha256(args.tree.read_bytes()).hexdigest(),
        status='Development parameter inference only; no MST estimate, image correction or runtime adoption')
    print(json.dumps(result,indent=2,allow_nan=False))
if __name__=='__main__':main()
