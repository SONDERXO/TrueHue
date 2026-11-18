"""Actual received Exposure-only admission; no features/fits or other photo subsets."""
from pathlib import Path
import sys,json,hashlib,zipfile,io,csv,collections
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=Path(r'C:\Users\NYTHAN\Downloads\PIQ2023-Dataset.zip')
OUT=ROOT/'outputs/piq23_actual_admission_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
    return h.hexdigest()
def write(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
    if OUT.exists():raise FileExistsError(OUT)
    OUT.mkdir();(OUT/'rgb256').mkdir();results=[]
    try:
        expected_path=ROOT/'outputs/piq23_expected_admission_v1/expected_roster.json'
        verification=read(expected_path.parent/'verification.json');assert sha(expected_path)==verification['roster_sha256']
        expected=read(expected_path);stat=ARCHIVE.stat();archive_sha=sha(ARCHIVE)
        write(OUT/'source.json',dict(archive_path=str(ARCHIVE),bytes=stat.st_size,mtime_ns=stat.st_mtime_ns,sha256=archive_sha,
              expected_roster_sha256=sha(expected_path),protocol_sha256=sha(ROOT/'docs/piq23-actual-admission-protocol-2026-11-18.md'),
              script_sha256=sha(Path(__file__)),user_reported_owner_access=True,training_fits=0))
        with zipfile.ZipFile(ARCHIVE) as z:
            entries=z.infolist();names=[i.filename for i in entries];assert len(names)==len(set(names))
            raw=z.read('Dataset/Scores_Exposure.csv');csvrows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline=None)))
            csvrows=[r for r in csvrows if r.get('IMAGE')];by_id={r['IMAGE']:r for r in csvrows}
            assert len(csvrows)==len(by_id)==len(expected)==5116 and set(by_id)=={r['id'] for r in expected}
            exact_paths={'Dataset/'+r['image_relative_path'] for r in expected}
            assert {i.filename for i in entries if i.filename.startswith('Dataset/Exposure/') and not i.is_dir()}==exact_paths
            for r in expected:
                a=by_id[r['id']]
                assert a['IMAGE PATH'].replace('\\','/')==r['image_relative_path'] and a['SCENE']==r['scene']
                assert [float(a[k]) for k in ['CI LOW','JOD','CI HIGH']]==[r[k] for k in ['low','score','high']]
            write(OUT/'join_verification.json',dict(passed=True,exact_rows=5116,actual_csv_sha256=hashlib.sha256(raw).hexdigest(),missing=0,extras=0))
            for i,r in enumerate(expected):
                member='Dataset/'+r['image_relative_path'];b=z.read(member)
                with Image.open(io.BytesIO(b)) as image:
                    original_mode=image.mode;image.load();orientation=image.getexif().get(274)
                    icc=bool(image.info.get('icc_profile'));rgb=image.convert('RGB');size=rgb.size
                    decoded=np.asarray(rgb);native=hashlib.sha256(str(decoded.shape).encode()+decoded.tobytes()).hexdigest()
                    small=np.asarray(rgb.resize((256,256),Image.Resampling.BICUBIC)).copy()
                pixel_sha=hashlib.sha256(small.tobytes()).hexdigest();p=OUT/'rgb256'/f'{i:05d}.npy';np.save(p,small,allow_pickle=False)
                results.append(dict(r,admitted_for_experiment=True,image_sha256=hashlib.sha256(b).hexdigest(),
                    decoded_rgb_sha256=native,rgb256_sha256=pixel_sha,original_size=list(size),original_mode=original_mode,
                    supplied_icc=icc,exif_orientation=orientation,archive_member=member,
                    rgb256_path=p.relative_to(ROOT).as_posix(),rgb256_file_sha256=sha(p)))
                if (i+1)%256==0:print('PIQ23 images decoded/hash-bound '+str(i+1)+'/5116',flush=True)
        duplicates={};cross=[]
        for key in ['image_sha256','decoded_rgb_sha256','rgb256_sha256']:
            groups=collections.defaultdict(list)
            for r in results:groups[r[key]].append(r)
            repeated=[rr for rr in groups.values() if len(rr)>1]
            duplicates[key]=[[dict(id=r['id'],scene=r['scene'],partition=r['partition']) for r in rr] for rr in repeated]
            cross.extend(dict(kind=key,ids=[r['id'] for r in rr]) for rr in repeated if len({r['partition'] for r in rr})>1)
        assert ARCHIVE.stat().st_size==stat.st_size and ARCHIVE.stat().st_mtime_ns==stat.st_mtime_ns
        write(OUT/'duplicate_audit.json',dict(groups=duplicates,cross_partition=cross,person_separation='UNKNOWN_NOT_INFERRED'))
        write(OUT/'roster.json',results)
        write(OUT/'verification.json',dict(passed=not cross,images=5116,decode_failures=0,cross_partition_exact_duplicate_groups=len(cross),
            partitions=dict(collections.Counter(r['partition'] for r in results)),
            scene_counts={p:len({r['scene'] for r in results if r['partition']==p}) for p in ['Train','Test']},
            sizes=dict(collections.Counter(str(r['original_size']) for r in results)),modes=dict(collections.Counter(r['original_mode'] for r in results)),
            supplied_icc_count=sum(r['supplied_icc'] for r in results),orientation_counts=dict(collections.Counter(str(r['exif_orientation']) for r in results)),
            admitted_images=5116 if not cross else 0,features=0,head_fits=0,provided_MST=False,archive_sha256=archive_sha,
            roster_sha256=sha(OUT/'roster.json'),source_sha256=sha(OUT/'source.json'),duplicates_sha256=sha(OUT/'duplicate_audit.json')))
        print('COMPLETE5116Exposure admission; crosspartition_duplicate_groups='+str(len(cross)),flush=True)
    except Exception as exc:write(OUT/'failure.json',dict(error=repr(exc),completed_decodes=len(results)));raise
if __name__=='__main__':main()
