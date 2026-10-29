"""Minimal local desktop. Kdenlive owns playback and timeline editing."""
from dataclasses import replace
from fractions import Fraction
import os
from pathlib import Path
from queue import Empty
import shutil
import tkinter as tk
from tkinter import filedialog, ttk

from .application import RunOptions, read_record
from .contracts import dumps, loads
from .desktop_workflow import (DesktopJob, Worker, absolute_mapping, discover_mapping,
    error_message, open_edit_copy, prepare_job, restored_request, review_run)
from .intake import MappingManifest


MODES = {'Inspect inputs': 'inspect', 'Analyze audio': 'analyze',
         'Preview edits': 'plan', 'Create editable project': 'run'}
RECORDS = (('analysis', 'Reviewed analysis'), ('request', 'Global gap approvals'),
           ('picture', 'Recorded picture observations'), ('picture_request', 'Picture review request'),
           ('cleanup_request', 'Idle cleanup approvals'))


def review_seconds(value):
    if value is None:
        return 'removed / no output time'
    return str(Fraction(value['numerator'], value['denominator'])) if isinstance(value, dict) else str(value)


class Desktop:
    def __init__(self, root):
        self.root = root
        root.title('InterviewAutoEditor - local desktop')
        root.geometry(f'{min(1080, root.winfo_screenwidth()-80)}x{min(820, root.winfo_screenheight()-120)}')
        root.minsize(850, 690)
        self.worker = Worker()
        self.mapping = None
        self.confirmed = tk.BooleanVar(value=False)
        self.experimental = tk.BooleanVar(value=False)
        self.project = tk.StringVar()
        self.output = tk.StringVar()
        self.preset = tk.StringVar(value='tight')
        self.mode = tk.StringVar(value='Create editable project')
        self.status = tk.StringVar(value='Choose an unedited starter, confirm participants, then select a new private run folder.')
        self.records = {key: tk.StringVar() for key, label in RECORDS}
        self.assets = {key: tk.StringVar(value=os.environ.get(env, '') or (shutil.which(tool) if tool else '') or '')
            for key, env, tool in (('ffprobe', 'IAE_FFPROBE', 'ffprobe'), ('ffmpeg', 'IAE_FFMPEG', 'ffmpeg'),
                ('speech_model', 'IAE_S04_MODEL', ''), ('reaction_model', 'IAE_S05_MODEL', ''),
                ('cache', 'IAE_CACHE', ''), ('kdenlive', 'IAE_KDENLIVE', 'kdenlive'))}
        self.draft = None
        self.run_directory = None
        self.analysis = self.request = None
        self.complete = None
        self.build()
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.poll_timer = root.after(80, self.poll)

    def button(self, parent, label, command):
        widget = ttk.Button(parent, text=label, command=command)
        widget.pack(side='left', padx=(0, 7), pady=3)
        return widget

    def build(self):
        self.form = ttk.Frame(self.root, padding=18)
        self.form.pack(fill='both', expand=True)
        ttk.Label(self.form, text='InterviewAutoEditor', font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        ttk.Label(self.form, text='Local processing  |  EXPERIMENTAL - Kdenlive 26.08.2 rev. d4e87e4').pack(anchor='w', pady=(2, 12))
        row = ttk.Frame(self.form); row.pack(fill='x')
        self.button(row, 'Choose starter project', self.choose_project)
        if (Path(__file__).resolve().parents[1] / 'tests/fixtures/s09-picture-26.08.2/before.kdenlive').is_file():
            self.button(row, 'Load synthetic example', self.load_example)
        ttk.Entry(row, textvariable=self.project, state='readonly').pack(side='left', fill='x', expand=True)
        row = ttk.Frame(self.form); row.pack(fill='x', pady=(8, 0))
        ttk.Label(row, text='Participants - verify every file and name; shared microphone labels stay together').pack(side='left')
        self.mapping_tree = self.tree(self.form, ('file', 'id', 'name', 'labels'), ('Audio file', 'Source ID', 'Track name', 'Channel labels'), 3)
        self.mapping_tree.bind('<Double-1>', lambda e: self.edit_participant())
        row = ttk.Frame(self.form); row.pack(fill='x')
        self.button(row, 'Load mapping', self.load_mapping)
        self.button(row, 'Edit selected participant', self.edit_participant)
        ttk.Checkbutton(row, text='I confirm this file-to-participant mapping', variable=self.confirmed).pack(side='left')
        row = ttk.Frame(self.form); row.pack(fill='x', pady=(8, 3))
        ttk.Label(row, text='Pacing').pack(side='left', padx=(0, 8))
        for value in ('tight', 'gentle'):
            ttk.Radiobutton(row, text=value.title(), value=value, variable=self.preset).pack(side='left', padx=(0, 14))
        ttk.Combobox(row, textvariable=self.mode, values=list(MODES), state='readonly', width=25).pack(side='left')
        self.button(row, 'Reviewed records', self.reviewed_records)
        self.button(row, 'Local setup', self.local_setup)
        self.record_status = ttk.Label(self.form, text='No reviewed records selected. Fresh analysis retains origin/tail review and cannot certify export.')
        self.record_status.pack(anchor='w')
        row = ttk.Frame(self.form); row.pack(fill='x', pady=(8, 2))
        self.button(row, 'New private run folder', self.choose_output)
        ttk.Entry(row, textvariable=self.output).pack(side='left', fill='x', expand=True)
        ttk.Checkbutton(self.form, text='Allow experimental export to a new copy; original source project/media remain unchanged', variable=self.experimental).pack(anchor='w')
        row = ttk.Frame(self.form); row.pack(fill='x', pady=(8, 4))
        self.button(row, 'Start', self.start)
        self.button(row, 'Resume saved job', self.resume)
        self.button(row, 'Review saved run', self.load_run)
        self.open_button = self.button(row, 'Open copy in Kdenlive', self.open_kdenlive)
        self.open_button.configure(state='disabled')
        ttk.Label(self.form, text='Review source / output seconds - exact fractions; removed locations have no output time').pack(anchor='w', pady=(10, 0))
        self.review_tree = self.tree(self.form, ('kind', 'source', 'output', 'reason'), ('Review', 'Source seconds', 'Output seconds', 'Reason'), 5)
        self.review_tree.bind('<Double-1>', self.review_detail)
        row = ttk.Frame(self.form); row.pack(fill='x')
        self.button(row, 'Keep / Restore source interval', self.restore)
        self.button(row, 'Discard pending restoration', self.clear_draft)
        self.restore_status = ttk.Label(self.form, text='Keep retains shared time; Restore audible also restores unity on all microphones. Recreate into a NEW run.')
        self.restore_status.pack(anchor='w')
        ttk.Label(self.form, text='Whole runs, mappings, reports, caches and review records are PRIVATE for real interviews.\nSave manual Kdenlive edits in the opened copy. Full originals remain in its bin.', wraplength=980).pack(anchor='w', pady=(8, 3))
        footer = ttk.Frame(self.root, padding=(18, 6, 18, 16)); footer.pack(side='bottom', before=self.form, fill='x')
        self.progress = ttk.Progressbar(footer, mode='indeterminate'); self.progress.pack(fill='x')
        ttk.Label(footer, textvariable=self.status, wraplength=980).pack(side='left', fill='x', expand=True, pady=7)
        self.cancel_button = ttk.Button(footer, text='Cancel', command=self.cancel, state='disabled'); self.cancel_button.pack(side='right')

    def tree(self, parent, columns, labels, height):
        frame = ttk.Frame(parent); frame.pack(fill='both', expand=True, pady=4)
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=height, selectmode='browse')
        for col, label in zip(columns, labels):
            tree.heading(col, text=label); tree.column(col, width=180, minwidth=90)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side='left', fill='both', expand=True); scroll.pack(side='right', fill='y')
        return tree

    def guard(self, action):
        try:
            return action()
        except Exception as exc:
            self.status.set(error_message(exc))
            return None

    def busy(self, value):
        def visit(parent):
            for child in parent.winfo_children():
                if isinstance(child, (ttk.Button, ttk.Checkbutton, ttk.Radiobutton, ttk.Combobox, ttk.Entry)):
                    if value:
                        child._previous_state = str(child.cget('state'))
                        child.configure(state='disabled')
                    else:
                        child.configure(state=getattr(child, '_previous_state', 'normal'))
                visit(child)
        visit(self.form)
        self.mapping_tree.unbind('<Double-1>') if value else self.mapping_tree.bind('<Double-1>', lambda e: self.edit_participant())
        self.open_button.configure(state='disabled' if value or not self.can_open() else 'normal')
        self.cancel_button.configure(state='normal' if value else 'disabled')
        self.progress.start(15) if value else self.progress.stop()

    def launch(self, task, complete):
        self.complete = complete
        self.busy(True)
        self.status.set('Preparing local inputs...')
        self.worker.start(task)

    def poll(self):
        try:
            while True:
                kind, value = self.worker.events.get_nowait()
                if kind == 'progress':
                    self.status.set(value)
                else:
                    self.busy(False)
                    complete, self.complete = self.complete, None
                    if kind == 'done':
                        self.guard(lambda: complete(value))
                    else:
                        self.status.set(value)
        except Empty:
            pass
        self.poll_timer = self.root.after(80, self.poll)

    def cancel(self):
        self.worker.cancel.set()
        self.status.set('Cancelling safely; waiting for the current bounded operation...')

    def close(self):
        if self.worker.busy:
            self.cancel()
            self.status.set('Cancellation requested. Wait for it to finish, then close; recovery evidence is preserved.')
        else:
            self.root.after_cancel(self.poll_timer)
            self.complete = None
            self.root.destroy()

    def choose_project(self):
        path = filedialog.askopenfilename(parent=self.root, title='Choose unedited starter', filetypes=[('Kdenlive project', '*.kdenlive')])
        if path:
            def loaded(mapping):
                self.project.set(path); self.mapping = mapping; self.confirmed.set(False)
                self.draft = self.analysis = self.request = self.run_directory = None
                for v in self.records.values(): v.set('')
                self.update_record_status(); self.show_mapping(); self.review_tree.delete(*self.review_tree.get_children())
                self.open_button.configure(state='disabled')
                self.status.set('Starter loaded. Review every participant row; neutral suggestions do not identify people.')
            self.launch(lambda app: discover_mapping(Path(path)), loaded)

    def show_mapping(self):
        self.mapping_tree.delete(*self.mapping_tree.get_children())
        for i, p in enumerate(self.mapping.participants):
            self.mapping_tree.insert('', 'end', iid=str(i), values=(Path(p.resource).name, p.source_id, p.display_name, ', '.join(p.channel_labels)))

    def load_example(self):
        folder = Path(__file__).resolve().parents[1] / 'tests/fixtures/s09-picture-26.08.2'
        def loaded(mapping):
            self.project.set(str(folder / 'before.kdenlive')); self.mapping = mapping
            self.confirmed.set(False); self.clear_draft()
            self.analysis = self.request = self.run_directory = None
            self.records['analysis'].set(str(folder / 'analysis.json'))
            self.records['request'].set(str(folder.parent / 's10-cli-26.08.2/planner-request.json'))
            self.records['picture'].set(str(folder / 'picture-analysis.json'))
            self.records['picture_request'].set('')
            self.records['cleanup_request'].set(str(folder / 'cleanup-request.json'))
            self.update_record_status(); self.show_mapping()
            self.review_tree.delete(*self.review_tree.get_children()); self.open_button.configure(state='disabled')
            self.status.set('Generated tones/noise/pictures with construction-labelled origins and approvals; no recorded people. Confirm mapping and choose a NEW private run folder.')
        self.launch(lambda app: absolute_mapping(folder / 'mapping.json'), loaded)

    def load_mapping(self):
        path = filedialog.askopenfilename(parent=self.root, title='Load explicit participant mapping', filetypes=[('JSON', '*.json')])
        if path:
            def load():
                self.mapping = absolute_mapping(Path(path)); self.confirmed.set(False); self.show_mapping()
                self.status.set('Mapping loaded. Confirm the file-to-participant assignments before starting.')
            self.guard(load)

    def edit_participant(self):
        if self.worker.busy or not self.mapping_tree.selection(): return
        index = int(self.mapping_tree.selection()[0]); old = self.mapping.participants[index]
        dialog = tk.Toplevel(self.root); dialog.title('Participant mapping'); dialog.transient(self.root); dialog.grab_set()
        variables = []
        for label, value in (('Audio file (from starter)', old.resource), ('Source ID', old.source_id), ('Track name', old.display_name), ('Channel labels, comma separated; shared mic uses multiple labels', ', '.join(old.channel_labels))):
            ttk.Label(dialog, text=label).pack(anchor='w', padx=14, pady=(8, 0))
            v = tk.StringVar(value=value); variables.append(v)
            ttk.Entry(dialog, textvariable=v, width=78, state='readonly' if len(variables) == 1 else 'normal').pack(padx=14, pady=3)
        def save():
            def action():
                values = [v.get() for v in variables]
                current = replace(old, source_id=values[1], display_name=values[2], channel_labels=tuple(x.strip() for x in values[3].split(',')))
                participants = list(self.mapping.participants); participants[index] = current
                self.mapping = loads(MappingManifest, dumps(replace(self.mapping, participants=tuple(participants))))
                self.confirmed.set(False); self.show_mapping(); dialog.destroy()
            self.guard(action)
        ttk.Button(dialog, text='Apply mapping', command=save).pack(pady=12)

    def path_dialog(self, title, fields, directory_keys=()):
        dialog = tk.Toplevel(self.root); dialog.title(title); dialog.transient(self.root); dialog.grab_set()
        dialog.columnconfigure(1, weight=1)
        for i, (key, label, var) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, sticky='w', padx=10, pady=7)
            ttk.Entry(dialog, textvariable=var, width=65).grid(row=i, column=1, sticky='ew', pady=7)
            def browse(k=key, v=var, l=label):
                p = filedialog.askdirectory(parent=dialog, title=l) if k in directory_keys else filedialog.askopenfilename(parent=dialog, title=l)
                if p: v.set(p)
            ttk.Button(dialog, text='Browse', command=browse).grid(row=i, column=2, padx=10)
            ttk.Button(dialog, text='Clear', command=lambda v=var: v.set('')).grid(row=i, column=3, padx=(0, 10))
        ttk.Label(dialog, text='Files stay local. Existing approvals must match the original analysis and refined plan.\nAfter Keep or pacing changes, stale cleanup refuses; explicitly review/rebind or clear cleanup for unity.').grid(row=len(fields), column=0, columnspan=4, padx=10, pady=10)
        ttk.Button(dialog, text='Done', command=lambda: (dialog.destroy(), self.update_record_status())).grid(row=len(fields)+1, column=0, columnspan=4, pady=10)

    def reviewed_records(self):
        self.path_dialog('Explicit reviewed records (optional)', [(k, l, self.records[k]) for k, l in RECORDS])

    def local_setup(self):
        labels = {'ffprobe':'Media probe (ffprobe)', 'ffmpeg':'Media decoder (ffmpeg)', 'speech_model':'Installed speech asset',
                  'reaction_model':'Installed reaction asset', 'cache':'Private reusable cache folder', 'kdenlive':'Installed Kdenlive executable'}
        self.path_dialog('Local setup - existing assets, no downloads', [(k, labels[k], v) for k, v in self.assets.items()], ('cache',))

    def update_record_status(self):
        labels = [label for key, label in RECORDS if self.records[key].get()]
        self.record_status.configure(text='Selected: ' + ', '.join(labels) if labels else 'No reviewed records selected. Fresh analysis retains origin/tail review and cannot certify export.')

    def choose_output(self):
        path = filedialog.asksaveasfilename(parent=self.root, title='Name a NEW private run folder', confirmoverwrite=False)
        if path: self.output.set(path)

    def start(self):
        if not self.mapping or not self.confirmed.get():
            self.status.set('Review and explicitly confirm every participant mapping before starting.'); return
        if not self.project.get() or not self.output.get() or not self.assets['ffprobe'].get():
            self.status.set('Choose a starter, a new private output folder and the media probe in Local setup.'); return
        options = RunOptions(MODES[self.mode.get()], Path(self.project.get()), Path('unused'), Path(self.assets['ffprobe'].get()), Path(self.output.get()),
            preset=self.preset.get(), experimental=self.experimental.get(),
            **{k: Path(v.get()) if v.get() else None for k, v in self.records.items()},
            **{k: Path(v.get()) if v.get() else None for k, v in self.assets.items() if k not in ('ffprobe', 'kdenlive')})
        mapping, draft = self.mapping, self.draft
        self.run_directory = None
        def run(app):
            path, job = prepare_job(options, mapping, draft)
            app.run(job.run_options())
            return options.output.absolute(), review_run(options.output.absolute())
        self.launch(run, self.display_run)

    def resume(self):
        path = filedialog.askopenfilename(parent=self.root, title='Resume immutable original desktop job (form edits are not applied)', filetypes=[('Desktop job', '*desktop-job.json')])
        if path:
            self.run_directory = None
            def run(app):
                options = read_record(DesktopJob, path).run_options()
                app.run(options, resume=True)
                return options.output, review_run(options.output)
            self.launch(run, self.display_run)

    def load_run(self):
        path = filedialog.askdirectory(parent=self.root, title='Review completed or incomplete private run')
        if path:
            self.launch(lambda app: (Path(path), review_run(path)), self.display_run)

    def display_run(self, value):
        path, (manifest, report, analysis, request) = value
        path = Path(path)
        self.run_directory = Path(path); self.analysis = analysis; self.request = request; self.clear_draft()
        self.review_tree.delete(*self.review_tree.get_children())
        for d in report.get('intake', {}).get('diagnostics', []):
            self.review_tree.insert('', 'end', values=(d['severity'] + ' ' + d['source'], '', '', d['code'].replace('_', ' ').lower()))
        for gap in report.get('planning', {}).get('gaps', []):
            self.review_tree.insert('', 'end', values=('gap', ' - '.join(gap['source_seconds']),
                ', '.join(str(r['output_seam']) for r in gap['removed']) or 'retained', gap['reason'].replace('_', ' ')))
        for review in report.get('planning', {}).get('reviews', []):
            self.review_tree.insert('', 'end', values=('review', review['source_seconds'], review['output_seconds'] if review['output_seconds'] is not None else 'removed / no output time', review['reason']))
        for marker in report.get('picture_markers', []):
            self.review_tree.insert('', 'end', values=('picture', review_seconds(marker['source_time']), review_seconds(marker['output_time']), marker['reason'].replace('_', ' ')))
        self.open_button.configure(state='normal' if self.can_open() else 'disabled')
        self.status.set('Run ' + manifest.state + '. Review required; alignment and full-interview quality are not certified. Private report: ' + str(path / 'report.json'))

    def can_open(self):
        return self.run_directory is not None and (self.run_directory / 'project.kdenlive').is_file() and not self.run_directory.name.endswith('.incomplete')

    def review_detail(self, event=None):
        if self.worker.busy or not self.review_tree.selection(): return
        values = self.review_tree.item(self.review_tree.selection()[0], 'values')
        dialog = tk.Toplevel(self.root); dialog.title('Private review detail'); dialog.transient(self.root)
        for label, value in zip(('Review', 'Original source seconds', 'Output seconds', 'Reason'), values):
            ttk.Label(dialog, text=label + ': ' + value, wraplength=650, justify='left').pack(anchor='w', padx=16, pady=9)
        ttk.Button(dialog, text='Close', command=dialog.destroy).pack(pady=10)

    def restore(self):
        if self.analysis is None or self.request is None:
            self.status.set('Review a completed plan/export run with verified exact coverage before adding Keep/Restore.'); return
        dialog = tk.Toplevel(self.root); dialog.title('Keep / Restore in original source seconds'); dialog.transient(self.root); dialog.grab_set()
        source = tk.StringVar(value=next(s.source_id for s in self.analysis.sources if s.kind == 'participant_audio'))
        action = tk.StringVar(value='keep'); start = tk.StringVar(); end = tk.StringVar()
        ttk.Label(dialog, text='Applies to ALL tracks. Enter decimal seconds or an exact fraction (for example 9/2).').pack(padx=15, pady=10)
        ttk.Combobox(dialog, textvariable=source, values=[s.source_id for s in self.analysis.sources], state='readonly').pack()
        for label, var in (('Source start (inclusive)', start), ('Source end (exclusive)', end)):
            ttk.Label(dialog, text=label).pack(pady=(8, 0)); ttk.Entry(dialog, textvariable=var).pack()
        ttk.Radiobutton(dialog, text='Keep shared time', value='keep', variable=action).pack(anchor='w', padx=15, pady=(10, 0))
        ttk.Radiobutton(dialog, text='Restore audible (shared time + unity gain)', value='audible', variable=action).pack(anchor='w', padx=15)
        def apply():
            def update():
                self.draft = restored_request(self.analysis, self.draft or self.request, source.get(), start.get(), end.get(), action.get())
                self.records['analysis'].set(str(self.run_directory / 'analysis.json'))
                self.records['request'].set(str(self.run_directory / 'planner-request.json'))
                self.restore_status.configure(text='Pending source-time overrides: ' + str(len(self.draft.overrides)) + '. Choose a NEW run folder. Cleanup must be explicitly reviewed/rebound or cleared.')
                dialog.destroy()
            self.guard(update)
        ttk.Button(dialog, text='Apply to next new run', command=apply).pack(pady=12)

    def clear_draft(self):
        self.draft = None
        self.restore_status.configure(text='Keep retains shared time; Restore audible also restores unity on all microphones. Recreate into a NEW run.')

    def open_kdenlive(self):
        if not self.assets['kdenlive'].get():
            self.status.set('Select the installed Kdenlive executable in Local setup.'); return
        directory, executable = self.run_directory, self.assets['kdenlive'].get()
        self.launch(lambda app: open_edit_copy(directory, executable),
                    lambda path: self.status.set('Opened editable copy in Kdenlive. Save manual edits there. Copy: ' + str(path)))


def main():
    if os.name == 'nt':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('InterviewAutoEditor.Desktop')
    root = tk.Tk()
    Desktop(root)
    root.mainloop()


if __name__ == '__main__':
    main()
