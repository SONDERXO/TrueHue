"""Identity-first early rejection around the unchanged durable review UI."""
import json,hashlib,uuid
from pathlib import Path
from .oblique_comparison_review import handler as base_handler,validate

def assess_saved(folder,revision):
    folder=Path(folder)
    if Path(revision).name!=revision or not revision.endswith('.json'):raise ValueError('Exact saved revision filename required')
    public=json.loads((folder/'review_public.json').read_text())
    saved=json.loads((folder/'ratings'/revision).read_text())
    # Reject/close using ratings ONLY; do not read controls or metrics for partial review.
    failures=identity_failure(public,saved)
    if failures:
        close_if_failed(folder,public,saved,revision)
        return json.loads((folder/'early_identity_failure_PRIVATE.json').read_text())
    if (folder/'early_identity_failure_PRIVATE.json').exists():
        return json.loads((folder/'early_identity_failure_PRIVATE.json').read_text())
    if not validate(public,saved):raise ValueError('All44initial ratings required before unblinding')
    import importlib.util
    path=Path(__file__).resolve().parents[2]/'scripts/850_assess_saved_oblique_review.py'
    spec=importlib.util.spec_from_file_location('accepted_complete_assessment',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.assess(public,saved,json.loads((folder/'predictions_PRIVATE.json').read_text()),json.loads((folder/'summary_PRIVATE.json').read_text())['primary'])

def identity_failure(public,saved):
    validate(public,saved)  # Incomplete is valid progress, never interpreted as PASS.
    return [c['id'] for c in public['cases'] if c['kind']=='identity' and saved['ratings'].get(c['id'],{}).get('identity')=='noticeable_change']

def close_if_failed(folder,public,saved,revision):
    failures=identity_failure(public,saved)
    if not failures:return False
    path=Path(folder)/'early_identity_failure_PRIVATE.json'
    if path.exists():return True
    report=dict(development_status='FAIL_CLOSED_NOT_ADOPTED',reason='Saved noticeable identity change',
        revision=revision,identity_cases=failures,ratings_saved=len(saved['ratings']),total_cases=len(public['cases']),
        unreviewed_cases=[c['id'] for c in public['cases'] if c['id'] not in saved['ratings']],
        scores_or_controls_unblinded=False,model_adopted=False)
    with path.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2)
    return True

def handler(folder):
    folder=Path(folder);parent=base_handler(folder);public=json.loads((folder/'review_public.json').read_text())
    class ReviewHandler(parent):
        def reply(self,status,data,kind='application/json'):
            if kind.startswith('text/html'):
                extra=Path(__file__).with_name('joint_colour_review_status.js').read_bytes()
                data=data+b'\n<script>'+extra+b'</script>'
            return super().reply(status,data,kind)
        def do_GET(self):
            if self.path=='/review-status':
                return self.reply(200,dict(closed=(folder/'early_identity_failure_PRIVATE.json').exists(),
                    message='A saved unchanged-photo rating establishes a noticeable change. This candidate is closed; no further ratings are needed.' if (folder/'early_identity_failure_PRIVATE.json').exists() else 'Review unchanged photos first. Save regularly.'))
            return super().do_GET()
        def do_POST(self):
            if self.path!='/save':return super().do_POST()
            if (folder/'early_identity_failure_PRIVATE.json').exists():return self.reply(409,dict(error='Candidate closed; saved ratings preserved. Download them; no further ratings required.'))
            # Parent saves immutable, validated and fsynced revision. Then inspect only ratings.
            super().do_POST()
            files=sorted((folder/'ratings').glob('*.json'),key=lambda p:p.stat().st_mtime_ns) if (folder/'ratings').exists() else []
            if files:
                latest=files[-1]
                close_if_failed(folder,public,json.loads(latest.read_text()),latest.name)
    return ReviewHandler
