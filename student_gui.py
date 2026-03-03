#!/usr/bin/env python3
"""
Student-friendly GUI wrapper for FSTIC.
"""

from __future__ import annotations

import glob
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import fstic

COMMON_AUDIO_EXTENSIONS = ["wav", "mp3", "ogg", "flac", "aac", "wma", "m4a", "aiff", "opus"]


class FSTICStudentApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("FSTIC Student Tool")
        self.root.geometry("860x620")

        self.mode = tk.StringVar(value="single")
        self.input_file = tk.StringVar()
        self.input_folder = tk.StringVar()
        self.compare_file_a = tk.StringVar()
        self.compare_file_b = tk.StringVar()
        self.output_dir = tk.StringVar(value=str(Path.cwd() / "output" / "student-runs"))
        self.window_ms = tk.StringVar(value="500")
        self.hop_ms = tk.StringVar(value="250")
        self.create_pdf = tk.BooleanVar(value=False)
        self.status_text = tk.StringVar(value="Ready.")

        self._build_ui()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        mode_frame = ttk.LabelFrame(main, text="Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(mode_frame, text="Single File", variable=self.mode, value="single", command=self._refresh_mode).pack(side=tk.LEFT, padx=(0, 18))
        ttk.Radiobutton(mode_frame, text="Folder (Batch)", variable=self.mode, value="folder", command=self._refresh_mode).pack(side=tk.LEFT, padx=(0, 18))
        ttk.Radiobutton(mode_frame, text="Compare Two Files", variable=self.mode, value="compare", command=self._refresh_mode).pack(side=tk.LEFT)

        self.single_frame = ttk.LabelFrame(main, text="Single File Input", padding=10)
        self.folder_frame = ttk.LabelFrame(main, text="Folder Input", padding=10)
        self.compare_frame = ttk.LabelFrame(main, text="Comparison Input", padding=10)

        self._build_single_frame()
        self._build_folder_frame()
        self._build_compare_frame()
        self._refresh_mode()

        settings = ttk.LabelFrame(main, text="Settings", padding=10)
        settings.pack(fill=tk.X, pady=(10, 10))

        ttk.Label(settings, text="Output Folder").grid(row=0, column=0, sticky="w")
        ttk.Entry(settings, textvariable=self.output_dir, width=70).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(settings, text="Browse", command=self._pick_output_folder).grid(row=0, column=2, sticky="w")

        ttk.Label(settings, text="Window (ms)").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(settings, textvariable=self.window_ms, width=12).grid(row=1, column=1, sticky="w", padx=8, pady=(8, 0))
        ttk.Label(settings, text="Hop (ms)").grid(row=1, column=1, sticky="w", padx=(120, 0), pady=(8, 0))
        ttk.Entry(settings, textvariable=self.hop_ms, width=12).grid(row=1, column=1, sticky="w", padx=(180, 0), pady=(8, 0))
        ttk.Checkbutton(settings, text="Generate PDF reports", variable=self.create_pdf).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

        settings.columnconfigure(1, weight=1)

        controls = ttk.Frame(main)
        controls.pack(fill=tk.X, pady=(0, 10))
        self.run_button = ttk.Button(controls, text="Run Analysis", command=self._run_clicked)
        self.run_button.pack(side=tk.LEFT)
        ttk.Label(controls, textvariable=self.status_text).pack(side=tk.LEFT, padx=14)

        log_frame = ttk.LabelFrame(main, text="Results", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log = tk.Text(log_frame, height=14, wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=True)
        self.log.insert(tk.END, "Select a mode, choose files/folders, and click 'Run Analysis'.\n")
        self.log.configure(state=tk.DISABLED)

    def _build_single_frame(self) -> None:
        ttk.Label(self.single_frame, text="Audio File").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.single_frame, textvariable=self.input_file, width=76).grid(row=0, column=1, padx=8, sticky="ew")
        ttk.Button(self.single_frame, text="Browse", command=self._pick_single_file).grid(row=0, column=2, sticky="w")
        self.single_frame.columnconfigure(1, weight=1)

    def _build_folder_frame(self) -> None:
        ttk.Label(self.folder_frame, text="Audio Folder").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.folder_frame, textvariable=self.input_folder, width=76).grid(row=0, column=1, padx=8, sticky="ew")
        ttk.Button(self.folder_frame, text="Browse", command=self._pick_input_folder).grid(row=0, column=2, sticky="w")
        self.folder_frame.columnconfigure(1, weight=1)

    def _build_compare_frame(self) -> None:
        ttk.Label(self.compare_frame, text="File A").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.compare_frame, textvariable=self.compare_file_a, width=76).grid(row=0, column=1, padx=8, sticky="ew")
        ttk.Button(self.compare_frame, text="Browse", command=lambda: self._pick_compare_file("a")).grid(row=0, column=2, sticky="w")

        ttk.Label(self.compare_frame, text="File B").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(self.compare_frame, textvariable=self.compare_file_b, width=76).grid(row=1, column=1, padx=8, sticky="ew", pady=(8, 0))
        ttk.Button(self.compare_frame, text="Browse", command=lambda: self._pick_compare_file("b")).grid(row=1, column=2, sticky="w", pady=(8, 0))

        self.compare_frame.columnconfigure(1, weight=1)

    def _refresh_mode(self) -> None:
        for frame in (self.single_frame, self.folder_frame, self.compare_frame):
            frame.pack_forget()
        mode = self.mode.get()
        if mode == "single":
            self.single_frame.pack(fill=tk.X, pady=(0, 10))
        elif mode == "folder":
            self.folder_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.compare_frame.pack(fill=tk.X, pady=(0, 10))

    def _pick_single_file(self) -> None:
        file_path = filedialog.askopenfilename(title="Select audio file")
        if file_path:
            self.input_file.set(file_path)

    def _pick_input_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select folder containing audio files")
        if folder:
            self.input_folder.set(folder)

    def _pick_compare_file(self, target: str) -> None:
        file_path = filedialog.askopenfilename(title=f"Select compare file {target.upper()}")
        if not file_path:
            return
        if target == "a":
            self.compare_file_a.set(file_path)
        else:
            self.compare_file_b.set(file_path)

    def _pick_output_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_dir.set(folder)

    def _append_log(self, text: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _run_clicked(self) -> None:
        try:
            window_ms = int(self.window_ms.get())
            hop_ms = int(self.hop_ms.get())
            if window_ms <= 0 or hop_ms <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid settings", "Window and Hop must be positive integers.")
            return

        output_dir = Path(self.output_dir.get().strip())
        if not output_dir:
            messagebox.showerror("Missing output folder", "Please provide an output folder.")
            return
        output_dir.mkdir(parents=True, exist_ok=True)

        self.run_button.configure(state=tk.DISABLED)
        self.status_text.set("Running...")
        self._append_log("-" * 70)

        thread = threading.Thread(
            target=self._run_analysis,
            args=(window_ms, hop_ms, str(output_dir), self.create_pdf.get()),
            daemon=True,
        )
        thread.start()

    def _run_analysis(self, window_ms: int, hop_ms: int, output_dir: str, create_pdf: bool) -> None:
        mode = self.mode.get()
        try:
            if mode == "single":
                self._run_single(window_ms, hop_ms, output_dir, create_pdf)
            elif mode == "folder":
                self._run_folder(window_ms, hop_ms, output_dir, create_pdf)
            else:
                self._run_compare(window_ms, hop_ms, output_dir, create_pdf)
            self.root.after(0, lambda: self.status_text.set("Completed."))
        except Exception as exc:
            self.root.after(0, lambda: self.status_text.set("Failed."))
            self.root.after(0, lambda: self._append_log(f"Error: {exc}"))
            self.root.after(0, lambda: messagebox.showerror("Analysis failed", str(exc)))
        finally:
            self.root.after(0, lambda: self.run_button.configure(state=tk.NORMAL))

    def _run_single(self, window_ms: int, hop_ms: int, output_dir: str, create_pdf: bool) -> None:
        input_path = self.input_file.get().strip()
        if not input_path or not os.path.isfile(input_path):
            raise ValueError("Choose a valid audio file.")
        self.root.after(0, lambda: self._append_log(f"Single file: {input_path}"))
        success, sti = fstic.process_audio_file(input_path, output_dir, window_ms, hop_ms, create_pdf=create_pdf)
        if success:
            self.root.after(0, lambda: self._append_log(f"Success: STI={sti:.3f}"))
        else:
            raise RuntimeError("Could not process selected file.")

    def _run_folder(self, window_ms: int, hop_ms: int, output_dir: str, create_pdf: bool) -> None:
        input_dir = self.input_folder.get().strip()
        if not input_dir or not os.path.isdir(input_dir):
            raise ValueError("Choose a valid folder.")

        files = []
        for ext in COMMON_AUDIO_EXTENSIONS:
            files.extend(glob.glob(os.path.join(input_dir, f"*.{ext}")))
        files = sorted(files)
        if not files:
            raise ValueError("No audio files found in selected folder.")

        self.root.after(0, lambda: self._append_log(f"Batch files found: {len(files)}"))
        ok_count = 0
        for fp in files:
            self.root.after(0, lambda p=fp: self._append_log(f"Processing: {os.path.basename(p)}"))
            success, sti = fstic.process_audio_file(fp, output_dir, window_ms, hop_ms, create_pdf=create_pdf)
            if success and sti is not None:
                ok_count += 1
                self.root.after(0, lambda p=fp, s=sti: self._append_log(f"  OK {os.path.basename(p)} -> STI={s:.3f}"))
            else:
                self.root.after(0, lambda p=fp: self._append_log(f"  FAIL {os.path.basename(p)}"))
        self.root.after(0, lambda: self._append_log(f"Batch complete: {ok_count}/{len(files)} succeeded"))

    def _run_compare(self, window_ms: int, hop_ms: int, output_dir: str, create_pdf: bool) -> None:
        file_a = self.compare_file_a.get().strip()
        file_b = self.compare_file_b.get().strip()
        if not file_a or not os.path.isfile(file_a):
            raise ValueError("Choose a valid File A.")
        if not file_b or not os.path.isfile(file_b):
            raise ValueError("Choose a valid File B.")

        self.root.after(0, lambda: self._append_log(f"Comparing:\n  A: {file_a}\n  B: {file_b}"))
        success, sti_a, sti_b = fstic.compare_two_audio_files(file_a, file_b, output_dir, window_ms, hop_ms, create_pdf=create_pdf)
        if success:
            self.root.after(0, lambda: self._append_log(f"Success: A={sti_a:.3f}, B={sti_b:.3f}"))
        else:
            raise RuntimeError("Comparison failed.")


def main() -> None:
    root = tk.Tk()
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    FSTICStudentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
