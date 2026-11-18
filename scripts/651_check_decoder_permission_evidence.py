"""Read-only pinned public-source and local permission evidence; no author contact."""
from pathlib import Path
import urllib.request,json,hashlib,re
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/decoder_permission_evidence_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve evidence')
    base='https://api.github.com/repos/jseobyun/FaceParsing'
    def fetch(url):
        req=urllib.request.Request(url,headers={'User-Agent':'TrueHue-research-permission-check','Accept':'application/vnd.github+json'})
        with urllib.request.urlopen(req,timeout=30) as r:return r.read()
    repo=json.loads(fetch(base));commit=json.loads(fetch(base+'/commits/master'));rev=commit['sha'];tree=json.loads(fetch(base+'/git/trees/'+rev+'?recursive=1'));assert not tree['truncated']
    issues=json.loads(fetch(base+'/issues?state=all&per_page=100'));assert len(issues)<100
    OUT.mkdir();(OUT/'repository.json').write_text(json.dumps(repo));(OUT/'tree.json').write_text(json.dumps(tree));(OUT/'issues.json').write_text(json.dumps(issues))
    blobs=[x['path'] for x in tree['tree'] if x['type']=='blob'];candidates=[p for p in blobs if re.search(r'licen[cs]e|copying|notice|readme|permission',p,re.I)]
    own=[p for p in blobs if (p.endswith(('.py','.md','.txt','.yaml','.yml')) or p=='.gitignore') and not p.startswith(('src/models/dinov3/','assets/'))]
    hits=[];hashes={}
    for i,path in enumerate(sorted(set(own+candidates))):
        raw=fetch('https://raw.githubusercontent.com/jseobyun/FaceParsing/'+rev+'/'+path);text=raw.decode('utf-8',errors='replace');dest=OUT/f'source_{i:02d}.txt';dest.write_bytes(raw);hashes[path]=hashlib.sha256(raw).hexdigest()
        for n,line in enumerate(text.splitlines(),1):
            if re.search(r'licen[cs]e|copyright|permission|research.use|commercial|redistribut',line,re.I):hits.append(dict(path=path,line=n,text=line.strip()[:400]))
    comments=[]
    for issue in issues:
        if issue['comments']:
            comments+=json.loads(fetch(issue['comments_url']))
    local=ROOT/'models/dinov3_face_parser_candidate_v1';localfiles=[p.name for p in local.iterdir() if p.is_file()]
    result=dict(revision=rev,tree_sha=tree['sha'],tree_complete=True,repository_license=repo.get('license'),named_permission_files=candidates,
        own_source_files_scanned=len(hashes),source_sha256=hashes,permission_keyword_hits=hits,
        issues=[dict(number=i['number'],title=i['title'],comments=i['comments'],body=i['body']) for i in issues],comments=comments,
        local_package_files=localfiles,drive_page_inspection='Web tool could not access file preview; no Drive sidecar terms verified',
        conclusion='No explicit separate code/decoder research-use permission located in checked sources. README addresses DINOv3 weights only. Not proof that permission is absent elsewhere.',
        author_contacted=False,new_inference=0,new_fits=0,holdout_image_reads=0)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ('revision','tree_complete','repository_license','named_permission_files','own_source_files_scanned','permission_keyword_hits','issues','conclusion')},indent=2))
if __name__=='__main__':main()
