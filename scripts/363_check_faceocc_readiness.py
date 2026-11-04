"""Acquire public model/source metadata only; never photos or training data."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/faceocc_readiness_v2'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir()
    evidence = []

    def fetch(name, url):
        request = urllib.request.Request(url, headers={'User-Agent': 'TrueHue-model-readiness'})
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                raw = response.read()
            (OUT / name).write_bytes(raw)
            evidence.append(dict(file=name, url=url, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
            return json.loads(raw) if name.endswith('.json') else raw.decode('utf-8')
        except Exception as error:
            evidence.append(dict(file=name, url=url, error=str(error)))
            return None

    model = fetch('model_api.json', 'https://huggingface.co/api/models/mertakin/FaceOcc')
    repo = fetch('repository_api.json', 'https://api.github.com/repos/mertakinstd/FaceOcc')
    if model and model.get('sha'):
        revision = model['sha']
        for name in ['config.json', 'README.md', 'LICENSE']:
            fetch('model_' + name, 'https://huggingface.co/mertakin/FaceOcc/resolve/' + revision + '/' + name)
    if repo:
        branch = repo['default_branch']
        commit = fetch('source_commit.json', 'https://api.github.com/repos/mertakinstd/FaceOcc/commits/' + branch)
        if commit and commit.get('sha'):
            revision = commit['sha']
            tree = fetch('source_tree.json', 'https://api.github.com/repos/mertakinstd/FaceOcc/git/trees/' + revision + '?recursive=1')
            for name in ['README.md', 'LICENSE', 'NOTICE.md']:
                fetch('source_' + name, 'https://raw.githubusercontent.com/mertakinstd/FaceOcc/' + revision + '/' + name)
            if tree:
                candidates = [r['path'] for r in tree['tree'] if r['type']=='blob' and r['path'].endswith('.py') and any(w in r['path'].lower() for w in ['infer','predict','align','dataset'])]
                for i,path in enumerate(candidates[:8]):
                    fetch('source_contract_' + str(i) + '.txt', 'https://raw.githubusercontent.com/mertakinstd/FaceOcc/' + revision + '/' + path)
    (OUT / 'acquisition.json').write_text(json.dumps(dict(evidence=evidence,
        model_revision=None if not model else model.get('sha'),
        model_files=[] if not model else [r['rfilename'] for r in model.get('siblings',[])],
        weights_downloaded=False, inference=False, runtime_changed=False),indent=2))
    print(json.dumps(evidence,indent=2))


if __name__ == '__main__':
    main()
