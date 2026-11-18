"""One bounded frozen-predictor pass on20cached normal V2 reference photographs."""
from pathlib import Path
import base64
import hashlib
import json
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wb314_research_predictor import FrozenWB314, MODEL_SHA256
from wb_feature_direct_verify import route
from src.evaluation.luminance_chroma_scalar import replay

PARENT = ROOT/'outputs/wb314_mste_development_packet_v2_area'
OUT = ROOT/'outputs/wb314_normal_photo_preview_v1'
DELIVERY = ROOT/'output/wb314-normal-photo-preview-2026-11-19'
PROTOCOL = ROOT/'docs/wb314-normal-photo-preview-protocol-2026-11-19.md'


def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,ensure_ascii=False,allow_nan=False)
def embedded(p):return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode('ascii')
def recheck(bindings):
    for path,digest in bindings.items():assert sha(Path(path))==digest,path


def main():
    if OUT.exists() or DELIVERY.exists():raise FileExistsError('Preserve prior normal-input run; no automatic restart')
    assert read(PARENT/'presentation_audit.json')['passed']
    rows=read(PARENT/'selected_references.json');assert len(rows)==20
    bindings={str(p):sha(p) for p in [PROTOCOL,Path(__file__),PARENT/'selected_references.json',
        PARENT/'presentation_audit.json',ROOT/'outputs/wb314_final_training_v1/model.json',
        ROOT/'scripts/wb314_research_predictor.py',ROOT/'src/model_training/luminance_chroma_operator.py',
        ROOT/'src/evaluation/luminance_chroma_scalar.py',ROOT/'scripts/wb_feature_direct_verify.py']}
    for r in rows:
        pack=PARENT/'references'/r['candidate_id']/'reference_support.npz'
        assert sha(pack)==r['pack_sha256'];bindings[str(pack)]=sha(pack)
        p=pack.parent/'parent_report.json';bindings[str(p)]=sha(p)
    assert sha(ROOT/'outputs/wb314_final_training_v1/model.json')==MODEL_SHA256
    OUT.mkdir();(OUT/'evaluation').mkdir()
    write(OUT/'bindings.json',bindings)
    write(OUT/'plan.json',dict(cases=20,source='exact existing20cached V2reference arrays',
        input_role='undistorted_normal_photograph',model_sha256=MODEL_SHA256,
        logical_correction_budget=20,fits=0,original_JPEG_decodes=0,mask_inference=0,
        synthetic_distortion_calls=0,source_reselection=False,high_resolution_output=False))
    predictor=FrozenWB314();records=[]
    write(OUT/'started.json',dict(budget=20,automatic_retry=False))
    try:
        for i,r in enumerate(rows,1):
            folder=PARENT/'references'/r['candidate_id']
            with np.load(folder/'reference_support.npz',allow_pickle=False) as z:
                image,measurement,alpha,protected=[z[k].copy() for k in ['reference','measurement','alpha','protected']]
            before=[a.tobytes() for a in [image,measurement,alpha,protected]]
            result=predictor.correct(image,measurement,alpha,protected)
            leaf,controls=route(predictor.model,result['features'])
            assert leaf==result['leaf'] and controls==result['controls']
            scalar,_=replay(image,image,alpha,protected,controls)
            assert np.array_equal(scalar,result['output'])
            assert np.array_equal(result['output'][protected],image[protected])
            assert np.array_equal(result['output'][alpha==0],image[alpha==0])
            assert before==[a.tobytes() for a in [image,measurement,alpha,protected]]
            path=OUT/'evaluation'/(r['pair_id']+'.npz')
            np.savez(path,input=image,candidate=result['output'],measurement=measurement,alpha=alpha,protected=protected)
            row={k:r[k] for k in ['case_id','subject_id','MST','candidate_id','pair_id']}
            row.update(input_role='undistorted_normal_photograph',features=result['features'],controls=controls,leaf=leaf,
                evaluation_sha256=sha(path),source_pack_sha256=r['pack_sha256'],
                face_box=read(folder/'parent_report.json')['face_box'],scalar_RGB8_exact=True,inputs_immutable=True)
            records.append(row);print(f'Normal-input model/scalar {i}/20',flush=True)
        recheck(bindings)
        write(OUT/'predictions_sealed.json',dict(records=records,model_sha256=MODEL_SHA256,
            sealed_before_descriptive_summary_and_view=True,fits=0))
        DELIVERY.mkdir()
        for name in ['pairs','native-pairs','full-frames']:(DELIVERY/name).mkdir()
        statistics=[];sections=[];face_images=[]
        for r in records:
            with np.load(OUT/'evaluation'/(r['pair_id']+'.npz'),allow_pickle=False) as z:
                image,candidate,alpha,protected=[z[k] for k in ['input','candidate','alpha','protected']]
            changed=np.any(candidate!=image,axis=2);support=alpha>0
            statistics.append(dict(pair_id=r['pair_id'],MST=r['MST'],exact_input_preserved=bool(not changed.any()),
                changed_application_pixels=int(changed[support].sum()),application_pixels=int(support.sum()),
                mean_abs_channel_change_in_support=float(np.abs(candidate.astype(float)-image.astype(float))[support].mean()),
                change_is_not_proof_of_improvement_or_harm=True))
            x,y,w,h=r['face_box'];native=np.concatenate([image[y:y+h,x:x+w],candidate[y:y+h,x:x+w]],axis=1)
            full=np.concatenate([image,candidate],axis=1)
            large=np.repeat(np.repeat(native,4,axis=0),4,axis=1)
            name=r['pair_id']+f'_mst{r["MST"]:02d}.png'
            for folder,pixels in [('pairs',large),('native-pairs',native),('full-frames',full)]:
                p=DELIVERY/folder/name;Image.fromarray(pixels).save(p)
                with Image.open(p) as im:assert np.array_equal(np.asarray(im),pixels)
            face_images.append(Image.fromarray(native))
            exact=statistics[-1]['exact_input_preserved']
            label='Output exactly matches input' if exact else 'Model adjusted this normal input; benefit is not established'
            sections.append(f'<section><h2>Photo {int(r["pair_id"].split("_")[-1]):02d} - MST {r["MST"]:02d}</h2>'
                f'<p>{label}</p><p><strong>Normal original input (left) | Frozen model output (right)</strong></p>'
                f'<div class="viewport"><img width="{w*8}" height="{h*4}" src="{embedded(DELIVERY/"pairs"/name)}" alt="Normal input and actual frozen-model output"></div>'
                '<details><summary>Native full-frame comparison</summary>'
                f'<img width="512" height="256" src="{embedded(DELIVERY/"full-frames"/name)}" alt="Full normal input and output"></details></section>')
        unchanged=sum(r['exact_input_preserved'] for r in statistics)
        summary=dict(passed=True,model_sha256=MODEL_SHA256,cases=20,subjects=len({r['subject_id'] for r in records}),
            MST_categories=10,input_role='undistorted_normal_photographs',exact_unchanged_outputs=unchanged,
            changed_outputs=20-unchanged,logical_model_calls=20,portable_route_checks=20,exact_scalar_RGB8_checks=20,
            input_immutability_checks=20,protected_outside_checks=20,PNG_roundtrips=60,
            new_fits=0,new_source_portrait_decodes=0,synthetic_distortion_calls=0,mask_inference=0,
            model_changed=False,high_resolution_output=False,expert_responses=0,new_human_ratings=0,
            improvement_on_naturally_faulty_photos_established=False,independent_final_validation=False,
            automatic_new_photo_masking_qualified=False,Form_edits=0,automatic_expert_packet_replacement=False)
        write(OUT/'summary.json',summary);write(OUT/'descriptive_changes_PRIVATE.json',statistics)
        for start in range(0,20,4):
            sheet=Image.new('RGB',(512,1120),'white');draw=ImageDraw.Draw(sheet)
            for j,im in enumerate(face_images[start:start+4]):
                s=statistics[start+j];draw.text((4,j*280+4),f'{s["pair_id"]} | normal input / output | exact: {s["exact_input_preserved"]}',fill='black')
                sheet.paste(im,(0,j*280+24))
            sheet.save(OUT/f'contact_{start//4+1:02d}.png')
        page=('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>WB314 normal-photo preview</title><style>body{font:18px system-ui;max-width:1150px;margin:24px auto;padding:0 20px}'
            'section{border-top:1px solid #aaa;margin:30px 0}.viewport{overflow-x:auto}img{max-width:none;image-rendering:pixelated}'
            '.note{background:#edf3f7;padding:16px}</style><h1>Actual correction of normal photos</h1><div class="note">'
            f'<p><strong>No added synthetic distortion. {unchanged}/20outputs exactly preserve the input; {20-unchanged}/20change it.</strong></p>'
            '<p>Same frozen model and same20selected photos. These outputs were computed from the normal inputs themselves, not reused from distorted-input predictions.</p></div>'
            '<p>This is a diagnostic preview, not a replacement expert packet or proof of real-world improvement. '
            'These are previously exposed well-lit dataset photographs with approximate cached masks. '
            'Changing a normal photo does not by itself establish benefit or harm.</p>'
            '<p>Processing remains256x256. The face views repeat pixels4x for size; no HD detail is added. '
            'Original-resolution mask/render integration remains unqualified. Full-frame comparisons are available beneath each pair.</p>'+''.join(sections))
        (DELIVERY/'START_HERE.html').write_text(page,encoding='utf-8')
        (DELIVERY/'README.txt').write_text('Normal-photo research preview\n\n'+json.dumps(summary,indent=2)+
            '\n\nNo synthetic perturbation was applied. A changed output is not automatically an improvement. '
            'No real-world quality ratings or expert-corrected targets exist for this preview. '
            'Do not transfer earlier synthetic reviews or replace the expert Form automatically. Native256px/mask/prior-exposure limitations remain.\n',encoding='utf-8')
        write(DELIVERY/'SUMMARY.json',summary)
        with zipfile.ZipFile(DELIVERY/'WB314-normal-photo-preview.zip','x',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(DELIVERY.rglob('*')):
                if p.is_file() and p.suffix!='.zip':z.write(p,p.relative_to(DELIVERY).as_posix())
        with zipfile.ZipFile(DELIVERY/'WB314-normal-photo-preview.zip') as z:assert z.testzip() is None
        recheck(bindings)
        write(OUT/'verification.json',dict(**summary,zip_CRC_pass=True,artifacts={p.relative_to(DELIVERY).as_posix():sha(p) for p in DELIVERY.rglob('*') if p.is_file()}))
        print(json.dumps(summary),flush=True)
    except Exception as e:
        write(OUT/'failure.json',dict(error=repr(e),completed_model_calls=len(records),automatic_retry=False));raise


if __name__=='__main__':main()
