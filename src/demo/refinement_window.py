"""Stdlib-only Tk editor, usable by the compatibility and project frontends."""
import hashlib,json,os,subprocess,sys,uuid
from datetime import datetime,timezone
from pathlib import Path
import tkinter as tk
from tkinter import ttk,messagebox
from src.demo.manual_brush import refine_masks
ROOT=Path(__file__).resolve().parents[2]


class RefinementWindow:
    def __init__(self,root,folder,worker_python,on_applied,*,research=False,annotation_parent=None,jobs_parent=None,drafts_parent=None):
        self.folder=Path(folder);self.worker_python=str(worker_python);self.on_applied=on_applied
        self.research=research;self.annotation_parent=annotation_parent;self.jobs_parent=jobs_parent
        self.drafts_parent=drafts_parent;self.draft_file=None
        self.manifest_sha=hashlib.sha256((self.folder/'manifest.json').read_bytes()).hexdigest()
        report=json.loads((self.folder/'report.json').read_text(encoding='utf-8'))
        if research:
            if report.get('schema_version') not in ('truehue_photographic_support_task_v1','truehue_photographic_support_annotation_v1'):
                raise ValueError('Explicit photographic support task required')
        elif report.get('masking_mode')!='current' or report.get('status')!='development_experimental_mst':
            raise ValueError('Run the current-mask demo successfully before refining')
        self.window=tk.Toplevel(root);self.window.title('TrueHue | Refine skin mask')
        self.window.transient(root);self.window.grab_set();self.strokes=[];self.pending=None;self.process=None
        if research:
            # Keep save actions and review confirmations ahead of the image in
            # pack order: a tall image must never push these controls offscreen.
            self.research_controls=ttk.Frame(self.window)
            self.research_controls.pack(side='top',fill='x',padx=8,pady=5)
            self.action_buttons=ttk.Frame(self.research_controls)
            self.action_buttons.pack(side='top',pady=3)
        self.original=tk.PhotoImage(file=os.path.relpath(self.folder/'photo_used.png',ROOT))
        self.width,self.height=self.original.width(),self.original.height()
        self.rgb=[self.original.get(x,y) for y in range(self.height) for x in range(self.width)]
        self.base=[]
        for name in ['correction_mask.png','measurement_mask.png','protected_mask.png']:
            photo=tk.PhotoImage(file=os.path.relpath(self.folder/name,ROOT))
            if (photo.width(),photo.height())!=(self.width,self.height):raise ValueError('Matching masks required')
            self.base.append(bytes(255 if photo.get(x,y)[0] else 0 for y in range(self.height) for x in range(self.width)))
        ttk.Label(self.window,text='Paint visible skin green. Remove hair/beard or objects from the selected area.',wraplength=700).pack(padx=14,pady=(12,4))
        ttk.Label(self.window,text=('Research masks only; no brightness correction or model prediction. Review both masks separately.' if research else 'Facial measurement: face skin only. Correction may include visible neck. Older model controls stay unchanged.'),wraplength=700).pack(padx=14,pady=4)
        toolbar=ttk.Frame(self.window);toolbar.pack(padx=8,pady=6)
        self.target=tk.StringVar(value='measurement' if research else 'both');self.mode=tk.StringVar(value='remove');self.radius=tk.IntVar(value=4)
        for label,value in [('Both masks','both'),('Correction','correction'),('Measurement','measurement')]:
            ttk.Radiobutton(toolbar,text=label,variable=self.target,value=value,command=self.render).pack(side='left',padx=3)
        tools=ttk.Frame(self.window);tools.pack(pady=4)
        for label,value in [('Remove','remove'),('Add skin','add'),('Restore before editing','restore')]:
            ttk.Radiobutton(tools,text=label,variable=self.mode,value=value).pack(side='left',padx=5)
        tk.Scale(tools,from_=1,to=32,orient='horizontal',label='Brush radius',variable=self.radius,length=130).pack(side='left')
        self.unlock=tk.BooleanVar(value=False)
        ttk.Checkbutton(self.window,text='Allow additions in protected areas (only where you have checked the visible skin)',variable=self.unlock).pack(padx=12,pady=4)
        self.scale=1 if research else max(1,min(2,(root.winfo_screenheight()-350)//self.height))
        self.canvas=tk.Canvas(self.window,width=self.width*self.scale,height=self.height*self.scale,highlightthickness=0)
        self.canvas.pack(padx=12,pady=5)
        self.status=tk.StringVar(value='Green: selected area. Undo/reset are available. Cancel keeps the current result.')
        ttk.Label(self.window,textvariable=self.status,wraplength=700).pack(padx=12,pady=5)
        if research:
            self.measurement_reviewed=tk.BooleanVar(value=False);self.correction_reviewed=tk.BooleanVar(value=False)
            self.review_checkbuttons=[]
            for text,variable in [('I reviewed facial measurement (exclude hair/beard, eyes, lips and neck)',self.measurement_reviewed),
                                  ('I reviewed correction support and retained protection (face and visible neck)',self.correction_reviewed)]:
                checkbox=ttk.Checkbutton(self.research_controls,text=text,variable=variable)
                checkbox.pack(anchor='w',padx=6);self.review_checkbuttons.append(checkbox)
            self.note=tk.StringVar();self.note_entry=ttk.Entry(self.research_controls,textvariable=self.note,width=65)
            self.note_entry.pack(padx=6,pady=3,fill='x')
            self.note.trace_add('write',lambda *_:self._save_draft())
        buttons=self.action_buttons if research else ttk.Frame(self.window)
        if not research:buttons.pack(pady=(3,12))
        self.buttons=[]
        for label,command in [('Undo',self.undo),('Reset edits',self.reset),('Cancel',self.cancel),('Apply refinement',self.apply)]:
            b=ttk.Button(buttons,text=label,command=command)
            if research:
                i=len(self.buttons)
                b.grid(row=0 if i==3 else 1,column=0 if i==3 else i,columnspan=2 if i==3 else 1,padx=4,pady=3,sticky='ew')
            else:b.pack(side='left',padx=5)
            self.buttons.append(b)
        if research:
            self.buttons[-1].configure(text='Save reviewed masks')
            b=ttk.Button(buttons,text='Save as unjudgeable',command=lambda:self.apply('unjudgeable'));b.grid(row=0,column=2,padx=4,pady=3,sticky='ew');self.buttons.append(b)
        self.canvas.bind('<ButtonPress-1>',self.down);self.canvas.bind('<B1-Motion>',self.drag);self.canvas.bind('<ButtonRelease-1>',self.up)
        self.window.protocol('WM_DELETE_WINDOW',self.cancel)
        if research:self._restore_draft()
        self.render()
        if research:
            self.window.update_idletasks()
            width=min(root.winfo_screenwidth()-60,max(680,self.window.winfo_reqwidth()))
            height=min(root.winfo_screenheight()-90,self.window.winfo_reqheight())
            self.window.geometry(f'{width}x{height}+20+20')

    def _restore_draft(self):
        parent=Path(self.drafts_parent) if self.drafts_parent else ROOT/'outputs/photographic_support_drafts_v1'
        folder=parent/self.manifest_sha;folder.mkdir(parents=True,exist_ok=True)
        pending=[]
        for path in folder.glob('draft_*.json'):
            data=json.loads(path.read_text(encoding='utf-8'))
            if data.get('status')=='draft_not_reviewed' and data.get('base_manifest_sha256')==self.manifest_sha:
                pending.append((path,data))
        if pending:
            path,data=max(pending,key=lambda item:item[0].stat().st_mtime_ns)
            if messagebox.askyesno('Restore unsaved mask edits','An autosaved draft exists for this exact result. Restore its painted edits and note? Both masks will still need review confirmation.',parent=self.window):
                refine_masks(*self.base,self.width,self.height,data['strokes'])
                self.strokes=data['strokes'];self.note.set(data.get('note',''))
                self.status.set('Restored autosaved edits. Review both masks, then use Save reviewed masks at the top.')
        self.draft_file=folder/('draft_'+uuid.uuid4().hex+'.json')

    def _save_draft(self,status='draft_not_reviewed',annotation=None):
        if not self.research or self.draft_file is None:return
        strokes=self.strokes+([self.pending] if self.pending else [])
        if not strokes and not self.note.get() and not self.draft_file.exists() and status=='draft_not_reviewed':return
        data=dict(schema_version='truehue_photographic_support_draft_v1',status=status,
            base_manifest_sha256=self.manifest_sha,base_folder=str(self.folder.resolve()),
            saved_utc=datetime.now(timezone.utc).isoformat(),strokes=strokes,note=self.note.get(),
            annotation=str(annotation) if annotation else None,review_approved=False)
        temporary=self.draft_file.with_suffix('.tmp')
        temporary.write_text(json.dumps(data,indent=2),encoding='utf-8');os.replace(temporary,self.draft_file)

    def point(self,event):return [max(0,min(self.width-1,event.x/self.scale)),max(0,min(self.height-1,event.y/self.scale))]
    def down(self,event):
        if self.process is not None:return
        self.pending=dict(target=self.target.get(),mode=self.mode.get(),radius=self.radius.get(),unlock=self.unlock.get(),points=[self.point(event)])
        self.render()
    def drag(self,event):
        if self.pending is not None:self.pending['points'].append(self.point(event));self.render()
    def up(self,event):
        if self.pending is not None:
            self.pending['points'].append(self.point(event));self.strokes.append(self.pending);self.pending=None;self._save_draft();self.render()
    def undo(self):
        if self.strokes:self.strokes.pop()
        self.pending=None;self._save_draft();self.render()
    def reset(self):self.strokes.clear();self.pending=None;self.unlock.set(False);self._save_draft();self.render()
    def render(self):
        strokes=self.strokes+([self.pending] if self.pending else [])
        c,m,p=refine_masks(*self.base,self.width,self.height,strokes)
        mask=m if self.target.get()=='measurement' else c
        values=bytearray()
        for rgb,on in zip(self.rgb,mask):
            values.extend((round(.65*rgb[0]),round(.65*rgb[1]+.35*255),round(.65*rgb[2])) if on else rgb)
        data=f'P6\n{self.width} {self.height}\n255\n'.encode()+values
        self.photo=tk.PhotoImage(data=data,format='PPM').zoom(self.scale,self.scale)
        self.canvas.delete('all');self.canvas.create_image(0,0,image=self.photo,anchor='nw')
    def cancel(self):
        if self.process is not None:return
        self._save_draft()
        self.window.destroy()
    def apply(self,review='reviewed_selection'):
        if self.pending:self.strokes.append(self.pending);self.pending=None
        if not self.research and not self.strokes:self.window.destroy();return
        if self.research and review=='reviewed_selection' and not (self.measurement_reviewed.get() and self.correction_reviewed.get()):
            messagebox.showerror('Review both masks','Check measurement and correction separately, then confirm both review boxes.',parent=self.window);return
        self._save_draft()
        parent=Path(self.jobs_parent) if self.jobs_parent else ROOT/('outputs/photographic_support_jobs_v1' if self.research else 'outputs/manual_editor_jobs')
        job=parent/uuid.uuid4().hex;job.mkdir(parents=True,exist_ok=False)
        data=dict(schema_version='truehue_photographic_support_edits_v1' if self.research else 'truehue_manual_mask_edits_v1',base_manifest_sha256=self.manifest_sha,strokes=self.strokes)
        if self.research:data.update(review=review,measurement_reviewed=self.measurement_reviewed.get(),correction_reviewed=self.correction_reviewed.get(),note=self.note.get())
        self.payload=job/'edits.json';self.payload.write_text(json.dumps(data,indent=2),encoding='utf-8')
        self.log=(job/'worker.log').open('w',encoding='utf-8')
        try:
            command=[self.worker_python,str(ROOT/('scripts/737_save_photographic_support.py' if self.research else 'scripts/719_apply_manual_refinement.py')),
                '--export-folder',str(self.folder),'--payload',str(self.payload)]
            if self.research and self.annotation_parent:command+=['--output-parent',str(self.annotation_parent)]
            self.process=subprocess.Popen(command,cwd=ROOT,stdout=self.log,stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        except OSError:
            self.log.close();raise
        for b in self.buttons:b.configure(state='disabled')
        if self.research:
            for b in self.review_checkbuttons+[self.note_entry]:b.configure(state='disabled')
        self.status.set('Applying your mask edits locally…');self.window.after(100,self.poll)
    def poll(self):
        if self.process.poll() is None:self.window.after(100,self.poll);return
        code=self.process.returncode;self.process=None;self.log.close()
        if code:
            for b in self.buttons:b.configure(state='normal')
            if self.research:
                for b in self.review_checkbuttons+[self.note_entry]:b.configure(state='normal')
            text=self.payload.parent.joinpath('worker.log').read_text(encoding='utf-8')
            self.status.set('Edits were not applied. Undo or restore skin, then try again.')
            messagebox.showerror('Refinement not applied',text[-1600:],parent=self.window);return
        folder=Path(json.loads(self.payload.with_suffix('.result.json').read_text())['export'])
        self._save_draft('saved',folder)
        self.on_applied(folder);self.window.destroy()


def open_refinement(root,folder,worker_python,on_applied):
    return RefinementWindow(root,folder,worker_python,on_applied)
