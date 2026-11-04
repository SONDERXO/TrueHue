"""Frozen new-group extension of the authorised PPR10K operator comparison."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config
BASE=ROOT/get_config().OUTPUTS_ROOT
OUT=BASE/'ppr10k_new_group_comparison_v1'


def module(number,name):
    path=next((ROOT/'scripts').glob(number+'_*py'))
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def freeze():
    OUT.mkdir(exist_ok=True)
    if (OUT/'frozen_sample.json').exists(): raise FileExistsError('Sample already frozen')
    inventory=BASE/'ppr10k_inspection_v1/inventory.json'
    inv=json.loads(inventory.read_text())
    source={Path(x['name']).stem for x in inv['source']['entries']}
    target={Path(x['name']).stem for x in inv['target_a']['entries']}
    groups={x.split('_')[0] for x in source&target if int(x.split('_')[0])<1356}
    groups-=set(json.loads((BASE/'ppr10k_inspection_v1/frozen_sample.json').read_text())['groups'])
    chosen=sorted(groups,key=lambda g:hashlib.sha256(('TrueHue-PPR10K-newgroups-v1:'+g).encode()).hexdigest())[:8]
    frames=[min((s for s in source&target if s.split('_')[0]==g),key=lambda s:int(s.split('_')[1])) for g in chosen]
    plan=dict(groups=chosen,frames=frames,editor='a',rule='Eight SHA256-ranked previously uninspected publisher-training group IDs, first numeric frame each, no replacements.',
        seed='TrueHue-PPR10K-newgroups-v1:',inventory_sha256=hashlib.sha256(inventory.read_bytes()).hexdigest(),
        note='Distinct group IDs do not certify different people, lighting diversity or tone coverage. Inspect all selected photos; unusable faces retained as failures.',
        face_rule='One largest visible face by source-only approximate outline bounding area; tie image-left. No targets or fitted outputs used for outlining. No visible/usable face => retained failure.',
        fitting='Compare frozen3/4control operators: one identity start each, squared-sRGB, same bounds/tolerances as392/394,8px checker fit/check. No tuning or new candidate.',
        source_colour='RGB16/65535,targetRGB8/255; embedded sRGB required; no registration adjustment.',
        reporting='All8 outcomes and clipping/regressions; target-aware approximation not prediction, independent-person validation or skin truth.',
        stop='No automatic expansion/tree/MST training/runtime adoption/user-review task.',
        three_protocol_sha256=hashlib.sha256((BASE/'ppr10k_operator_diagnostic_v1/protocol.json').read_bytes()).hexdigest(),
        four_protocol_sha256=hashlib.sha256((BASE/'ppr10k_contrast_diagnostic_v1/protocol.json').read_bytes()).hexdigest())
    (OUT/'frozen_sample.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
    print(json.dumps(plan,indent=2))


def acquire():
    reader=module('391','reader');reader.OUT=OUT
    reader.acquire()


if __name__=='__main__': {'freeze':freeze,'acquire':acquire}[sys.argv[1]]()
