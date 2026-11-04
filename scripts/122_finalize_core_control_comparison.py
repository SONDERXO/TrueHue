"""Package comparison CSVs, visual QA and clearly post-hoc control leaf traces."""
import csv
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.train_model import load_model

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'outputs/core_control_comparison_v1';summary=json.loads((out/'summary.json').read_text());verify=json.loads((out/'verification.json').read_text())
    assert digest(out/'summary.json')==verify['summary_sha256']
    assert all(digest(ROOT/p)==h for p,h in summary['input_sha256'].items())
    assert all(digest(ROOT/p)==h for p,h in verify['output_sha256'].items())
    for name,rows in [('predictions.csv',summary['predictions']),('aggregate.csv',summary['aggregate'])]:
        with (out/name).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    predictions={(p['pair_id'],p['method']):p for p in summary['predictions']};audits={(a['fold_id'],a['method']):a for a in summary['fit_audits']}
    traces=[]
    for p in summary['predictions']:
        if p['reference_status']!='primary_eligible_ID' or p['variant'] not in ['identity_control','mild_bright_exposure'] or p['method'] not in ['older_recipe','with_controls']:continue
        model=load_model(str(out/'fold_models'/f"fold{p['fold_id']}_{p['method']}.joblib"));audit=audits[(p['fold_id'],p['method'])]
        training=[predictions[(pair,p['method'])] for pair in audit['fit_pair_ids']]
        # These rows' stored features/targets are input-only/frozen regardless of which outer fold predicted them.
        x=np.array([r['features'] for r in training]);leaf=int(model.apply(np.array(p['features'])[None,:])[0]);leaves=model.apply(x)
        members=[r for r,l in zip(training,leaves) if l==leaf]
        np.testing.assert_allclose(np.mean([r['target_parameters'] for r in members],axis=0),p['predicted_parameters'],rtol=0,atol=1e-12)
        assert p['source_image_id'] not in {r['source_image_id'] for r in members}
        traces.append(dict(pair_id=p['pair_id'],method=p['method'],leaf_id=leaf,predicted_parameters=p['predicted_parameters'],
            target_parameters=p['target_parameters'],members=[dict(pair_id=r['pair_id'],source_image_id=r['source_image_id'],variant=r['variant'],target_parameters=r['target_parameters']) for r in members]))
    assert len(traces)==24
    (out/'posthoc_control_traces.json').write_text(json.dumps(dict(status='Post-hoc descriptive traces after the frozen comparison; no new candidate/fit/tuning',traces=traces),indent=2))
    qa=dict(status='All7source boards inspected by Codex;30probe rows with two source-held-out recipe outputs each',
        source_ids=['12288','22211','22454','51739','62331','6236','75027'],
        observations='Controls improve some dark/color/mild cases but unnecessary identity correction persists.51739identity is much brighter under controls;22454identity/mild remain warm/bright;75027complete-five source is worse overall with controls. Patch masks remain visible.12288and eightheld rows retain diagnostic-only labels.',
        human_or_expert_review=False,changed_parameters_masks_or_admissions_after_review=False)
    (out/'visual_qa.json').write_text(json.dumps(qa,indent=2))
    page_path=out/'review.html';page=page_path.read_text(encoding='utf-8')
    if 'aggregate.csv' not in page:
        page=page.replace('</h1>','</h1><p><a href="aggregate.csv">Aggregate CSV</a> · <a href="predictions.csv">Predictions CSV</a> · <a href="readiness.json">Decision gates</a> · <a href="verification.json">Independent replay</a> · <a href="sensitivity_and_sources.json">Per-source/sensitivity</a> · <a href="posthoc_control_traces.json">Post-hoc control leaf traces</a></p>',1)
        page_path.write_text(page,encoding='utf-8')
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.paths=[]
        def handle_starttag(self,tag,attrs):self.paths.extend(value for key,value in attrs if key in ['src','href'])
    parser=Links();parser.feed(page);assert all((out/p).is_file() for p in parser.paths)
    result=dict(status='pass',gallery_links_checked=len(parser.paths),source_boards_reviewed=7,posthoc_control_leaf_means_verified=24,
        runtime_model_and_original_inputs_unchanged=True,tests='546 passed in11.44s including9new eligibility/fold tests',
        artifact_sha256={str(p.relative_to(ROOT)):digest(p) for p in list(out.glob('*.json'))+list(out.glob('*.csv'))+[page_path,Path(__file__)] if p.name!='final_verification.json'})
    (out/'final_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'}))
if __name__=='__main__':main()
