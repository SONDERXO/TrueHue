"""Versioned post-hoc acceptability review; original trial never rewritten."""
from http.server import BaseHTTPRequestHandler
from pathlib import Path
import json,os,uuid

IDENTITY={'no_unwanted_change','slight_acceptable_change','unwanted_change','cannot_judge'}
PREFERENCE={'A','B','no_noticeable_difference','both_unacceptable','cannot_judge'}
ARTIFACT={'A','B','both','none','cannot_judge'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def validate(public,value):
    if value.get('protocol_id')!=public['protocol_id']:raise ValueError('Wrong review revision')
    if not all(isinstance(value.get('display',{}).get(k),str) and value['display'][k].strip() for k in ['browser','resolution','os_scale','colour_settings']):raise ValueError('Complete the viewing setup')
    ratings=value.get('ratings',{})
    if not isinstance(ratings,dict) or set(ratings)-{c['id'] for c in public['cases']}:raise ValueError('Unknown rating case')
    for c in public['cases']:
        if c['id'] not in ratings:continue
        r=ratings[c['id']]
        if not isinstance(r,dict) or not isinstance(r.get('reason',''),str):raise ValueError('Valid rating and reason required')
        if c['kind']=='identity':
            if r.get('identity') not in IDENTITY:raise ValueError('Choose acceptability, not just visibility')
        elif r.get('preference') not in PREFERENCE or r.get('artifact') not in ARTIFACT:raise ValueError('Choose preference and artifact')
    return len(ratings)==len(public['cases'])

def save(folder,public,value):
    complete=validate(public,value);ratings=Path(folder)/'ratings';ratings.mkdir(exist_ok=True)
    name=uuid.uuid4().hex+'.json';payload=dict(value,complete=complete)
    with (ratings/name).open('xb') as f:f.write((json.dumps(payload,indent=2,allow_nan=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    bad=[c['id'] for c in public['cases'] if c['kind']=='identity' and payload['ratings'].get(c['id'],{}).get('identity')=='unwanted_change']
    if bad and not (Path(folder)/'early_unwanted_change_PRIVATE.json').exists():
        with (Path(folder)/'early_unwanted_change_PRIVATE.json').open('x',encoding='utf-8') as f:json.dump(dict(status='POSTHOC_REVIEW_NOTREADY',revision=name,cases=bad,scores_unblinded=False),f,indent=2)
    return dict(saved=True,revision=name,complete=complete)

def page():
    text=Path(__file__).with_name('oblique_comparison_review.html').read_text(encoding='utf-8')
    old="['no_noticeable_change','noticeable_change','cannot_judge']"
    assert old in text
    text=text.replace(old,"['no_unwanted_change','slight_acceptable_change','unwanted_change','cannot_judge']")
    text=text.replace('Is there a noticeable change in brightness, colour, natural appearance, boundaries or protection?',
        'Is there an unwanted change? Slight acceptable differences are allowed; unwanted brightness, colour or boundary changes are not.')
    assert 'dirty=false;show();' in text
    text=text.replace('dirty=false;show();',"dirty=false;index=manifest.cases.findIndex(c=>!state.ratings[c.id]);if(index<0)index=0;show();")
    extra=Path(__file__).with_name('joint_colour_review_status.js').read_text(encoding='utf-8')
    return (text+'\n<script>'+extra+'</script>').encode()

def handler(folder):
    folder=Path(folder);public=read(folder/'review_public.json')
    assets={c[k] for c in public['cases'] for k in ['A','B','R'] if c[k]}
    class ReviewHandler(BaseHTTPRequestHandler):
        def reply(self,status,data,kind='application/json'):
            data=data if isinstance(data,bytes) else json.dumps(data).encode()
            self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
        def do_GET(self):
            if self.path=='/':return self.reply(200,page(),'text/html; charset=utf-8')
            if self.path=='/public':return self.reply(200,public)
            if self.path=='/latest':
                paths=sorted((folder/'ratings').glob('*.json'),key=lambda p:p.stat().st_mtime_ns)
                return self.reply(200,read(paths[-1]) if paths else None)
            if self.path=='/review-status':
                closed=(folder/'early_unwanted_change_PRIVATE.json').exists()
                return self.reply(200,dict(closed=closed,message='An unwanted change was saved. This continuation is stopped; no further ratings are needed.' if closed else 'Slight acceptable differences are allowed.'))
            if self.path in {'/'+p for p in assets}:return self.reply(200,(folder/self.path[1:]).read_bytes(),'image/png')
            return self.reply(404,dict(error='Unknown review asset'))
        def do_POST(self):
            if self.path!='/save':return self.reply(404,{})
            if (folder/'early_unwanted_change_PRIVATE.json').exists():return self.reply(409,dict(error='Review stopped; download saved answers'))
            origin=self.headers.get('Origin')
            if origin and origin!='http://'+self.headers.get('Host',''):return self.reply(403,{})
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=200000:raise ValueError('Invalid save size')
                return self.reply(200,save(folder,public,json.loads(self.rfile.read(length))))
            except (ValueError,TypeError,KeyError) as e:return self.reply(400,dict(error=str(e)))
        def log_message(self,*args):pass
    return ReviewHandler

def assess(folder,revision):
    folder=Path(folder)
    if Path(revision).name!=revision or not revision.endswith('.json'):raise ValueError('Revision filename only')
    public=read(folder/'review_public.json');saved=read(folder/'ratings'/revision)
    complete=validate(public,saved)
    if (folder/'early_unwanted_change_PRIVATE.json').exists():
        return dict(development_status='POSTHOC_REVIEW_NOTREADY',reason='Unwanted identity change',model_adopted=False,scores_unblinded=False)
    if not complete:raise ValueError('Complete initial review before unblinding scores or controls')
    provenance=read(folder/'provenance_PRIVATE.json');original=Path(provenance['original_comparison'])
    expected=Path(__file__).resolve().parents[2]/'outputs/joint_colour_source_held_comparison_v1'
    assert original.resolve()==expected.resolve()
    predictions=read(original/'predictions_PRIVATE.json');summary=read(original/'summary_PRIVATE.json')
    mapping={p['review_id']:p for p in predictions};useful=set();concerns=[];outcomes=[]
    for c in public['cases']:
        r=saved['ratings'][c['id']];p=mapping[c['id']]
        if c['kind']=='identity':
            outcome=r['identity']
            if outcome not in ['no_unwanted_change','slight_acceptable_change']:concerns.append(c['id'])
        else:
            choice=r['preference'];outcome=('output_preferred' if choice==p['output_panel'] else 'input_preferred') if choice in ['A','B'] else choice
            if outcome=='output_preferred':useful.add(p['role'])
            if outcome in ['input_preferred','both_unacceptable','cannot_judge'] or r['artifact'] in [p['output_panel'],'both','cannot_judge']:concerns.append(c['id'])
        outcomes.append(dict(review_id=c['id'],outcome=outcome,rating=r))
    numeric=all(summary['primary']['by_role'][r]['source_equal_DE_improvement']>0 for r in ['exposure_under','exposure_over','colour_cool'])
    passed=numeric and {'exposure_under','exposure_over','colour_cool'}<=useful and not concerns
    return dict(development_status='POSTHOC_REVIEW_ACCEPTABLE' if passed else 'POSTHOC_REVIEW_NOTREADY',
        numeric_families_pass=numeric,useful_families=sorted(useful),concerns=concerns,outcomes=outcomes,
        original_assessment_preserved=True,criterion_changed_after_initial_results=True,independent_validation=False,model_adopted=False)
