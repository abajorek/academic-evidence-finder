#!/usr/bin/env python3
"""
Edgar Import Test & Debug Tool
Test all imports and diagnose issues

"Let's see what's broken this time" - Strong Bad
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test all required imports and report status"""
    print("🔧 Edgar Import Diagnostic Tool")
    print("=" * 50)
    
    # Python info
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Script Location: {Path(__file__).parent}")
    print()
    
    # Test basic imports
    imports_to_test = [
        ("tkinter", "GUI framework"),
        ("pygame", "8-bit audio effects"),
        ("threading", "background processing"), 
        ("subprocess", "scan execution"),
        ("pathlib", "file path handling"),
        ("time", "timing functions"),
        ("random", "randomization")
    ]
    
    print("📦 Testing Required Imports:")
    print("-" * 30)
    
    all_good = True
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {module:<12} - {description}")
        except ImportError as e:
            print(f"❌ {module:<12} - FAILED: {e}")
            all_good = False
    
    print()
    
    # Test custom module imports
    print("📁 Testing Edgar Modules:")
    print("-" * 25)
    
    script_dir = Path(__file__).parent
    edgar_modules = [
        ("edgar_sprites", "8-bit graphics and styling"),
        ("edgar_font_manager", "retro font management"),
        ("edgar_gui", "original GUI"),
        ("edgar_gui_8bit", "8-bit enhanced GUI")
    ]
    
    for module, description in edgar_modules:
        try:
            # Add script directory to path
            if str(script_dir) not in sys.path:
                sys.path.insert(0, str(script_dir))
            
            __import__(module)
            print(f"✅ {module:<18} - {description}")
        except ImportError as e:
            print(f"❌ {module:<18} - FAILED: {e}")
            all_good = False
        except Exception as e:
            print(f"⚠️  {module:<18} - WARNING: {e}")
    
    print()
    
    # Pygame specific test
    print("🎮 Pygame Detailed Test:")
    print("-" * 22)
    try:
        import pygame
        print(f"✅ Pygame Version: {pygame.version.ver}")
        print(f"✅ SDL Version: {pygame.version.SDL}")
        
        # Test mixer initialization
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("✅ Pygame mixer initialized successfully")
            pygame.mixer.quit()
        except Exception as e:
            print(f"⚠️  Pygame mixer issue: {e}")
            
    except ImportError as e:
        print(f"❌ Pygame not available: {e}")
        all_good = False
    
    print()
    
    # Summary
    if all_good:
        print("🎉 All imports successful! Edgar should work perfectly.")
    else:
        print("⚠️  Some imports failed. See details above.")
        print()
        print("🔧 SUGGESTED FIXES:")
        print("1. Make sure you're running from the virtual environment:")
        print("   cd /Users/andrewbajorek/Documents/GitHub/academic-evidence-finder")
        print("   source .venv/bin/activate")
        print("   python scripts/edgar_launcher.py")
        print()
        print("2. If pygame is missing:")
        print("   pip install pygame")
        print()
        print("3. If custom modules fail:")
        print("   Make sure all edgar_*.py files are in the scripts/ directory")
    
    return all_good

def run_simple_gui_test():
    """Run a simple GUI test without complex imports"""
    try:
        import tkinter as tk
        
        root = tk.Tk()
        root.title("Edgar Simple Test")
        root.geometry("400x200")
        root.configure(bg="#000000")
        
        label = tk.Label(root, text="Edgar GUI Test\\n\\nIf you see this, basic GUI works!\\nCheck console for import details.",
                        bg="#000000", fg="#00FF00",
                        font=("Courier New", 12))
        label.pack(expand=True)
        
        def close_test():
            print("✅ Simple GUI test completed successfully!")
            root.quit()
        
        btn = tk.Button(root, text="Close Test",
                       bg="#004400", fg="#00FF00",
                       command=close_test)
        btn.pack(pady=10)
        
        print("🖥️  Simple GUI test window opened...")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Simple GUI test failed: {e}")

if __name__ == "__main__":
    print("Starting Edgar diagnostic tests...\\n")
    
    # Run import tests
    imports_ok = test_imports()
    
    print("\\n" + "="*50)
    input("Press Enter to run simple GUI test...")
    
    # Run simple GUI test
    run_simple_gui_test()
