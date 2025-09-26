#!/usr/bin/env python3
"""
Edgar 8-bit GUI Launcher & Font Tester
Launch the enhanced 8-bit GUI with font management

"It's like, a launcher for a launcher. Very meta." - Strong Bad
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

def launch_8bit_gui():
    """Launch the main 8-bit Edgar GUI"""
    try:
        from edgar_gui_8bit import Edgar8BitGUI
        print("🎮 Launching Edgar 8-bit GUI...")
        app = Edgar8BitGUI()
        app.run()
    except ImportError as e:
        messagebox.showerror("Import Error", 
                           f"Could not import 8-bit GUI module:\\n{e}\\n\\nMake sure edgar_gui_8bit.py is in the same directory.")
    except Exception as e:
        messagebox.showerror("Launch Error", 
                           f"Error launching 8-bit GUI:\\n{e}")

def launch_font_tester():
    """Launch the font showcase and manager"""
    try:
        from edgar_font_manager import test_retro_fonts
        print("🔤 Launching font showcase...")
        test_retro_fonts()
    except ImportError as e:
        messagebox.showerror("Import Error", 
                           f"Could not import font manager:\\n{e}\\n\\nMake sure edgar_font_manager.py is in the same directory.")
    except Exception as e:
        messagebox.showerror("Font Error", 
                           f"Error launching font tester:\\n{e}")

def launch_original_gui():
    """Launch the original Edgar GUI for comparison"""
    try:
        from edgar_gui import EdgarGUI
        print("🖥️  Launching original Edgar GUI...")
        app = EdgarGUI()
        app.run()
    except ImportError as e:
        messagebox.showerror("Import Error", 
                           f"Could not import original GUI module:\\n{e}\\n\\nMake sure edgar_gui.py is in the same directory.")
    except Exception as e:
        messagebox.showerror("Launch Error", 
                           f"Error launching original GUI:\\n{e}")

def create_launcher_gui():
    """Create the main launcher interface"""
    launcher = tk.Tk()
    launcher.title("Edgar GUI Launcher - Choose Your Adventure")
    launcher.geometry("600x500")
    launcher.configure(bg="#000000")
    launcher.resizable(False, False)
    
    # Header
    header_text = """
╔══════════════════════════════════════════════════════════╗
║                    EDGAR GUI LAUNCHER                     ║
║                                                          ║
║                  Choose Your Experience:                 ║
╚══════════════════════════════════════════════════════════╝
    """
    
    header = tk.Label(launcher, text=header_text,
                     bg="#000000", fg="#00FFFF", 
                     font=("Courier New", 10, "bold"),
                     justify="left")
    header.pack(pady=20)
    
    # Button styling
    button_style = {
        'font': ("Courier New", 12, "bold"),
        'width': 40,
        'height': 2,
        'relief': 'raised',
        'bd': 3
    }
    
    # 8-bit GUI button (main attraction)
    gui_8bit_btn = tk.Button(launcher, text="🎮 LAUNCH 8-BIT EDGAR GUI",
                            bg="#004400", fg="#00FF00",
                            activebackground="#00FF00", activeforeground="#000000",
                            command=launch_8bit_gui,
                            **button_style)
    gui_8bit_btn.pack(pady=10)
    
    # Font tester button
    font_btn = tk.Button(launcher, text="🔤 FONT SHOWCASE & MANAGER",
                        bg="#000044", fg="#0000FF", 
                        activebackground="#0000FF", activeforeground="#FFFFFF",
                        command=launch_font_tester,
                        **button_style)
    font_btn.pack(pady=10)
    
    # Original GUI button (for comparison)
    gui_original_btn = tk.Button(launcher, text="🖥️  LAUNCH ORIGINAL GUI",
                                bg="#404000", fg="#FFFF00",
                                activebackground="#FFFF00", activeforeground="#000000", 
                                command=launch_original_gui,
                                **button_style)
    gui_original_btn.pack(pady=10)
    
    # Info section
    info_text = """
ℹ️  ABOUT THE 8-BIT VERSION:
• Full retro gaming aesthetic with pixelated Edgar sprites
• Authentic 8-bit colors (bright cyans, magentas, greens)
• Enhanced sound effects and gaming-style UI elements
• Same functionality as original, but with maximum style!

💡 FONT TIP:
• Use the Font Showcase to see available retro fonts
• Install "Press Start 2P" or "Perfect DOS VGA 437" for best results
• Restart Edgar after installing new fonts
    """
    
    info_label = tk.Label(launcher, text=info_text,
                         bg="#000000", fg="#FFFF00",
                         font=("Courier New", 9),
                         justify="left")
    info_label.pack(pady=20, padx=20)
    
    # Exit button
    exit_btn = tk.Button(launcher, text="❌ EXIT",
                        bg="#440000", fg="#FF0000",
                        activebackground="#FF0000", activeforeground="#FFFFFF",
                        font=("Courier New", 10, "bold"),
                        width=15, height=1,
                        command=launcher.quit)
    exit_btn.pack(pady=10)
    
    return launcher

def main():
    """Main launcher function"""
    print("🚀 Edgar GUI Launcher starting...")
    
    # Check if we're in the right directory
    script_dir = Path(__file__).parent
    required_files = ["edgar_gui_8bit.py", "edgar_sprites.py", "edgar_font_manager.py"]
    
    missing_files = []
    for file in required_files:
        if not (script_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Warning: Missing files: {missing_files}")
        print("Some features may not work correctly.")
    
    # Launch the launcher GUI
    launcher = create_launcher_gui()
    launcher.mainloop()
    
    print("👋 Edgar GUI Launcher exiting...")

if __name__ == "__main__":
    main()
