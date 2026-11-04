"""Small Tk desktop app; all inference runs sequentially on one worker."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from tkinter.scrolledtext import ScrolledText
import cv2
from PIL import Image,ImageTk
from src.demo.service import ROOT,DEMO_NOTICE,build_demo_pipeline,example_path,read_photo,analyze_photo,skin_overlay,stage_labels,save_run,run_report


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
        self.run=None;self.path=None;self.future=None;self.photos=[];self.closed=False
        root.title('TrueHue · Python demo')
        width=min(1140,root.winfo_screenwidth()-80);height=min(820,root.winfo_screenheight()-100)
        root.geometry(f'{width}x{height}+20+20');root.minsize(min(850,width),min(640,height))
        root.configure(background='#f3f5f8')
        style=ttk.Style(root);style.theme_use('clam')
        style.configure('TFrame',background='#f3f5f8');style.configure('TLabel',background='#f3f5f8',font=('Segoe UI',10))
        style.configure('Title.TLabel',font=('Segoe UI',23,'bold'));style.configure('TButton',font=('Segoe UI',11),padding=9)
        outer=ttk.Frame(root,padding=20);outer.pack(fill='both',expand=True)
        ttk.Label(outer,text='TrueHue',style='Title.TLabel').pack(anchor='w')
        ttk.Label(outer,text='Choose a photo. Run the demo. Compare the result.').pack(anchor='w',pady=(0,8))
        warning=tk.Label(outer,text=DEMO_NOTICE,
            bg='#fff0cf',fg='#624800',font=('Segoe UI',10),padx=12,pady=9,anchor='w',wraplength=760,justify='left')
        warning.pack(fill='x',pady=(0,12))
        controls=ttk.Frame(outer);controls.pack(fill='x')
        self.choose=ttk.Button(controls,text='1. Choose photo',command=self.choose_photo);self.choose.pack(side='left',padx=(0,8))
        self.example=ttk.Button(controls,text='Try example',command=self.open_example);self.example.pack(side='left',padx=(0,8))
        self.analyze=ttk.Button(controls,text='2. Run demo',command=self.start,state='disabled');self.analyze.pack(side='left',padx=(0,8))
        self.save=ttk.Button(controls,text='3. Save result / report',command=self.save_files,state='disabled');self.save.pack(side='left')
        self.filename=ttk.Label(outer,text='No photo selected',wraplength=1000);self.filename.pack(anchor='w',pady=8)
        self.progress=ttk.Progressbar(outer,mode='indeterminate');self.progress.pack(fill='x')
        self.message=ttk.Label(outer,text='Choose a clear photo with one face.',wraplength=1000,font=('Segoe UI',11,'bold'));self.message.pack(anchor='w',pady=10)
        cards=ttk.Frame(outer);cards.pack(fill='both',expand=True)
        self.images=[]
        for index,title in enumerate(['Photo used by model','Selected skin (green)','Trial correction']):
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

    def show_images(self,values):
        self.photos=[]
        for widget,bgr in zip(self.images,values):
            if bgr is None:widget.configure(image='',text='Not available');continue
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB);image=Image.fromarray(rgb)
            image.thumbnail((256,256),Image.Resampling.LANCZOS)
            photo=ImageTk.PhotoImage(image);self.photos.append(photo)
            widget.configure(image=photo,text='',width=256,height=256)

    def select(self,path):
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
        self.set_details('')
        self.run=None;self.save.configure(state='disabled');self.metrics.configure(text='');self.steps.configure(text='')
        for button in [self.choose,self.example,self.analyze]:button.configure(state='disabled')
        self.show_images([None,None,None]);self.message.configure(text='Working…');self.progress.start(12)
        path=self.path
        def work():
            if self.pipeline is None:self.pipeline,self.provenance=build_demo_pipeline()
            return analyze_photo(path,self.pipeline,self.provenance)
        self.future=self.executor.submit(work);self.root.after(80,self.poll)

    def poll(self):
        if self.closed:return
        if not self.future.done():self.root.after(80,self.poll);return
        self.progress.stop()
        for button in [self.choose,self.example,self.analyze]:button.configure(state='normal')
        future=self.future;self.future=None
        try:self.run=future.result()
        except Exception as error:
            self.run=None;self.show_images([None,None,None]);self.message.configure(text='The demo could not start. Check the technical details or try another photo.')
            self.set_details(str(error));return
        result=self.run.result
        self.show_images([result.image,skin_overlay(self.run),result.corrected if self.run.success else None])
        self.message.configure(text=self.run.message);self.save.configure(state='normal')
        self.steps.configure(text='   →   '.join(('✓ ' if ok else '— ')+name for name,ok in stage_labels(self.run)))
        mst=result.report.get('mst') or {};features=result.report.get('features') or {}
        if mst.get('label') is not None:
            self.metrics.configure(text=f'Estimated MST: {mst["label"]} (trial estimate)    ITA: {features.get("input_ita_degrees",0):.1f}°')
        self.set_details(json.dumps(run_report(self.run),indent=2))

    def set_details(self,text):
        self.details.configure(state='normal');self.details.delete('1.0','end');self.details.insert('1.0',text);self.details.configure(state='disabled')

    def toggle_details(self):
        if self.details_visible.get():self.details_window.deiconify();self.details_window.lift()
        else:self.details_window.withdraw()

    def hide_details(self):
        self.details_visible.set(False);self.details_window.withdraw()

    def save_files(self):
        if self.run is None:return
        path=filedialog.askdirectory(title='Choose where to save the demo files',initialdir=str(ROOT/'outputs'))
        if not path:return
        try:folder=save_run(self.run,path)
        except Exception as error:messagebox.showerror('Could not save',str(error));return
        self.message.configure(text='Saved in '+str(folder))

    def close(self):
        self.closed=True;self.executor.shutdown(wait=False,cancel_futures=True);self.root.destroy()


def launch():
    enable_dpi_awareness()
    root=tk.Tk();DemoApp(root);root.mainloop()
