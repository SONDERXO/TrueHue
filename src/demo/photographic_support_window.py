"""Stdlib queue around the shared brush editor, with explicit research schemas."""
from pathlib import Path
import json,os
import tkinter as tk
from tkinter import ttk,messagebox
from src.demo.refinement_window import RefinementWindow
from src.demo.photographic_reference_review import verify_bundle,sha

ROOT=Path(__file__).resolve().parents[2]


class PhotographicSupportQueue:
    def __init__(self,root,package,worker_python,*,annotations_parent=None,jobs_parent=None,drafts_parent=None):
        self.root=root;self.package=Path(package);self.worker_python=worker_python
        self.annotations_parent=Path(annotations_parent) if annotations_parent else ROOT/'outputs/photographic_support_annotations_v1'
        self.jobs_parent=Path(jobs_parent) if jobs_parent else ROOT/'outputs/photographic_support_jobs_v1'
        self.drafts_parent=Path(drafts_parent) if drafts_parent else self.jobs_parent.parent/'photographic_support_drafts_v1'
        self.presentation=json.loads((self.package/'queue.json').read_text(encoding='utf-8')).get('presentation',{})
        self.queue=json.loads((self.package/'queue.json').read_text(encoding='utf-8'))['tasks'];self.index=0
        self.scan();self.index=next((i for i,r in enumerate(self.queue) if r['manifest_sha256'] not in self.saved),0)
        root.title(self.presentation.get('title','TrueHue | Photographic source and target support review'))
        ttk.Label(root,text=self.presentation.get('description','Review source and target masks separately. No correction model or brightness adjustment runs here.'),wraplength=750).pack(padx=14,pady=8)
        self.heading=tk.StringVar();ttk.Label(root,textvariable=self.heading,wraplength=750).pack(padx=14,pady=5)
        self.warning=tk.StringVar();ttk.Label(root,textvariable=self.warning,wraplength=750).pack(padx=14,pady=5)
        self.image=ttk.Label(root);self.image.pack(padx=12,pady=4)
        self.status=tk.StringVar();ttk.Label(root,textvariable=self.status,wraplength=750).pack(padx=14,pady=5)
        toolbar=ttk.Frame(root);toolbar.pack(pady=8)
        ttk.Button(toolbar,text='Previous',command=lambda:self.navigate(-1)).pack(side='left',padx=5)
        self.edit_button=ttk.Button(toolbar,text='Open mask editor / save both reviews',command=self.edit);self.edit_button.pack(side='left',padx=5)
        ttk.Button(toolbar,text='Next',command=lambda:self.navigate(1)).pack(side='left',padx=5)
        ttk.Button(toolbar,text='First unsaved review',command=self.first_missing).pack(side='left',padx=5)
        self.load()

    def scan(self):
        self.saved={};known={r['manifest_sha256'] for r in self.queue}
        for p in self.annotations_parent.glob('support_*/report.json'):
            verify_bundle(p.parent);r=json.loads(p.read_text(encoding='utf-8'));key=r['task_manifest_sha256']
            if key in known and (key not in self.saved or r['saved_utc']>self.saved[key][1]['saved_utc']):self.saved[key]=(p.parent,r)

    def load(self):
        self.scan();row=self.queue[self.index]
        if Path(row['folder']).name!=row['folder'] or '/' in row['folder'] or '\\' in row['folder']:raise ValueError('Local task required')
        folder=self.package/row['folder'];verify_bundle(folder)
        if sha(folder/'manifest.json')!=row['manifest_sha256']:raise ValueError('Task changed')
        old=self.saved.get(row['manifest_sha256']);self.current=old[0] if old else folder
        report=json.loads((self.current/'report.json').read_text(encoding='utf-8'))
        zoom=self.presentation.get('display_zoom',2)
        if zoom not in (1,2):raise ValueError('Research queue zoom must be1 or2')
        self.photo=tk.PhotoImage(file=os.path.relpath(self.current/'photo_used.png',ROOT)).zoom(zoom,zoom);self.image.configure(image=self.photo)
        self.heading.set(f"{len(self.saved)}/{len(self.queue)} editable roles saved | {report['frame']} — {report['role']} ({self.index+1}/{len(self.queue)})")
        self.warning.set(self.presentation.get('warning','904 source/target remain blocked for wrong-person pairing. '+('1188: sparse native profile detail remains a limitation; mark unjudgeable if needed.' if report['frame']=='1188_0' else 'Measurement: facial skin only. Correction may include visible neck; retained protection overrides.')))
        self.status.set(('Saved: '+old[1]['status']+'. Revisions remain preserved.') if old else 'No saved support review. Open the editor, inspect each mask and confirm both boxes or mark unjudgeable.')

    def navigate(self,delta):
        target=max(0,min(len(self.queue)-1,self.index+delta))
        if target==self.index:return
        self.scan()
        if self.queue[self.index]['manifest_sha256'] not in self.saved:
            if not messagebox.askyesno('Support review not saved',
                'This role has no saved support review. Viewing it or pressing Next does not save it. Move on without saving?',parent=self.root):return
        self.index=target;self.load()
    def first_missing(self):
        self.scan();self.index=next((i for i,r in enumerate(self.queue) if r['manifest_sha256'] not in self.saved),self.index);self.load()
    def edit(self):
        self.editor=RefinementWindow(self.root,self.current,self.worker_python,lambda _:self.load(),research=True,
            annotation_parent=self.annotations_parent,jobs_parent=self.jobs_parent,
            drafts_parent=self.drafts_parent)
