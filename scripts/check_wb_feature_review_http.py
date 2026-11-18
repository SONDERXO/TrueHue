"""Local read-only HTTP asset checks. No ratings or external network requests."""
import hashlib
import json
from pathlib import Path
import urllib.request
import urllib.error

def main():
    root=Path(__file__).resolve().parents[1]/'outputs/wb_feature_identity_review_v1'
    dest=root/'qa_verification_PRIVATE.json'
    if dest.exists():raise FileExistsError(dest)
    base='http://127.0.0.1:8881/'
    assert urllib.request.urlopen(base,timeout=10).read()==(root/'index.html').read_bytes()
    manifest=json.loads((root/'manifest_PRIVATE.json').read_text(encoding='utf-8'))
    for case in manifest['cases']:
        for field in ['input','candidate']:
            data=urllib.request.urlopen(base+case[field],timeout=10).read()
            assert hashlib.sha256(data).hexdigest()==case[field+'_sha256']
    try:urllib.request.urlopen(base+'manifest_PRIVATE.json',timeout=10)
    except urllib.error.HTTPError as exc:assert exc.code==404
    else:raise AssertionError('Private manifest exposed')
    result=dict(http_page_exact=True,served_png_hashes=22,private_manifest_denied=True,
                interactive_browser_qa=False,browser_discovery=[],ratings_generated=0)
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8');print(result)

if __name__=='__main__':main()
