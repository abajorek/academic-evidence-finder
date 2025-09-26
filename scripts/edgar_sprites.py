#!/usr/bin/env python3
"""
Edgar 8-bit Sprite Collection
Classic gaming sprites for the Edgar Academic Evidence Scanner

"It's like, way more pixelated than it needs to be" - Strong Bad
"""

# 8-bit Edgar character sprites (16x16 character grid style)
EDGAR_NORMAL = """
    ████████████    
  ██░░░░░░░░░░██  
 ██░░██░░░░██░░██ 
██░░░░░░░░░░░░░░██
██░░██░░░░░░██░░██
██░░░░░░██░░░░░░██
██░░░░████░░░░░░██
 ██░░░░░░░░░░██ 
  ████████████  
    ██████████    
    ██      ██    
    ██      ██    
    ██      ██    
  ████      ████  
 ██          ██ 
██            ██
"""

EDGAR_SCANNING = """
    ████████████    
  ██░░░░░░░░░░██  
 ██░░██░░░░██░░██ 
██░░░░░░░░░░░░░░██
██░░░░░░░░░░░░░░██
██░░░░░░██░░░░░░██
██░░░░████░░░░░░██
 ██░░░░░░░░░░██ 
  ████████████  
    ██████████    
    ██〓〓〓〓██    
    ██〓〓〓〓██    
    ██      ██    
  ████      ████  
 ██          ██ 
██            ██
"""

EDGAR_COMPLETE = """
    ████████████    
  ██░░░░░░░░░░██  
 ██░░██░░░░██░░██ 
██░░░░░░░░░░░░░░██
██░░░░░░▲▲░░░░░░██
██░░░░░░██░░░░░░██
██░░░░████░░░░░░██
 ██░░░░░░░░░░██ 
  ████████████  
    ██████████    
    ██  ▲▲  ██    
    ██      ██    
    ██      ██    
  ████      ████  
 ██          ██ 
██            ██
"""

EDGAR_ERROR = """
    ████████████    
  ██░░░░░░░░░░██  
 ██░░██░░░░██░░██ 
██░░░░░░░░░░░░░░██
██░░XX░░░░░░XX░░██
██░░░░░░██░░░░░░██
██░░░░████░░░░░░██
 ██░░░░░░░░░░██ 
  ████████████  
    ██████████    
    ██  ××  ██    
    ██      ██    
    ██      ██    
  ████      ████  
 ██          ██ 
██            ██
"""

# Classic gaming UI elements
RETRO_BORDER_TOP = "╔═══════════════════════════════════════════════════════════════════════╗"
RETRO_BORDER_MID = "║                                                                       ║"
RETRO_BORDER_BOT = "╚═══════════════════════════════════════════════════════════════════════╝"

RETRO_BUTTON_NORMAL = "▓▓▓▓▓▓▓▓▓▓▓"
RETRO_BUTTON_PRESSED = "▒▒▒▒▒▒▒▒▒▒▒"
RETRO_BUTTON_DISABLED = "░░░░░░░░░░░"

# Gaming-style status indicators
STATUS_READY = "● READY"
STATUS_SCANNING = "◆ SCANNING"
STATUS_COMPLETE = "★ COMPLETE"
STATUS_ERROR = "✗ ERROR"
STATUS_WAITING = "◯ WAITING"

# Classic gaming color schemes (hex values for tkinter)
RETRO_COLORS = {
    'black': '#000000',
    'white': '#FFFFFF',
    'bright_green': '#00FF00',
    'bright_cyan': '#00FFFF', 
    'bright_magenta': '#FF00FF',
    'bright_yellow': '#FFFF00',
    'bright_red': '#FF0000',
    'bright_blue': '#0000FF',
    'dark_green': '#008000',
    'dark_cyan': '#008080',
    'dark_magenta': '#800080',
    'dark_yellow': '#808000',
    'dark_red': '#800000',
    'dark_blue': '#000080',
    'gray': '#808080',
    'dark_gray': '#404040'
}

# Retro gaming fonts (will search for these on system)
RETRO_FONTS = [
    "Consolas",
    "Monaco", 
    "DejaVu Sans Mono",
    "Liberation Mono",
    "Courier New",
    "monospace"
]

def get_retro_font():
    """Get the best available retro/monospace font"""
    import tkinter as tk
    import tkinter.font as tkFont
    
    root = tk.Tk()
    root.withdraw()  # Hide window
    
    available_fonts = tkFont.families()
    
    for font in RETRO_FONTS:
        if font in available_fonts:
            root.destroy()
            return font
    
    root.destroy()
    return "Courier New"  # Fallback

def create_pixel_font(size=12):
    """Create a pixelated-looking font configuration"""
    font_family = get_retro_font()
    return (font_family, size, "bold")

# Text styling for different UI elements
TITLE_STYLE = {
    'bg': RETRO_COLORS['black'],
    'fg': RETRO_COLORS['bright_cyan'],
    'font': create_pixel_font(14)
}

BUTTON_STYLE_NORMAL = {
    'bg': RETRO_COLORS['dark_green'],
    'fg': RETRO_COLORS['bright_green'], 
    'activebackground': RETRO_COLORS['bright_green'],
    'activeforeground': RETRO_COLORS['black'],
    'font': create_pixel_font(10),
    'relief': 'raised',
    'bd': 3
}

BUTTON_STYLE_DANGER = {
    'bg': RETRO_COLORS['dark_red'],
    'fg': RETRO_COLORS['bright_red'],
    'activebackground': RETRO_COLORS['bright_red'], 
    'activeforeground': RETRO_COLORS['black'],
    'font': create_pixel_font(10),
    'relief': 'raised',
    'bd': 3
}

LABEL_STYLE = {
    'bg': RETRO_COLORS['black'],
    'fg': RETRO_COLORS['bright_green'],
    'font': create_pixel_font(9)
}

STATUS_STYLE = {
    'bg': RETRO_COLORS['black'], 
    'fg': RETRO_COLORS['bright_yellow'],
    'font': create_pixel_font(8)
}

# ASCII art title screens (like your examples!)
EDGAR_TITLE_SCREEN = '''
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    ████████╗██╗  ██╗███████╗    ██╗   ██╗██╗██████╗██╗   ██╗███████╗ ║
║    ╚══██╔══╝██║  ██║██╔════╝    ██║   ██║██║██╔══██╗██║   ██║██╔════╝ ║
║       ██║   ███████║█████╗      ██║   ██║██║██████╔╝██║   ██║███████╗ ║
║       ██║   ██╔══██║██╔══╝      ╚██╗ ██╔╝██║██╔══██╗██║   ██║╚════██║ ║
║       ██║   ██║  ██║███████╗     ╚████╔╝ ██║██║  ██║╚██████╔╝███████║ ║
║       ╚═╝   ╚═╝  ╚═╝╚══════╝      ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ║
║                           HUNTER                                     ║
║                                                                      ║
║            ████████████                    ██████████████            ║
║          ██░░░░░░░░░░██                  ████            ████        ║
║         ██░░██░░░░██░░██                ██                  ██      ║
║        ██░░░░░░░░░░░░░░██              ██                    ██      ║
║        ██░░██░░░░░░██░░██              ██  ██████████████    ██      ║
║        ██░░░░░░██░░░░░░██              ██  ██          ██    ██      ║
║        ██░░░░████░░░░░░██              ██  ██          ██    ██      ║
║         ██░░░░░░░░░░██                 ██  ██████████████    ██      ║
║          ████████████                  ██                  ██        ║
║            ██████████                    ████            ████        ║
║            ██      ██                      ██████████████            ║
║            ██      ██                                                ║
║            ██      ██                                                ║
║          ████      ████                                              ║
║         ██          ██                                               ║
║        ██            ██                                              ║
║                                                                      ║
║                  programmed entirely in                              ║
║                   the dungeon of Castle Edgar                       ║
║                        by Edgar (c)1982                             ║
║                                                                      ║
║        "It's like, way more professional than it has any            ║
║                    right to be." - The Cheat                        ║
╚══════════════════════════════════════════════════════════════════════╝
'''

def get_edgar_sprite(state='normal'):
    """Get Edgar sprite based on current state"""
    sprites = {
        'normal': EDGAR_NORMAL,
        'scanning': EDGAR_SCANNING,
        'complete': EDGAR_COMPLETE,
        'error': EDGAR_ERROR
    }
    return sprites.get(state, EDGAR_NORMAL)

def colorize_sprite(sprite_text, fg_color='#00FF00', bg_color='#000000'):
    """Apply colors to sprite (for tkinter display)"""
    return {
        'text': sprite_text,
        'fg': fg_color,
        'bg': bg_color,
        'font': create_pixel_font(8),
        'justify': 'left'
    }
