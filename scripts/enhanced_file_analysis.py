#!/usr/bin/env python3
"""
Enhanced file analysis with real effort tracking for music/drill design files
Add this to your existing scripts/ folder
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import re

class FileEffortAnalyzer:
    """Analyze actual file effort based on filesystem metadata"""
    
    def __init__(self):
        # Music and drill design file extensions
        self.creative_extensions = {
            # Finale music notation
            '.mus': 'finale_legacy',
            '.musx': 'finale_current', 
            '.ftm': 'finale_template',
            '.ftmx': 'finale_template_current',
            
            # Sibelius music notation  
            '.sib': 'sibelius',
            
            # Pyware drill design
            '.3dj': 'pyware_project',
            '.3dz': 'pyware_compressed',
            '.3da': 'pyware_animation',
            '.prod': 'pyware_production',
            
            # Other music formats
            '.musicxml': 'musicxml',
            '.mxl': 'musicxml_compressed',
            '.mid': 'midi',
            '.midi': 'midi',
            
            # Generic creative files
            '.pdf': 'document',
            '.docx': 'document', 
            '.pptx': 'presentation',
            '.xlsx': 'spreadsheet'
        }
        
        # Work session parameters
        self.max_session_gap_hours = 4  # Max gap between saves in same session
        self.min_work_minutes = 5       # Minimum time to count as work
        self.typical_save_intervals = {
            'finale_current': 15,    # Minutes between typical saves
            'finale_legacy': 20,
            'sibelius': 15,
            'pyware_project': 10,    # Drill design = frequent saves
            'pyware_compressed': 30, # Final exports = less frequent
            'document': 10,
            'presentation': 20,
            'spreadsheet': 15
        }

    def extract_pyware_metadata(self, filepath):
        """Extract metadata from Pyware files (drill design info)"""
        try:
            # Pyware files are binary, but we can extract some basic info
            # from filename patterns and file size progression
            filename = os.path.basename(filepath)
            
            # Common Pyware naming patterns
            patterns = {
                'show_name': r'([A-Za-z\s]+)[\d_-]',
                'movement': r'(mvmt?\s?\d+|movement\s?\d+)',
                'version': r'(v\d+|version\s?\d+)',
                'date': r'(\d{4}[-_]\d{2}[-_]\d{2})'
            }
            
            metadata = {'filename': filename, 'type': 'drill_design'}
            
            for key, pattern in patterns.items():
                match = re.search(pattern, filename, re.IGNORECASE)
                if match:
                    metadata[key] = match.group(1)
            
            return metadata
        except:
            return {'filename': os.path.basename(filepath), 'type': 'drill_design'}

    def extract_finale_metadata(self, filepath):
        """Extract metadata from Finale files"""
        try:
            # For now, extract from filename patterns
            # Could be enhanced to read actual Finale metadata
            filename = os.path.basename(filepath)
            
            patterns = {
                'piece_title': r'^([^_\d]+)',
                'movement': r'(mvmt?\s?\d+|movement\s?\d+)',
                'version': r'(v\d+|version\s?\d+)',
                'instrument': r'(score|parts?|piano|vocal)',
                'date': r'(\d{4}[-_]\d{2}[-_]\d{2})'
            }
            
            metadata = {'filename': filename, 'type': 'musical_score'}
            
            for key, pattern in patterns.items():
                match = re.search(pattern, filename, re.IGNORECASE)
                if match:
                    metadata[key] = match.group(1)
            
            return metadata
        except:
            return {'filename': os.path.basename(filepath), 'type': 'musical_score'}

    def analyze_file_versions(self, file_paths):
        """Group files by likely project and analyze version progression"""
        projects = defaultdict(list)
        
        for filepath in file_paths:
            # Group by base name (removing version numbers, dates, etc.)
            base_name = self._get_project_base_name(filepath)
            projects[base_name].append(filepath)
        
        version_analysis = {}
        
        for project, files in projects.items():
            if len(files) <= 1:
                continue
                
            # Sort by modification time
            files_with_stats = []
            for f in files:
                try:
                    stat = os.stat(f)
                    files_with_stats.append({
                        'path': f,
                        'mtime': stat.st_mtime,
                        'size': stat.st_size,
                        'ctime': stat.st_ctime
                    })
                except:
                    continue
            
            files_with_stats.sort(key=lambda x: x['mtime'])
            
            if len(files_with_stats) > 1:
                version_analysis[project] = self._analyze_work_progression(files_with_stats)
        
        return version_analysis

    def _get_project_base_name(self, filepath):
        """Extract likely project name from file path"""
        filename = os.path.basename(filepath)
        name = os.path.splitext(filename)[0]
        
        # Remove common version indicators
        patterns_to_remove = [
            r'_v\d+$', r'_version_?\d+$', r'_\d{4}[-_]\d{2}[-_]\d{2}$',
            r'_copy$', r'_final$', r'_draft$', r'_backup$',
            r'\s+\(\d+\)$'  # (1), (2), etc from duplicates
        ]
        
        for pattern in patterns_to_remove:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        return name.strip()

    def _analyze_work_progression(self, files_with_stats):
        """Analyze work progression through file versions"""
        if len(files_with_stats) < 2:
            return {}
        
        first_file = files_with_stats[0]
        last_file = files_with_stats[-1]
        
        total_span_days = (last_file['mtime'] - first_file['mtime']) / 86400
        size_growth = last_file['size'] - first_file['size'] 
        
        # Detect work sessions
        sessions = self._detect_work_sessions([f['mtime'] for f in files_with_stats])
        
        return {
            'file_count': len(files_with_stats),
            'span_days': round(total_span_days, 1),
            'size_growth_bytes': size_growth,
            'size_growth_kb': round(size_growth / 1024, 1),
            'work_sessions': len(sessions),
            'estimated_hours': self._estimate_work_hours(sessions, files_with_stats),
            'first_created': datetime.fromtimestamp(first_file['ctime']).isoformat(),
            'last_modified': datetime.fromtimestamp(last_file['mtime']).isoformat(),
            'files': [f['path'] for f in files_with_stats]
        }

    def _detect_work_sessions(self, timestamps):
        """Detect work sessions from file modification timestamps"""
        if len(timestamps) < 2:
            return []
        
        sessions = []
        current_session_start = timestamps[0]
        current_session_end = timestamps[0]
        
        for i in range(1, len(timestamps)):
            time_gap_hours = (timestamps[i] - current_session_end) / 3600
            
            if time_gap_hours <= self.max_session_gap_hours:
                # Continue current session
                current_session_end = timestamps[i]
            else:
                # Start new session
                if current_session_end - current_session_start >= 300:  # 5+ minutes
                    sessions.append({
                        'start': current_session_start,
                        'end': current_session_end,
                        'duration_minutes': (current_session_end - current_session_start) / 60
                    })
                
                current_session_start = timestamps[i]
                current_session_end = timestamps[i]
        
        # Add final session
        if current_session_end - current_session_start >= 300:
            sessions.append({
                'start': current_session_start,
                'end': current_session_end,  
                'duration_minutes': (current_session_end - current_session_start) / 60
            })
        
        return sessions

    def _estimate_work_hours(self, sessions, files_with_stats):
        """Estimate actual work hours from sessions and save patterns"""
        if not sessions:
            return 0
        
        total_minutes = 0
        
        for session in sessions:
            session_minutes = session['duration_minutes']
            
            # For very long sessions, assume some idle time
            if session_minutes > 180:  # 3+ hours
                # Assume 70% active work for long sessions
                session_minutes *= 0.7
            elif session_minutes > 60:  # 1-3 hours  
                # Assume 85% active work
                session_minutes *= 0.85
            
            total_minutes += session_minutes
        
        # Add time for sessions that were likely longer than last save
        # (work continued after last save)
        if sessions:
            file_type = self._guess_file_type(files_with_stats[0]['path'])
            typical_interval = self.typical_save_intervals.get(file_type, 15)
            
            # Add typical interval to each session 
            total_minutes += len(sessions) * typical_interval
        
        return round(total_minutes / 60, 1)

    def _guess_file_type(self, filepath):
        """Guess file type from extension"""
        ext = os.path.splitext(filepath)[1].lower()
        return self.creative_extensions.get(ext, 'document')

    def analyze_single_file(self, filepath):
        """Analyze a single file for effort indicators"""
        try:
            stat = os.stat(filepath)
            ext = os.path.splitext(filepath)[1].lower()
            file_type = self._guess_file_type(filepath)
            
            analysis = {
                'path': filepath,
                'filename': os.path.basename(filepath),
                'file_type': file_type,
                'extension': ext,
                'size_kb': round(stat.st_size / 1024, 1),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'work_span_days': round((stat.st_mtime - stat.st_ctime) / 86400, 1)
            }
            
            # Extract specific metadata based on file type
            if ext in ['.3dj', '.3dz', '.3da', '.prod']:
                analysis['metadata'] = self.extract_pyware_metadata(filepath)
                analysis['category'] = 'Creative Works'
                analysis['subcategory'] = 'Drill Design'
                
            elif ext in ['.mus', '.musx', '.sib']:
                analysis['metadata'] = self.extract_finale_metadata(filepath)
                analysis['category'] = 'Creative Works' 
                analysis['subcategory'] = 'Musical Composition'
                
            elif ext in ['.musicxml', '.mxl']:
                analysis['category'] = 'Creative Works'
                analysis['subcategory'] = 'Musical Score'
                
            # Estimate effort based on file characteristics
            analysis['estimated_hours'] = self._estimate_single_file_effort(analysis)
            
            return analysis
            
        except Exception as e:
            return {'path': filepath, 'error': str(e)}

    def _estimate_single_file_effort(self, analysis):
        """Estimate effort for single file based on characteristics"""
        base_hours = 1.0
        
        # Base effort by file type
        effort_multipliers = {
            'pyware_project': 8.0,     # Drill design is time-intensive
            'pyware_compressed': 12.0,  # Finalized shows = even more work
            'finale_current': 6.0,     # Music composition/arrangement  
            'finale_legacy': 6.0,
            'sibelius': 6.0,
            'musicxml': 2.0,           # Usually exports/imports
            'document': 2.0,
            'presentation': 4.0,
            'spreadsheet': 3.0
        }
        
        base_hours = effort_multipliers.get(analysis['file_type'], 2.0)
        
        # Adjust for file size (larger = more complex)
        size_kb = analysis['size_kb']
        if size_kb > 5000:      # > 5MB
            base_hours *= 2.0
        elif size_kb > 1000:    # > 1MB  
            base_hours *= 1.5
        elif size_kb > 500:     # > 500KB
            base_hours *= 1.2
        
        # Adjust for work span (longer span = more iterations)
        work_span = analysis['work_span_days']
        if work_span > 30:      # > 1 month of work
            base_hours *= 1.8
        elif work_span > 7:     # > 1 week
            base_hours *= 1.3
        elif work_span > 1:     # > 1 day
            base_hours *= 1.1
        
        return round(base_hours, 1)

    def generate_effort_report(self, file_paths, output_dir):
        """Generate comprehensive effort analysis report"""
        
        print("🔍 Analyzing file effort patterns...")
        
        # Analyze individual files
        individual_analyses = []
        for filepath in file_paths:
            ext = os.path.splitext(filepath)[1].lower()
            if ext in self.creative_extensions:
                analysis = self.analyze_single_file(filepath)
                if 'error' not in analysis:
                    individual_analyses.append(analysis)
        
        # Analyze version progressions
        print("📁 Detecting project versions...")
        version_analysis = self.analyze_file_versions(file_paths)
        
        # Generate summary statistics
        summary = self._generate_effort_summary(individual_analyses, version_analysis)
        
        # Write detailed reports
        os.makedirs(output_dir, exist_ok=True)
        
        # Individual file analysis
        with open(os.path.join(output_dir, 'file_effort_analysis.json'), 'w') as f:
            json.dump(individual_analyses, f, indent=2)
        
        # Project version analysis  
        with open(os.path.join(output_dir, 'project_analysis.json'), 'w') as f:
            json.dump(version_analysis, f, indent=2)
        
        # Summary report
        with open(os.path.join(output_dir, 'effort_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary

    def _generate_effort_summary(self, individual_analyses, version_analysis):
        """Generate summary of effort analysis"""
        
        total_files = len(individual_analyses)
        total_estimated_hours = sum(f.get('estimated_hours', 0) for f in individual_analyses)
        
        # Group by file type
        by_type = defaultdict(list)
        for analysis in individual_analyses:
            by_type[analysis['file_type']].append(analysis)
        
        type_summaries = {}
        for file_type, files in by_type.items():
            type_summaries[file_type] = {
                'count': len(files),
                'total_hours': sum(f.get('estimated_hours', 0) for f in files),
                'avg_hours_per_file': round(sum(f.get('estimated_hours', 0) for f in files) / len(files), 1) if files else 0,
                'total_size_mb': round(sum(f.get('size_kb', 0) for f in files) / 1024, 1),
                'files': [f['filename'] for f in files[:5]]  # Sample filenames
            }
        
        # Project analysis summary
        project_summary = {
            'total_projects': len(version_analysis),
            'total_project_hours': sum(p.get('estimated_hours', 0) for p in version_analysis.values()),
            'avg_files_per_project': round(sum(p.get('file_count', 0) for p in version_analysis.values()) / len(version_analysis), 1) if version_analysis else 0,
            'projects_over_10_hours': len([p for p in version_analysis.values() if p.get('estimated_hours', 0) > 10])
        }
        
        return {
            'analysis_date': datetime.now().isoformat(),
            'total_files_analyzed': total_files,
            'total_estimated_hours': round(total_estimated_hours, 1),
            'by_file_type': type_summaries,
            'project_analysis': project_summary,
            'top_time_investments': sorted([
                {'name': name, 'hours': data.get('estimated_hours', 0), 'files': data.get('file_count', 1)}
                for name, data in version_analysis.items()
            ], key=lambda x: x['hours'], reverse=True)[:10]
        }

# Integration function to add to your existing scan.py
def analyze_creative_files_effort(rows, output_dir):
    """Analyze effort for creative files found in evidence scan"""
    
    analyzer = FileEffortAnalyzer()
    
    # Extract creative file paths from scan results
    creative_files = []
    for row in rows:
        if row.get('source') == 'files':
            filepath = row['path']
            ext = os.path.splitext(filepath)[1].lower()
            if ext in analyzer.creative_extensions:
                creative_files.append(filepath)
    
    if not creative_files:
        print("No creative files (Finale, Sibelius, Pyware) found in scan results.")
        return {}
    
    print(f"Found {len(creative_files)} creative files for effort analysis...")
    
    # Run effort analysis
    summary = analyzer.generate_effort_report(creative_files, output_dir)
    
    print(f"📊 Creative Work Effort Summary:")
    print(f"   Total files: {summary['total_files_analyzed']}")
    print(f"   Estimated hours: {summary['total_estimated_hours']}")
    print(f"   Projects identified: {summary['project_analysis']['total_projects']}")
    print(f"   Major projects (>10hrs): {summary['project_analysis']['projects_over_10_hours']}")
    
    return summary

# Usage: Add this call to your main scan.py after the evidence analysis
# effort_summary = analyze_creative_files_effort(rows, args.out)