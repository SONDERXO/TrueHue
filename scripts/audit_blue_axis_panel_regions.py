"""Six fixed saved-panel cases. Descriptive metrics only; no new correction."""
from pathlib import Path
import json,hashlib,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def metrics(image,reference,mask):
    if not mask.any():return None
    return dict(RGB=float(np.abs(image[mask].astype(float)-reference[mask]).mean()),DE=float(deltaE_ciede2000(rgb2lab(image[mask]/255),rgb2lab(reference[mask]/255)).mean()),channel_MAE=np.abs(image[mask].astype(float)-reference[mask]).mean(axis=0).tolist())
def main():
    folder=ROOT/'outputs/blue_axis_source_held_comparison_v1';out=ROOT/'outputs/blue_axis_panel_region_audit_v1'
    if out.exists():raise FileExistsError('Preserve audit')
    checked=read(folder/'verification_PRIVATE.json');pred={p['review_id']:p for p in read(folder/'predictions_PRIVATE.json')}
    supportids={s['source']:s['source_id'] for s in read(ROOT/'outputs/blue_axis_source_held_design_v1/plan_PRIVATE.json')['support_sources']}
    ids=['case-04','case-12','case-16','case-24','case-48','case-52'];results=[];bindings={};fig,axes=plt.subplots(6,4,figsize=(12,18),dpi=120)
    def bound(rel):
        path=folder/rel;assert sha(path)==checked['artifact_sha256'][rel];bindings[rel]=sha(path);return path
    for row,ident in enumerate(ids):
        p=pred[ident];outputpanel=p['output_panel'];inputpanel='B' if outputpanel=='A' else 'A'
        image=cv2.imread(str(bound(f'review_assets/{ident}_{inputpanel}.png')))[:,:,::-1].copy()
        output=cv2.imread(str(bound(f'review_assets/{ident}_{outputpanel}.png')))[:,:,::-1].copy()
        reference=cv2.imread(str(bound(f'review_assets/{ident}_R.png')))[:,:,::-1].copy()
        support='supports/'+supportids[p['source']];alpha=np.load(bound(support+'/alpha.npy'),allow_pickle=False);protected=cv2.imread(str(bound(support+'/protected_mask.png')),0)>0
        assert image.shape==output.shape==reference.shape==(256,256,3) and alpha.shape==(256,256)
        assert np.array_equal(output[alpha==0],image[alpha==0]) and np.array_equal(output[protected],image[protected])
        regions=dict(primary=alpha>0,whole=np.ones_like(protected),core=alpha==1,feather=(alpha>0)&(alpha<1),outside=alpha==0,protected=protected)
        clipped=reference[:,:,2]>245 if p['role']=='blue_increase' else None
        measured={}
        for name,mask in regions.items():
            a=metrics(image,reference,mask);b=metrics(output,reference,mask)
            measured[name]=dict(pixels=int(mask.sum()),input=a,output=b,DE_benefit=a['DE']-b['DE'] if a else None,RGB_benefit=a['RGB']-b['RGB'] if a else None,
                changed_pixels=int((np.any(output!=image,axis=2)&mask).sum()),reference_exact_output_pixels=int((np.all(output==reference,axis=2)&mask).sum()),forward_blue_clipped_pixels=int((clipped&mask).sum()) if clipped is not None else None)
        for a in ['input','output']:
            for k in ['RGB','DE']:assert math.isclose(measured['primary'][a][k],p['primary'][a][k],abs_tol=1e-10,rel_tol=1e-10)
        assert math.isclose(measured['whole']['DE_benefit'],measured['primary']['DE_benefit']*measured['primary']['pixels']/65536,abs_tol=1e-10,rel_tol=1e-10)
        results.append(dict(review_id=ident,case_id=p['case_id'],role=p['role'],regions=measured,primary_fraction=measured['primary']['pixels']/65536))
        for col,(arr,title) in enumerate([(image,'Input'),(output,'Saved output'),(reference,'Photographic reference'),(image,'Scoring region: yellow contour')]):
            ax=axes[row,col];ax.imshow(arr)
            if col==3:ax.contour(alpha>0,levels=[.5],colors=['yellow'],linewidths=.6)
            ax.set_title(ident+' '+title,fontsize=9);ax.axis('off')
    fig.tight_layout();out.mkdir();fig.savefig(out/'six_case_contact.png');plt.close(fig)
    report=dict(passed=True,cases=results,protocol_sha256=sha(ROOT/'docs/blue-axis-panel-region-audit-protocol-2026-11-13.md'),source_hashes=bindings,primary_metric_replays=6,descriptive_regions_not_gates=True,new_fits=0,new_predictions=0,new_correction_renders=0,NPZ_decodes=0,model_adopted=False)
    (out/'results_PRIVATE.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    assert all(sha(folder/n)==h for n,h in bindings.items())
    print(json.dumps([dict(id=r['review_id'],primary_fraction=r['primary_fraction'],primaryDE=r['regions']['primary']['DE_benefit'],wholeDE=r['regions']['whole']['DE_benefit'],coreDE=r['regions']['core']['DE_benefit'],featherDE=r['regions']['feather']['DE_benefit'],clip_primary=r['regions']['primary']['forward_blue_clipped_pixels'],clip_outside=r['regions']['outside']['forward_blue_clipped_pixels'],primary_output_MAE=r['regions']['primary']['output']['channel_MAE']) for r in results],indent=2))
if __name__=='__main__':main()
