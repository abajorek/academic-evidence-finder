#!/usr/bin/env python3
"""
Edgar 8-bit Font Manager
Download and manage authentic retro gaming fonts

"It's like, way more pixelated than it has any right to be" - Strong Bad
"""

import tkinter as tk
import tkinter.font as tkFont
import os
import urllib.request
import zipfile
from pathlib import Path
import tempfile
import shutil

class RetroFontManager:
    def __init__(self):
        self.font_dir = Path.home() / ".edgar_fonts"
        self.font_dir.mkdir(exist_ok=True)
        
        # List of great free retro/pixel fonts with download URLs
        self.retro_fonts = {
            "Perfect DOS VGA 437": {
                "url": "https://www.dafont.com/perfect-dos-vga-437.font",
                "file": "PerfectDOSVGA437.ttf",
                "description": "Authentic DOS-style monospace font",
                "license": "Free for personal use"
            },
            "8-bit Operator": {
                "url": "https://www.dafont.com/8bit-operator.font", 
                "file": "8bitOperator.ttf",
                "description": "Classic 8-bit arcade style",
                "license": "Free"
            },
            "Pixel Millennium": {
                "url": "https://www.dafont.com/pixel-millennium.font",
                "file": "PixelMillennium.ttf", 
                "description": "Crisp pixel font perfect for UIs",
                "license": "Free for personal use"
            },
            "Press Start 2P": {
                "url": "https://fonts.google.com/specimen/Press+Start+2P",
                "file": "PressStart2P.ttf",
                "description": "Google Fonts 8-bit gaming font",
                "license": "SIL Open Font License"
            }
        }
        
        # System fonts that work well for retro look
        self.system_retro_fonts = [
            "Consolas",
            "Monaco", 
            "Menlo",
            "DejaVu Sans Mono",
            "Liberation Mono",
            "Lucida Console",
            "Courier New",
            "monospace"
        ]
    
    def get_available_retro_fonts(self):
        """Get list of available retro fonts on system"""
        root = tk.Tk()
        root.withdraw()
        
        available_fonts = list(tkFont.families())
        retro_available = []
        
        for font in self.system_retro_fonts:
            if font in available_fonts:
                retro_available.append(font)
        
        # Check for downloaded fonts
        for font_name, info in self.retro_fonts.items():
            font_path = self.font_dir / info["file"]
            if font_path.exists():
                retro_available.append(font_name)
        
        root.destroy()
        return retro_available
    
    def get_best_retro_font(self, preferred_size=12):
        """Get the best available retro font"""
        available = self.get_available_retro_fonts()
        
        # Priority order for best retro look
        priority_fonts = [
            "Perfect DOS VGA 437",
            "8-bit Operator", 
            "Press Start 2P",
            "Pixel Millennium",
            "Consolas",
            "Monaco",
            "Menlo",
            "DejaVu Sans Mono",
            "Courier New"
        ]
        
        for font in priority_fonts:
            if font in available:
                return self.create_font_config(font, preferred_size)
        
        # Fallback
        return ("Courier New", preferred_size, "bold")
    
    def create_font_config(self, font_name, size, weight="bold"):
        """Create a font configuration tuple"""
        return (font_name, size, weight)
    
    def install_google_font(self, font_name="Press Start 2P"):
        """Install Press Start 2P from Google Fonts (most reliable)"""
        try:
            # Google Fonts direct download URL for Press Start 2P
            url = "https://fonts.google.com/download?family=Press%20Start%202P"
            font_file = self.font_dir / "PressStart2P.ttf"
            
            if not font_file.exists():
                print(f"Downloading {font_name}...")
                urllib.request.urlretrieve(url, font_file)
                print(f"✅ {font_name} downloaded successfully!")
                return True
            else:
                print(f"✅ {font_name} already installed")
                return True
                
        except Exception as e:
            print(f"❌ Failed to download {font_name}: {e}")
            return False
    
    def create_font_showcase(self):
        """Create a window showing available retro fonts"""
        showcase = tk.Toplevel()
        showcase.title("Edgar's Retro Font Showcase")
        showcase.geometry("800x600")
        showcase.configure(bg="#000000")
        
        # Header
        header = tk.Label(showcase, text="Edgar's 8-bit Font Collection",
                         bg="#000000", fg="#00FFFF",
                         font=("Courier New", 16, "bold"))
        header.pack(pady=10)
        
        # Scrollable font list
        frame = tk.Frame(showcase, bg="#000000")
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Test text
        test_text = "▓▓▓ EDGAR ACADEMIC EVIDENCE SCANNER ▓▓▓\\n0123456789 ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        available_fonts = self.get_available_retro_fonts()
        
        for i, font_name in enumerate(available_fonts):
            try:
                font_config = self.create_font_config(font_name, 10)
                
                # Font name label
                name_label = tk.Label(frame, text=f"Font: {font_name}",
                                    bg="#000000", fg="#00FF00",
                                    font=("Courier New", 9))
                name_label.pack(anchor="w", pady=(10, 2))
                
                # Sample text with the font
                sample_label = tk.Label(frame, text=test_text,
                                      bg="#000000", fg="#FFFF00", 
                                      font=font_config,
                                      justify="left")
                sample_label.pack(anchor="w", padx=20, pady=2)
                
                # Separator
                separator = tk.Label(frame, text="─" * 80,
                                   bg="#000000", fg="#404040",
                                   font=("Courier New", 8))
                separator.pack(pady=2)
                
            except Exception as e:
                error_label = tk.Label(frame, text=f"❌ {font_name}: Error loading",
                                     bg="#000000", fg="#FF0000",
                                     font=("Courier New", 9))
                error_label.pack(anchor="w", pady=2)
        
        # Close button
        close_btn = tk.Button(showcase, text="▓▓▓ [CLOSE] ▓▓▓",
                             bg="#440000", fg="#FF0000",
                             font=("Courier New", 10, "bold"),
                             command=showcase.destroy)
        close_btn.pack(pady=10)
        
        return showcase

    def suggest_font_installation(self):
        """Provide font installation suggestions"""
        suggestions = """
▓▓▓ EDGAR'S RETRO FONT INSTALLATION GUIDE ▓▓▓

For the most authentic 8-bit experience, install these fonts:

🎮 RECOMMENDED FONTS:
1. "Press Start 2P" (Google Fonts) - Classic arcade font
   → https://fonts.google.com/specimen/Press+Start+2P
   
2. "Perfect DOS VGA 437" (DaFont) - Authentic DOS terminal
   → https://www.dafont.com/perfect-dos-vga-437.font
   
3. "8-bit Operator" (DaFont) - Clean pixel font
   → https://www.dafont.com/8bit-operator.font

🔧 INSTALLATION INSTRUCTIONS:
   macOS: Download .ttf files and double-click to install
   Windows: Download .ttf files, right-click > Install
   Linux: Copy .ttf files to ~/.fonts/ directory

🎯 CURRENT BEST AVAILABLE:
"""
        
        available = self.get_available_retro_fonts()
        for font in available[:5]:  # Show top 5
            suggestions += f"   ✅ {font}\\n"
        
        suggestions += """
💡 TIP: After installing new fonts, restart Edgar for them to appear!

🎨 FALLBACK FONTS (already available):
   • Consolas (Windows/Office)
   • Monaco (macOS)
   • DejaVu Sans Mono (Linux)
   • Courier New (Universal)
"""
        
        return suggestions

def test_retro_fonts():
    """Test function to display font showcase"""
    font_manager = RetroFontManager()
    
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Show font showcase
    showcase = font_manager.create_font_showcase()
    
    # Add suggestion button
    def show_suggestions():
        suggestions = font_manager.suggest_font_installation()
        suggestion_window = tk.Toplevel()
        suggestion_window.title("Font Installation Guide")
        suggestion_window.geometry("700x500")
        suggestion_window.configure(bg="#000000")
        
        text_widget = tk.Text(suggestion_window,
                             bg="#000000", fg="#00FF00",
                             font=("Courier New", 10),
                             wrap=tk.WORD)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", suggestions)
        text_widget.config(state="disabled")
    
    info_btn = tk.Button(showcase, text="▓▓▓ [INSTALLATION GUIDE] ▓▓▓",
                        bg="#004400", fg="#00FF00",
                        font=("Courier New", 10, "bold"),
                        command=show_suggestions)
    info_btn.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_retro_fonts()
