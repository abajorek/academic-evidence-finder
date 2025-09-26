#!/usr/bin/env python3
"""
Edgar Academic Evidence Scanner - 8-Bit Retro Gaming GUI
Full retro gaming aesthetic with authentic 80s vibes

"It's like, totally more pixelated than it needs to be" - Strong Bad
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import threading
import time
import random
import subprocess
import os
from pathlib import Path

# Import our retro gaming assets
try:
    from edgar_sprites import *
except ImportError:
    print("Warning: edgar_sprites.py not found. Using fallback styling.")
    # Fallback color scheme
    RETRO_COLORS = {
        'black': '#000000',
        'bright_green': '#00FF00',
        'bright_cyan': '#00FFFF', 
        'bright_magenta': '#FF00FF',
        'bright_yellow': '#FFFF00',
        'bright_red': '#FF0000'
    }

class Edgar8BitGUI:
    def __init__(self):
        self.root = tk.Tk()
        
        # Initialize configuration FIRST
        self.current_scan_process = None
        self.scanning = False
        self.selected_years = []
        self.scan_mode = "pass1"
        self.selected_directories = []
        self.edgar_state = 'normal'  # For sprite animation
        
        # Enhanced Homestar Runner commentary for 8-bit version
        self.retro_messages = [
            "Whoa! This is like, totally 8-bit or whatever!",
            "It's like someone put my Atari through a blender and made a GUI.",
            "These pixels are so big I can see them from space!",
            "Strong Bad would be so jealous of these graphics.",
            "This is more retro than a Strong Sad poetry reading.",
            "Oh great, now we're in 8-bit mode. What's next, punch cards?",
            "The graphics are blocky, but the functionality is... questionable.",
            "It's like playing video games, but with academic evidence!",
            "This thing has more pixels than my brain has thoughts.",
            "Scanning files in glorious 8-bit vision! Because why not?",
            "The Cheat's computer looks more advanced than this.",
            "Welcome to the future! ...of 1982.",
            "These sound effects are totally authentic or whatever.",
            "More beeps than a smoke detector with a low battery.",
            "Files! Why'd it have to be files? In 8-bit!",
            "This GUI has more style than Strong Sad's turtleneck collection."
        ]
        
        self.setup_8bit_window()
        self.setup_pygame_audio()
        self.create_8bit_widgets()
        self.start_retro_animations()
        
    def setup_8bit_window(self):
        """Configure the main window with full 8-bit gaming style"""
        self.root.title("Edgar's Luddie Paw-Paw's ACADEMIC EVIDENCE HUNTER v1982")
        self.root.geometry("1200x900")
        self.root.configure(bg=RETRO_COLORS['black'])
        self.root.resizable(True, True)
        self.root.minsize(1000, 800)
        
        # Try to get the best retro font
        try:
            self.retro_font_family = get_retro_font()
        except:
            self.retro_font_family = "Courier New"
    
    def setup_pygame_audio(self):
        """Initialize enhanced 8-bit audio system"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.audio_enabled = True
        except Exception as e:
            self.audio_enabled = False
            print(f"8-bit audio disabled: {e}")
    
    def play_8bit_beep(self, frequency=800, duration=100, wave_type='square'):
        """Play authentic 8-bit gaming beeps"""
        if not self.audio_enabled:
            return
            
        try:
            import numpy as np
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            
            t = np.linspace(0, duration/1000, frames)
            
            if wave_type == 'square':
                # Classic 8-bit square wave
                wave = np.sign(np.sin(2 * np.pi * frequency * t)) * 0.3
            elif wave_type == 'triangle':
                # Triangle wave for softer tones
                wave = (2/np.pi) * np.arcsin(np.sin(2 * np.pi * frequency * t)) * 0.3
            else:
                # Sine wave fallback
                wave = np.sin(2 * np.pi * frequency * t) * 0.3
            
            wave = (wave * 32767).astype(np.int16)
            stereo_wave = np.array([wave, wave]).T
            
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.play()
            
        except Exception:
            # Simple fallback beep
            try:
                print(f"\\a")  # System beep
            except:
                pass
    
    def play_startup_fanfare(self):
        """Play the iconic 8-bit startup sequence"""
        startup_notes = [
            (523, 200),  # C5
            (659, 200),  # E5
            (784, 200),  # G5
            (1047, 400), # C6
            (784, 200),  # G5
            (1047, 600)  # C6
        ]
        
        def play_sequence():
            for freq, duration in startup_notes:
                self.play_8bit_beep(freq, duration, 'square')
                time.sleep(duration/1000 + 0.1)
        
        threading.Thread(target=play_sequence, daemon=True).start()
    
    def create_8bit_widgets(self):
        """Create all widgets with authentic 8-bit gaming style"""
        # Main container with gaming-style border
        main_frame = tk.Frame(self.root, bg=RETRO_COLORS['black'], bd=3, relief='raised')
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create the retro gaming header
        self.create_8bit_header(main_frame)
        
        # Edgar sprite display area
        self.create_edgar_sprite_area(main_frame)
        
        # Gaming-style control panels
        self.create_8bit_mode_panel(main_frame)
        self.create_8bit_year_panel(main_frame)
        self.create_8bit_directory_panel(main_frame)
        self.create_8bit_scan_panel(main_frame)
        
        # Retro status terminal
        self.create_8bit_status_panel(main_frame)
    
    def create_8bit_header(self, parent):
        """Create the 8-bit gaming title screen header"""
        header_frame = tk.Frame(parent, bg=RETRO_COLORS['black'], bd=2, relief='sunken')
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Use the full retro title screen
        try:
            title_text = EDGAR_TITLE_SCREEN
        except:
            # Fallback title
            title_text = """
╔═══════════════════════════════════════════════════════════════════════╗
║                    EDGAR ACADEMIC EVIDENCE HUNTER                     ║
║                              v1982                                    ║
║                                                                       ║
║                      8-BIT RETRO GAMING EDITION                       ║
║                                                                       ║
║                "It's like, totally pixelated!" - The Cheat           ║
╚═══════════════════════════════════════════════════════════════════════╝
            """
        
        title_label = tk.Label(header_frame, text=title_text,
                              bg=RETRO_COLORS['black'], 
                              fg=RETRO_COLORS['bright_cyan'],
                              font=(self.retro_font_family, 8, 'bold'),
                              justify="left")
        title_label.pack()
    
    def create_edgar_sprite_area(self, parent):
        """Create Edgar's sprite display area with animations"""
        sprite_frame = tk.Frame(parent, bg=RETRO_COLORS['black'], bd=2, relief='sunken')
        sprite_frame.pack(fill="x", pady=5)
        
        # Edgar sprite display
        try:
            sprite_config = colorize_sprite(get_edgar_sprite(self.edgar_state), 
                                          RETRO_COLORS['bright_green'], 
                                          RETRO_COLORS['black'])
            self.edgar_sprite = tk.Label(sprite_frame, **sprite_config)
        except:
            # Fallback sprite
            self.edgar_sprite = tk.Label(sprite_frame, 
                                       text="[EDGAR SPRITE]",
                                       bg=RETRO_COLORS['black'],
                                       fg=RETRO_COLORS['bright_green'],
                                       font=(self.retro_font_family, 16, 'bold'))
        
        self.edgar_sprite.pack(side="left", padx=20)
        
        # Status indicator next to Edgar
        status_text = f"STATUS: {STATUS_READY}"
        self.edgar_status = tk.Label(sprite_frame,
                                   text=status_text,
                                   bg=RETRO_COLORS['black'],
                                   fg=RETRO_COLORS['bright_yellow'],
                                   font=(self.retro_font_family, 14, 'bold'))
        self.edgar_status.pack(side="right", padx=20)
    
    def create_8bit_mode_panel(self, parent):
        """Create 8-bit styled scan mode selection"""
        mode_frame = tk.LabelFrame(parent, text=" ░▒▓ SCAN MODE (Choose Your Weapon) ▓▒░ ",
                                  bg=RETRO_COLORS['black'], 
                                  fg=RETRO_COLORS['bright_magenta'],
                                  font=(self.retro_font_family, 10, 'bold'),
                                  bd=3, relief='raised')
        mode_frame.pack(fill="x", pady=5)
        
        self.mode_var = tk.StringVar(value="pass1")
        
        modes = [
            ("pass1", "▓ LEVEL 1: Quick Metadata Scan ▓"),
            ("pass2", "▓ LEVEL 2: Full Text Extraction ▓"),
            ("full", "▓ BOSS LEVEL: Complete Analysis ▓")
        ]
        
        for i, (value, text) in enumerate(modes):
            rb = tk.Radiobutton(mode_frame, text=text,
                               variable=self.mode_var, value=value,
                               bg=RETRO_COLORS['black'], 
                               fg=RETRO_COLORS['bright_green'],
                               activebackground=RETRO_COLORS['dark_green'],
                               activeforeground=RETRO_COLORS['bright_green'],
                               selectcolor=RETRO_COLORS['dark_green'],
                               font=(self.retro_font_family, 10, 'bold'),
                               command=self.on_8bit_mode_change)
            rb.grid(row=0, column=i, padx=20, pady=15, sticky="w")
    
    def create_8bit_year_panel(self, parent):
        """Create 8-bit styled year selection"""
        year_frame = tk.LabelFrame(parent, text=" ░▒▓ TARGET YEARS (Time Machine Settings) ▓▒░ ",
                                  bg=RETRO_COLORS['black'],
                                  fg=RETRO_COLORS['bright_cyan'],
                                  font=(self.retro_font_family, 10, 'bold'),
                                  bd=3, relief='raised')
        year_frame.pack(fill="x", pady=5)
        
        self.year_vars = {}
        years = [2021, 2022, 2023, 2024, 2025]
        
        for i, year in enumerate(years):
            var = tk.BooleanVar(value=True if year >= 2024 else False)
            self.year_vars[year] = var
            
            cb = tk.Checkbutton(year_frame, text=f"▓ {year} ▓",
                               variable=var,
                               bg=RETRO_COLORS['black'],
                               fg=RETRO_COLORS['bright_yellow'],
                               activebackground=RETRO_COLORS['dark_yellow'],
                               activeforeground=RETRO_COLORS['bright_yellow'],
                               selectcolor=RETRO_COLORS['dark_yellow'],
                               font=(self.retro_font_family, 12, 'bold'),
                               command=self.on_8bit_year_change)
            cb.grid(row=0, column=i, padx=20, pady=15)
    
    def create_8bit_directory_panel(self, parent):
        """Create 8-bit styled directory management"""
        dir_frame = tk.LabelFrame(parent, text=" ░▒▓ SCAN DIRECTORIES (Where The Files Live) ▓▒░ ",
                                 bg=RETRO_COLORS['black'],
                                 fg=RETRO_COLORS['bright_green'],
                                 font=(self.retro_font_family, 10, 'bold'),
                                 bd=3, relief='raised')
        dir_frame.pack(fill="x", pady=5)
        
        # Directory listbox with 8-bit styling
        list_frame = tk.Frame(dir_frame, bg=RETRO_COLORS['black'])
        list_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.dir_listbox = tk.Listbox(list_frame,
                                     bg=RETRO_COLORS['black'],
                                     fg=RETRO_COLORS['bright_green'],
                                     selectbackground=RETRO_COLORS['dark_green'],
                                     selectforeground=RETRO_COLORS['bright_green'],
                                     font=(self.retro_font_family, 9, 'bold'),
                                     height=4,
                                     bd=2, relief='sunken')
        self.dir_listbox.pack(side="left", fill="both", expand=True)
        
        # 8-bit scrollbar
        scrollbar = tk.Scrollbar(list_frame, 
                                bg=RETRO_COLORS['dark_green'],
                                troughcolor=RETRO_COLORS['black'])
        scrollbar.pack(side="right", fill="y")
        self.dir_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.dir_listbox.yview)
        
        # Gaming-style buttons
        btn_frame = tk.Frame(dir_frame, bg=RETRO_COLORS['black'])
        btn_frame.pack(fill="x", padx=15, pady=10)
        
        add_btn = tk.Button(btn_frame, text="▓▓▓ [ADD DIRECTORY] ▓▓▓",
                           **BUTTON_STYLE_NORMAL,
                           command=self.add_8bit_directory)
        add_btn.pack(side="left", padx=10)
        
        remove_btn = tk.Button(btn_frame, text="▓▓▓ [DELETE] ▓▓▓",
                              **BUTTON_STYLE_DANGER,
                              command=self.remove_8bit_directory)
        remove_btn.pack(side="left", padx=10)
        
        # Add default directories with 8-bit flair
        default_dirs = [
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop")
        ]
        for dir_path in default_dirs:
            if os.path.exists(dir_path):
                self.dir_listbox.insert("end", f"▓ {dir_path}")
                self.selected_directories.append(dir_path)
    
    def create_8bit_scan_panel(self, parent):
        """Create the main scan control panel with gaming style"""
        scan_frame = tk.LabelFrame(parent, text=" ░▒▓ SCAN CONTROL (The Big Red Button) ▓▒░ ",
                                  bg=RETRO_COLORS['black'],
                                  fg=RETRO_COLORS['bright_red'],
                                  font=(self.retro_font_family, 12, 'bold'),
                                  bd=3, relief='raised')
        scan_frame.pack(fill="x", pady=10)
        
        # Main scan button with epic styling
        self.scan_btn = tk.Button(scan_frame, 
                                 text="▓▓▓ >>> INITIATE SCAN SEQUENCE <<< ▓▓▓",
                                 bg=RETRO_COLORS['dark_green'],
                                 fg=RETRO_COLORS['bright_green'],
                                 activebackground=RETRO_COLORS['bright_green'],
                                 activeforeground=RETRO_COLORS['black'],
                                 font=(self.retro_font_family, 16, 'bold'),
                                 height=3,
                                 relief='raised', bd=4,
                                 command=self.start_8bit_scan)
        self.scan_btn.pack(side="left", padx=30, pady=15)
        
        # Panic button with danger styling
        self.stop_btn = tk.Button(scan_frame, 
                                 text="▓▓▓ [ABORT MISSION] ▓▓▓",
                                 bg=RETRO_COLORS['dark_red'],
                                 fg=RETRO_COLORS['bright_red'],
                                 activebackground=RETRO_COLORS['bright_red'],
                                 activeforeground=RETRO_COLORS['black'],
                                 font=(self.retro_font_family, 14, 'bold'),
                                 state="disabled",
                                 relief='raised', bd=4,
                                 command=self.stop_8bit_scan)
        self.stop_btn.pack(side="right", padx=30, pady=15)
    
    def create_8bit_status_panel(self, parent):
        """Create the retro terminal status display"""
        status_frame = tk.LabelFrame(parent, text=" ░▒▓ SYSTEM TERMINAL (The Matrix Has You) ▓▒░ ",
                                    bg=RETRO_COLORS['black'],
                                    fg=RETRO_COLORS['bright_cyan'],
                                    font=(self.retro_font_family, 10, 'bold'),
                                    bd=3, relief='raised')
        status_frame.pack(fill="both", expand=True, pady=5)
        
        # Terminal text area with proper 8-bit styling
        terminal_frame = tk.Frame(status_frame, bg=RETRO_COLORS['black'])
        terminal_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.status_text = tk.Text(terminal_frame,
                                  bg=RETRO_COLORS['black'],
                                  fg=RETRO_COLORS['bright_green'],
                                  insertbackground=RETRO_COLORS['bright_green'],
                                  selectbackground=RETRO_COLORS['dark_green'],
                                  selectforeground=RETRO_COLORS['bright_green'],
                                  font=(self.retro_font_family, 9, 'bold'),
                                  height=15, width=150,
                                  wrap=tk.WORD,
                                  bd=2, relief='sunken')
        
        # 8-bit terminal scrollbar
        terminal_scrollbar = tk.Scrollbar(terminal_frame,
                                         bg=RETRO_COLORS['dark_green'],
                                         troughcolor=RETRO_COLORS['black'])
        terminal_scrollbar.pack(side="right", fill="y")
        self.status_text.pack(side="left", fill="both", expand=True)
        
        self.status_text.config(yscrollcommand=terminal_scrollbar.set)
        terminal_scrollbar.config(command=self.status_text.yview)
        
        # Progress bar area (retro style)
        progress_frame = tk.Frame(status_frame, bg=RETRO_COLORS['black'])
        progress_frame.pack(fill="x", padx=15, pady=5)
        
        self.progress_var = tk.StringVar()
        self.progress_label = tk.Label(progress_frame,
                                      textvariable=self.progress_var,
                                      bg=RETRO_COLORS['black'],
                                      fg=RETRO_COLORS['bright_yellow'],
                                      font=(self.retro_font_family, 10, 'bold'))
        self.progress_label.pack()
        
        # Initialize with 8-bit startup messages
        self.log_8bit_message("▓▓▓ EDGAR 8-BIT ACADEMIC EVIDENCE HUNTER ONLINE ▓▓▓")
        self.log_8bit_message("System Status: TOTALLY READY FOR RETRO ACTION")
        self.log_8bit_message("8-bit Audio: " + ("ENABLED - Beeps incoming!" if self.audio_enabled else "DISABLED - Silent mode"))
        self.log_8bit_message("Graphics Mode: MAXIMUM PIXELATION ENGAGED")
        self.log_8bit_message("Retro Factor: Over 9000!")
        self.log_8bit_message("Ready to scan files in glorious 8-bit vision!")
        self.progress_var.set("▓▓▓ STATUS: READY TO ROCK (in 8-bit) ▓▓▓")
    
    def start_retro_animations(self):
        """Start background 8-bit animations and effects"""
        self.animate_8bit_edgar()
        self.play_startup_fanfare()
    
    def animate_8bit_edgar(self):
        """Animate Edgar sprite based on current state"""
        if not self.scanning:
            # Idle animation - occasionally blink or move
            if random.random() < 0.1:  # 10% chance
                old_state = self.edgar_state
                self.edgar_state = 'scanning' if old_state == 'normal' else 'normal'
                self.update_edgar_sprite()
                
                # Play a subtle beep
                self.play_8bit_beep(random.randint(600, 800), 50)
                
                # Reset after a moment
                self.root.after(500, lambda: self.set_edgar_state(old_state))
        
        # Schedule next animation frame
        self.root.after(5000, self.animate_8bit_edgar)
    
    def update_edgar_sprite(self):
        """Update Edgar's sprite display"""
        try:
            sprite_config = colorize_sprite(get_edgar_sprite(self.edgar_state),
                                          RETRO_COLORS['bright_green'],
                                          RETRO_COLORS['black'])
            self.edgar_sprite.config(**sprite_config)
        except:
            # Fallback sprite update
            state_text = {
                'normal': "[EDGAR: READY]",
                'scanning': "[EDGAR: SCANNING]", 
                'complete': "[EDGAR: COMPLETE]",
                'error': "[EDGAR: ERROR]"
            }
            self.edgar_sprite.config(text=state_text.get(self.edgar_state, "[EDGAR]"))
    
    def set_edgar_state(self, state):
        """Set Edgar's state and update sprite"""
        self.edgar_state = state
        self.update_edgar_sprite()
        
        # Update status display
        status_display = {
            'normal': STATUS_READY,
            'scanning': STATUS_SCANNING,
            'complete': STATUS_COMPLETE,
            'error': STATUS_ERROR
        }
        self.edgar_status.config(text=f"STATUS: {status_display.get(state, STATUS_READY)}")
    
    def log_8bit_message(self, message):
        """Add message to 8-bit terminal with timestamp and styling"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] ▓ {message}\\n"
        
        self.status_text.insert("end", log_entry)
        self.status_text.see("end")
        self.root.update_idletasks()
    
    def on_8bit_mode_change(self):
        """Handle 8-bit scan mode change with enhanced feedback"""
        mode = self.mode_var.get()
        self.play_8bit_beep(800, 150, 'square')
        
        mode_comments = {
            "pass1": "Level 1 selected! Quick metadata scan for speed runners.",
            "pass2": "Level 2 engaged! Full text extraction - the main quest.",
            "full": "Boss Level activated! Complete scan - prepare for epic battle!"
        }
        
        self.log_8bit_message(f"8-BIT MODE CHANGE: {mode.upper()}")
        self.log_8bit_message(mode_comments.get(mode, "Unknown mode selected. Winging it!"))
    
    def on_8bit_year_change(self):
        """Handle year selection with 8-bit flair"""
        selected = [year for year, var in self.year_vars.items() if var.get()]
        self.selected_years = selected
        self.play_8bit_beep(1000, 120, 'triangle')
        
        if not selected:
            self.log_8bit_message("TIME MACHINE ERROR: No years selected!")
        elif len(selected) == 1:
            self.log_8bit_message(f"TIME LOCK: Targeting {selected[0]} with laser precision!")
        else:
            self.log_8bit_message(f"TEMPORAL SWEEP: Scanning years {selected} - time paradox engaged!")
    
    def add_8bit_directory(self):
        """Add directory with 8-bit feedback"""
        directory = filedialog.askdirectory(title="Select Directory for 8-bit Scanning")
        if directory:
            self.dir_listbox.insert("end", f"▓ {directory}")
            self.selected_directories.append(directory)
            self.play_8bit_beep(1200, 200, 'square')
            self.log_8bit_message(f"DIRECTORY ACQUIRED: {directory}")
            self.log_8bit_message("Another location added to the scan matrix!")
    
    def remove_8bit_directory(self):
        """Remove directory with 8-bit feedback"""
        selection = self.dir_listbox.curselection()
        if selection:
            index = selection[0]
            directory_display = self.dir_listbox.get(index)
            directory = directory_display.replace("▓ ", "")  # Remove the prefix
            self.dir_listbox.delete(index)
            if directory in self.selected_directories:
                self.selected_directories.remove(directory)
            self.play_8bit_beep(600, 200, 'square')
            self.log_8bit_message(f"DIRECTORY DELETED: {directory}")
            self.log_8bit_message("Target eliminated from scan matrix!")
        else:
            self.log_8bit_message("DELETE ERROR: No target selected!")
            self.play_8bit_beep(300, 300, 'square')
    
    def start_8bit_scan(self):
        """Start scan with full 8-bit presentation"""
        if not self.selected_directories:
            messagebox.showerror("8-Bit Error", 
                               "No directories selected!\\n\\nEven 8-bit Edgar needs somewhere to scan!")
            self.log_8bit_message("SCAN ABORT: No directories in scan matrix!")
            return
            
        if not self.selected_years:
            messagebox.showerror("8-Bit Error", 
                               "No years selected!\\n\\nTime machine needs target coordinates!")
            self.log_8bit_message("SCAN ABORT: Temporal coordinates missing!")
            return
        
        # Update UI state with 8-bit style
        self.scanning = True
        self.scan_btn.config(state="disabled", text="▓▓▓ SCANNING IN PROGRESS ▓▓▓")
        self.stop_btn.config(state="normal")
        self.set_edgar_state('scanning')
        
        # Epic scan initiation sequence
        self.play_8bit_startup_sequence()
        
        self.log_8bit_message("▓" * 70)
        self.log_8bit_message("8-BIT ACADEMIC EVIDENCE SCAN SEQUENCE INITIATED")
        self.log_8bit_message("Engaging warp drive... stand by for retro action!")
        self.log_8bit_message("▓" * 70)
        
        # Start scan in separate thread
        scan_thread = threading.Thread(target=self.run_8bit_scan, daemon=True)
        scan_thread.start()
    
    def play_8bit_startup_sequence(self):
        """Play epic 8-bit scan startup sounds"""
        def play_sequence():
            # Power up sound
            for freq in range(400, 1200, 100):
                self.play_8bit_beep(freq, 50, 'square')
                time.sleep(0.05)
            
            # Final power-up chord
            self.play_8bit_beep(1200, 300, 'square')
            time.sleep(0.1)
            self.play_8bit_beep(1500, 200, 'square')
        
        threading.Thread(target=play_sequence, daemon=True).start()
    
    def run_8bit_scan(self):
        """Execute scan with 8-bit monitoring and effects"""
        try:
            mode = self.mode_var.get()
            years = self.selected_years
            directories = self.selected_directories
            
            self.log_8bit_message(f"SCAN PARAMETERS LOCKED:")
            self.log_8bit_message(f"  ▓ Mode: {mode.upper()} (8-bit style)")
            self.log_8bit_message(f"  ▓ Years: {years} (temporal coordinates)")
            self.log_8bit_message(f"  ▓ Directories: {len(directories)} locations")
            
            # 8-bit scan initialization sequence
            self.simulate_8bit_scan_startup()
            
            # Build scan command (same logic as original, but with 8-bit logging)
            script_dir = Path(__file__).parent
            year_start = f"{min(years)}-01-01"
            year_end = f"{max(years)}-12-31"
            
            # Command building with 8-bit commentary
            if mode == "pass1":
                self.log_8bit_message("LEVEL 1 MODE: Metadata scan protocol engaged!")
                optimized_script = script_dir / "scan_optimized.py"
                if optimized_script.exists():
                    cmd = ["python", str(optimized_script), "--pass1-only",
                           "--modified-since", year_start, "--modified-until", year_end,
                           "--out", "results"]
                else:
                    cmd = ["python", str(script_dir / "scan.py"),
                           "--modified-since", year_start, "--modified-until", year_end,
                           "--out", "results"]
            elif mode == "pass2":
                self.log_8bit_message("LEVEL 2 MODE: Full text extraction matrix online!")
                optimized_script = script_dir / "scan_optimized.py"
                if optimized_script.exists():
                    cmd = ["python", str(optimized_script),
                           "--modified-since", year_start, "--modified-until", year_end,
                           "--out", "results"]
                else:
                    cmd = ["python", str(script_dir / "scan.py"),
                           "--modified-since", year_start, "--modified-until", year_end,
                           "--out", "results"]
            else:
                self.log_8bit_message("BOSS LEVEL MODE: Complete scan protocol - no mercy!")
                cmd = ["python", str(script_dir / "scan.py"),
                       "--modified-since", year_start, "--modified-until", year_end,
                       "--out", "results", "--edgar", "--edgar-interval", "0.3"]
            
            # Add directories
            for directory in directories:
                cmd.extend(["--include", directory])
            
            self.log_8bit_message("COMMAND MATRIX ASSEMBLED - EXECUTING...")
            
            # Execute with 8-bit monitoring
            scan_start_time = time.time()
            self.current_scan_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, bufsize=0, cwd=script_dir.parent
            )
            
            # Monitor with 8-bit style
            line_count = 0
            last_beep_time = time.time()
            
            while True:
                output = self.current_scan_process.poll()
                
                try:
                    line = self.current_scan_process.stdout.readline()
                    if line:
                        line_count += 1
                        self.log_8bit_message(f"[{line_count:04d}] {line.strip()}")
                        
                        # 8-bit progress beeps
                        current_time = time.time()
                        if current_time - last_beep_time > 2:  # Every 2 seconds
                            self.play_8bit_beep(random.randint(800, 1200), 80, 'triangle')
                            last_beep_time = current_time
                        
                        # 8-bit progress comments
                        if line_count % 30 == 0:
                            comment = random.choice([
                                f"8-bit progress update: {line_count} lines processed!",
                                "Files are being scanned in glorious retro style!",
                                "The pixels are flowing through the matrix!",
                                f"Scan level {line_count // 30}: Still going strong!",
                                "Edgar's 8-bit brain is working overtime!"
                            ])
                            self.log_8bit_message(f"  ▓▓▓ {comment}")
                    
                    # Update progress with 8-bit style
                    elapsed = time.time() - scan_start_time
                    self.progress_var.set(f"▓▓▓ 8-BIT SCANNING... ({elapsed:.0f}s) - {line_count} LINES ▓▓▓")
                    self.root.update()
                
                except Exception:
                    pass
                
                if output is not None:
                    break
                if not self.scanning:
                    break
                    
                time.sleep(0.1)
            
            # 8-bit scan completion
            if self.current_scan_process.returncode == 0:
                self.log_8bit_message("▓" * 70)
                self.log_8bit_message("8-BIT SCAN SEQUENCE COMPLETE - MISSION ACCOMPLISHED!")
                self.log_8bit_message("All files have been successfully evidenced in retro style!")
                self.log_8bit_message("Results archived in: results/ directory")
                self.log_8bit_message("Edgar's 8-bit mission: SUCCESS!")
                self.log_8bit_message("▓" * 70)
                
                self.set_edgar_state('complete')
                self.play_8bit_victory_fanfare()
                
                victory_msg = random.choice([
                    "8-bit victory achieved! The pixels have been conquered!",
                    "Scan complete! Time to admire those blocky graphics!",
                    "Mission accomplished in authentic retro style!",
                    "All evidence successfully located and pixelated!",
                    "Edgar's 8-bit adventure: Complete with extra pixels!"
                ])
                self.log_8bit_message(victory_msg)
            else:
                self.log_8bit_message("8-BIT SCAN ERROR: Process terminated!")
                self.log_8bit_message("The pixels have encountered a glitch!")
                self.set_edgar_state('error')
                self.play_8bit_beep(200, 800, 'square')
                
        except Exception as e:
            self.log_8bit_message(f"8-BIT FATAL ERROR: {str(e)}")
            self.log_8bit_message("The 8-bit matrix has experienced a critical failure!")
            self.set_edgar_state('error')
            self.play_8bit_beep(150, 1000, 'square')
            
        finally:
            # Reset UI with 8-bit style
            self.scanning = False
            self.scan_btn.config(state="normal", text="▓▓▓ >>> INITIATE SCAN SEQUENCE <<< ▓▓▓")
            self.stop_btn.config(state="disabled")
            self.set_edgar_state('normal')
            self.progress_var.set("▓▓▓ STATUS: READY FOR NEXT 8-BIT ADVENTURE ▓▓▓")
    
    def simulate_8bit_scan_startup(self):
        """8-bit scan startup sequence with epic flair"""
        startup_steps = [
            "Initializing 8-bit Edgar subsystems...",
            "Loading retro evidence detection patterns...",
            "Calibrating pixelated text extraction algorithms...",
            "Mounting target directories in 8-bit mode...", 
            "Activating classic gaming file protocols...",
            "Engaging pattern matching matrix...",
            "8-bit scan sequence ready - commencing operation!"
        ]
        
        step_comments = [
            "Like booting up an old Atari, but slower.",
            "Loading patterns with authentic 80s delay...",
            "Pixelated algorithms are the best algorithms.",
            "Mounting drives like it's 1982!",
            "Classic gaming meets file scanning - what could go wrong?",
            "The matrix is extra pixelated today.",
            "Here we go! Time for some 8-bit action!"
        ]
        
        for i, step in enumerate(startup_steps):
            self.log_8bit_message(step)
            if i < len(step_comments):
                self.log_8bit_message(f"  ({step_comments[i]})")
            
            self.progress_var.set(f"▓▓▓ {step} ▓▓▓")
            
            # 8-bit startup sound effects
            for j in range(3):
                freq = 500 + i * 100 + j * 50
                self.play_8bit_beep(freq, 100, 'square')
                time.sleep(0.2)
            
            time.sleep(0.8)
    
    def play_8bit_victory_fanfare(self):
        """Play epic 8-bit victory music"""
        victory_notes = [
            (523, 200), (659, 200), (784, 200), (1047, 400),
            (784, 200), (1047, 200), (1319, 600),
            (1047, 200), (1319, 200), (1568, 800)
        ]
        
        def play_fanfare():
            for freq, duration in victory_notes:
                self.play_8bit_beep(freq, duration, 'square')
                time.sleep(duration/1000 + 0.1)
        
        threading.Thread(target=play_fanfare, daemon=True).start()
    
    def stop_8bit_scan(self):
        """Stop scan with 8-bit drama"""
        if self.current_scan_process:
            self.current_scan_process.terminate()
            self.log_8bit_message("8-BIT SCAN TERMINATION SEQUENCE INITIATED...")
        
        self.scanning = False
        self.scan_btn.config(state="normal", text="▓▓▓ >>> INITIATE SCAN SEQUENCE <<< ▓▓▓")
        self.stop_btn.config(state="disabled")
        self.set_edgar_state('error')
        
        self.log_8bit_message("▓▓▓ SCAN ABORTED BY USER INTERVENTION ▓▓▓")
        self.log_8bit_message("The 8-bit scan has been terminated!")
        
        # Dramatic abort sound sequence
        for freq in [400, 300, 200]:
            self.play_8bit_beep(freq, 300, 'square')
            time.sleep(0.1)
        
        abort_msg = random.choice([
            "8-bit scan aborted! The pixels shall live to fight another day!",
            "Mission terminated! Edgar returns to standby mode.",
            "Scan cancelled! The retro matrix remains unsearched.",
            "Operation halted! Even 8-bit Edgar needs a break sometimes.",
            "Aborted! The files will have to wait for their pixelated destiny."
        ])
        self.log_8bit_message(abort_msg)
        self.progress_var.set("▓▓▓ STATUS: SCAN ABORTED (User got scared) ▓▓▓")
        
        # Return to normal after a delay
        self.root.after(3000, lambda: self.set_edgar_state('normal'))
    
    def run(self):
        """Start the 8-bit GUI application"""
        startup_msg = random.choice([
            "8-bit Edgar GUI online! Prepare for maximum pixelation!",
            "Retro mode engaged! Time to scan files like it's 1982!",
            "8-bit graphics loaded! Everything is more awesome in pixels!",
            "Welcome to the 8-bit academic evidence matrix!",
            "Edgar v1982 initialized! Let the retro scanning commence!"
        ])
        self.log_8bit_message(startup_msg)
        self.log_8bit_message(random.choice(self.retro_messages))
        
        self.root.mainloop()

def main():
    """Launch the 8-bit Edgar GUI"""
    print("🎮 Launching Edgar 8-bit Academic Evidence Scanner...")
    print("   Get ready for maximum retro action!")
    app = Edgar8BitGUI()
    app.run()

if __name__ == "__main__":
    main()
