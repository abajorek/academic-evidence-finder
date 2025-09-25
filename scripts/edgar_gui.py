#!/usr/bin/env python3
"""
Edgar Academic Evidence Scanner - Retro GUI Interface
Inspired by classic 1980s virus scanners and terminal interfaces

"Man, this thing is like, so retro it makes my Commodore 64 jealous"
                                                    - The Cheat, probably

Features authentic 80s computer sounds because apparently that's what we do now.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import threading
import time
import random
import subprocess
import os
from functools import partial
from pathlib import Path

class EdgarGUI:
    def __init__(self):
        self.root = tk.Tk()
        
        # Initialize configuration FIRST (before creating widgets)
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
        
        # Track the Tk main thread so we can safely schedule UI work later
        self.main_thread = threading.current_thread()

        # Now setup everything else
        self.setup_window()
        self.setup_pygame_audio()
        self.create_widgets()
        self.setup_styles()
        self.duck_animation_job = None
        self.current_duck_frame = 0
        self.duck_frames = []
        self.duck_animation_delay = 250
        
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

        style.configure("Edgar.Horizontal.TProgressbar",
                       troughcolor="#001100",
                       background="#00FF00",
                       bordercolor="#003300",
                       lightcolor="#00FF00",
                       darkcolor="#009900")
    
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
        controls_frame = tk.Frame(status_frame, bg="#000000")
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.progress_label = ttk.Label(controls_frame, textvariable=self.progress_var,
                                       style="Status.TLabel")
        self.progress_label.pack(side="left")

        self.progress_bar = ttk.Progressbar(controls_frame, style="Edgar.Horizontal.TProgressbar",
                                            mode="determinate", length=350)
        self.progress_bar.pack(side="left", padx=20, fill="x", expand=True)

        self.duck_label = tk.Label(controls_frame, bg="#000000")
        self.duck_label.pack(side="right")

        self.duck_frames = self.create_duck_frames()
        if self.duck_frames:
            self.duck_label.config(image=self.duck_frames[0])

        # Initial status
        self.log_message("EDGAR ACADEMIC EVIDENCE SCANNER INITIALIZED")
        self.log_message("Status: Ready to scan some files, I guess...")
        if self.audio_enabled:
            self.log_message("Audio initialized. Prepare for authentic 80s beeps!")
        else:
            self.log_message("Audio disabled. Silent but still deadly.")
        self.log_message("Tip: This thing actually works, which is more than we can say for most software.")
        self.set_progress_status("Status: READY (and slightly sarcastic)")

    def create_duck_frames(self):
        """Build adorable retro duck animation frames for the status bar"""
        duck_patterns = [
            [
                "000000011100000000",
                "000000111110000000",
                "000001111111000000",
                "000011111111100100",
                "000111111111110110",
                "000111111111110110",
                "000011111111111000",
                "000001111111110000",
                "000000111111100000",
                "000000011111000000",
                "000000111111100000",
                "000000110111000000",
                "000001100111100000",
                "000011100110110000",
                "000011000000110000",
                "000001100001100000",
                "000000011111000000",
                "000000001110000000",
            ],
            [
                "000000000111000000",
                "000000001111100000",
                "000000011111110000",
                "000000111111111000",
                "000001111111111100",
                "000001111111111100",
                "000000111111111000",
                "000000011111110000",
                "000000001111100000",
                "000000011111100000",
                "000000011011100000",
                "000000111001111000",
                "000001110001101100",
                "000001100000001100",
                "000011100000011000",
                "000001110000110000",
                "000000111111100000",
                "000000011111000000",
            ],
        ]

        frames = []
        for pattern in duck_patterns:
            height = len(pattern)
            width = len(pattern[0])
            image = tk.PhotoImage(width=width, height=height)

            for y, row in enumerate(pattern):
                for x, char in enumerate(row):
                    color = "#FFD447" if char == "1" else "#000000"
                    image.put(color, (x, y))

            # Scale the sprite up for better visibility
            frames.append(image.zoom(4, 4))

        return frames

    def start_duck_animation(self):
        """Kick off the duck status animation"""
        if not self.duck_frames:
            return

        if self.duck_animation_job is None:
            self.duck_animation_job = self.root.after(0, self.animate_duck)

    def stop_duck_animation(self):
        """Stop the duck animation and reset to the first frame"""
        if self.duck_animation_job is not None:
            self.root.after_cancel(self.duck_animation_job)
            self.duck_animation_job = None

        if self.duck_frames:
            self.current_duck_frame = 0
            self.duck_label.config(image=self.duck_frames[0])

    def animate_duck(self):
        """Animate the duck sprite while scans are running"""
        if not self.scanning or not self.duck_frames:
            self.duck_animation_job = None
            return

        self.current_duck_frame = (self.current_duck_frame + 1) % len(self.duck_frames)
        self.duck_label.config(image=self.duck_frames[self.current_duck_frame])
        self.duck_animation_job = self.root.after(self.duck_animation_delay, self.animate_duck)

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
        self.dispatch_to_ui(self._append_log_entry, log_entry)

    def _append_log_entry(self, log_entry):
        """Actually append log output on the main thread."""
        self.status_text.insert("end", log_entry)
        self.status_text.see("end")
        self.root.update_idletasks()

    def dispatch_to_ui(self, func, *args, **kwargs):
        """Execute ``func`` on the Tk main thread."""
        if threading.current_thread() is self.main_thread:
            func(*args, **kwargs)
        else:
            self.root.after(0, partial(func, *args, **kwargs))

    def set_progress_status(self, text):
        """Update the status label text safely."""
        self.dispatch_to_ui(self.progress_var.set, text)

    def update_progress_bar(self, *, mode=None, maximum=None, value=None, start=None,
                             stop=False, step=None, update_idletasks=False):
        """Thread-safe helper to tweak the progress bar."""
        if not hasattr(self, "progress_bar"):
            return

        def _apply():
            if stop:
                self.progress_bar.stop()
            if mode is not None:
                self.progress_bar.config(mode=mode)
            if maximum is not None:
                self.progress_bar.config(maximum=maximum)
            if value is not None:
                self.progress_bar["value"] = value
            if step is not None:
                self.progress_bar.step(step)
            if start is not None:
                self.progress_bar.start(start)
            if update_idletasks:
                self.progress_bar.update_idletasks()

        self.dispatch_to_ui(_apply)

    def schedule_beep_sequence(self, sequence):
        """Play a series of beeps without blocking the UI."""
        delay = 0
        for frequency, duration, pause_after in sequence:
            self.root.after(int(delay), lambda f=frequency, d=duration: self.play_beep(f, d))
            delay += int(duration + pause_after)
    
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

        self.update_progress_bar(mode="determinate", maximum=100, value=0, stop=True)

        self.start_duck_animation()

        # Play scan initiation sound sequence without blocking the UI
        self.schedule_beep_sequence([
            (1200, 200, 100),
            (800, 300, 100),
            (1000, 200, 0),
        ])
        
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

            self.update_progress_bar(mode="indeterminate", start=120)

            # Build command based on mode
            script_dir = Path(__file__).parent
            
            if mode == "pass1":
                self.log_message("Executing metadata-only analysis...")
                self.log_message("This is the quick and dirty approach. Fast, but not very thorough.")
                # Try to find the optimized scanner
                optimized_script = script_dir / "scan_optimized.py"
                if optimized_script.exists():
                    cmd = [
                        "python", str(optimized_script),
                        "--pass1-only",
                        "--modified-since", year_start,
                        "--modified-until", year_end,
                        "--out", "results"
                    ]
                else:
                    self.log_message("Optimized scanner not found. Falling back to regular scan.")
                    cmd = [
                        "python", str(script_dir / "scan.py"),
                        "--modified-since", year_start,
                        "--modified-until", year_end,
                        "--out", "results"
                    ]
                
            elif mode == "pass2":
                self.log_message("Executing full text extraction...")
                self.log_message("Now we're getting serious. Text extraction engaged.")
                optimized_script = script_dir / "scan_optimized.py"
                if optimized_script.exists():
                    cmd = [
                        "python", str(optimized_script), 
                        "--modified-since", year_start,
                        "--modified-until", year_end,
                        "--out", "results"
                    ]
                else:
                    cmd = [
                        "python", str(script_dir / "scan.py"),
                        "--modified-since", year_start,
                        "--modified-until", year_end,
                        "--out", "results"
                    ]
                
            else:  # full scan
                self.log_message("Executing complete scan sequence...")
                self.log_message("Full scan mode: No mercy, no prisoners.")
                # Run original scanner with Edgar mode
                cmd = [
                    "python", str(script_dir / "scan.py"),
                    "--modified-since", year_start, 
                    "--modified-until", year_end,
                    "--out", "results",
                    "--edgar",  # Enable Edgar mode for authentic experience
                    "--edgar-interval", "0.3"
                ]
            
            # Add directories to command
            for directory in directories:
                cmd.extend(["--include", directory])
            
            self.log_message(f"Command: {' '.join(cmd)}")
            self.log_message("Here we go! Executing scan command...")
            
            scan_start_time = time.time()  # Track scan duration
            
            # Execute scan process with real-time output
            self.current_scan_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                universal_newlines=True, bufsize=0, cwd=script_dir.parent  # Unbuffered
            )
            
            self.log_message("Scan process started. Monitoring progress...")
            
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
                        self.set_progress_status(f"Status: SCANNING... ({elapsed:.0f}s elapsed)")
                        
                        if line_count == 0:
                            self.log_message("   → Still initializing... (this is normal, probably)")
                        
                        last_update_time = current_time
                        
                        # Play a little progress beep
                        if random.random() < 0.3:
                            self.play_beep(random.randint(600, 1000), 60)
                    
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
                self.log_message("Results saved to: results/")
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
            self.scanning = False
            def _reset_ui():
                self.scan_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.update_progress_bar(mode="determinate", maximum=100, value=0, stop=True)
                self.stop_duck_animation()
                self.set_progress_status("Status: READY (and hopefully wiser)")

            self.dispatch_to_ui(_reset_ui)

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

        total_steps = len(scan_steps)
        self.update_progress_bar(mode="determinate", maximum=total_steps, value=0, stop=True)

        for i, step in enumerate(scan_steps):
            self.log_message(step)
            if i < len(step_comments):
                self.log_message(f"   ({step_comments[i]})")

            self.set_progress_status(f"Status: {step}")
            self.update_progress_bar(value=i + 1, update_idletasks=True)

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
            
        self.scanning = False
        self.scan_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_progress_bar(mode="determinate", maximum=100, value=0, stop=True)
        self.stop_duck_animation()

        self.log_message("SCAN ABORTED BY USER")
        self.log_message("Well, that was fun while it lasted.")
        self.play_beep(300, 400)  # Abort sound (sad trombone)
        self.set_progress_status("Status: ABORTED (user got impatient)")
        
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

def main():
    """Launch Edgar GUI (the entry point)"""
    print("🎮 Launching Edgar Academic Evidence Scanner GUI...")
    print("   (With authentic 80s computer sounds!)")
    app = EdgarGUI()
    app.run()

if __name__ == "__main__":
    main()
