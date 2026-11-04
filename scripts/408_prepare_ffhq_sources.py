"""Bounded FFHQ photographic source preparation; MST/calibration/training deferred."""
import ast
import hashlib
import json
from pathlib import Path
import time

import requests
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/ffhq_source_preparation_v1'
RAW = ROOT/'data/raw/ffhq_source_preparation_v1'
REV = '4826aa6ea77aa7f1a7802b938ed7c40afb985cda'
COUNT = 12


def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def download(session, url, destination, size, md5):
    """Public official URL, bounded bytes, exact checksum; no cookie/account bypass."""
    attempts = []
    urls = [url]
    if 'drive.google.com/uc?id=' in url:
        file_id = url.split('id=',1)[1].split('&',1)[0]
        urls.append('https://drive.usercontent.google.com/download?id='+file_id+'&export=download&confirm=t')
    for endpoint in urls:
        partial = destination.with_suffix(destination.suffix+'.partial')
        try:
            count = 0; last = time.monotonic()
            with session.get(endpoint, stream=True, timeout=(20, 40)) as response:
                response.raise_for_status()
                if 'text/html' in response.headers.get('Content-Type','').lower():
                    raise ValueError('HTML access/confirmation response, not the expected artifact')
                with partial.open('wb') as stream:
                    for block in response.iter_content(1024*1024):
                        count += len(block)
                        if count > size:
                            raise ValueError('Response exceeds publisher byte count')
                        stream.write(block)
                        if time.monotonic()-last > 20:
                            print(f'{destination.name}: {count}/{size} bytes', flush=True)
                            last = time.monotonic()
            if count != size or digest(partial,'md5') != md5:
                raise ValueError('Publisher byte-count/MD5 mismatch')
            partial.replace(destination)
            return dict(success=True, bytes=count, md5=md5, sha256=digest(destination),
                        endpoint=endpoint, prior_attempts=attempts)
        except (requests.RequestException, ValueError) as error:
            attempts.append(dict(endpoint=endpoint,error=str(error)))
            # Only this explicitly named partial file is removed, never raw datasets.
            if partial.exists():
                partial.unlink()
    return dict(success=False, attempts=attempts)


def main():
    if OUT.exists() or RAW.exists():
        raise FileExistsError('Use a new version; do not overwrite source evidence')
    OUT.mkdir(); RAW.mkdir(parents=True)
    protocol = dict(version='ffhq_fixed12_source_only_v1', repository_revision=REV,
        user_scope='FFHQ photographic sources now; ITA-to-MST later; no full-method training',
        count=COUNT, selection='publisher training only; SHA256(TrueHue-FFHQ-source-v1:+id), unique photo_url',
        before_pixels=True, no_replacements=True, images='aligned 1024x1024 only',
        limitations=['alignment/padding may affect skin/neck','photo_url not person identity',
                     'no MST labels','not final evaluation or source admission'],
        source_role='development-exposed on acquisition, final-unseen-ineligible',
        inference=0, fits=0, reserved_roles_changed=False)
    write(OUT/'protocol.json', protocol)
    session = requests.Session()
    source = session.get(f'https://raw.githubusercontent.com/NVlabs/ffhq-dataset/{REV}/download_ffhq.py',timeout=30)
    source.raise_for_status()
    source_path = OUT/'upstream_download_ffhq.py.txt'; source_path.write_bytes(source.content)
    pinned_tree = json.loads((ROOT/'outputs/dataset_role_assessment_20261103_v1/ffhq-repository.json').read_text())
    expected_blob = next(x['sha'] for x in pinned_tree['tree']['tree'] if x['path']=='download_ffhq.py')
    blob = hashlib.sha1(b'blob '+str(len(source.content)).encode()+b'\0'+source.content).hexdigest()
    assert blob == expected_blob
    # Parse only the literal published specification; never execute upstream code.
    node = next(n.value for n in ast.parse(source.text).body if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=='json_spec' for t in n.targets))
    spec = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords}
    metadata_path = RAW/'ffhq-dataset-v2.json'
    metadata_result = download(session,spec['file_url'],metadata_path,spec['file_size'],spec['file_md5'])
    write(OUT/'metadata_access.json',dict(upstream_git_blob=blob,spec=spec,result=metadata_result))
    if not metadata_result['success']:
        write(OUT/'decision.json',dict(status='blocked_official_metadata_access',photos=0,
            training_admitted=False, MST_deferred=True, no_mirror_or_unverified_fallback=True))
        write(OUT/'sha256.json',{p.name:digest(p) for p in OUT.iterdir() if p.is_file()})
        print('Official metadata access unavailable; saved exact failures, no photos or fits.',flush=True)
        return
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    assert len(metadata)==70000
    ranked = sorted((key for key,value in metadata.items() if value['category']=='training'),
        key=lambda key:hashlib.sha256(('TrueHue-FFHQ-source-v1:'+key).encode()).hexdigest())
    selected = []; urls = set()
    for key in ranked:
        item = metadata[key]; url = item['metadata']['photo_url']
        if not url or url in urls:
            continue
        urls.add(url)
        selected.append(dict(id=key, publisher_category=item['category'],metadata=item['metadata'],
            image=item['image'], in_the_wild=item['in_the_wild'],
            photo_group=url,person_group=None,MST=None,training_admitted=False,
            role='development_source_feasibility_not_final_evaluation'))
        if len(selected)==COUNT:
            break
    assert len(selected)==COUNT
    write(OUT/'selected_before_pixels.json',dict(metadata_sha256=digest(metadata_path),sources=selected))
    results = []
    images_dir = RAW/'images'; images_dir.mkdir()
    for row in selected:
        info = row['image']; target = images_dir/(row['id'].zfill(5)+'.png')
        access = download(session,info['file_url'],target,info['file_size'],info['file_md5'])
        result = dict(id=row['id'],access=access,training_admitted=False)
        if access['success']:
            with Image.open(target) as image:
                image.load()
                assert image.mode=='RGB' and list(image.size)==info['pixel_size']==[1024,1024]
                assert hashlib.md5(np.asarray(image).tobytes()).hexdigest()==info['pixel_md5']
                result.update(path=target.relative_to(ROOT).as_posix(),pixel_md5=info['pixel_md5'],
                    mode=image.mode,size=list(image.size),ICC_present=bool(image.info.get('icc_profile')))
        results.append(result)
        write(OUT/'attempts.json',results)
        print(f"FFHQ {row['id']}: {'verified' if access['success'] else 'unavailable, retained'}",flush=True)
    board=Image.new('RGB',(4*272,3*296),'#eeeeee'); draw=ImageDraw.Draw(board)
    for i,row in enumerate(results):
        x=(i%4)*272; y=(i//4)*296
        if row['access']['success']:
            with Image.open(ROOT/row['path']) as im:
                preview=im.copy(); preview.thumbnail((256,256)); board.paste(preview,(x+8,y+8))
        draw.text((x+8,y+268),'FFHQ '+row['id']+('' if row['access']['success'] else ' unavailable'),fill='black')
    board.save(OUT/'source_contact_sheet.jpg',quality=94)
    write(OUT/'decision.json',dict(status='source_visual_assessment_pending',attempted=COUNT,
        verified=sum(r['access']['success'] for r in results), training_admitted=False,
        MST_deferred=True, inference=0,fits=0, roles_changed=False))
    write(OUT/'sha256.json',{p.name:digest(p) for p in OUT.iterdir() if p.is_file()})
    print('Bounded source acquisition complete; no segmentation, labels or training.',flush=True)


if __name__=='__main__':
    main()
