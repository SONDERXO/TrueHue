"""Standard-library Tk frontend for installations whose project Python lacks Tk.

The worker always uses the project interpreter and unchanged demo service.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.demo.research_progress import BRIEF_PATH, PROGRESS_TITLE, PROGRESS_TEXT


class CompatDemoApp:
    def __init__(self, root, worker_python):
        self.root = root
        self.worker_python = str(worker_python)
        self.path = None
        self.process = None
        self.export = None
        self.photos = []
        self.job = None
        root.title('TrueHue | Python demo')
        root.geometry('1120x780')
        root.minsize(850, 640)
        outer = ttk.Frame(root, padding=18)
        outer.pack(fill='both', expand=True)
        ttk.Label(outer, text='TrueHue', font=('Segoe UI', 24, 'bold')).pack(anchor='w')
        ttk.Label(outer, text='Current masking | Optional mask refinement | Research prototype').pack(anchor='w', pady=5)
        tk.Label(outer, text='Current face/neck masks with older correction controls. MST uses the older measurement method. Quality is unvalidated.',
                 bg='#fff0cf', fg='#624800', wraplength=950, justify='left', padx=12, pady=10).pack(fill='x', pady=8)
        controls = ttk.Frame(outer)
        controls.pack(fill='x')
        self.choose = ttk.Button(controls, text='1. Choose photo', command=self.choose_photo)
        self.choose.pack(side='left', padx=4)
        self.analyze = ttk.Button(controls, text='2. Run demo', command=self.start, state='disabled')
        self.analyze.pack(side='left', padx=4)
        self.save = ttk.Button(controls, text='3. Save result / report', command=self.save_files, state='disabled')
        self.save.pack(side='left', padx=4)
        self.refine=ttk.Button(controls,text='Refine mask',command=self.refine_mask,state='disabled')
        self.refine.pack(side='left',padx=4)
        options=ttk.Frame(outer);options.pack(fill='x',pady=7)
        self.mask_mode=tk.StringVar(value='current')
        self.glasses=tk.StringVar(value='uncertain')
        self.mask_view=tk.StringVar(value='Correction area')
        self.option_widgets=[]
        for title,variable,values in [('Masking',self.mask_mode,['current','legacy']),
                ('Glasses',self.glasses,['uncertain','clear','opaque']),
                ('Green overlay',self.mask_view,['Correction area','Facial measurement'])]:
            ttk.Label(options,text=title+':').pack(side='left',padx=4)
            choice=ttk.Combobox(options,textvariable=variable,values=values,state='readonly',width=20)
            choice.pack(side='left',padx=4);self.option_widgets.append(choice)
            choice.bind('<<ComboboxSelected>>',lambda event,v=variable:self.refresh_mask() if v is self.mask_view else self.settings_changed())
        self.filename = ttk.Label(outer, text='Use a personal or otherwise permitted single-face photo.', wraplength=1000)
        self.filename.pack(anchor='w', pady=8)
        self.progress = ttk.Progressbar(outer, mode='indeterminate')
        self.progress.pack(fill='x')
        self.message = ttk.Label(outer, text='Choose a photo, then run the demo.', wraplength=1000, font=('Segoe UI', 11, 'bold'))
        self.message.pack(anchor='w', pady=10)
        cards = ttk.Frame(outer)
        cards.pack(fill='both', expand=True)
        self.images = []
        for i, title in enumerate(['Photo used by model', 'Selected area (green)', 'Trial correction']):
            cards.columnconfigure(i, weight=1)
            box = ttk.Frame(cards, padding=6)
            box.grid(row=0, column=i, sticky='nsew')
            ttk.Label(box, text=title, font=('Segoe UI', 11, 'bold')).pack(pady=8)
            label = tk.Label(box, text='No image yet', bg='#e3e8f0', width=32, height=18)
            label.pack(fill='both', expand=True)
            self.images.append(label)
        self.metrics = ttk.Label(outer, text='', wraplength=1000)
        self.metrics.pack(anchor='w', pady=8)
        ttk.Label(outer, text='Clear = transparent prescription lenses; opaque = sunglasses. Uncertain keeps glasses protected. Original photo unchanged.', wraplength=1000).pack(anchor='w', pady=5)
        ttk.Button(outer, text='Show technical report', command=self.show_report).pack(anchor='w')
        root.protocol('WM_DELETE_WINDOW', self.close)

    def clear(self):
        self.refine.configure(state='disabled')
        self.export = None
        self.photos = []
        self.save.configure(state='disabled')
        self.metrics.configure(text='')
        for label in self.images:
            label.configure(image='', text='No image yet', width=32, height=18)

    def settings_changed(self):
        self.clear()
        self.message.configure(text='Settings changed. Run the photo again to update masks and result.')

    def refresh_mask(self):
        if self.export is None:return
        name='facial_measurement.png' if self.mask_view.get()=='Facial measurement' else 'selected_skin.png'
        path=self.export/name
        if not path.exists():path=self.export/'selected_skin.png'
        if not path.exists():return
        photo=tk.PhotoImage(file=os.path.relpath(path,ROOT))
        self.photos[1]=photo
        self.images[1].configure(image=photo,text='',width=256,height=256)

    def select(self, path):
        self.clear()
        self.path = Path(path)
        self.filename.configure(text=self.path.name)
        self.analyze.configure(state='normal')
        self.message.configure(text='Photo selected. Click Run demo to open and process it.')

    def choose_photo(self):
        path = filedialog.askopenfilename(title='Choose one permitted photo', filetypes=[('Photos', '*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff'), ('All files', '*.*')])
        if path:
            self.select(path)

    def open_example(self):
        # Same historical example selection as the unchanged service; no new data.
        try:
            plan = json.loads((ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1/fit_plan.json').read_text(encoding='utf-8'))
            ids = set(plan['folds'][0]['inner_validation_pair_ids'])
            row = next(r for r in plan['rows'] if r['pair_id'] in ids and r['variant'] != 'identity')
            self.select(ROOT/row['input_path'])
        except (OSError, ValueError, KeyError, StopIteration) as error:
            self.message.configure(text='Example unavailable. Choose your own photo.')

    def start(self):
        if self.path is None or self.process is not None:
            return
        self.clear()
        self.job = ROOT/'outputs'/('desktop_meeting_run_'+uuid.uuid4().hex)
        self.job.mkdir(parents=True, exist_ok=False)
        command = [self.worker_python, str(ROOT/'scripts/246_run_python_demo.py'),
                   '--analyze-photo', str(self.path), '--output-dir', str(self.job/'result'),
                   '--masking',self.mask_mode.get(),'--glasses',self.glasses.get()]
        try:
            self.log = (self.job/'worker.log').open('w', encoding='utf-8')
            self.process = subprocess.Popen(command, cwd=ROOT, stdout=self.log, stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        except OSError as error:
            self.log.close()
            self.message.configure(text='Could not start photo processing: '+str(error))
            return
        for button in [self.choose, self.analyze]:
            button.configure(state='disabled')
        for choice in self.option_widgets:choice.configure(state='disabled')
        self.message.configure(text='Processing locally...')
        self.progress.start(12)
        self.root.after(100, self.poll)

    def poll(self):
        if self.process.poll() is None:
            self.root.after(100, self.poll)
            return
        code = self.process.returncode
        self.process = None
        self.log.close()
        self.progress.stop()
        for button in [self.choose, self.analyze]:
            button.configure(state='normal')
        for choice in self.option_widgets:choice.configure(state='readonly')
        try:
            if code != 0:
                raise RuntimeError('Photo processing failed. See technical report for details.')
            summary = json.loads((self.job/'result/desktop_result.json').read_text(encoding='utf-8'))
            folder = Path(summary['export'])
            report = json.loads((folder/'report.json').read_text(encoding='utf-8'))
            for label, name in zip(self.images, ['photo_used.png', 'selected_skin.png', 'experimental_correction.png']):
                path = folder/name
                if not path.exists():
                    label.configure(image='', text='Not available')
                    continue
                photo = tk.PhotoImage(file=os.path.relpath(path, ROOT))
                if max(photo.width(), photo.height()) > 280:
                    photo = photo.subsample((max(photo.width(), photo.height())+279)//280)
                self.photos.append(photo)
                label.configure(image=photo, text='', width=256, height=256)
            self.export = folder
            self.refresh_mask()
            self.message.configure(text=summary['message'])
            mst = report.get('mst') or {}
            features = report.get('display_features') or report.get('features') or {}
            if mst.get('label') is not None:
                prefix='Older-mask MST' if report.get('masking_mode')=='current' else 'Estimated MST'
                self.metrics.configure(text=f"{prefix}: {mst['label']} (unvalidated) | Mask ITA: {features.get('input_ita_degrees', 0):.1f} degrees")
            self.save.configure(state='normal')
            self.refine.configure(state='normal' if report.get('status')=='development_experimental_mst' and report.get('masking_mode')=='current' else 'disabled')
        except (OSError, ValueError, KeyError, RuntimeError, tk.TclError) as error:
            self.clear()
            self.message.configure(text=str(error))

    def save_files(self):
        if self.export is None:
            return
        parent = filedialog.askdirectory(title='Choose where to save the demo files')
        if not parent:
            return
        folder = Path(parent)/('truehue_demo_'+uuid.uuid4().hex[:12])
        try:
            shutil.copytree(self.export, folder)
            self.message.configure(text='Saved in '+str(folder))
        except OSError as error:
            messagebox.showerror('Could not save', str(error))

    def refine_mask(self):
        if self.export is None or self.process is not None:return
        from src.demo.refinement_window import open_refinement
        def applied(folder):
            self.export=Path(folder);self.photos=[]
            report=json.loads((self.export/'report.json').read_text(encoding='utf-8'))
            for widget,name in zip(self.images,['photo_used.png','selected_skin.png','experimental_correction.png']):
                photo=tk.PhotoImage(file=os.path.relpath(self.export/name,ROOT));self.photos.append(photo)
                widget.configure(image=photo,text='',width=256,height=256)
            self.refresh_mask();self.message.configure(text='Mask refined by you. Older controls and MST remain experimental.')
            self.metrics.configure(text=f'Refined mask ITA: {report["display_features"]["input_ita_degrees"]:.1f} degrees | Older-mask MST retained')
        open_refinement(self.root,self.export,self.worker_python,applied)

    def text_window(self, title, content):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry('900x650')
        text = ScrolledText(window, wrap='word', font=('Consolas', 10), padx=16, pady=12)
        text.pack(fill='both', expand=True)
        text.insert('1.0', content)
        text.configure(state='disabled')
        return window

    def show_progress(self):
        import os
        window = self.text_window(PROGRESS_TITLE, PROGRESS_TEXT)
        ttk.Button(window, text='Open full adviser briefing', command=lambda: os.startfile(str(ROOT/BRIEF_PATH))).pack(pady=8)

    def show_report(self):
        if self.export:
            content = (self.export/'report.json').read_text(encoding='utf-8')
        elif self.job and (self.job/'worker.log').exists():
            content = (self.job/'worker.log').read_text(encoding='utf-8', errors='replace')
        else:
            content = 'No photo has been processed yet.'
        self.text_window('TrueHue technical report', content)

    def close(self):
        if self.process is not None:
            self.process.terminate()
            self.process.wait(timeout=10)
            self.log.close()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker-python', required=True, type=Path)
    args = parser.parse_args()
    root = tk.Tk()
    CompatDemoApp(root, args.worker_python)
    root.mainloop()


if __name__ == '__main__':
    main()
