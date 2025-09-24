#!/bin/bash
# Edgar Academic Evidence Scanner Setup
# "Because sometimes you need a script to run a script" - Strong Bad

echo "🎮 Setting up Edgar Academic Evidence Scanner..."
echo "   (The retro way to find your academic stuff)"

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
    echo "❌ Error: Run this script from the academic-evidence-finder directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [[ ! -d ".venv" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade pip and requirements
echo "⬇️  Installing requirements..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Check if pygame installed correctly
if python3 -c "import pygame" 2>/dev/null; then
    echo "🔊 Pygame installed successfully - authentic 80s beeps enabled!"
else
    echo "⚠️  Pygame installation might have issues - sounds may not work"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/edgar_gui.py
chmod +x scripts/scan.py
chmod +x scripts/scan_optimized.py

# Create output directory
mkdir -p out
mkdir -p results

echo ""
echo "✅ Edgar setup complete!"
echo ""
echo "🎯 To run Edgar GUI:"
echo "   python3 scripts/edgar_gui.py"
echo ""
echo "🔍 To run command-line scanner:"
echo "   python3 scripts/scan.py --help"
echo ""
echo "⚡ To run optimized two-pass scanner:"
echo "   python3 scripts/scan_optimized.py --help"
echo ""
echo "🎵 Note: Edgar GUI includes authentic 80s computer sounds"
echo "   because apparently that's what we do now."
echo ""
echo "Ready to scan some academic evidence! 🎉"
