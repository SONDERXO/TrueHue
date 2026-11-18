"""Local paired-photo reference preference UI; never starts inference/training."""
from pathlib import Path
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from src.demo.photographic_reference_review import sha, verify_bundle, save_preference, latest_preferences

ROOT = Path(__file__).resolve().parents[2]


class PhotographicReferenceWindow:
    def __init__(self, root, package, output_parent=None):
        self.root = root
        self.package = Path(package)
        self.output_parent = Path(output_parent) if output_parent else ROOT / 'outputs/photographic_reference_decisions_v1'
        self.queue = json.loads((self.package / 'queue.json').read_text(encoding='utf-8'))['tasks']
        self.saved = latest_preferences(self.queue, self.output_parent)
        self.index = next((i for i, r in enumerate(self.queue) if r['manifest_sha256'] not in self.saved), 0)
        root.title('TrueHue | Photographic reference appearance')
        ttk.Label(root, text='Does the editor-A image show a suitable target appearance for skin correction?', wraplength=850).pack(padx=14, pady=8)
        ttk.Label(root, text='This reviews appearance only. It does not approve masks, alignment or training.', wraplength=850).pack(padx=14)
        self.heading = tk.StringVar()
        ttk.Label(root, textvariable=self.heading, wraplength=850).pack(pady=5)
        self.issue = tk.StringVar()
        ttk.Label(root, textvariable=self.issue, wraplength=850).pack(padx=14, pady=5)
        panel = ttk.Frame(root)
        panel.pack()
        self.images = [ttk.Label(panel), ttk.Label(panel)]
        for label in self.images:
            label.pack(side='left', padx=5)
        ttk.Label(root, text='LEFT: original source                     RIGHT: editor-A photographic reference').pack(pady=5)
        self.choice = tk.StringVar(value='')
        choices = ttk.Frame(root)
        choices.pack(pady=5)
        for label, value in [('Suitable target', 'suitable'), ('Too bright', 'too_bright'), ('Too dark', 'too_dark'),
                             ('Other concern', 'other_concern'), ('Uncertain', 'uncertain')]:
            ttk.Radiobutton(choices, text=label, variable=self.choice, value=value).pack(side='left', padx=5)
        self.note = tk.StringVar()
        ttk.Entry(root, textvariable=self.note, width=95).pack(padx=14, pady=4)
        buttons = ttk.Frame(root)
        buttons.pack(pady=8)
        ttk.Button(buttons, text='Previous', command=lambda: self.navigate(-1)).pack(side='left', padx=5)
        self.save_button = ttk.Button(buttons, text='Save choice and next', command=self.save)
        self.save_button.pack(side='left', padx=5)
        ttk.Button(buttons, text='Next without saving', command=lambda: self.navigate(1)).pack(side='left', padx=5)
        self.status = tk.StringVar(value='No automatic decisions. Choose the target appearance you want.')
        ttk.Label(root, textvariable=self.status, wraplength=850).pack(padx=14, pady=6)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.load()

    def load(self):
        row = self.queue[self.index]
        if Path(row['folder']).name != row['folder'] or '/' in row['folder'] or '\\' in row['folder']:
            raise ValueError('Local photographic task required')
        self.folder = self.package / row['folder']
        verify_bundle(self.folder)
        if sha(self.folder / 'manifest.json') != row['manifest_sha256']:
            raise ValueError('Photographic task changed')
        self.photos = [tk.PhotoImage(file=os.path.relpath(self.folder / (role + '.png'), ROOT)) for role in ['source', 'target']]
        for label, photo in zip(self.images, self.photos):
            label.configure(image=photo)
        self.saved = latest_preferences(self.queue, self.output_parent)
        previous = self.saved.get(row['manifest_sha256'])
        self.choice.set(previous['choice'] if previous else '')
        self.note.set(previous['note'] if previous else '')
        self.initial = (self.choice.get(), self.note.get())
        self.heading.set(f"{len(self.saved)}/{len(self.queue)} saved | pair {row['frame']} ({self.index+1}/{len(self.queue)})")
        self.issue.set('Known limitation: ' + row['issue'])

    def navigate(self, delta):
        row = self.queue[self.index]
        if row['manifest_sha256'] not in self.saved or (self.choice.get(), self.note.get()) != self.initial:
            if not messagebox.askyesno('Choice not saved', 'Move on without saving the current reference choice?', parent=self.root):
                return
        self.index = max(0, min(len(self.queue)-1, self.index+delta))
        self.load()

    def close(self):
        if (self.choice.get(), self.note.get()) != self.initial:
            if not messagebox.askyesno('Choice not saved', 'Close without saving the current choice?', parent=self.root):
                return
        self.root.destroy()

    def save(self):
        row = self.queue[self.index]
        try:
            save_preference(self.folder, row['manifest_sha256'], self.choice.get(), self.note.get(), self.output_parent)
        except (OSError, ValueError) as error:
            messagebox.showerror('Choice not saved', str(error), parent=self.root)
            return
        self.saved = latest_preferences(self.queue, self.output_parent)
        missing = [i for i, r in enumerate(self.queue) if r['manifest_sha256'] not in self.saved]
        if missing:
            self.index = next((i for i in missing if i > self.index), missing[0])
        self.load()
        self.status.set('All reference choices are saved. Tell Codex they are ready.' if not missing else 'Saved. Review the next photographic reference.')
