"""Bounded32-file retrieval from the existing publisher PPR10K archives."""
from pathlib import Path
import io,json,hashlib,re,zipfile
import requests
ROOT=Path(__file__).resolve().parents[1]
DESIGN=ROOT/'outputs/existing_ppr_additional_evidence_design_v1'
OUT=ROOT/'outputs/existing_ppr_additional_evidence_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2)+'\n')


class BoundedZip(io.RawIOBase):
    def __init__(self,key,inventory,ledger,cap):
        self.key=key;self.ledger=ledger;self.cap=cap;self.pos=0;self.session=requests.Session()
        self.url='https://drive.usercontent.google.com/download'
        self.params=dict(id=inventory['archive_id'],export='download')
        response=self.session.get(self.url,params=self.params,headers={'Range':'bytes=-128'},timeout=45,stream=True)
        response.raise_for_status()
        if response.status_code==200 and 'text/html' in response.headers.get('Content-Type',''):
            html=self.consume(response,128_000).decode('utf-8');params=dict(re.findall(r'name="([^"]+)" value="([^"]*)"',html))
            if 'confirm' not in params:raise ValueError('No public publisher download confirmation; stop')
            self.params=params
            response=self.session.get(self.url,params=self.params,headers={'Range':'bytes=-128'},timeout=45,stream=True)
            response.raise_for_status()
        if response.status_code!=206:response.close();raise ValueError('Range response required; full download rejected')
        content_range=response.headers.get('Content-Range','');match=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',content_range)
        if not match:response.close();raise ValueError('Declared archive range required')
        self.size=int(match[3]);assert self.size==inventory['archive_bytes'];assert int(match[2])-int(match[1])+1==128
        self.consume(response,128)
    def consume(self,response,limit):
        data=bytearray()
        try:
            for chunk in response.iter_content(65536):
                self.ledger['transferred_bytes']+=len(chunk)
                if len(data)+len(chunk)>limit or self.ledger['transferred_bytes']>self.cap:
                    raise ValueError('Bounded transfer cap reached')
                data.extend(chunk)
            return bytes(data)
        finally:response.close()
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
        return self.pos
    def read(self,size=-1):
        if size<0:size=self.size-self.pos
        size=min(size,self.size-self.pos)
        if size<=0:return b''
        if size>4_000_000 or self.ledger['transferred_bytes']+size>self.cap:raise ValueError('Range/cumulative limit')
        start=self.pos;end=start+size-1
        r=self.session.get(self.url,params=self.params,headers={'Range':f'bytes={start}-{end}'},timeout=45,stream=True)
        r.raise_for_status()
        if r.status_code!=206 or r.headers.get('Content-Range')!=f'bytes {start}-{end}/{self.size}':
            r.close();raise ValueError('Exact partial response required')
        data=self.consume(r,size);assert len(data)==size;self.pos+=size
        return data


def main():
    if OUT.exists():raise FileExistsError('Preserve completed or partial batch; no automatic restart')
    plan_path=DESIGN/'plan_PRIVATE.json';plan=read(plan_path)
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    inventory=read(ROOT/'outputs/ppr10k_inspection_v1/inventory.json')
    assert len(plan['rows'])==16 and plan['whole_archive_download_allowed'] is False
    OUT.mkdir();ledger=dict(status='in_progress',transferred_bytes=0,maximum_transfer_bytes=plan['maximum_transfer_bytes'],files=[])
    write(OUT/'execution_plan_PRIVATE.json',dict(plan_sha256=sha(plan_path),publisher_url='https://github.com/csjliang/PPR10K',dataset_terms='noncommercial_research',new_models=0,tree_fits=0,holdout_reads=0))
    try:
        for role in ['source','target_a']:
            remote=BoundedZip(role,inventory[role],ledger,plan['maximum_transfer_bytes'])
            with zipfile.ZipFile(remote) as archive:
                for row in plan['rows']:
                    expected=row[role];member=archive.getinfo(expected['name'])
                    assert member.file_size==expected['size'] and member.compress_size==expected['compressed'] and member.CRC==expected['crc']
                    data=archive.read(member);assert len(data)==expected['size']
                    dest=OUT/'originals'/role/(row['frame']+'.tif');dest.parent.mkdir(parents=True,exist_ok=True)
                    with dest.open('xb') as f:f.write(data)
                    ledger['files'].append(dict(frame=row['frame'],group=row['group'],role=role,path=str(dest.relative_to(ROOT)),bytes=len(data),sha256=sha(dest),member=expected['name'],zip_CRC_verified=True,publisher_training=True))
                    write(OUT/'acquisition_PRIVATE.json',ledger);print(role,row['frame'],'verified',len(data),'bytes',flush=True)
            remote.session.close()
        assert len(ledger['files'])==32 and all(sha(p)==h for p,h in plan['input_sha256'].items())
        ledger['status']='complete';write(OUT/'acquisition_PRIVATE.json',ledger)
        print('Complete32files; transferred',ledger['transferred_bytes'],'bytes; no model/image inference',flush=True)
    except Exception as e:
        ledger['status']='incomplete_preserved';ledger['error']=type(e).__name__+': '+str(e);write(OUT/'acquisition_PRIVATE.json',ledger);raise

if __name__=='__main__':main()
