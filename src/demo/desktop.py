"""Small Tk desktop app; all inference runs sequentially on one worker."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from tkinter.scrolledtext import ScrolledText
import cv2
from PIL import Image,ImageTk
from src.demo.service import ROOT,DEMO_NOTICE,build_demo_pipeline,example_path,read_photo,analyze_photo,skin_overlay,measurement_overlay,stage_labels,save_run,run_report
from src.demo.research_progress import BRIEF_PATH,PROGRESS_TITLE,PROGRESS_TEXT


def enable_dpi_awareness():
    # Avoid Windows enlarging the whole demo beyond a laptop's screen.
    import sys
    if sys.platform=='win32':
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except (AttributeError,OSError):pass


class DemoApp:
    def __init__(self,root):
        self.root=root;self.executor=ThreadPoolExecutor(max_workers=1);self.pipeline=None;self.provenance=None
        self.run=None;self.path=None;self.future=None;self.photos=[];self.closed=False;self.refinement_export=None
        root.title('TrueHue · Python demo')
        width=min(1140,root.winfo_screenwidth()-80);height=min(820,root.winfo_screenheight()-100)
        root.geometry(f'{width}x{height}+20+20');root.minsize(min(850,width),min(640,height))
        root.configure(background='#f3f5f8')
        style=ttk.Style(root);style.theme_use('clam')
        style.configure('TFrame',background='#f3f5f8');style.configure('TLabel',background='#f3f5f8',font=('Segoe UI',10))
        style.configure('Title.TLabel',font=('Segoe UI',23,'bold'));style.configure('TButton',font=('Segoe UI',11),padding=9)
        outer=ttk.Frame(root,padding=20);outer.pack(fill='both',expand=True)
        ttk.Label(outer,text='TrueHue',style='Title.TLabel').pack(anchor='w')
        meeting=ttk.Frame(outer);meeting.pack(fill='x',pady=(0,6))
        ttk.Label(meeting,text='Current masks | Optional mask refinement | Older experimental controls').pack(side='left')
        ttk.Label(outer,text='Choose a photo. Run the demo. Refine the mask if needed. Compare the result.').pack(anchor='w',pady=(0,8))
        warning=tk.Label(outer,text=DEMO_NOTICE,
            bg='#fff0cf',fg='#624800',font=('Segoe UI',10),padx=12,pady=9,anchor='w',wraplength=760,justify='left')
        warning.pack(fill='x',pady=(0,12))
        controls=ttk.Frame(outer);controls.pack(fill='x')
        self.choose=ttk.Button(controls,text='1. Choose photo',command=self.choose_photo);self.choose.pack(side='left',padx=(0,8))
        self.analyze=ttk.Button(controls,text='2. Run demo',command=self.start,state='disabled');self.analyze.pack(side='left',padx=(0,8))
        self.save=ttk.Button(controls,text='3. Save result / report',command=self.save_files,state='disabled');self.save.pack(side='left')
        self.refine=ttk.Button(controls,text='Refine mask',command=self.refine_mask,state='disabled');self.refine.pack(side='left',padx=8)
        options=ttk.Frame(outer);options.pack(fill='x',pady=6)
        self.mask_mode=tk.StringVar(value='current');self.glasses=tk.StringVar(value='uncertain');self.mask_view=tk.StringVar(value='Correction area')
        self.option_widgets=[]
        for title,variable,values in [('Masking',self.mask_mode,['current','legacy']),('Glasses',self.glasses,['uncertain','clear','opaque']),('Overlay',self.mask_view,['Correction area','Facial measurement'])]:
            ttk.Label(options,text=title+':').pack(side='left',padx=3)
            choice=ttk.Combobox(options,textvariable=variable,values=values,state='readonly',width=19)
            choice.pack(side='left',padx=3);self.option_widgets.append(choice)
            choice.bind('<<ComboboxSelected>>',lambda event,v=variable:self.refresh_mask() if v is self.mask_view else self.settings_changed())
        self.filename=ttk.Label(outer,text='No photo selected',wraplength=1000);self.filename.pack(anchor='w',pady=8)
        self.progress=ttk.Progressbar(outer,mode='indeterminate');self.progress.pack(fill='x')
        self.message=ttk.Label(outer,text='Choose a clear photo with one face.',wraplength=1000,font=('Segoe UI',11,'bold'));self.message.pack(anchor='w',pady=10)
        cards=ttk.Frame(outer);cards.pack(fill='both',expand=True)
        self.images=[]
        for index,title in enumerate(['Photo used by model','Selected area (green)','Trial correction']):
            cards.columnconfigure(index,weight=1)
            box=ttk.Frame(cards,padding=5);box.grid(row=0,column=index,sticky='nsew')
            ttk.Label(box,text=title,font=('Segoe UI',11,'bold')).pack(pady=5)
            image=tk.Label(box,text='No image yet',bg='#e3e8f0',fg='#475569',width=32,height=18)
            image.pack(fill='both',expand=True);self.images.append(image)
        ttk.Label(outer,text='The demo uses a small square copy. Your original photo is not changed. Everything stays on this computer.').pack(anchor='w',pady=8)
        self.steps=ttk.Label(outer,text='');self.steps.pack(anchor='w')
        self.metrics=ttk.Label(outer,text='');self.metrics.pack(anchor='w',pady=5)
        self.details_visible=tk.BooleanVar(value=False)
        ttk.Checkbutton(outer,text='Show technical details',variable=self.details_visible,command=self.toggle_details).pack(anchor='w')
        self.details_window=tk.Toplevel(root);self.details_window.title('TrueHue · technical report')
        self.details_window.geometry('800x500');self.details_window.withdraw()
        self.details=ScrolledText(self.details_window,wrap='word',font=('Consolas',9),state='disabled')
        self.details.pack(fill='both',expand=True)
        self.details_window.protocol('WM_DELETE_WINDOW',self.hide_details)
        root.protocol('WM_DELETE_WINDOW',self.close)

    def settings_changed(self):
        self.refinement_export=None;self.refine.configure(state='disabled')
        self.pipeline=None;self.run=None;self.save.configure(state='disabled')
        self.show_images([None,None,None]);self.metrics.configure(text='');self.steps.configure(text='')
        self.message.configure(text='Settings changed. Run the photo again.')

    def refresh_mask(self):
        if self.run is None:return
        result=self.run.result
        overlay=measurement_overlay(self.run) if self.mask_view.get()=='Facial measurement' else skin_overlay(self.run)
        self.show_images([result.image,overlay,result.corrected if self.run.success else None])

    def show_progress(self):
        window=tk.Toplevel(self.root);window.title(PROGRESS_TITLE)
        window.geometry('900x650')
        text=ScrolledText(window,wrap='word',font=('Consolas',10),padx=16,pady=12)
        text.pack(fill='both',expand=True);text.insert('1.0',PROGRESS_TEXT);text.configure(state='disabled')
        ttk.Button(window,text='Open full adviser briefing',command=self.open_briefing).pack(pady=8)

    def open_briefing(self):
        import os
        try:os.startfile(str(ROOT/BRIEF_PATH))
        except OSError as error:messagebox.showerror('Could not open briefing',str(error))

    def show_images(self,values):
        self.photos=[]
        for widget,bgr in zip(self.images,values):
            if bgr is None:widget.configure(image='',text='Not available');continue
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB);image=Image.fromarray(rgb)
            image.thumbnail((256,256),Image.Resampling.LANCZOS)
            photo=ImageTk.PhotoImage(image);self.photos.append(photo)
            widget.configure(image=photo,text='',width=256,height=256)

    def select(self,path):
        self.refinement_export=None;self.refine.configure(state='disabled')
        try:image,_=read_photo(path)
        except Exception as error:
            self.run=None;self.path=None;self.analyze.configure(state='disabled');self.save.configure(state='disabled')
            self.show_images([None,None,None]);self.metrics.configure(text='');self.steps.configure(text='')
            self.filename.configure(text='No photo selected');self.set_details(str(error))
            self.message.configure(text='This photo could not be opened. Choose a JPG or PNG.');return
        self.path=Path(path);self.run=None;self.filename.configure(text=self.path.name)
        self.save.configure(state='disabled');self.analyze.configure(state='normal');self.metrics.configure(text='');self.steps.configure(text='')
        self.show_images([cv2.resize(image,(256,256)),None,None]);self.message.configure(text='Photo ready. Click Run demo.')
        self.set_details('')

    def choose_photo(self):
        path=filedialog.askopenfilename(title='Choose one photo',filetypes=[('Photos','*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff'),('All files','*.*')])
        if path:self.select(path)

    def open_example(self):
        try:self.select(example_path())
        except Exception:self.message.configure(text='The example is unavailable. You can choose your own photo.')

    def start(self):
        if self.path is None or self.future is not None:return
        self.refinement_export=None;self.refine.configure(state='disabled')
        self.set_details('')
        self.run=None;self.save.configure(state='disabled');self.metrics.configure(text='');self.steps.configure(text='')
        for button in [self.choose,self.analyze]:button.configure(state='disabled')
        for choice in self.option_widgets:choice.configure(state='disabled')
        self.show_images([None,None,None]);self.message.configure(text='Working…');self.progress.start(12)
        path=self.path
        masking,glasses=self.mask_mode.get(),self.glasses.get()
        def work():
            if self.pipeline is None:self.pipeline,self.provenance=build_demo_pipeline(masking,glasses)
            return analyze_photo(path,self.pipeline,self.provenance)
        self.future=self.executor.submit(work);self.root.after(80,self.poll)

    def poll(self):
        if self.closed:return
        if not self.future.done():self.root.after(80,self.poll);return
        self.progress.stop()
        for button in [self.choose,self.analyze]:button.configure(state='normal')
        for choice in self.option_widgets:choice.configure(state='readonly')
        future=self.future;self.future=None
        try:self.run=future.result()
        except Exception as error:
            self.run=None;self.show_images([None,None,None]);self.message.configure(text='The demo could not start. Check the technical details or try another photo.')
            self.set_details(str(error));return
        result=self.run.result
        self.refine.configure(state='normal' if self.run.success and result.report.get('masking_mode')=='current' else 'disabled')
        self.refresh_mask()
        self.message.configure(text=self.run.message);self.save.configure(state='normal')
        self.steps.configure(text='   →   '.join(('✓ ' if ok else '— ')+name for name,ok in stage_labels(self.run)))
        mst=result.report.get('mst') or {};features=result.report.get('display_features') or result.report.get('features') or {}
        if mst.get('label') is not None:
            prefix='Older-mask MST' if result.report.get('masking_mode')=='current' else 'Estimated MST'
            self.metrics.configure(text=f'{prefix}: {mst["label"]} (trial estimate)    Mask ITA: {features.get("input_ita_degrees",0):.1f}°')
        self.set_details(json.dumps(run_report(self.run),indent=2))

    def set_details(self,text):
        self.details.configure(state='normal');self.details.delete('1.0','end');self.details.insert('1.0',text);self.details.configure(state='disabled')

    def refine_mask(self):
        if self.run is None or not self.run.success or self.future is not None:return
        import sys
        from src.demo.refinement_window import open_refinement
        from src.demo.service import load_refined_run
        if self.refinement_export is None:self.refinement_export=save_run(self.run,ROOT/'outputs/manual_editor_sessions')
        def applied(folder):
            self.run=load_refined_run(folder);self.refinement_export=folder
            self.refresh_mask();self.message.configure(text=self.run.message)
            features=self.run.result.report['display_features']
            self.metrics.configure(text=f'Refined mask ITA: {features["input_ita_degrees"]:.1f}° | Older-mask MST and controls retained')
            self.set_details(json.dumps(run_report(self.run),indent=2))
        open_refinement(self.root,self.refinement_export,sys.executable,applied)

    def toggle_details(self):
        if self.details_visible.get():self.details_window.deiconify();self.details_window.lift()
        else:self.details_window.withdraw()

    def hide_details(self):
        self.details_visible.set(False);self.details_window.withdraw()

    def save_files(self):
        if self.run is None:return
        path=filedialog.askdirectory(title='Choose where to save the demo files',initialdir=str(ROOT/'outputs'))
        if not path:return
        try:
            if self.refinement_export is not None and self.run.result.report.get('manual_refinement'):
                import shutil,uuid
                folder=Path(path)/('truehue_demo_'+uuid.uuid4().hex[:12]);shutil.copytree(self.refinement_export,folder)
            else:folder=save_run(self.run,path)
        except Exception as error:messagebox.showerror('Could not save',str(error));return
        self.message.configure(text='Saved in '+str(folder))

    def close(self):
        self.closed=True;self.executor.shutdown(wait=False,cancel_futures=True);self.root.destroy()


def launch():
    enable_dpi_awareness()
    root=tk.Tk();DemoApp(root);root.mainloop()
