"""Regenerate navigation only; preserve research paths, source bytes and evidence."""
import hashlib
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT/'outputs/project_navigation'
GROUPS = [
    ('Data and references', ('ffhq','fairface','scin','stw','dast','ppr10k','dataset','source','reference','duplicate','cohort','capture')),
    ('ITA and MST', ('mst','ita','calibrat','isotonic','monotone','lookup')),
    ('Masks and rendering', ('mask','faceocc','face-','facial','skin','neck','brow','nostril','occlu','material','boundary','contour','mouth','graphcut','parser','landmark','seamless','support')),
    ('Android and demos', ('android','emulator','device','jvm','portable','demo','desktop','apk')),
    ('Thesis and decisions', ('thesis','proposal','panel','adviser','advisor','brief','handoff','decision','implementation','delivery','consent','expirement','experiment-log')),
    ('Correction experiments', ('correction','tree','gamma','brightness','chromatic','contrast','operator','recovery','endpoint','table2','recipe','feature','distortion','stress','clean','tone','variant','training')),
    ('Reproducibility', ('verify','verification','check','audit','test','replay','export','build','config','access','preflight','parity','acqui','environment','provenance','setup','prepare','readiness')),
]
CURRENT = [
    ('Partner clone, setup and collaboration','docs/collaborator-setup.md'),
    ('Latest handoff: newest entries first','docs/session-handoff-2026-10-30.md'),
    ('Current documentation guide','docs/README.md'),
    ('FFHQ source preparation and next support check','docs/ffhq-source-preparation-results-2026-11-03.md'),
    ('FFHQ source gallery (local)','outputs/ffhq_source_visual_assessment_v1/review.html'),
    ('Methods and interim results','docs/thesis-methods-results-draft-2026-11-03.md'),
    ('Discussion and interim conclusion','docs/thesis-discussion-limitations-conclusion-draft-2026-11-03.md'),
    ('Changes from the proposal','docs/panel-change-register.md'),
    ('Integrated development plan','docs/integrated-correction-development-plan-2026-11-03.md'),
    ('Adopted masking design','docs/adopted-masking-design-2026-11-01.md'),
    ('Android implementation and setup','android-app/README.md'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def topic(name):
    value=name.lower().replace('_','-')
    for label,terms in GROUPS:
        if any(term in value for term in terms):
            return label
    return 'Other records'


def title(path):
    if path.suffix.lower() in ('.md','.py','.ps1'):
        with path.open(encoding='utf-8',errors='replace') as stream:
            for _ in range(5):
                line=stream.readline().strip().lstrip('\ufeff')
                if not line:
                    continue
                if line.startswith('#') or line.startswith(('"""', "'''")):
                    return line.strip('#\'" ').strip() or path.stem
                break
    return path.stem.replace('_',' ').replace('-',' ')


def record(path,kind,label=None,group=None):
    relative=path.relative_to(ROOT).as_posix()
    return dict(id=kind+':'+relative,kind=kind,topic=group or topic(path.name),
        title=label or title(path),path=relative,
        href=quote(relative,safe='/')+('/' if path.is_dir() else ''))


def source_files(folder,extensions):
    for base,dirs,files in os.walk(ROOT/folder):
        dirs[:]=sorted(d for d in dirs if d not in ['__pycache__','navigation'] and not d.startswith('oracleJdk-'))
        for name in sorted(files):
            path=Path(base)/name
            if path.suffix.lower() in extensions and not (folder=='scripts' and name=='README.md'):
                yield path


def relative_link(target,from_file):
    return quote(os.path.relpath(ROOT/target,from_file.parent).replace('\\','/'),safe='/')


def markdown_catalogue(path,items,heading,intro):
    lines=['# '+heading,'',intro,'',f'{len(items)} entries. Topic labels are navigation aids, not validation or activation status.','']
    for group in [g[0] for g in GROUPS]+['Other records']:
        rows=[r for r in items if r['topic']==group]
        if not rows:
            continue
        lines += ['## '+group,'']
        for row in sorted(rows,key=lambda r:r['path']):
            label=row['title'].replace('[','(').replace(']',')').replace('\n',' ')
            lines.append(f'- [{label}]({relative_link(row["path"],path)}) — `{Path(row["path"]).name}`')
        lines.append('')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8')


JS = r'''
const records=JSON.parse(document.getElementById('catalog-data').textContent);
const query=document.getElementById('query'),kind=document.getElementById('kind'),topic=document.getElementById('topic');
const body=document.getElementById('rows'),count=document.getElementById('count'),more=document.getElementById('more');
let limit=75;
for(const name of [...new Set(records.map(r=>r.topic))].sort()){
  const option=document.createElement('option'); option.value=name; option.textContent=name; topic.append(option);
}
function matches(r){
  const q=query.value.trim().toLowerCase();
  return (!kind.value||r.kind===kind.value)&&(!topic.value||r.topic===topic.value)&&
    (!q||[r.title,r.path,r.kind,r.topic].join(' ').toLowerCase().includes(q));
}
function render(){
  const found=records.filter(matches); body.replaceChildren();
  for(const r of found.slice(0,limit)){
    const tr=document.createElement('tr');
    const first=document.createElement('td'),a=document.createElement('a');
    a.href=r.href;a.textContent=r.title; first.append(a);
    const path=document.createElement('small');path.textContent=r.path;first.append(path);tr.append(first);
    for(const text of [r.kind,r.topic]){const td=document.createElement('td');td.textContent=text;tr.append(td);}
    body.append(tr);
  }
  count.textContent=`Showing ${Math.min(limit,found.length)} of ${found.length} matches (${records.length} catalogue entries).`;
  more.hidden=found.length<=limit;
}
for(const element of [query,kind,topic])element.addEventListener('input',()=>{limit=75;render();});
more.addEventListener('click',()=>{limit+=75;render();});
document.getElementById('reset').addEventListener('click',()=>{query.value='';kind.value='';topic.value='';limit=75;render();query.focus();});
render();
'''


def main():
    docs=list(source_files('docs',{'.md','.txt'}))
    scripts=list(source_files('scripts',{'.py','.ps1','.cjs','.js','.html','.css','.json','.txt'}))
    tests=list(source_files('tests',{'.py','.json'}))
    protected={p.relative_to(ROOT).as_posix():sha(p) for p in docs+scripts+tests}
    records=[]
    for label,name in CURRENT:
        path=ROOT/name
        if path.exists():
            records.append(record(path,'Current pointers',label,'Current work'))
    doc_rows=[record(p,'Documents') for p in docs]
    script_rows=[record(p,'Scripts') for p in scripts]
    test_rows=[record(p,'Tests') for p in tests]
    records+=doc_rows+script_rows+test_rows
    for path in sorted((ROOT/'outputs').iterdir()):
        if path.name.startswith('.') or path.name in ['project_navigation','__pycache__']:
            continue
        tooling=any(k in path.name for k in ['toolchain','inference_env','runtime_env'])
        label=path.name.replace('_',' ')
        target=path
        if path.is_dir() and not tooling and 'pytest' not in path.name and 'full_tests' not in path.name:
            for name in ['review.html','index.html','comparison.html','all_results.html']:
                candidate=path/name
                if candidate.is_file():
                    target=candidate;break
        records.append(record(target,'Local tools' if tooling else 'Saved results',label,topic(path.name)))
    for name,label in [('data/raw','Raw photographs (local)'),('data/processed','Processed data (local)'),
            ('data/manifests','Dataset manifests (local)'),('models','Model files (local)'),
            ('output/pdf','Generated PDF reports (local)'),('tmp','Build/render intermediates (local)')]:
        path=ROOT/name
        if path.exists():records.append(record(path,'Local artifacts',label,'Local artifacts'))
    assert len({r['id'] for r in records})==len(records)
    assert all((ROOT/r['path']).exists() for r in records)
    markdown_catalogue(ROOT/'docs/navigation/research-library.md',doc_rows,'Research library by topic',
        'Start with [the current guide](../README.md). Older protocols, failed candidates and dated drafts stay in their original locations. This complete catalogue does not mean every record is current.')
    markdown_catalogue(ROOT/'scripts/README.md',script_rows,'Experiment and helper script catalogue',
        'Run from the project root. Read the individual protocol and current [handoff](../docs/session-handoff-2026-10-30.md) before executing a script. Inclusion is not permission to rerun a stopped experiment.')
    kinds=['Current pointers','Documents','Scripts','Tests','Saved results','Local tools','Local artifacts']
    options=''.join('<option value="'+html.escape(k)+'">'+html.escape(k)+'</option>' for k in kinds)
    payload=json.dumps(records,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TrueHue project catalogue</title><style>
body{margin:0;background:#f5f7fa;color:#172230;font:16px/1.5 system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:28px}
h1{margin-bottom:6px}.status{border-left:4px solid #286a68;background:#eaf4f2;padding:12px 16px}.quick{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}.quick a,button{background:white;border:1px solid #ccd5df;border-radius:6px;padding:8px 12px;color:#164d81;text-decoration:none}
.filters{display:grid;grid-template-columns:2fr 1fr 1fr auto;gap:12px;align-items:end;margin-top:24px}label{display:grid;gap:5px}input,select{font:inherit;padding:9px;border:1px solid #b9c5d2;border-radius:5px;min-width:0}button{font:inherit;cursor:pointer}button:hover,.quick a:hover{background:#e9eff7}
table{width:100%;border-collapse:collapse;background:white}th,td{text-align:left;padding:12px;vertical-align:top;border-bottom:1px solid #e0e6ee}th{background:#e8edf4}td:first-child{width:65%}a{color:#145b94}small{display:block;color:#5b6878;overflow-wrap:anywhere;margin-top:4px}#more{display:block;margin:18px auto}#more[hidden]{display:none}.note{color:#586578;font-size:14px}
@media(max-width:750px){main{padding:16px}.filters{grid-template-columns:1fr}th:nth-child(3),td:nth-child(3){display:none}td:first-child{width:75%}}
</style></head><body><main><h1>TrueHue project catalogue</h1>
<p class="status"><strong>Development is ongoing.</strong> Next: check masks/support on the same 12 FFHQ sources. ITA-to-MST is deferred for source work.</p>
<nav class="quick" aria-label="Start here"><a href="docs/README.md">Current guide</a><a href="docs/thesis-methods-results-draft-2026-11-03.md">Methods/results draft</a><a href="docs/thesis-discussion-limitations-conclusion-draft-2026-11-03.md">Discussion draft</a><a href="outputs/ffhq_source_visual_assessment_v1/review.html">FFHQ gallery (local)</a><a href="TrueHue.code-workspace">VS Code workspace</a></nav>
<p class="note">Search titles, filenames or topics. Current pointers are selected explicitly; the remaining library preserves historical work. Local results/data need the existing workstation files.</p>
<div class="filters"><label>Search<input id="query" type="search" placeholder="For example: FFHQ, nostril, Android, 405"></label><label>Show<select id="kind"><option value="">Everything</option>'''+options+'''</select></label><label>Topic<select id="topic"><option value="">Every topic</option></select></label><button id="reset" type="button">Reset</button></div>
<p id="count" role="status" aria-live="polite"></p><table><thead><tr><th>File or folder</th><th>Collection</th><th>Topic</th></tr></thead><tbody id="rows"></tbody></table><button id="more" type="button">Show 75 more</button>
<noscript><p>Use <a href="docs/navigation/research-library.md">the document catalogue</a> or <a href="scripts/README.md">the script catalogue</a>.</p></noscript>
<script id="catalog-data" type="application/json">'''+payload+'''</script><script>'''+JS+'''</script></main></body></html>'''
    (ROOT/'PROJECT.html').write_text(page,encoding='utf-8')
    LOCAL.mkdir(exist_ok=True)
    (LOCAL/'catalogue.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
    (LOCAL/'navigation.js').write_text(JS,encoding='utf-8')
    for name,digest in protected.items():assert sha(ROOT/name)==digest,name
    frozen=ROOT/'outputs/integrated_correction_plan_v1'
    sources=json.loads((frozen/'source_hashes.json').read_text())
    parents=json.loads((frozen/'parent_manifest_hashes.json').read_text())
    assert all(sha(ROOT/k)==v for k,v in sources.items())
    assert all(sha(ROOT/'outputs'/k/'sha256.json')==v for k,v in parents.items())
    workspace=json.loads((ROOT/'TrueHue.code-workspace').read_text())
    assert all((ROOT/r['path']).is_dir() for r in workspace['folders'])
    checked=0
    for filename in ['README.md','docs/README.md','docs/project-organisation-2026-11-05.md',
                     'docs/navigation/research-library.md','scripts/README.md']:
        path=ROOT/filename
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):continue
            assert (path.parent/unquote(target.split('#',1)[0])).exists(),(filename,target)
            checked+=1
    from collections import Counter
    report=dict(records=len(records),collections=dict(Counter(r['kind'] for r in records)),
        existing_research_files_preserved=len(protected),markdown_links_checked=checked,
        integrated_sources_unchanged=len(sources),parent_manifests_unchanged=len(parents),
        workspace_roots=len(workspace['folders']),research_files_moved=0,research_files_deleted=0,
        experiments_run=0,new_fits=0,new_photos=0,
        generated_sha256={name:sha(ROOT/name) for name in ['PROJECT.html','docs/navigation/research-library.md','scripts/README.md','TrueHue.code-workspace']})
    (LOCAL/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
