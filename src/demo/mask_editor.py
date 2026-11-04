"""Local exclusion-brush editor; cannot add pixels outside the preferred mask."""
import base64
import hashlib
import json
from pathlib import Path
import uuid
import cv2
import numpy as np
from src.skin_masking.facial_hair_exclusion import paint_exclusions,apply_exclusions


class MaskEditSession:
    def __init__(self,image,base_mask,*,suggestion=None):
        if not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3:
            raise ValueError('uint8 BGR image required')
        apply_exclusions(base_mask,np.zeros(image.shape[:2],bool))
        self.image=image.copy();self.base_mask=base_mask.copy();self.strokes=[]
        self.suggestion=None if suggestion is None else np.asarray(suggestion).copy()
        if self.suggestion is not None and (self.suggestion.dtype!=bool or self.suggestion.shape!=base_mask.shape):
            raise ValueError('Matching boolean suggestion required')
        self.use_suggestion=False

    def current(self,*,pending=None):
        if self.use_suggestion and self.suggestion is None:raise ValueError('No auxiliary suggestion available')
        initial=self.suggestion if self.use_suggestion else None
        strokes=self.strokes+([pending] if pending is not None else [])
        veto=paint_exclusions(self.base_mask.shape,strokes,initial=initial)
        mask,alpha=apply_exclusions(self.base_mask,veto)
        return mask,alpha,veto

    def add(self,stroke):
        self.current(pending=stroke)
        self.strokes.append(json.loads(json.dumps(stroke)))

    def undo(self):
        if self.strokes:self.strokes.pop()

    def reset(self):
        self.strokes.clear();self.use_suggestion=False

    def save(self,preview_folder):
        parent=Path(preview_folder)
        base_path=parent/'mask.png';image_path=parent/'input.png'
        stored_mask=cv2.imread(str(base_path),0);stored_image=cv2.imread(str(image_path))
        if not np.array_equal(stored_mask,self.base_mask) or not np.array_equal(stored_image,self.image):
            raise ValueError('Original preview evidence changed; save refused')
        mask,alpha,veto=self.current();folder=parent/'edits'/('edit_'+uuid.uuid4().hex[:12])
        folder.mkdir(parents=True)
        a=.5*alpha.astype(float)/255
        overlay=np.rint(self.image*(1-a[:,:,None])+np.array([0,255,0])*a[:,:,None]).astype(np.uint8)
        for name,array in [('mask.png',mask),('alpha.png',alpha),('exclusion.png',veto.astype(np.uint8)*255),('overlay.png',overlay)]:
            if not cv2.imwrite(str(folder/name),array):raise OSError(folder/name)
        payload=dict(schema_version='truehue_manual_exclusion_v1',
            input_sha256=hashlib.sha256(image_path.read_bytes()).hexdigest(),
            base_mask_sha256=hashlib.sha256(base_path.read_bytes()).hexdigest(),
            base_input_path=str(image_path.resolve()),base_mask_path=str(base_path.resolve()),
            strokes=self.strokes,auxiliary_suggestion_enabled=self.use_suggestion,
            suggestion_mask_sha256=None if not self.use_suggestion else hashlib.sha256(self.suggestion.astype(np.uint8).tobytes()).hexdigest(),
            removed_selected_pixels=int(((self.base_mask>0)&(mask==0)).sum()),
            added_pixels=0,annotation_method='explicit_user_exclusion_brush',
            automatic_beard_accuracy_claim=False,training_admitted=False,ITA_MST_calls=0,
            output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()})
        if self.use_suggestion:
            cv2.imwrite(str(folder/'suggestion_used.png'),self.suggestion.astype(np.uint8)*255)
            payload['output_sha256']['suggestion_used.png']=hashlib.sha256((folder/'suggestion_used.png').read_bytes()).hexdigest()
        (folder/'edit.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
        return folder


def open_mask_editor(preview_folder,*,suggestion=None):
    import tkinter as tk
    from tkinter import messagebox
    folder=Path(preview_folder)
    image=cv2.imread(str(folder/'input.png'));base=cv2.imread(str(folder/'mask.png'),0)
    session=MaskEditSession(image,base,suggestion=suggestion)
    root=tk.Tk();root.title('TrueHue · facial-hair exclusion brush')
    root.configure(bg='#151923')
    tk.Label(root,text='Brush over beard or moustache to exclude it. Your preferred full-face mask stays preserved.',
        bg='#151923',fg='white',wraplength=720,pady=12).pack()
    canvas=tk.Canvas(root,width=image.shape[1]*2,height=image.shape[0]*2,highlightthickness=0)
    canvas.pack(padx=16)
    toolbar=tk.Frame(root);toolbar.pack(fill='x',padx=16,pady=12)
    mode=tk.StringVar(value='exclude');radius=tk.IntVar(value=4);marks=tk.BooleanVar(value=True);automatic=tk.BooleanVar(value=False)
    tk.Radiobutton(toolbar,text='Exclude hair',variable=mode,value='exclude').pack(side='left')
    tk.Radiobutton(toolbar,text='Restore original skin',variable=mode,value='restore').pack(side='left')
    tk.Scale(toolbar,label='Brush size',from_=1,to=24,orient='horizontal',variable=radius,length=150).pack(side='left')
    status=tk.StringVar(value='Green: selected skin. Red: excluded region. Undo reverses the last stroke.')
    pending=None
    def render():
        mask,alpha,veto=session.current(pending=pending)
        a=.5*alpha.astype(float)/255
        shown=np.rint(image*(1-a[:,:,None])+np.array([0,255,0])*a[:,:,None]).astype(np.uint8)
        if marks.get():
            removed=(base>0)&(mask==0);shown[removed]=np.rint(.5*image[removed]+.5*np.array([0,0,255])).astype(np.uint8)
        shown=cv2.resize(shown,(image.shape[1]*2,image.shape[0]*2),interpolation=cv2.INTER_NEAREST)
        ok,encoded=cv2.imencode('.png',shown);assert ok
        canvas.photo=tk.PhotoImage(data=base64.b64encode(encoded).decode('ascii'),format='png')
        canvas.delete('all');canvas.create_image(0,0,image=canvas.photo,anchor='nw')
    def point(event):return [float(np.clip(event.x/2,0,image.shape[1]-1)),float(np.clip(event.y/2,0,image.shape[0]-1))]
    def down(event):
        nonlocal pending
        pending=dict(mode=mode.get(),radius=radius.get(),points=[point(event)]);canvas.grab_set();render()
    def drag(event):
        if pending is not None:pending['points'].append(point(event));render()
    def up(event):
        nonlocal pending
        if pending is not None:
            pending['points'].append(point(event));session.add(pending);pending=None;canvas.grab_release();render()
    canvas.bind('<ButtonPress-1>',down);canvas.bind('<B1-Motion>',drag);canvas.bind('<ButtonRelease-1>',up)
    def undo():session.undo();render()
    def reset():session.reset();automatic.set(False);render()
    def save():
        try:
            saved=session.save(folder);status.set('Saved: '+str(saved))
        except Exception as error:messagebox.showerror('Could not save mask',str(error))
    def toggle():session.use_suggestion=automatic.get();render()
    tk.Button(toolbar,text='Undo',command=undo).pack(side='left',padx=5)
    tk.Button(toolbar,text='Reset',command=reset).pack(side='left',padx=5)
    tk.Button(toolbar,text='Save edited mask',command=save).pack(side='left',padx=5)
    options=tk.Frame(root);options.pack(fill='x',padx=16)
    tk.Checkbutton(options,text='Show excluded areas in red',variable=marks,command=render).pack(side='left')
    if suggestion is not None:
        tk.Checkbutton(options,text='Preview experimental exclusion suggestion — inspect skin loss',variable=automatic,command=toggle).pack(side='left')
    tk.Label(root,textvariable=status,wraplength=760,padx=16,pady=12).pack(fill='x')
    root.bind('<Control-z>',lambda event:undo());render();root.mainloop()
