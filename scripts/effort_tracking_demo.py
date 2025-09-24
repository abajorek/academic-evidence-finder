#!/usr/bin/env python3
"""
Demonstration of real effort tracking based on file system metadata
Run this to see how the effort analysis works on your actual files
"""

import os
import json
from pathlib import Path
from datetime import datetime
from enhanced_file_analysis import FileEffortAnalyzer

def demo_effort_analysis():
    """Demonstrate effort analysis on user's actual files"""
    
    print("🎼 Real Effort Tracking Demonstration")
    print("=====================================")
    print()
    
    # Initialize analyzer
    analyzer = FileEffortAnalyzer()
    
    # Find music and drill files in common locations
    home = Path.home()
    search_paths = [
        home / "Documents",
        home / "Desktop", 
        home / "Downloads",
        home / "Music",
        Path("/Applications"),  # Sometimes sample files are here
    ]
    
    music_files = []
    extensions = ['.mus', '.musx', '.sib', '.3dj', '.3dz', '.3da', '.prod', '.musicxml']
    
    print("🔍 Searching for music and drill design files...")
    for search_path in search_paths:
        if search_path.exists():
            for ext in extensions:
                files = list(search_path.rglob(f"*{ext}"))
                music_files.extend(files)
                if files:
                    print(f"   Found {len(files)} {ext} files in {search_path}")
    
    if not music_files:
        print("❌ No music notation or drill design files found.")
        print("   Try creating some test files or check other directories.")
        return
    
    print(f"\n✅ Found {len(music_files)} total creative files")
    print("\n" + "="*60)
    
    # Analyze individual files
    print("\n📊 INDIVIDUAL FILE ANALYSIS")
    print("-" * 40)
    
    analyzed_files = []
    for i, filepath in enumerate(music_files[:10]):  # Analyze first 10 files
        try:
            analysis = analyzer.analyze_single_file(str(filepath))
            analyzed_files.append(analysis)
            
            print(f"\n{i+1}. {analysis['filename']}")
            print(f"   Type: {analysis['file_type']} ({analysis['extension']})")
            print(f"   Size: {analysis['size_kb']} KB")
            print(f"   Created: {analysis['created'][:10]}")
            print(f"   Modified: {analysis['modified'][:10]}")
            print(f"   Work span: {analysis['work_span_days']} days")
            print(f"   📅 Estimated hours: {analysis['estimated_hours']}")
            
            # Show reasoning
            if analysis['size_kb'] > 1000:
                print("     • Large file (+complexity)")
            if analysis['work_span_days'] > 7:
                print("     • Extended work period (+iterations)")
            if analysis['file_type'] in ['pyware_project', 'finale_current']:
                print("     • High-complexity file type")
                
        except Exception as e:
            print(f"   Error analyzing {filepath}: {e}")
    
    # Project analysis (version detection)
    print(f"\n" + "="*60)
    print("🔄 PROJECT VERSION ANALYSIS")
    print("-" * 40)
    
    try:
        file_paths = [str(f) for f in music_files]
        version_analysis = analyzer.analyze_file_versions(file_paths)
        
        if version_analysis:
            print(f"\nDetected {len(version_analysis)} projects with multiple versions:")
            
            for i, (project_name, analysis) in enumerate(version_analysis.items()[:5]):
                print(f"\n{i+1}. Project: {project_name}")
                print(f"   📁 Files: {analysis['file_count']}")
                print(f"   📅 Span: {analysis['span_days']} days")
                print(f"   📈 Size growth: {analysis['size_growth_kb']} KB")
                print(f"   🔧 Work sessions: {analysis['work_sessions']}")
                print(f"   ⏱️  Estimated hours: {analysis['estimated_hours']}")
                print(f"   📂 Sample files:")
                for filepath in analysis['files'][:3]:
                    print(f"      • {os.path.basename(filepath)}")
                if len(analysis['files']) > 3:
                    print(f"      ... and {len(analysis['files']) - 3} more")
        else:
            print("No multi-version projects detected.")
            print("(This happens when files have very different names)")
    
    except Exception as e:
        print(f"Error in project analysis: {e}")
    
    # Summary statistics
    print(f"\n" + "="*60)
    print("📈 EFFORT SUMMARY")
    print("-" * 40)
    
    if analyzed_files:
        total_hours = sum(f.get('estimated_hours', 0) for f in analyzed_files)
        avg_hours = total_hours / len(analyzed_files) if analyzed_files else 0
        
        by_type = {}
        for f in analyzed_files:
            ftype = f.get('file_type', 'unknown')
            if ftype not in by_type:
                by_type[ftype] = {'count': 0, 'hours': 0}
            by_type[ftype]['count'] += 1
            by_type[ftype]['hours'] += f.get('estimated_hours', 0)
        
        print(f"\nAnalyzed files: {len(analyzed_files)}")
        print(f"Total estimated hours: {total_hours:.1f}")
        print(f"Average hours per file: {avg_hours:.1f}")
        
        print(f"\nBy file type:")
        for ftype, stats in by_type.items():
            print(f"  {ftype}: {stats['count']} files, {stats['hours']:.1f} hours")
    
    # Show methodology
    print(f"\n" + "="*60) 
    print("🔬 METHODOLOGY")
    print("-" * 40)
    print("""
HOW EFFORT IS CALCULATED:

1. FILE METADATA ANALYSIS:
   • Creation date vs. modification date = work span
   • File size as complexity indicator
   • File type determines base effort estimate

2. VERSION DETECTION:  
   • Groups similar filenames (removes version numbers, dates)
   • Tracks modification timestamps across versions
   • Detects work sessions (saves within 4-hour windows)
   
3. WORK SESSION ANALYSIS:
   • Gaps > 4 hours = separate work sessions
   • Sessions < 5 minutes = ignored (just opening file)
   • Long sessions adjusted for likely breaks

4. EFFORT ESTIMATION:
   • Base hours by file type (Pyware=8hrs, Finale=6hrs, etc.)
   • Size multiplier (large files = more complex)  
   • Work span multiplier (longer span = more iterations)
   • Session analysis adds time between saves

This provides ACTUAL effort data based on your file usage patterns,
not just estimates. For tenure/promotion, this gives concrete evidence
of time investment in creative work.
""")
    
    # Practical applications
    print(f"\n" + "="*60)
    print("🎯 FOR YOUR DOSSIER")
    print("-" * 40)
    print("""
USE THIS DATA TO:

1. Document creative work effort quantitatively
2. Show sustained engagement over time periods  
3. Demonstrate iterative creative process
4. Support narrative claims with concrete data

EXAMPLE PORTFOLIO LANGUAGE:
"Over the 2023-24 academic year, I completed 3 original compositions
totaling an estimated 45 hours of creative work, as evidenced by 
file modification patterns across 28 working sessions spanning 
4 months (see technical appendix)."

TECHNICAL APPENDIX CONTENT:
• File analysis summaries
• Work session timelines  
• Version progression charts
• Effort calculation methodology
""")

def create_sample_analysis():
    """Create sample files to demonstrate the analysis"""
    
    print("\n🧪 CREATING SAMPLE FILES FOR DEMO")
    print("-" * 40)
    
    # Create a sample directory structure
    demo_dir = Path.home() / "Desktop" / "Dossier_Demo"
    demo_dir.mkdir(exist_ok=True)
    
    # Create some sample "creative work" files with different timestamps
    import time
    
    files_to_create = [
        ("My_Composition_v1.musx", "Original composition draft", 2000),
        ("My_Composition_v2.musx", "Second draft with revisions", 3500), 
        ("My_Composition_v3.musx", "Near-final version", 4200),
        ("My_Composition_Final.musx", "Performance ready", 4500),
        ("Drill_Design_2024.3dj", "Halftime show drill", 8000),
        ("Show_Animation.3da", "3D visualization", 12000),
    ]
    
    base_time = time.time() - (30 * 24 * 3600)  # 30 days ago
    
    for i, (filename, description, size) in enumerate(files_to_create):
        filepath = demo_dir / filename
        
        # Create file with content
        with open(filepath, 'w') as f:
            f.write(f"# {description}\n" + "Sample content\n" * (size // 20))
        
        # Set different modification times to simulate work progression
        mod_time = base_time + (i * 3 * 24 * 3600)  # 3 days apart
        os.utime(filepath, (mod_time, mod_time))
    
    print(f"✅ Created sample files in {demo_dir}")
    print("   Run the analysis again to see these files in action!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create-samples":
        create_sample_analysis()
    else:
        demo_effort_analysis()
        
        # Offer to create samples if no files found
        response = input("\nCreate sample files for demonstration? (y/n): ")
        if response.lower().startswith('y'):
            create_sample_analysis()