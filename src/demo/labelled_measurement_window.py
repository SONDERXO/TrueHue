"""Stdlib research queue UI. Reference labels are intentionally hidden."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import uuid

from src.demo.manual_brush import refine_masks
from src.demo.labelled_measurement_progress import saved_reviews, first_unsaved

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class MeasurementQueueWindow:
    def __init__(self, root, queue_folder, worker_python, *, annotations_parent=None, jobs_parent=None, compact_controls=False):
        self.root = root
        self.queue_folder = Path(queue_folder)
        self.worker_python = str(worker_python)
        self.annotations_parent = Path(annotations_parent) if annotations_parent else ROOT / 'outputs/labelled_measurement_annotations_v1'
        self.jobs_parent = Path(jobs_parent) if jobs_parent else ROOT / 'outputs/labelled_measurement_jobs_v1'
        self.queue = json.loads((self.queue_folder / 'queue.json').read_text(encoding='utf-8'))['tasks']
        self.saved_hashes = saved_reviews(self.queue, self.annotations_parent)
        self.index = first_unsaved(self.queue, self.saved_hashes)
        self.process = None
        self.pending = None
        self.strokes = []
        root.title('TrueHue | Labelled facial measurement review')
        ttk.Label(root, text='Select visible facial skin. Exclude beard, hair, brows, eyes, lips, objects and neck.', wraplength=950).pack(padx=12, pady=8)
        self.heading = tk.StringVar()
        ttk.Label(root, textvariable=self.heading, wraplength=950).pack(padx=12)
        toolbar = ttk.Frame(root)
        toolbar.pack(pady=6)
        self.mode = tk.StringVar(value='remove')
        self.radius = tk.IntVar(value=4)
        for text, value in [('Remove', 'remove'), ('Add skin', 'add'), ('Restore initial selection', 'restore')]:
            ttk.Radiobutton(toolbar, text=text, value=value, variable=self.mode).pack(side='left', padx=4)
        tk.Scale(toolbar, from_=1, to=32, orient='horizontal', label='Brush radius', variable=self.radius, length=140).pack(side='left')
        images = ttk.Frame(root)
        images.pack()
        self.scale = 2 if not compact_controls and root.winfo_screenwidth() >= 1100 and root.winfo_screenheight() >= 850 else 1
        self.original_canvas = tk.Canvas(images, width=256*self.scale, height=256*self.scale)
        self.original_canvas.pack(side='left', padx=5)
        self.canvas = tk.Canvas(images, width=256*self.scale, height=256*self.scale)
        self.canvas.pack(side='left', padx=5)
        self.canvas.bind('<ButtonPress-1>', self.down)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.canvas.bind('<ButtonRelease-1>', self.up)
        ttk.Label(root, text='Left: photograph. Right: selected measurement skin in green. Reference scores are hidden.').pack(pady=4)
        self.note = tk.StringVar()
        ttk.Entry(root, textvariable=self.note, width=90).pack(padx=12, pady=4)
        controls = ttk.Frame(root)
        controls.pack(pady=8)
        self.buttons = []
        for text, callback in [('Previous', lambda: self.navigate(-1)), ('Undo', self.undo), ('Reset edits', self.reset),
                               ('Save reviewed selection', lambda: self.save('reviewed_selection')),
                               ('Save as unjudgeable', lambda: self.save('unjudgeable')), ('Next', lambda: self.navigate(1))]:
            button = ttk.Button(controls, text=text, command=callback)
            button.pack(side='left', padx=3)
            self.buttons.append(button)
        button = ttk.Button(root, text='Go to first unsaved review', command=self.go_to_unsaved)
        button.pack(pady=3)
        self.buttons.append(button)
        if compact_controls:
            controls.pack_configure(before=toolbar)
            button.pack_configure(before=toolbar)
        self.status = tk.StringVar(value='No annotation has been saved in this session.')
        ttk.Label(root, textvariable=self.status, wraplength=950).pack(padx=12, pady=6)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.load()

    def load(self):
        row = self.queue[self.index]
        name = row['task_folder']
        if Path(name).name != name or '/' in name or '\\' in name:
            raise ValueError('Local task folder required')
        self.folder = self.queue_folder / name
        self.manifest_sha = sha(self.folder / 'manifest.json')
        if self.manifest_sha != row['task_manifest_sha256']:
            raise ValueError('Task manifest changed')
        manifest = json.loads((self.folder / 'manifest.json').read_text(encoding='utf-8'))
        if {p.name for p in self.folder.iterdir()} != set(manifest['files']) | {'manifest.json'}:
            raise ValueError('Task membership changed')
        for filename, entry in manifest['files'].items():
            if Path(filename).name != filename or '/' in filename or '\\' in filename or (self.folder / filename).is_symlink():
                raise ValueError('Local regular task files required')
            if sha(self.folder / filename) != entry['sha256']:
                raise ValueError('Task evidence changed')
        self.photo = tk.PhotoImage(file=os.path.relpath(self.folder / 'image.png', ROOT))
        seed = tk.PhotoImage(file=os.path.relpath(self.folder / 'seed.png', ROOT))
        if (self.photo.width(), self.photo.height(), seed.width(), seed.height()) != (256, 256, 256, 256):
            raise ValueError('256px research images required')
        self.rgb = [self.photo.get(x, y) for y in range(256) for x in range(256)]
        self.seed = bytes(255 if seed.get(x, y)[0] else 0 for y in range(256) for x in range(256))
        self.strokes = []
        self.pending = None
        self.note.set('')
        self.dirty = False
        self.original_photo = self.photo.zoom(self.scale, self.scale)
        self.original_canvas.delete('all')
        self.original_canvas.create_image(0, 0, image=self.original_photo, anchor='nw')
        start = 'empty canvas: paint skin manually' if row['seed_origin'] == 'empty_manual_annotation_start' else 'saved automatic selection: check every region'
        self.update_heading(start)
        self.status.set('No saved review for this case. Click Save reviewed selection even if no edits are needed.')
        # Resume the most recent bound annotation, without changing the task seed.
        records = []
        for path in self.annotations_parent.glob('annotation_*/annotation.json'):
            record = json.loads(path.read_text(encoding='utf-8'))
            if record.get('task_manifest_sha256') == self.manifest_sha:
                records.append(path)
        if records:
            latest = max(records, key=lambda p: p.stat().st_mtime_ns)
            edits = json.loads(latest.with_name('edits.json').read_text(encoding='utf-8'))
            saved_manifest = json.loads(latest.with_name('manifest.json').read_text(encoding='utf-8'))
            for filename in ['annotation.json', 'edits.json']:
                if sha(latest.with_name(filename)) != saved_manifest['files'][filename]['sha256']:
                    raise ValueError('Saved annotation changed')
            self.strokes = edits['strokes']
            self.note.set(edits.get('note', ''))
            self.status.set('Loaded saved annotation. New saves preserve all preceding revisions.')
        self.saved_note = self.note.get()
        self.render()

    def update_heading(self, start=None):
        self.saved_hashes = saved_reviews(self.queue, self.annotations_parent)
        row = self.queue[self.index]
        state = 'SAVED REVIEW' if row['task_manifest_sha256'] in self.saved_hashes else 'NOT SAVED'
        self.heading.set(f"{len(self.saved_hashes)}/{len(self.queue)} reviews saved | {row['case_id']} ({self.index+1}/{len(self.queue)}): {state}"
                         + (f' — {start}.' if start else ''))

    def go_to_unsaved(self):
        if self.process is not None:
            return
        self.saved_hashes = saved_reviews(self.queue, self.annotations_parent)
        target = first_unsaved(self.queue, self.saved_hashes)
        if len(self.saved_hashes) == len(self.queue):
            self.status.set('All cases have a saved review. They remain pending scientific admission.')
            return
        if target == self.index:
            self.status.set('This is the first unsaved review. Save your selection or mark it unjudgeable.')
            return
        self.navigate(target-self.index)

    def point(self, event):
        return [max(0, min(255, event.x/self.scale)), max(0, min(255, event.y/self.scale))]

    def down(self, event):
        if self.process is not None:
            return
        self.pending = dict(target='measurement', mode=self.mode.get(), radius=self.radius.get(), unlock=False, points=[self.point(event)])
        self.render()

    def drag(self, event):
        if self.pending is not None:
            self.pending['points'].append(self.point(event))
            self.render()

    def up(self, event):
        if self.pending is not None:
            self.pending['points'].append(self.point(event))
            self.strokes.append(self.pending)
            self.pending = None
            self.dirty = True
            self.render()

    def undo(self):
        if self.strokes:
            self.strokes.pop()
            self.dirty = True
        self.pending = None
        self.render()

    def reset(self):
        self.strokes = []
        self.pending = None
        self.dirty = True
        self.render()

    def render(self):
        empty = bytes(256*256)
        _, mask, _ = refine_masks(empty, self.seed, empty, 256, 256, self.strokes + ([self.pending] if self.pending else []))
        values = bytearray()
        for rgb, selected in zip(self.rgb, mask):
            values.extend((round(.65*rgb[0]), round(.65*rgb[1]+.35*255), round(.65*rgb[2])) if selected else rgb)
        self.overlay = tk.PhotoImage(data=b'P6\n256 256\n255\n'+values, format='PPM').zoom(self.scale, self.scale)
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, image=self.overlay, anchor='nw')

    def navigate(self, delta):
        if self.process is not None:
            return
        if (self.dirty or self.note.get() != self.saved_note) and not messagebox.askyesno('Unsaved edits', 'Discard these unsaved mask edits?', parent=self.root):
            return
        if not self.dirty and self.note.get() == self.saved_note and self.manifest_sha not in self.saved_hashes:
            if not messagebox.askyesno('Review not saved', 'This case has no saved review. Move on without saving it?', parent=self.root):
                return
        self.index = max(0, min(len(self.queue)-1, self.index+delta))
        self.load()

    def close(self):
        if self.process is not None:
            return
        if not (self.dirty or self.note.get() != self.saved_note) or messagebox.askyesno('Unsaved edits', 'Close without saving these mask edits?', parent=self.root):
            self.root.destroy()

    def save(self, review):
        if self.process is not None:
            return
        if self.pending is not None:
            self.strokes.append(self.pending)
            self.pending = None
        job = self.jobs_parent / uuid.uuid4().hex
        job.mkdir(parents=True, exist_ok=False)
        self.payload = job / 'edits.json'
        self.payload.write_text(json.dumps(dict(schema_version='truehue_labelled_measurement_edits_v1',
            task_manifest_sha256=self.manifest_sha, strokes=self.strokes, review=review, note=self.note.get()), indent=2), encoding='utf-8')
        self.log = (job / 'worker.log').open('w', encoding='utf-8')
        try:
            self.process = subprocess.Popen([self.worker_python, str(ROOT / 'scripts/724_save_labelled_measurement.py'),
                '--task', str(self.folder), '--payload', str(self.payload), '--output-parent', str(self.annotations_parent)], cwd=ROOT, stdout=self.log,
                stderr=subprocess.STDOUT, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        except OSError:
            self.log.close()
            raise
        for button in self.buttons:
            button.configure(state='disabled')
        self.status.set('Saving your annotation locally…')
        self.root.after(100, self.poll)

    def poll(self):
        if self.process.poll() is None:
            self.root.after(100, self.poll)
            return
        code = self.process.returncode
        self.process = None
        self.log.close()
        for button in self.buttons:
            button.configure(state='normal')
        if code:
            self.status.set('Not saved. Your edits remain available.')
            messagebox.showerror('Annotation not saved', self.payload.with_name('worker.log').read_text(encoding='utf-8')[-1600:], parent=self.root)
            return
        folder = Path(json.loads(self.payload.with_suffix('.result.json').read_text(encoding='utf-8'))['annotation'])
        record = json.loads((folder / 'annotation.json').read_text(encoding='utf-8'))
        self.dirty = False
        self.saved_note = json.loads(self.payload.read_text(encoding='utf-8')).get('note', '')
        self.update_heading()
        self.status.set('Saved: ' + record['status'] + '. ' + record['reason'] + ' — use Next to continue.')
