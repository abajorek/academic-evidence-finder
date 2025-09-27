#!/usr/bin/env python3
"""Modern desktop interface for the Academic Evidence Finder."""

from __future__ import annotations

import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Iterable, List

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class EvidenceFinderApp:
    """High-level controller for the desktop GUI."""

    YEAR_CHOICES = (2021, 2022, 2023, 2024, 2025)

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Academic Evidence Finder")
        self.root.geometry("960x720")
        self.root.minsize(860, 620)

        self.runtime_scripts_dir = self._resolve_runtime_scripts_dir()
        self.working_dir = self._resolve_working_directory()
        self.results_dir = self.working_dir / "results"
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.current_scan_process: subprocess.Popen[str] | None = None
        self.scan_thread: threading.Thread | None = None
        self.scanning = False
        self.scan_started_at: float | None = None

        self.mode_var = tk.StringVar(value="pass1")
        self.year_vars: dict[int, tk.BooleanVar] = {}
        self.selected_directories: List[str] = []

        self.status_var = tk.StringVar(value="Status: Ready")

        self._configure_styles()
        self._build_layout()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Initialisation helpers
    def _resolve_runtime_scripts_dir(self) -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            runtime_root = Path(getattr(sys, "_MEIPASS"))  # type: ignore[attr-defined]
            bundled_scripts = runtime_root / "embedded_scripts"
            if bundled_scripts.exists():
                return bundled_scripts
        return Path(__file__).resolve().parent

    def _resolve_working_directory(self) -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return Path.home() / "AcademicEvidenceFinder"
        return Path(__file__).resolve().parents[1]

    def _configure_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background="#f5f7fb")
        style.configure("Section.TLabelframe", background="#f5f7fb", font=("Segoe UI", 11, "bold"))
        style.configure("Section.TLabelframe.Label", foreground="#1a2b49")
        style.configure("Heading.TLabel", background="#f5f7fb", foreground="#1a2b49", font=("Segoe UI", 20, "bold"))
        style.configure("Subheading.TLabel", background="#f5f7fb", foreground="#51617d", font=("Segoe UI", 11))
        style.configure("Status.TLabel", background="#f5f7fb", foreground="#1a2b49", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))

    # ------------------------------------------------------------------
    # Layout
    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, style="App.TFrame", padding=(24, 24, 24, 16))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container, style="App.TFrame")
        header.pack(fill="x", pady=(0, 20))

        ttk.Label(header, text="Academic Evidence Finder", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Scan curated folders for teaching, service, and scholarship evidence.",
            style="Subheading.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        controls = ttk.Frame(container, style="App.TFrame")
        controls.pack(fill="x")

        self._build_mode_panel(controls)
        self._build_year_panel(controls)
        self._build_directory_panel(container)
        self._build_scan_panel(container)
        self._build_status_panel(container)

    def _build_mode_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent, text="Scan mode", style="Section.TLabelframe")
        frame.pack(fill="x", pady=(0, 12))

        descriptions = {
            "pass1": "Quick metadata review",
            "pass2": "Full text extraction",
            "full": "Complete scan",
        }
        for idx, (value, label) in enumerate(descriptions.items()):
            rb = ttk.Radiobutton(
                frame,
                text=label,
                value=value,
                variable=self.mode_var,
                command=lambda mode=value: self._log(f"Mode set to: {mode}"),
            )
            rb.grid(row=0, column=idx, padx=(8, 16), pady=12, sticky="w")

    def _build_year_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent, text="Target years", style="Section.TLabelframe")
        frame.pack(fill="x", pady=(0, 12))

        for idx, year in enumerate(self.YEAR_CHOICES):
            var = tk.BooleanVar(value=year >= 2024)
            self.year_vars[year] = var
            cb = ttk.Checkbutton(frame, text=str(year), variable=var, command=self._update_year_log)
            cb.grid(row=0, column=idx, padx=(8, 16), pady=12, sticky="w")

    def _build_directory_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent, text="Directories", style="Section.TLabelframe")
        frame.pack(fill="both", expand=True, pady=(0, 12))

        list_container = ttk.Frame(frame)
        list_container.pack(fill="both", expand=True, padx=12, pady=12)

        self.dir_listbox = tk.Listbox(list_container, height=6, activestyle="none")
        self.dir_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.dir_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.dir_listbox.configure(yscrollcommand=scrollbar.set)

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Button(button_row, text="Add folders", style="Accent.TButton", command=self._add_directory).pack(
            side="left"
        )
        ttk.Button(button_row, text="Remove selected", command=self._remove_directory).pack(side="left", padx=(12, 0))

    def _build_scan_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent, style="App.TFrame")
        frame.pack(fill="x", pady=(0, 12))

        self.scan_button = ttk.Button(frame, text="Start scan", style="Accent.TButton", command=self.start_scan)
        self.scan_button.pack(side="left")

        self.stop_button = ttk.Button(frame, text="Stop", command=self.stop_scan, state="disabled")
        self.stop_button.pack(side="left", padx=(12, 0))

    def _build_status_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.Labelframe(parent, text="Status", style="Section.TLabelframe")
        frame.pack(fill="both", expand=True)

        self.status_text = ScrolledText(frame, wrap="word", height=18)
        self.status_text.pack(fill="both", expand=True, padx=12, pady=12)
        self.status_text.configure(state="disabled")

        progress_row = ttk.Frame(frame)
        progress_row.pack(fill="x", padx=12, pady=(0, 12))

        self.progress_bar = ttk.Progressbar(progress_row, mode="indeterminate")
        self.progress_bar.pack(fill="x", expand=True)

        ttk.Label(progress_row, textvariable=self.status_var, style="Status.TLabel").pack(anchor="w", pady=(8, 0))

    # ------------------------------------------------------------------
    # Directory helpers
    def _add_directory(self) -> None:
        directory = filedialog.askdirectory(title="Select a folder to scan")
        if directory and directory not in self.selected_directories:
            self.selected_directories.append(directory)
            self.dir_listbox.insert("end", directory)
            self._log(f"Added directory: {directory}")

    def _remove_directory(self) -> None:
        selection = list(self.dir_listbox.curselection())
        if not selection:
            return
        for index in reversed(selection):
            directory = self.dir_listbox.get(index)
            self.dir_listbox.delete(index)
            if directory in self.selected_directories:
                self.selected_directories.remove(directory)
                self._log(f"Removed directory: {directory}")

    def _update_year_log(self) -> None:
        years = [str(year) for year, var in self.year_vars.items() if var.get()]
        self._log(f"Target years: {', '.join(years) if years else 'None'}")

    # ------------------------------------------------------------------
    # Logging helpers
    def _log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")

        def append() -> None:
            self.status_text.configure(state="normal")
            self.status_text.insert("end", f"[{timestamp}] {message}\n")
            self.status_text.see("end")
            self.status_text.configure(state="disabled")

        self.root.after(0, append)

    def _set_status(self, text: str) -> None:
        self.root.after(0, lambda: self.status_var.set(text))

    # ------------------------------------------------------------------
    # Scan execution
    def start_scan(self) -> None:
        if self.scanning:
            return

        directories = list(self.selected_directories)
        if not directories:
            messagebox.showinfo("Select folders", "Add at least one folder to scan before starting.")
            return

        years = [year for year, var in self.year_vars.items() if var.get()]
        if not years:
            messagebox.showinfo("Select years", "Choose at least one target year.")
            return

        mode = self.mode_var.get()

        self.scanning = True
        self.scan_started_at = time.time()
        self.scan_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.progress_bar.start(12)
        self._set_status("Status: Preparing scan…")
        self._log("Starting scan…")

        self.scan_thread = threading.Thread(
            target=self._run_scan,
            args=(mode, years, directories),
            daemon=True,
        )
        self.scan_thread.start()
        self._schedule_elapsed_updates()

    def _schedule_elapsed_updates(self) -> None:
        if not self.scanning or self.scan_started_at is None:
            return
        elapsed = int(time.time() - self.scan_started_at)
        self._set_status(f"Status: Scanning… ({elapsed}s elapsed)")
        self.root.after(1000, self._schedule_elapsed_updates)

    def _run_scan(self, mode: str, years: Iterable[int], directories: Iterable[str]) -> None:
        year_start = f"{min(years)}-01-01"
        year_end = f"{max(years)}-12-31"

        script_dir = self.runtime_scripts_dir
        optimized_script = script_dir / "scan_optimized.py"
        legacy_script = script_dir / "scan.py"

        if mode == "pass1":
            base_cmd = [sys.executable, str(optimized_script if optimized_script.exists() else legacy_script), "--pass1-only"]
        elif mode == "pass2":
            base_cmd = [sys.executable, str(optimized_script if optimized_script.exists() else legacy_script)]
        else:
            base_cmd = [sys.executable, str(legacy_script)]

        cmd = base_cmd + [
            "--modified-since",
            year_start,
            "--modified-until",
            year_end,
            "--out",
            str(self.results_dir.relative_to(self.working_dir)),
        ]

        for directory in directories:
            cmd.extend(["--include", directory])

        quoted = " ".join(shlex.quote(part) for part in cmd)
        self._log(f"Executing: {quoted}")

        try:
            self.current_scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.working_dir,
                bufsize=1,
            )
        except Exception as exc:  # pragma: no cover - defensive UI feedback
            self._log(f"Unable to start scan: {exc}")
            self._finish_scan()
            return

        assert self.current_scan_process.stdout is not None

        for line in self.current_scan_process.stdout:
            if not line:
                continue
            self._log(line.rstrip())

        return_code = self.current_scan_process.wait()
        if return_code == 0:
            self._log("Scan completed successfully.")
        else:
            self._log(f"Scan exited with code {return_code}.")
        self._finish_scan()

    def stop_scan(self) -> None:
        if not self.scanning:
            return
        if self.current_scan_process and self.current_scan_process.poll() is None:
            self._log("Stopping scan…")
            self.current_scan_process.terminate()
            try:
                self.current_scan_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.current_scan_process.kill()
        self._finish_scan()

    def _finish_scan(self) -> None:
        self.scanning = False
        self.current_scan_process = None
        self.scan_thread = None
        self.root.after(0, self.progress_bar.stop)
        self.root.after(0, lambda: self.scan_button.configure(state="normal"))
        self.root.after(0, lambda: self.stop_button.configure(state="disabled"))
        self._set_status("Status: Ready")

    # ------------------------------------------------------------------
    def _on_close(self) -> None:
        if self.scanning:
            if not messagebox.askyesno("Exit", "A scan is in progress. Stop it and close the application?"):
                return
            self.stop_scan()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = EvidenceFinderApp()
    app.run()


if __name__ == "__main__":
    main()
