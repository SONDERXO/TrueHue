"""Staged input-only real/generator adapter; no fitting or implicit source access."""
from pathlib import Path
import hashlib
import cv2
import numpy as np
from .blue_axis_preparation import features281

ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class IdentityParityError(ValueError):
    pass


class BoundInputs:
    def __init__(self,root,plan):
        self.root=Path(root).resolve();self.plan=plan;self.access=[];self.supports={}
        self.feature_sources={r['source_id']:r for r in plan['feature_sources']}
        ids={r['source_id'] for r in plan['rows']}
        if (len(plan['rows'])!=66 or len(ids)!=11 or len(self.feature_sources)!=11 or set(self.feature_sources)!=ids
                or len({r['case_id'] for r in plan['rows']})!=66
                or {(r['source_id'],r['role']) for r in plan['rows']}!={(s,r) for s in ids for r in ROLES}):
            raise ValueError('Exact66case/11source bindings required')
        self.files={}
        def declare(path,digest):
            p=self.path(path)
            if p in self.files and self.files[p]!=digest:raise ValueError('Conflicting file hash declarations')
            self.files[p]=digest
        for row in plan['rows']:
            if row['allowed_input_key']!='input':raise ValueError('Only cached actual input key allowed')
            declare(row['input_pack'],row['input_pack_sha256'])
            declare(row['cached_support_pack'],row['cached_support_sha256'])
        for item in plan['feature_sources']:
            declare(item['measurement_path'],item['measurement_sha256'])
            declare(item['selected_receipt'],item['selected_receipt_sha256'])
        # All declared files verified before any image/array decode.
        self.recheck()

    def path(self,value):
        p=(self.root/value).resolve()
        if not p.is_relative_to(self.root/'outputs'):
            raise ValueError('Only explicitly declared cached output artifacts allowed')
        if any('locked' in v.lower() or 'final24' in v.lower() for v in p.relative_to(self.root).parts):
            raise ValueError('Locked content/manifest access forbidden')
        return p

    def recheck(self):
        for p,digest in self.files.items():
            if sha(p)!=digest:raise ValueError('Declared input hash mismatch: '+str(p))

    def support(self,row):
        source=row['source_id']
        if source not in self.supports:
            p=self.path(row['cached_support_pack'])
            with np.load(p,allow_pickle=False) as pack:
                alpha=pack['alpha'];protected=pack['protected'] # Reference RGB not decoded.
            self.access.extend([dict(path=str(p),key=k) for k in ['alpha','protected']])
            item=self.feature_sources[source]
            measurement=cv2.imread(str(self.path(item['measurement_path'])),cv2.IMREAD_GRAYSCALE)
            self.access.append(dict(path=str(self.path(item['measurement_path'])),key='measurement_png'))
            if (measurement is None or measurement.dtype!=np.uint8 or measurement.shape!=(256,256)
                    or not set(np.unique(measurement))<={0,255}):raise ValueError('Bound binary measurement mask required')
            if (alpha.shape!=(256,256) or not np.issubdtype(alpha.dtype,np.floating)
                    or not np.isfinite(alpha).all() or (alpha<0).any() or (alpha>1).any()
                    or not (alpha>0).any() or protected.shape!=alpha.shape or protected.dtype!=bool
                    or np.any(alpha[protected]!=0)):
                raise ValueError('Invalid cached alpha/protection')
            self.supports[source]=(measurement,alpha,protected)
        return self.supports[source]

    def input(self,row):
        p=self.path(row['input_pack'])
        with np.load(p,allow_pickle=False) as pack:image=pack['input']
        self.access.append(dict(path=str(p),key='input',case_id=row['case_id'],role=row['role']))
        if image.dtype!=np.uint8 or image.shape!=(256,256,3):raise ValueError('Cached RGB8 input required')
        return image


def prepare(plan,inputs,mapping,*,extractor=features281,record=lambda event,row:None):
    prepared=[];names=plan['feature_names']
    if len(names)!=281:raise ValueError('Frozen281schema required')
    def extract(row):
        image=inputs.input(row);measurement,_,_=inputs.support(row)
        vector,detail=extractor(image,measurement,mapping,names)
        if len(vector)!=281 or not np.isfinite(vector).all():raise ValueError('Finite281features required')
        if np.asarray(vector,np.float32).astype(float).tolist()!=vector:raise ValueError('Exact float32 vectors required')
        return dict(case_id=row['case_id'],source_id=row['source_id'],role=row['role'],
            generated_fixture=row['generated_fixture'],y=list(row['y']),x=vector,feature_details=detail,
            input_pack_sha256=row['input_pack_sha256'],measurement_sha256=inputs.feature_sources[row['source_id']]['measurement_sha256'],
            parent_training_admitted=row['parent_training_admitted'],
            experimental_role='exposed_development_feature_preparation_not_final_admission')
    for row in plan['rows']:
        if row['role']!='identity':continue
        result=extract(row);expected=inputs.feature_sources[row['source_id']]['identity_saved_feature_vector']
        if result['x']!=expected:
            differences=[dict(index=i,name=names[i],expected=a,actual=b) for i,(a,b) in enumerate(zip(expected,result['x'])) if a!=b]
            record('identity_failure',dict(**result,expected=expected,differences=differences))
            raise IdentityParityError('Identity feature mismatch: '+row['source_id'])
        record('identity_pass',result);prepared.append(result)
    if len(prepared)!=11:raise ValueError('All11identities required before nonidentity input access')
    record('all_identities_passed',dict(count=11))
    for row in plan['rows']:
        if row['role']=='identity':continue
        result=extract(row);record('nonidentity_pass',result);prepared.append(result)
    if len(prepared)!=66:raise ValueError('Complete66prepared vectors required')
    by_case={r['case_id']:r for r in prepared}
    return [by_case[r['case_id']] for r in plan['rows']]
