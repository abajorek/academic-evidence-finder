#!/usr/bin/env python3
"""
Edgar Academic Evidence Scanner - Retro GUI Interface
Inspired by classic 1980s virus scanners and terminal interfaces

"Man, this thing is like, so retro it makes my Commodore 64 jealous"
                                                    - The Cheat, probably

Features authentic 80s computer sounds because apparently that's what we do now.
"""

import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import threading
import time
import random
import subprocess
import os
import sys
from pathlib import Path
from typing import List, Optional
import runpy


def is_frozen_build() -> bool:
    """Return True when running from a PyInstaller bundle."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_runtime_root() -> Path:
    """Return the base directory for bundled resources."""
    if is_frozen_build():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


def get_runtime_scripts_dir() -> Path:
    """Locate the directory that holds scan scripts at runtime."""
    runtime_root = get_runtime_root()
    bundled_scripts = runtime_root / "embedded_scripts"
    if bundled_scripts.exists():
        return bundled_scripts
    return Path(__file__).resolve().parent


def get_working_directory() -> Path:
    """Determine where scan output should be written."""
    if is_frozen_build():
        return Path.home() / "EdgarEvidence"
    return Path(__file__).resolve().parents[1]


def run_embedded_script(script_name: str, script_args: List[str], working_directory: Optional[Path] = None) -> int:
    """Execute an embedded script within the current interpreter context."""

    scripts_dir = get_runtime_scripts_dir()
    target = scripts_dir / script_name
    if not target.exists():
        print(f"[edgar] Unable to locate embedded script: {script_name}", file=sys.stderr)
        return 1

    previous_cwd = Path.cwd()
    previous_argv = sys.argv[:]
    previous_sys_path = sys.path[:]

    try:
        if working_directory is not None:
            os.makedirs(working_directory, exist_ok=True)
            os.chdir(working_directory)

        sys.argv = [str(target)] + script_args

        # Ensure embedded paths take precedence when the script resolves modules.
        runtime_root = get_runtime_root()
        for path in [str(scripts_dir), str(runtime_root)]:
            if path not in sys.path:
                sys.path.insert(0, path)

        runpy.run_path(str(target), run_name="__main__")
        return 0
    except SystemExit as exc:  # Allow CLI scripts to call sys.exit
        code = exc.code if isinstance(exc.code, int) else 0
        return code
    finally:
        sys.argv = previous_argv
        sys.path = previous_sys_path
        os.chdir(previous_cwd)

class EdgarGUI:
    def __init__(self):
        self.root = tk.Tk()

        # Initialize configuration FIRST (before creating widgets)
        self.runtime_scripts_dir = get_runtime_scripts_dir()
        self.working_dir = get_working_directory()
        self.results_dir = self.working_dir / "results"
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.current_scan_process = None
        self.scanning = False
        self.selected_years = []
        self.scan_mode = "pass1"  # pass1, pass2, full
        self.selected_directories = []
        
        # Random Homestar Runner-esque status messages
        self.homestar_messages = [
            "Oh, seriously!? This is gonna take forever...",
            "Whoa, check it out! Files are happening!",
            "Man, technology is pretty cool, I guess.",
            "This is like, way more complicated than it needs to be.",
            "Jorb well done, files! ...Wait, that doesn't make sense.",
            "Oh good, more waiting. I love waiting. It's my favorite.",
            "Scanning files like it's 1982, which apparently is a thing we do now.",
            "Homestar would totally mess this up somehow.",
            "Strong Sad probably uses something way more complicated than this.",
            "The System Is Down! ...Oh wait, no it's not. Never mind.",
            "Scanning... scanning... still scanning... yep, still doing that.",
            "This scan is taking longer than one of Strong Bad's techno songs.",
            "Files! Why'd it have to be files?",
            "Oh, for the love of... just scan already!",
            "Seriously, my computer runs DOS and it's faster than this.",
            "The Cheat would probably just eat the hard drive at this point."
        ]
        
        # Now setup everything else
        self.setup_window()
        self.setup_pygame_audio()
        self.create_widgets()
        self.setup_styles()

    def setup_window(self):
        """Configure the main window with retro styling"""
        self.root.title("Edgar Academic Evidence Scanner v2.1982 - \"It's like, totally authentic or whatever\"")
        self.root.geometry("1000x800")  # Made bigger
        self.root.configure(bg='#000000')
        self.root.resizable(True, True)  # Made resizable
        
        # Set minimum size
        self.root.minsize(900, 700)
        
        # Try to use a monospace font that looks retro
        try:
            self.font_family = "Consolas"
        except:
            self.font_family = "Courier New"
            
    def setup_pygame_audio(self):
        """Initialize pygame for retro sound effects"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.audio_enabled = True
        except Exception as e:
            self.audio_enabled = False
            print(f"Audio disabled - pygame mixer not available: {e}")
    
    def play_beep(self, frequency=800, duration=100):
        """Play a retro beep sound (because authenticity, apparently)"""
        if not self.audio_enabled:
            return
            
        try:
            import numpy as np
            # Generate a simple beep tone
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            
            # Create sine wave for cleaner sound
            t = np.linspace(0, duration/1000, frames)
            wave = np.sin(2 * np.pi * frequency * t) * 0.3  # Volume at 30%
            
            # Convert to pygame format
            wave = (wave * 32767).astype(np.int16)
            stereo_wave = np.array([wave, wave]).T
            
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.play()
        except ImportError:
            # Fallback without numpy - simple square wave
            try:
                sample_rate = 22050
                frames = int(duration * sample_rate / 1000)
                arr = []
                for i in range(frames):
                    # Square wave
                    wave = 8192 if (i % (sample_rate // frequency)) < (sample_rate // frequency // 2) else -8192
                    arr.append([wave, wave])
                
                sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
                sound.play()
            except Exception:
                pass
        except Exception:
            pass
    
    def setup_styles(self):
        """Configure ttk styles for that sweet, sweet retro look"""
        style = ttk.Style()
        
        # Configure frame styles
        style.configure("Edgar.TFrame", 
                       background="#000000",
                       borderwidth=2,
                       relief="raised")
        
        # Configure label styles  
        style.configure("Edgar.TLabel",
                       background="#000000", 
                       foreground="#00FF00",
                       font=(self.font_family, 10, "bold"))
        
        style.configure("Title.TLabel",
                       background="#000000",
                       foreground="#00FFFF", 
                       font=(self.font_family, 14, "bold"))
        
        style.configure("Status.TLabel",
                       background="#000000",
                       foreground="#FFFF00",
                       font=(self.font_family, 9))
    
    def create_widgets(self):
        """Create all GUI widgets (the boring part, but necessary I guess)"""
        # Main container
        main_frame = ttk.Frame(self.root, style="Edgar.TFrame", padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # ASCII Art Header
        self.create_header(main_frame)
        
        # Control panels
        self.create_mode_panel(main_frame)
        self.create_year_panel(main_frame) 
        self.create_directory_panel(main_frame)
        self.create_scan_panel(main_frame)

        # Status and progress
        self.create_status_panel(main_frame)

        # Start the retro animation (because why not?)
        self.start_retro_effects()

    def build_subprocess_env(self):
        """Prepare environment variables for spawned scan processes."""
        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")
        env.setdefault("PYTHONIOENCODING", "utf-8")
        env["EDGAR_RUNTIME_ROOT"] = str(get_runtime_root())
        env["EDGAR_WORKSPACE"] = str(self.working_dir)
        env["EDGAR_RESULTS_DIR"] = str(self.results_dir)
        return env

    def reset_scan_state(self, status_message: str = "Status: READY (and hopefully wiser)"):
        """Restore the UI to an idle state after a scan finishes or aborts."""
        self.scanning = False
        self.scan_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.progress_var.set(status_message)
        self.current_scan_process = None
    
    def create_header(self, parent):
        """Create the ASCII art header (the fancy part)"""
        header_frame = ttk.Frame(parent, style="Edgar.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ascii_art = """
╔════════════════════════════════════════════════════════════════════╗
║                      EDGAR ACADEMIC EVIDENCE                       ║
║                        SCANNER v2.1982                             ║
║                                                                    ║
║  ████████╗██╗  ██╗███████╗    ██╗   ██╗██╗██████╗██╗   ██╗███████╗ ║
║  ╚══██╔══╝██║  ██║██╔════╝    ██║   ██║██║██╔══██╗██║   ██║██╔════╝ ║
║     ██║   ███████║█████╗      ██║   ██║██║██████╔╝██║   ██║███████╗ ║
║     ██║   ██╔══██║██╔══╝      ╚██╗ ██╔╝██║██╔══██╗██║   ██║╚════██║ ║
║     ██║   ██║  ██║███████╗     ╚████╔╝ ██║██║  ██║╚██████╔╝███████║ ║
║     ╚═╝   ╚═╝  ╚═╝╚══════╝      ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ║
║                           HUNTER                                   ║
║                                                                    ║
║            Programmed entirely in mom's basement                   ║
║                      by Edgar (c)1982                             ║
║                                                                    ║
║        "It's like, way more professional than it has any          ║
║                    right to be." - The Cheat                      ║
╚════════════════════════════════════════════════════════════════════╝
        """
        
        header_label = tk.Label(header_frame, text=ascii_art,
                               bg="#000000", fg="#00FFFF",
                               font=(self.font_family, 8),
                               justify="left")
        header_label.pack()
    
    def create_mode_panel(self, parent):
        """Create scan mode selection panel"""
        mode_frame = ttk.LabelFrame(parent, text=" SCAN MODE (Pick your poison) ", style="Edgar.TFrame")
        mode_frame.pack(fill="x", pady=5)
        
        # Mode selection
        self.mode_var = tk.StringVar(value="pass1")
        
        modes = [
            ("pass1", "PASS 1: Quick & Dirty Metadata Scan"),
            ("pass2", "PASS 2: Full Monty Text Extraction"), 
            ("full", "FULL SCAN: Go For Broke")
        ]
        
        for i, (value, text) in enumerate(modes):
            rb = tk.Radiobutton(mode_frame, text=text,
                               variable=self.mode_var, value=value,
                               bg="#000000", fg="#00FF00",
                               selectcolor="#004400", 
                               font=(self.font_family, 10),
                               command=self.on_mode_change)
            rb.grid(row=0, column=i, padx=20, pady=10, sticky="w")
            
    def create_year_panel(self, parent):
        """Create year selection panel (because time is a flat circle)"""  
        year_frame = ttk.LabelFrame(parent, text=" TARGET YEARS (The Years That Matter) ", style="Edgar.TFrame")
        year_frame.pack(fill="x", pady=5)
        
        # Year checkboxes
        self.year_vars = {}
        years = [2021, 2022, 2023, 2024, 2025]
        
        for i, year in enumerate(years):
            var = tk.BooleanVar(value=True if year >= 2024 else False)
            self.year_vars[year] = var
            
            cb = tk.Checkbutton(year_frame, text=f"[{year}]",
                               variable=var, 
                               bg="#000000", fg="#00FF00",
                               selectcolor="#004400",
                               font=(self.font_family, 12, "bold"),
                               command=self.on_year_change)
            cb.grid(row=0, column=i, padx=15, pady=10)
    
    def create_directory_panel(self, parent):
        """Create directory selection panel (where the magic happens)"""
        dir_frame = ttk.LabelFrame(parent, text=" SCAN DIRECTORIES (Point me at the stuff) ", style="Edgar.TFrame")
        dir_frame.pack(fill="x", pady=5)
        
        # Directory list and controls
        list_frame = tk.Frame(dir_frame, bg="#000000")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Listbox for selected directories
        self.dir_listbox = tk.Listbox(list_frame, 
                                     bg="#000000", fg="#00FF00",
                                     font=(self.font_family, 9),
                                     height=4,
                                     selectbackground="#004400")
        self.dir_listbox.pack(side="left", fill="both", expand=True)
        
        # Scrollbar (for when you have way too many directories)
        scrollbar = tk.Scrollbar(list_frame, bg="#004400")
        scrollbar.pack(side="right", fill="y")
        self.dir_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.dir_listbox.yview)
        
        # Buttons
        btn_frame = tk.Frame(dir_frame, bg="#000000") 
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        add_btn = tk.Button(btn_frame, text="[ADD DIRECTORY]",
                           bg="#004400", fg="#00FF00",
                           font=(self.font_family, 10, "bold"),
                           command=self.add_directory,
                           relief="raised", bd=3)
        add_btn.pack(side="left", padx=5)
        
        remove_btn = tk.Button(btn_frame, text="[REMOVE]", 
                              bg="#440000", fg="#FF0000",
                              font=(self.font_family, 10, "bold"),
                              command=self.remove_directory,
                              relief="raised", bd=3)
        remove_btn.pack(side="left", padx=5)
        
        # Add default directories (because we're helpful like that)
        default_dirs = [
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop")
        ]
        for dir_path in default_dirs:
            if os.path.exists(dir_path):
                self.dir_listbox.insert("end", dir_path)
                self.selected_directories.append(dir_path)
    
    def create_scan_panel(self, parent):
        """Create scan control panel (the business end)"""
        scan_frame = ttk.LabelFrame(parent, text=" SCAN CONTROL (This is where it gets real) ", style="Edgar.TFrame")
        scan_frame.pack(fill="x", pady=5)
        
        # Scan button (the big red button, but green)
        self.scan_btn = tk.Button(scan_frame, text=">>> INITIATE SCAN SEQUENCE <<<",
                                 bg="#004400", fg="#00FF00",
                                 font=(self.font_family, 14, "bold"),
                                 height=2,
                                 command=self.start_scan,
                                 relief="raised", bd=4)
        self.scan_btn.pack(side="left", padx=20, pady=10)
        
        # Stop button (for when things go sideways)
        self.stop_btn = tk.Button(scan_frame, text="[PANIC BUTTON]",
                                 bg="#440000", fg="#FF0000", 
                                 font=(self.font_family, 12, "bold"),
                                 state="disabled",
                                 command=self.stop_scan,
                                 relief="raised", bd=4)
        self.stop_btn.pack(side="right", padx=20, pady=10)
    
    def create_status_panel(self, parent):
        """Create status and progress panel (where the magic words appear)"""
        status_frame = ttk.LabelFrame(parent, text=" SYSTEM STATUS (What's happening now) ", style="Edgar.TFrame")
        status_frame.pack(fill="both", expand=True, pady=5)
        
        # Status text area (the scrolling terminal goodness)
        text_frame = tk.Frame(status_frame, bg="#000000")
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.status_text = tk.Text(text_frame, 
                                  bg="#000000", fg="#00FF00",
                                  font=(self.font_family, 9),
                                  height=18, width=120,  # Made much bigger
                                  insertbackground="#00FF00",
                                  selectbackground="#004400",
                                  wrap=tk.WORD)  # Word wrap for long lines
        
        # Scrollbar for the status text
        status_scrollbar = tk.Scrollbar(text_frame, bg="#004400")
        status_scrollbar.pack(side="right", fill="y")
        self.status_text.pack(side="left", fill="both", expand=True)
        
        self.status_text.config(yscrollcommand=status_scrollbar.set)
        status_scrollbar.config(command=self.status_text.yview)
        
        # Progress indicator
        self.progress_var = tk.StringVar()
        self.progress_label = ttk.Label(status_frame, textvariable=self.progress_var,
                                       style="Status.TLabel")
        self.progress_label.pack(pady=(0, 10))
        
        # Initial status
        self.log_message("EDGAR ACADEMIC EVIDENCE SCANNER INITIALIZED")
        self.log_message("Status: Ready to scan some files, I guess...")
        if self.audio_enabled:
            self.log_message("Audio initialized. Prepare for authentic 80s beeps!")
        else:
            self.log_message("Audio disabled. Silent but still deadly.")
        self.log_message("Tip: This thing actually works, which is more than we can say for most software.")
        self.progress_var.set("Status: READY (and slightly sarcastic)")
    
    def start_retro_effects(self):
        """Start background retro effects (the atmospheric stuff)"""
        self.animate_scanner()
    
    def animate_scanner(self):
        """Animate the scanner display (blink blink bloop)"""
        if not self.scanning:
            # Random flicker effects and snarky comments
            if random.random() < 0.05:  # 5% chance
                self.play_beep(random.randint(400, 1200), 50)
                if random.random() < 0.3:  # Sometimes add a comment
                    msg = random.choice([
                        "Beep! (That was important, probably)",
                        "System alert: Everything is fine. Probably.",
                        "Random beep #" + str(random.randint(1, 999)),
                        "The computer is making noises. This is normal.",
                        "Edgar's still working. Barely.",
                    ])
                    self.log_message(msg)
        
        # Schedule next animation frame
        self.root.after(3000, self.animate_scanner)  # Every 3 seconds
    
    def log_message(self, message):
        """Add message to status log (with timestamp because we're thorough)"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\\n"
        
        self.status_text.insert("end", log_entry)
        self.status_text.see("end")
        self.root.update_idletasks()
    
    def on_mode_change(self):
        """Handle scan mode change (user made a choice!)"""
        mode = self.mode_var.get()
        self.play_beep(600, 100)
        
        mode_comments = {
            "pass1": "Fast and loose metadata scanning selected. Smart choice.",
            "pass2": "Full text extraction mode engaged. Hope you brought snacks.",
            "full": "Complete scan mode activated. This might take a while. Maybe make some coffee."
        }
        
        self.log_message(f"Scan mode: {mode.upper()} - {mode_comments.get(mode, 'Unknown mode, but we will roll with it like steve winwood.')}")
    
    def on_year_change(self):
        """Handle year selection change (time travel engaged)"""
        selected = [year for year, var in self.year_vars.items() if var.get()]
        self.selected_years = selected
        self.play_beep(800, 80)
        
        if not selected:
            self.log_message("No years selected. Scanning the void, apparently.")
        elif len(selected) == 1:
            self.log_message(f"Target year: {selected[0]}. Very focused. I like it.")
        else:
            self.log_message(f"Target years: {selected}. Casting a wide net, eh?")
    
    def add_directory(self):
        """Add directory to scan list (more stuff to look at)"""
        directory = filedialog.askdirectory(title="Select Directory to Scan (Choose wisely)")
        if directory:
            self.dir_listbox.insert("end", directory)
            self.selected_directories.append(directory)
            self.play_beep(1000, 120)
            self.log_message(f"Added directory: {directory}")
            self.log_message("Another directory added to the list. The plot thickens.")
    
    def remove_directory(self):
        """Remove selected directory (second thoughts are allowed)"""
        selection = self.dir_listbox.curselection()
        if selection:
            index = selection[0]
            directory = self.dir_listbox.get(index)
            self.dir_listbox.delete(index)
            self.selected_directories.remove(directory)
            self.play_beep(400, 120)
            self.log_message(f"Removed directory: {directory}")
            self.log_message("Directory removed. Good riddance, probably.")
        else:
            self.log_message("Nothing selected to remove. Click on something first, genius.")
    
    def start_scan(self):
        """Start the academic evidence scan (here we go!)"""
        if not self.selected_directories:
            messagebox.showerror("Error", "No directories selected!\\nEven Edgar needs somewhere to look.")
            self.log_message("Scan aborted: No directories selected. Can't scan thin air.")
            return
            
        if not self.selected_years:
            messagebox.showerror("Error", "No target years selected!\\nTime is important, apparently.")
            self.log_message("Scan aborted: No years selected. What are we, timeless?")
            return
        
        # Update UI state
        self.scanning = True
        self.scan_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # Play scan initiation sound sequence
        self.play_beep(1200, 200)
        time.sleep(0.1)
        self.play_beep(800, 300)
        time.sleep(0.1)
        self.play_beep(1000, 200)
        
        self.log_message("=" * 70)
        self.log_message("INITIATING ACADEMIC EVIDENCE SCAN SEQUENCE...")
        self.log_message("Buckle up, this might get bumpy.")
        self.log_message("=" * 70)
        
        # Start scan in separate thread (because threading is fun)
        scan_thread = threading.Thread(target=self.run_scan, daemon=True)
        scan_thread.start()
    
    def run_scan(self):
        """Execute the actual scan process (the meat and potatoes)"""
        try:
            mode = self.mode_var.get()
            years = self.selected_years
            directories = self.selected_directories
            
            self.log_message(f"Scan mode: {mode} (because that's what you picked)")
            self.log_message(f"Target years: {years} (time travel engaged)")
            self.log_message(f"Directories: {len(directories)} (that's a lot of places to look)")
            
            # Build year filter arguments
            year_start = f"{min(years)}-01-01"
            year_end = f"{max(years)}-12-31"
            
            # Simulate scan progress with retro effects and commentary
            self.simulate_scan_progress()
            
            script_dir = self.runtime_scripts_dir
            script_name = "scan.py"
            script_args: List[str] = [
                "--modified-since", year_start,
                "--modified-until", year_end,
                "--out", str(self.results_dir),
            ]

            if mode == "pass1":
                self.log_message("Executing metadata-only analysis...")
                self.log_message("This is the quick and dirty approach. Fast, but not very thorough.")
                optimized_script = script_dir / "scan_optimized.py"
                if optimized_script.exists():
                    script_name = "scan_optimized.py"
                    script_args = ["--pass1-only"] + script_args
                else:
                    self.log_message("Optimized scanner not found. Falling back to regular scan.")

            elif mode == "pass2":
                self.log_message("Executing full text extraction...")
                self.log_message("Now we're getting serious. Text extraction engaged.")
                optimized_script = script_dir / "scan_optimized.py"
                if optimized_script.exists():
                    script_name = "scan_optimized.py"

            else:  # full scan
                self.log_message("Executing complete scan sequence...")
                self.log_message("Full scan mode: No mercy, no prisoners.")
                script_args.extend(["--edgar", "--edgar-interval", "0.3"])

            # Add directories to command arguments
            for directory in directories:
                script_args.extend(["--include", directory])

            target_script = script_dir / script_name
            if not target_script.exists():
                message = f"Required scan script not found: {target_script}"
                self.log_message(message)
                messagebox.showerror("Missing Script", message)
                self.reset_scan_state()
                return

            cmd: List[str] = []

            if is_frozen_build():
                cmd.append(sys.executable)
            else:
                cmd.extend([sys.executable, str(Path(__file__).resolve())])

            cmd.extend([
                "--run-embedded",
                script_name,
                "--cwd",
                str(self.working_dir),
            ])

            cmd.extend(script_args)

            self.log_message(f"Command: {' '.join(cmd)}")
            self.log_message("Here we go! Executing scan command...")

            scan_start_time = time.time()  # Track scan duration

            # Execute scan process with real-time output
            self.current_scan_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=0,
                cwd=self.working_dir,
                env=self.build_subprocess_env()
            )

            self.log_message("Scan process started. Monitoring progress...")
            self.log_message(f"Working directory: {self.working_dir}")
            self.log_message(f"Results directory: {self.results_dir}")
            
            # Read output in real-time with commentary
            line_count = 0
            last_update_time = time.time()
            
            while True:
                output = self.current_scan_process.poll()
                
                # Read any available output
                try:
                    line = self.current_scan_process.stdout.readline()
                    if line:
                        line_count += 1
                        self.log_message(f"[{line_count:03d}] {line.strip()}")
                        
                        # Add progress comments every 25 lines
                        if line_count % 25 == 0:
                            progress_msg = random.choice([
                                f"Still working... {line_count} lines processed.",
                                "Files are being analyzed. This is what progress looks like.",
                                "The scan continues. Edgar is earning his keep.",
                                "Processing files like it's nobody's business.",
                                f"Line {line_count}! The numbers keep going up!"
                            ])
                            self.log_message(f"   → {progress_msg}")
                    
                    # Update status periodically even without output
                    current_time = time.time()
                    if current_time - last_update_time > 5:  # Every 5 seconds
                        elapsed = current_time - scan_start_time
                        self.progress_var.set(f"Status: SCANNING... ({elapsed:.0f}s elapsed)")
                        
                        if line_count == 0:
                            self.log_message("   → Still initializing... (this is normal, probably)")
                        
                        last_update_time = current_time
                        
                        # Play a little progress beep
                        if random.random() < 0.3:
                            self.play_beep(random.randint(600, 1000), 60)
                    
                    # Update the GUI
                    self.root.update()
                    
                except Exception as e:
                    # No more output available right now
                    pass
                
                # Check if process finished
                if output is not None:
                    break
                    
                # Check if user wants to stop
                if not self.scanning:
                    break
                    
                # Small delay to prevent busy waiting
                time.sleep(0.1)
            
            if self.current_scan_process.returncode == 0:
                self.log_message("=" * 70)
                self.log_message("SCAN COMPLETED SUCCESSFULLY!")
                self.log_message("Edgar has done his job. Results are ready for inspection.")
                self.log_message(f"Results saved to: {self.results_dir}")
                self.log_message("You can now bask in the glory of organized evidence.")
                self.log_message("=" * 70)
                
                # Victory sound sequence (the triumphant fanfare)
                for freq in [800, 1000, 1200, 1500]:
                    self.play_beep(freq, 150)
                    time.sleep(0.1)
                    
                # Random victory message
                victory_msg = random.choice([
                    "Jorb well done! Wait, that's not a word. Job well done!",
                    "Success! The files have been successfully evidenced.",
                    "Scan complete! Time to see what we found in there.",
                    "All done! Edgar can rest easy knowing the job is finished.",
                    "Mission accomplished! Now you can get back to more important things."
                ])
                self.log_message(victory_msg)
                
            else:
                self.log_message("SCAN ERROR: Process terminated with errors")
                self.log_message("Well, that didn't go as planned. Maybe try again?")
                self.play_beep(300, 500)  # Error sound (ominous)
                
        except Exception as e:
            self.log_message(f"FATAL ERROR: {str(e)}")
            self.log_message("Something went horribly wrong. This is not ideal.")
            self.play_beep(200, 800)  # Really ominous error sound
            
        finally:
            # Reset UI state
            self.reset_scan_state()
    
    def simulate_scan_progress(self):
        """Simulate retro scan progress display (the theatrical part)"""
        scan_steps = [
            "Initializing Edgar subsystems...",
            "Loading academic evidence detection patterns...", 
            "Calibrating text extraction algorithms...",
            "Mounting scan target directories...",
            "Activating file filtering protocols...",
            "Engaging pattern matching engines...",
            "Beginning systematic file analysis..."
        ]
        
        step_comments = [
            "This always takes longer than it should.",
            "Lots of fancy words for 'getting ready'.",
            "The computer is thinking. Slowly.",
            "Mounting directories sounds way cooler than it actually is.",
            "Filtering files like a coffee machine, but less useful.",
            "Pattern matching: finding needles in haystacks since 1982.",
            "And here... we... go!"
        ]
        
        for i, step in enumerate(scan_steps):
            self.log_message(step)
            if i < len(step_comments):
                self.log_message(f"   ({step_comments[i]})")
            
            self.progress_var.set(f"Status: {step}")
            
            # Retro progress animation with varying beeps
            for j in range(2):
                self.play_beep(400 + j * 200 + i * 50, 80)
                time.sleep(0.3)
                
            time.sleep(0.8)
    
    def stop_scan(self):
        """Stop the current scan (the escape hatch)"""
        if self.current_scan_process:
            self.current_scan_process.terminate()
            self.log_message("Terminating scan process...")
            
        self.log_message("SCAN ABORTED BY USER")
        self.log_message("Well, that was fun while it lasted.")
        self.play_beep(300, 400)  # Abort sound (sad trombone)
        self.reset_scan_state("Status: ABORTED (user got impatient)")
        
        # Random abort message
        abort_msg = random.choice([
            "Scan stopped. Hope you found what you were looking for.",
            "Aborted! The scan has been terminated with extreme prejudice.",
            "User intervention detected. Stopping all the things.",
            "Scan cancelled. Edgar is disappointed but not surprised.",
            "Operation halted. The files will have to wait for another day."
        ])
        self.log_message(abort_msg)
    
    def get_random_homestar_comment(self):
        """Get a random Homestar Runner-style comment"""
        return random.choice(self.homestar_messages)
    
    def run(self):
        """Start the GUI application (the main event)"""
        self.play_beep(1000, 200)  # Startup sound
        startup_msg = random.choice([
            "Edgar GUI initialized. Let the scanning commence!",
            "System ready. Time to find some academic evidence.",
            "Edgar is online and ready for action. Sort of.",
            "GUI loaded successfully. Now we can click on things!",
            "Welcome to Edgar! It's like the future, but retro."
        ])
        self.log_message(startup_msg)
        self.root.mainloop()

def parse_cli_args(argv: Optional[List[str]] = None):
    """Parse command-line arguments for embedded execution."""
    parser = argparse.ArgumentParser(
        description="Launch Edgar GUI or run bundled scanner scripts.")
    parser.add_argument(
        "--run-embedded",
        dest="embedded_script",
        metavar="SCRIPT",
        help="Execute an embedded scanner script instead of launching the GUI.")
    parser.add_argument(
        "--cwd",
        dest="embedded_cwd",
        metavar="PATH",
        help="Working directory to use when executing an embedded script.")

    args, remainder = parser.parse_known_args(argv)

    if args.embedded_cwd and not args.embedded_script:
        parser.error("--cwd can only be used together with --run-embedded")

    return args, remainder


def main(argv: Optional[List[str]] = None):
    """Launch Edgar GUI or dispatch to an embedded script."""
    args, remainder = parse_cli_args(argv)

    if args.embedded_script:
        working_dir = Path(args.embedded_cwd).expanduser() if args.embedded_cwd else None
        exit_code = run_embedded_script(args.embedded_script, remainder, working_dir)
        sys.exit(exit_code)

    if remainder:
        raise SystemExit(f"Unexpected arguments: {' '.join(remainder)}")

    print("🎮 Launching Edgar Academic Evidence Scanner GUI...")
    print("   (With authentic 80s computer sounds!)")
    app = EdgarGUI()
    app.run()


if __name__ == "__main__":
    main()
