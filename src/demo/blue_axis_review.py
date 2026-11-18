"""Prospective66 review with exact carried judgments; private results stay gated."""
from pathlib import Path
import json
from . import acceptability_review as base
from .blue_axis_review_policy import assess as policy_assess

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def page(public):
    text=base.page().decode('utf-8')
    # Preserve the same panel geometry, native button and question semantics.
    text=text.replace("index=Math.max(0,index-1);", "do{index=Math.max(0,index-1);}while(index>0&&(manifest.carried_ids||[]).includes(manifest.cases[index].id));")
    text=text.replace("index=Math.min(manifest.cases.length-1,index+1);", "do{index=Math.min(manifest.cases.length-1,index+1);}while(index<manifest.cases.length-1&&(manifest.carried_ids||[]).includes(manifest.cases[index].id));")
    return text.encode('utf-8')

def save(folder,public,value):
    seed=read(Path(folder)/'carry_forward_seed_PRIVATE.json')
    for ident,rating in seed['ratings'].items():
        if value.get('ratings',{}).get(ident)!=rating:raise ValueError('Carried exact judgments must remain intact')
    if seed['ratings'] and value.get('display')!=seed['display']:raise ValueError('Viewing setup differs from the confirmed reuse setup')
    return base.save(folder,public,value)

def handler(folder):
    folder=Path(folder);public=read(folder/'review_public.json');parent=base.handler(folder)
    class ReviewHandler(parent):
        def do_GET(self):
            if self.path=='/':return self.reply(200,page(public),'text/html; charset=utf-8')
            return super().do_GET()
        def do_POST(self):
            if self.path!='/save':return self.reply(404,{})
            if (folder/'early_unwanted_change_PRIVATE.json').exists():return self.reply(409,dict(error='Review stopped; download saved answers'))
            origin=self.headers.get('Origin')
            if origin and origin!='http://'+self.headers.get('Host',''):return self.reply(403,{})
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=200000:raise ValueError('Invalid save size')
                return self.reply(200,save(folder,public,json.loads(self.rfile.read(size))))
            except (ValueError,TypeError,KeyError) as error:return self.reply(400,dict(error=str(error)))
    return ReviewHandler

def assess(folder,revision):
    folder=Path(folder)
    if Path(revision).name!=revision or not revision.endswith('.json'):raise ValueError('Saved revision filename only')
    public=read(folder/'review_public.json');saved=read(folder/'ratings'/revision)
    base.validate(public,saved)
    seed=read(folder/'carry_forward_seed_PRIVATE.json')
    if any(saved['ratings'].get(k)!=v for k,v in seed['ratings'].items()):raise ValueError('Carry-forward altered')
    if (folder/'early_unwanted_change_PRIVATE.json').exists():return dict(status='FAIL_CLOSED_NOT_ADOPTED',scores_unblinded=False)
    def load_private():
        provenance=read(folder/'provenance_PRIVATE.json');source=Path(provenance['comparison'])
        expected=Path(__file__).resolve().parents[2]/'outputs/blue_axis_source_held_comparison_v1'
        if source.resolve()!=expected.resolve():raise ValueError('Bound comparison required')
        predictions=read(source/'predictions_PRIVATE.json');summary=read(source/'summary_PRIVATE.json')
        return dict(mapping={p['review_id']:p for p in predictions},benefits={r:s['source_equal_DE_improvement'] for r,s in summary['primary']['by_role'].items()})
    return policy_assess(public,saved,load_private)
