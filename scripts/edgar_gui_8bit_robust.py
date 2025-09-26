#!/usr/bin/env python3
"""
Edgar 8-bit GUI with Robust Error Handling
Handles import issues gracefully and provides fallbacks

"It's like error handling, but with more pixels" - Strong Bad
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import random
import subprocess
import os
import sys
from pathlib import Path

# Robust pygame import with fallback
PYGAME_AVAILABLE = False
try:
    import pygame
    PYGAME_AVAILABLE = True
    print("✅ Pygame audio system loaded")
except ImportError:
    print("⚠️  Pygame not available - audio disabled")
    print("   Install with: pip install pygame")
    pygame = None

# Robust sprite import with fallback
SPRITES_AVAILABLE = False
try:
    from edgar_sprites import *
    SPRITES_AVAILABLE = True
    print("✅ 8-bit sprites loaded")
except ImportError:
    print("⚠️  Edgar sprites not available - using fallback styling")
    # Fallback color scheme
    RETRO_COLORS = {
        'black': '#000000',
        'bright_green': '#00FF00',
        'bright_cyan': '#00FFFF', 
        'bright_magenta': '#FF00FF',
        'bright_yellow': '#FFFF00',
        'bright_red': '#FF0000',
        'dark_green': '#004400',
        'dark_cyan': '#004444',
        'dark_magenta': '#440044',
        'dark_yellow': '#444400',
        'dark_red': '#440000'
    }
    
    def get_edgar_sprite(state='normal'):
        return f"[EDGAR: {state.upper()}]"
    
    def colorize_sprite(sprite_text, fg_color='#00FF00', bg_color='#000000'):
        return {
            'text': sprite_text,
            'fg': fg_color,
            'bg': bg_color,
            'font': ("Courier New", 12, 'bold'),
            'justify': 'center'
        }

class Edgar8BitGUIRobust:
    def __init__(self):
        self.root = tk.Tk()
        
        # Initialize configuration
        self.current_scan_process = None
        self.scanning = False
        self.selected_years = []
        self.scan_mode = "pass1"
        self.selected_directories = []
        self.edgar_state = 'normal'
        
        # Enhanced messaging
        self.retro_messages = [
            "Whoa! This is like, totally 8-bit or whatever!",
            "It's like someone put my Atari through a blender!",
            "These pixels are so retro they're practically vintage!",
            "Strong Bad would be jealous of these graphics.",
            "This is more pixelated than a Strong Sad selfie.",
            "Oh great, now we're in full retro mode!",
            "The graphics are blocky, the functionality is solid!",
            "It's like playing video games, but with files!",
            "Scanning files in glorious low-resolution!",
            "Welcome to the future of 1982!",
            "More beeps than a microwave convention!",
            "Files! Why'd it have to be files? In pixels!"
        ]
        
        self.setup_robust_window()
        self.setup_robust_audio()
        self.create_robust_widgets()
        self.start_animations()
        
    def setup_robust_window(self):
        """Configure window with error handling"""
        try:
            self.root.title("Edgar's 8-bit Academic Evidence Hunter v1982 (Robust Edition)")
            self.root.geometry("1200x900")
            self.root.configure(bg=RETRO_COLORS['black'])
            self.root.resizable(True, True)
            self.root.minsize(1000, 800)
            
            # Font selection with fallbacks
            font_candidates = ["Consolas", "Monaco", "DejaVu Sans Mono", "Courier New"]
            self.retro_font_family = "Courier New"  # Default fallback
            
            available_fonts = list(tk.font.families())
            for font in font_candidates:
                if font in available_fonts:
                    self.retro_font_family = font
                    break
                    
            print(f"✅ Using font: {self.retro_font_family}")
            
        except Exception as e:
            print(f"⚠️  Window setup warning: {e}")
            self.retro_font_family = "Courier New"
    
    def setup_robust_audio(self):
        """Setup audio with graceful fallback"""
        self.audio_enabled = PYGAME_AVAILABLE
        
        if self.audio_enabled:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("✅ 8-bit audio system initialized")
            except Exception as e:
                print(f"⚠️  Audio initialization failed: {e}")
                self.audio_enabled = False
        else:
            print("ℹ️  Running in silent mode (no pygame)")
    
    def play_8bit_beep(self, frequency=800, duration=100, wave_type='square'):
        """Play beep with fallback to system beep"""
        if not self.audio_enabled:
            # Fallback to system beep
            try:
                print("\\a", end='', flush=True)  # Terminal bell
            except:
                pass
            return
        
        try:
            # Use numpy if available, otherwise simple fallback
            try:
                import numpy as np
                sample_rate = 22050
                frames = int(duration * sample_rate / 1000)
                t = np.linspace(0, duration/1000, frames)
                
                if wave_type == 'square':
                    wave = np.sign(np.sin(2 * np.pi * frequency * t)) * 0.3
                else:
                    wave = np.sin(2 * np.pi * frequency * t) * 0.3
                
                wave = (wave * 32767).astype(np.int16)
                stereo_wave = np.array([wave, wave]).T
                sound = pygame.sndarray.make_sound(stereo_wave)
                sound.play()
                
            except ImportError:
                # Fallback without numpy
                print("♪", end='', flush=True)  # Musical note as visual feedback
                
        except Exception as e:
            print(f"🔇 Audio error: {e}")
    
    def create_robust_widgets(self):
        """Create widgets with error handling"""
        try:
            # Main container
            main_frame = tk.Frame(self.root, bg=RETRO_COLORS['black'], bd=3, relief='raised')
            main_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Create all panels
            self.create_header(main_frame)
            self.create_sprite_area(main_frame) 
            self.create_mode_panel(main_frame)
            self.create_year_panel(main_frame)
            self.create_directory_panel(main_frame)
            self.create_scan_panel(main_frame)
            self.create_status_panel(main_frame)
            
        except Exception as e:
            print(f"❌ Widget creation error: {e}")
            self.create_fallback_gui()
    
    def create_header(self, parent):
        """Create header with fallback"""
        try:
            header_frame = tk.Frame(parent, bg=RETRO_COLORS['black'], bd=2, relief='sunken')
            header_frame.pack(fill="x", pady=(0, 10))
            
            title_text = """
╔══════════════════════════════════════════════════════════════════════╗
║                      EDGAR 8-BIT EVIDENCE HUNTER                     ║
║                              v1982                                   ║
║                                                                      ║
║                    (Robust Edition - Now With Fallbacks!)           ║
║                                                                      ║
║              "It's like, totally error-resistant!" - The Cheat      ║
╚══════════════════════════════════════════════════════════════════════╝
            """
            
            header_label = tk.Label(header_frame, text=title_text,
                                  bg=RETRO_COLORS['black'], 
                                  fg=RETRO_COLORS['bright_cyan'],
                                  font=(self.retro_font_family, 8, 'bold'),
                                  justify="left")
            header_label.pack()
            
        except Exception as e:
            print(f"⚠️  Header creation warning: {e}")
    
    def create_sprite_area(self, parent):
        """Create Edgar sprite area with fallback"""
        try:
            sprite_frame = tk.Frame(parent, bg=RETRO_COLORS['black'], bd=2, relief='sunken')
            sprite_frame.pack(fill="x", pady=5)
            
            # Edgar sprite
            if SPRITES_AVAILABLE:
                sprite_config = colorize_sprite(get_edgar_sprite(self.edgar_state), 
                                              RETRO_COLORS['bright_green'], 
                                              RETRO_COLORS['black'])
                self.edgar_sprite = tk.Label(sprite_frame, **sprite_config)
            else:
                # Fallback ASCII Edgar
                fallback_sprite = """
    ▓▓▓▓▓▓▓▓▓▓▓▓    
  ▓▓░░░░░░░░░░▓▓  
 ▓▓░░██░░░░██░░▓▓ 
▓▓░░░░░░░░░░░░░░▓▓
▓▓░░██░░░░░░██░░▓▓
▓▓░░░░░░██░░░░░░▓▓
▓▓░░░░████░░░░░░▓▓
 ▓▓░░░░░░░░░░▓▓ 
  ▓▓▓▓▓▓▓▓▓▓▓▓  
                """
                
                self.edgar_sprite = tk.Label(sprite_frame, text=fallback_sprite,
                                           bg=RETRO_COLORS['black'],
                                           fg=RETRO_COLORS['bright_green'],
                                           font=(self.retro_font_family, 8, 'bold'))
            
            self.edgar_sprite.pack(side="left", padx=20)
            
            # Status indicator
            self.edgar_status = tk.Label(sprite_frame,
                                       text="STATUS: ● READY",
                                       bg=RETRO_COLORS['black'],
                                       fg=RETRO_COLORS['bright_yellow'],
                                       font=(self.retro_font_family, 14, 'bold'))
            self.edgar_status.pack(side="right", padx=20)
            
        except Exception as e:
            print(f"⚠️  Sprite area creation warning: {e}")
    
    def create_mode_panel(self, parent):
        """Create mode selection with fallbacks"""
        try:
            mode_frame = tk.LabelFrame(parent, text=" ▓ SCAN MODE (Choose Your Weapon) ▓ ",
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
                                   selectcolor=RETRO_COLORS['dark_green'],
                                   font=(self.retro_font_family, 10, 'bold'),
                                   command=self.on_mode_change)
                rb.grid(row=0, column=i, padx=20, pady=15, sticky="w")
                
        except Exception as e:
            print(f"⚠️  Mode panel creation warning: {e}")
    
    def create_year_panel(self, parent):
        """Create year selection with fallbacks"""
        try:
            year_frame = tk.LabelFrame(parent, text=" ▓ TARGET YEARS (Time Machine Settings) ▓ ",
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
                                   selectcolor=RETRO_COLORS['dark_yellow'],
                                   font=(self.retro_font_family, 12, 'bold'),
                                   command=self.on_year_change)
                cb.grid(row=0, column=i, padx=20, pady=15)
                
        except Exception as e:
            print(f"⚠️  Year panel creation warning: {e}")
    
    def create_directory_panel(self, parent):
        """Create directory management with fallbacks"""
        try:
            dir_frame = tk.LabelFrame(parent, text=" ▓ SCAN DIRECTORIES (Where The Files Live) ▓ ",
                                     bg=RETRO_COLORS['black'],
                                     fg=RETRO_COLORS['bright_green'],
                                     font=(self.retro_font_family, 10, 'bold'),
                                     bd=3, relief='raised')
            dir_frame.pack(fill="x", pady=5)
            
            # Directory list
            list_frame = tk.Frame(dir_frame, bg=RETRO_COLORS['black'])
            list_frame.pack(fill="both", expand=True, padx=15, pady=15)
            
            self.dir_listbox = tk.Listbox(list_frame,
                                         bg=RETRO_COLORS['black'],
                                         fg=RETRO_COLORS['bright_green'],
                                         selectbackground=RETRO_COLORS['dark_green'],
                                         font=(self.retro_font_family, 9, 'bold'),
                                         height=4)
            self.dir_listbox.pack(side="left", fill="both", expand=True)
            
            scrollbar = tk.Scrollbar(list_frame, bg=RETRO_COLORS['dark_green'])
            scrollbar.pack(side="right", fill="y")
            self.dir_listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=self.dir_listbox.yview)
            
            # Buttons
            btn_frame = tk.Frame(dir_frame, bg=RETRO_COLORS['black'])
            btn_frame.pack(fill="x", padx=15, pady=10)
            
            add_btn = tk.Button(btn_frame, text="▓▓▓ [ADD DIRECTORY] ▓▓▓",
                               bg=RETRO_COLORS['dark_green'], fg=RETRO_COLORS['bright_green'],
                               font=(self.retro_font_family, 10, 'bold'),
                               command=self.add_directory)
            add_btn.pack(side="left", padx=10)
            
            remove_btn = tk.Button(btn_frame, text="▓▓▓ [REMOVE] ▓▓▓",
                                  bg=RETRO_COLORS['dark_red'], fg=RETRO_COLORS['bright_red'],
                                  font=(self.retro_font_family, 10, 'bold'),
                                  command=self.remove_directory)
            remove_btn.pack(side="left", padx=10)
            
            # Add defaults
            self.selected_directories = []
            default_dirs = [str(Path.home() / "Documents"), str(Path.home() / "Desktop")]
            for dir_path in default_dirs:
                if os.path.exists(dir_path):
                    self.dir_listbox.insert("end", f"▓ {dir_path}")
                    self.selected_directories.append(dir_path)
                    
        except Exception as e:
            print(f"⚠️  Directory panel creation warning: {e}")
    
    def create_scan_panel(self, parent):
        """Create scan controls with fallbacks"""
        try:
            scan_frame = tk.LabelFrame(parent, text=" ▓ SCAN CONTROL (The Big Button) ▓ ",
                                      bg=RETRO_COLORS['black'],
                                      fg=RETRO_COLORS['bright_red'],
                                      font=(self.retro_font_family, 12, 'bold'),
                                      bd=3, relief='raised')
            scan_frame.pack(fill="x", pady=10)
            
            self.scan_btn = tk.Button(scan_frame, 
                                     text="▓▓▓ >>> INITIATE SCAN SEQUENCE <<< ▓▓▓",
                                     bg=RETRO_COLORS['dark_green'],
                                     fg=RETRO_COLORS['bright_green'],
                                     font=(self.retro_font_family, 16, 'bold'),
                                     height=3,
                                     command=self.start_scan)
            self.scan_btn.pack(side="left", padx=30, pady=15)
            
            self.stop_btn = tk.Button(scan_frame, 
                                     text="▓▓▓ [ABORT] ▓▓▓",
                                     bg=RETRO_COLORS['dark_red'],
                                     fg=RETRO_COLORS['bright_red'],
                                     font=(self.retro_font_family, 14, 'bold'),
                                     state="disabled",
                                     command=self.stop_scan)
            self.stop_btn.pack(side="right", padx=30, pady=15)
            
        except Exception as e:
            print(f"⚠️  Scan panel creation warning: {e}")
    
    def create_status_panel(self, parent):
        """Create status display with fallbacks"""
        try:
            status_frame = tk.LabelFrame(parent, text=" ▓ SYSTEM TERMINAL (The Matrix) ▓ ",
                                        bg=RETRO_COLORS['black'],
                                        fg=RETRO_COLORS['bright_cyan'],
                                        font=(self.retro_font_family, 10, 'bold'),
                                        bd=3, relief='raised')
            status_frame.pack(fill="both", expand=True, pady=5)
            
            terminal_frame = tk.Frame(status_frame, bg=RETRO_COLORS['black'])
            terminal_frame.pack(fill="both", expand=True, padx=15, pady=15)
            
            self.status_text = tk.Text(terminal_frame,
                                      bg=RETRO_COLORS['black'],
                                      fg=RETRO_COLORS['bright_green'],
                                      insertbackground=RETRO_COLORS['bright_green'],
                                      selectbackground=RETRO_COLORS['dark_green'],
                                      font=(self.retro_font_family, 9, 'bold'),
                                      height=15, width=150,
                                      wrap=tk.WORD)
            
            terminal_scrollbar = tk.Scrollbar(terminal_frame, bg=RETRO_COLORS['dark_green'])
            terminal_scrollbar.pack(side="right", fill="y")
            self.status_text.pack(side="left", fill="both", expand=True)
            
            self.status_text.config(yscrollcommand=terminal_scrollbar.set)
            terminal_scrollbar.config(command=self.status_text.yview)
            
            # Progress display
            self.progress_var = tk.StringVar()
            self.progress_label = tk.Label(status_frame,
                                          textvariable=self.progress_var,
                                          bg=RETRO_COLORS['black'],
                                          fg=RETRO_COLORS['bright_yellow'],
                                          font=(self.retro_font_family, 10, 'bold'))
            self.progress_label.pack(pady=5)
            
            # Initialize status
            self.log_message("▓▓▓ EDGAR 8-BIT EVIDENCE HUNTER ONLINE (Robust Edition) ▓▓▓")
            self.log_message("System Status: READY FOR RETRO ACTION!")
            
            if self.audio_enabled:
                self.log_message("Audio: 8-bit beeps ENABLED - prepare your ears!")
            else:
                self.log_message("Audio: Silent mode (pygame not available)")
                
            if SPRITES_AVAILABLE:
                self.log_message("Graphics: Full 8-bit sprites loaded!")
            else:
                self.log_message("Graphics: Fallback ASCII mode engaged!")
                
            self.log_message("Ready to scan files in maximum retro style!")
            self.progress_var.set("▓▓▓ STATUS: READY TO ROCK (robustly) ▓▓▓")
            
        except Exception as e:
            print(f"⚠️  Status panel creation warning: {e}")
    
    def create_fallback_gui(self):
        """Create minimal fallback GUI if main creation fails"""
        try:
            fallback_frame = tk.Frame(self.root, bg="#000000")
            fallback_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            error_label = tk.Label(fallback_frame, 
                                  text="Edgar Fallback Mode\\n\\nSome components failed to load,\\nbut basic functionality is available.",
                                  bg="#000000", fg="#FF0000",
                                  font=("Courier New", 14, 'bold'))
            error_label.pack(pady=50)
            
        except Exception as e:
            print(f"❌ Even fallback GUI failed: {e}")
    
    def log_message(self, message):
        """Log message with error handling"""
        try:
            timestamp = time.strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] ▓ {message}\\n"
            self.status_text.insert("end", log_entry)
            self.status_text.see("end")
            self.root.update_idletasks()
        except Exception as e:
            print(f"Log: {message}")  # Fallback to console
    
    def on_mode_change(self):
        """Handle mode change with audio feedback"""
        try:
            self.play_8bit_beep(800, 150)
            mode = self.mode_var.get()
            self.log_message(f"8-BIT MODE: {mode.upper()} selected!")
        except Exception as e:
            print(f"Mode change error: {e}")
    
    def on_year_change(self):
        """Handle year change with feedback"""
        try:
            self.play_8bit_beep(1000, 120)
            selected = [year for year, var in self.year_vars.items() if var.get()]
            self.selected_years = selected
            self.log_message(f"TIME MACHINE: Years {selected} locked in!")
        except Exception as e:
            print(f"Year change error: {e}")
    
    def add_directory(self):
        """Add directory with error handling"""
        try:
            directory = filedialog.askdirectory(title="Select Directory for 8-bit Scanning")
            if directory:
                self.dir_listbox.insert("end", f"▓ {directory}")
                self.selected_directories.append(directory)
                self.play_8bit_beep(1200, 200)
                self.log_message(f"DIRECTORY ACQUIRED: {directory}")
        except Exception as e:
            print(f"Add directory error: {e}")
    
    def remove_directory(self):
        """Remove directory with error handling"""
        try:
            selection = self.dir_listbox.curselection()
            if selection:
                index = selection[0]
                directory_display = self.dir_listbox.get(index)
                directory = directory_display.replace("▓ ", "")
                self.dir_listbox.delete(index)
                if directory in self.selected_directories:
                    self.selected_directories.remove(directory)
                self.play_8bit_beep(600, 200)
                self.log_message(f"DIRECTORY REMOVED: {directory}")
            else:
                self.log_message("No directory selected for removal!")
        except Exception as e:
            print(f"Remove directory error: {e}")
    
    def start_scan(self):
        """Start scan with robust error handling"""
        try:
            if not self.selected_directories:
                messagebox.showerror("Scan Error", "No directories selected!")
                return
                
            if not self.selected_years:
                messagebox.showerror("Scan Error", "No years selected!")
                return
            
            self.scanning = True
            self.scan_btn.config(state="disabled", text="▓▓▓ SCANNING... ▓▓▓")
            self.stop_btn.config(state="normal")
            
            self.play_8bit_beep(1200, 300)
            self.log_message("▓" * 60)
            self.log_message("8-BIT SCAN SEQUENCE INITIATED!")
            self.log_message("▓" * 60)
            
            # Start scan thread
            scan_thread = threading.Thread(target=self.run_scan, daemon=True)
            scan_thread.start()
            
        except Exception as e:
            print(f"Start scan error: {e}")
            self.log_message(f"SCAN START ERROR: {e}")
    
    def run_scan(self):
        """Run scan with comprehensive error handling"""
        try:
            # This is a simplified version - you can expand with actual scan logic
            self.log_message("Scan simulation running (replace with actual scan code)...")
            
            # Simulate scan progress
            for i in range(10):
                if not self.scanning:
                    break
                    
                self.log_message(f"Processing files... step {i+1}/10")
                self.progress_var.set(f"▓▓▓ SCANNING: Step {i+1}/10 ▓▓▓")
                self.play_8bit_beep(800 + i*50, 100)
                time.sleep(1)
            
            if self.scanning:
                self.log_message("▓▓▓ SCAN COMPLETE! ▓▓▓")
                self.log_message("Results would be saved to: results/")
                self.play_8bit_beep(1500, 500)
            
        except Exception as e:
            self.log_message(f"SCAN ERROR: {e}")
            print(f"Scan error: {e}")
            
        finally:
            # Reset UI
            self.scanning = False
            self.scan_btn.config(state="normal", text="▓▓▓ >>> INITIATE SCAN SEQUENCE <<< ▓▓▓")
            self.stop_btn.config(state="disabled")
            self.progress_var.set("▓▓▓ STATUS: READY FOR NEXT MISSION ▓▓▓")
    
    def stop_scan(self):
        """Stop scan with error handling"""
        try:
            self.scanning = False
            self.log_message("SCAN ABORTED BY USER!")
            self.play_8bit_beep(400, 400)
        except Exception as e:
            print(f"Stop scan error: {e}")
    
    def start_animations(self):
        """Start animations with error handling"""
        try:
            self.animate_edgar()
            if self.audio_enabled:
                self.play_8bit_beep(1000, 200)  # Startup beep
        except Exception as e:
            print(f"Animation start error: {e}")
    
    def animate_edgar(self):
        """Animate Edgar with error handling"""
        try:
            if not self.scanning and random.random() < 0.1:
                self.play_8bit_beep(random.randint(600, 800), 80)
                
            self.root.after(5000, self.animate_edgar)
        except Exception as e:
            print(f"Animation error: {e}")
    
    def run(self):
        """Run GUI with comprehensive error handling"""
        try:
            startup_msg = random.choice([
                "8-bit Edgar GUI initialized (robust edition)!",
                "Retro mode engaged with error handling!",
                "8-bit pixels loaded with fallback support!",
                "Edgar v1982 online - now crash-resistant!",
                "Welcome to the robust retro matrix!"
            ])
            self.log_message(startup_msg)
            self.log_message(random.choice(self.retro_messages))
            
            print("🎮 8-bit Edgar GUI is running...")
            print("   Close the window or press Ctrl+C to exit")
            
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\\n👋 Edgar GUI interrupted by user")
        except Exception as e:
            print(f"❌ GUI runtime error: {e}")
            messagebox.showerror("Runtime Error", f"GUI encountered an error:\\n{e}")

def main():
    """Main entry point with robust error handling"""
    print("🚀 Launching Edgar 8-bit GUI (Robust Edition)...")
    print("=" * 50)
    
    # System info
    print(f"Python: {sys.version}")
    print(f"Pygame: {'Available' if PYGAME_AVAILABLE else 'Not Available'}")
    print(f"Sprites: {'Available' if SPRITES_AVAILABLE else 'Fallback Mode'}")
    print()
    
    try:
        app = Edgar8BitGUIRobust()
        app.run()
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        print("\\nTrying diagnostic mode...")
        
        # Fallback diagnostic
        try:
            root = tk.Tk()
            root.title("Edgar Diagnostic")
            root.geometry("500x300")
            root.configure(bg="#000000")
            
            error_text = f"""Edgar 8-bit GUI Error
            
Error Details:
{str(e)}

System Info:
Python: {sys.version[:50]}...
Pygame: {'Available' if PYGAME_AVAILABLE else 'Not Available'}
Sprites: {'Available' if SPRITES_AVAILABLE else 'Fallback Mode'}

Suggestions:
1. Make sure you're running from the virtual environment
2. Install pygame: pip install pygame
3. Run the diagnostic script: python edgar_test_imports.py
            """
            
            label = tk.Label(root, text=error_text,
                           bg="#000000", fg="#FF0000",
                           font=("Courier New", 10),
                           justify="left")
            label.pack(padx=20, pady=20, fill="both", expand=True)
            
            root.mainloop()
            
        except Exception as e2:
            print(f"❌ Even diagnostic mode failed: {e2}")
            print("\\nPlease run: python edgar_test_imports.py")

if __name__ == "__main__":
    main()
