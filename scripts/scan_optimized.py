#!/usr/bin/env python3
"""
Optimized two-pass academic evidence scanner
Pass 1: Metadata-only filtering into broad categories
Pass 2: Full text extraction and detailed analysis

"Because sometimes you need to sort the wheat from the chaff before you grind the wheat."
                                                                  - Strong Bad, probably
"""

import argparse, os, re, yaml, json, time
from pathlib import Path
from datetime import datetime, timezone
from tqdm import tqdm
from collections import Counter, defaultdict

class MetadataAnalyzer:
    """Fast metadata-only analysis for initial categorization"""
    
    def __init__(self, rules_config):
        self.config = rules_config
        self.load_metadata_rules()
        
        # Homestar-style commentary for different file types
        self.file_type_comments = {
            '.musx': "Finale file detected. Someone's been composing!",
            '.sib': "Sibelius file found. Fancy notation software user detected.",
            '.3dj': "Pyware drill design! Marching band magic happening here.",
            '.pdf': "PDF found. Could be anything. The mystery deepens.",
            '.docx': "Word document located. Probably has actual words in it.",
            '.pptx': "PowerPoint detected. Slides upon slides upon slides.",
            '.xlsx': "Spreadsheet discovered. Numbers and cells, oh my!"
        }
    
    def load_metadata_rules(self):
        """Load rules that can be applied to metadata only (the quick stuff)"""
        self.filename_patterns = {
            'teaching': [
                r'\\bsyllabus\\b', r'\\bassignment\\b', r'\\bexam\\b', r'\\bquiz\\b',
                r'\\bgrading\\b', r'\\brubric\\b', r'\\blesson\\b', r'\\bcourse\\b',
                r'\\bstudent\\b', r'\\bgrade\\b', r'\\bhomework\\b', r'\\btest\\b'
            ],
            'service': [
                r'\\bcommittee\\b', r'\\bmeeting\\b', r'\\bagenda\\b', r'\\bminutes\\b',
                r'\\breview\\b', r'\\bevaluation\\b', r'\\bproposal\\b', r'\\bservice\\b'
            ],
            'scholarship': [
                r'\\bresearch\\b', r'\\bpaper\\b', r'\\barticle\\b', r'\\bmanuscript\\b',
                r'\\babstract\\b', r'\\bpublication\\b', r'\\bconference\\b', r'\\bgrant\\b',
                r'\\bcomposition\\b', r'\\barrangement\\b', r'\\bdrill\\b', r'\\bscore\\b'
            ]
        }
        
        self.path_patterns = {
            'teaching': [r'/teaching/', r'/courses?/', r'/class/', r'/syllabi?/', r'/assignments?/'],
            'service': [r'/service/', r'/committee/', r'/admin/', r'/meetings?/'],
            'scholarship': [r'/research/', r'/publications?/', r'/manuscripts?/', r'/creative/', r'/compositions?/']
        }
        
        self.extension_hints = {
            'teaching': {'.pptx': 3, '.pdf': 1, '.docx': 2, '.xlsx': 2},  # Teaching files
            'scholarship': {'.pdf': 3, '.docx': 3, '.musx': 5, '.sib': 5, '.3dj': 5, '.musicxml': 4},  # Creative work
            'service': {'.pdf': 2, '.docx': 2, '.xlsx': 2, '.pptx': 1}  # Service files
        }
    
    def analyze_file_metadata(self, filepath, file_stats):
        """Analyze file metadata only - no text extraction (the fast lane)"""
        filename = os.path.basename(filepath).lower()
        path_lower = filepath.lower()
        ext = os.path.splitext(filename)[1]
        
        scores = {'teaching': 0, 'service': 0, 'scholarship': 0}
        reasons = []
        
        # Filename pattern matching (detective work)
        for category, patterns in self.filename_patterns.items():
            for pattern in patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    scores[category] += 2
                    reasons.append(f"filename:{pattern}")
        
        # Path pattern matching (location, location, location)
        for category, patterns in self.path_patterns.items():
            for pattern in patterns:
                if re.search(pattern, path_lower):
                    scores[category] += 3
                    reasons.append(f"path:{pattern}")
        
        # Extension hints (judging files by their covers)
        for category, ext_scores in self.extension_hints.items():
            if ext in ext_scores:
                scores[category] += ext_scores[ext]
                reasons.append(f"ext:{ext}")
        
        # Date-based hints (newer is probably better)
        age_days = (time.time() - file_stats.st_mtime) / 86400
        if age_days < 365:  # Files from last year get slight boost
            for category in scores:
                scores[category] += 0.5
            reasons.append("recent_file")
        
        # Size hints (too small or too big is suspicious)
        size_kb = file_stats.st_size / 1024
        size_penalty = 0
        if size_kb < 1:  # Tiny files are probably not important
            size_penalty = -2
            reasons.append("tiny_file")
        elif size_kb > 100000:  # Huge files are probably media or something  
            size_penalty = -1
            reasons.append("huge_file")
        
        for category in scores:
            scores[category] += size_penalty
        
        # Determine best category
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]
        
        # Minimum confidence threshold for categorization
        if confidence < 1.0:
            best_category = 'misc'
            confidence = 0
            reasons.append("low_confidence")
        
        return {
            'path': filepath,
            'category': best_category,
            'confidence': confidence,
            'scores': scores,
            'reasons': reasons,
            'size_kb': size_kb,
            'age_days': age_days,
            'extension': ext
        }


class TwoPassScanner:
    """Two-pass scanner: metadata first, then detailed analysis (because efficiency)"""
    
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.metadata_analyzer = MetadataAnalyzer(self.config)
        
    def pass1_metadata_scan(self, file_paths, output_dir):
        """Pass 1: Fast metadata-only categorization (the sorting hat)"""
        print("🔍 Pass 1: Metadata Analysis (The Quick and Dirty Survey)")
        os.makedirs(output_dir, exist_ok=True)
        
        categorized = {
            'teaching': [],
            'service': [], 
            'scholarship': [],
            'misc': []
        }
        
        stats = Counter()
        
        pbar = tqdm(
            file_paths, 
            desc="Analyzing metadata", 
            unit="file",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        
        for filepath in pbar:
            try:
                file_stats = os.stat(filepath)
                analysis = self.metadata_analyzer.analyze_file_metadata(filepath, file_stats)
                
                category = analysis['category']
                categorized[category].append(analysis)
                stats[category] += 1
                
                # Update progress bar with current stats
                pbar.set_postfix({
                    'T': stats['teaching'], 
                    'S': stats['service'],
                    'R': stats['scholarship'], 
                    'M': stats['misc']
                })
                
            except Exception as e:
                stats['errors'] += 1
                continue
        
        # Save pass 1 results
        with open(os.path.join(output_dir, 'pass1_categorized.json'), 'w') as f:
            json.dump(categorized, f, indent=2, default=str)
        
        # Summary report
        summary = {
            'total_files': len(file_paths),
            'teaching_files': len(categorized['teaching']),
            'service_files': len(categorized['service']),
            'scholarship_files': len(categorized['scholarship']),
            'misc_files': len(categorized['misc']),
            'high_confidence_teaching': len([f for f in categorized['teaching'] if f['confidence'] > 3]),
            'high_confidence_service': len([f for f in categorized['service'] if f['confidence'] > 3]),
            'high_confidence_scholarship': len([f for f in categorized['scholarship'] if f['confidence'] > 3])
        }
        
        print(f"\\n📊 Pass 1 Results (The Executive Summary):")
        print(f"   Teaching: {summary['teaching_files']} files ({summary['high_confidence_teaching']} high confidence)")
        print(f"   Service: {summary['service_files']} files ({summary['high_confidence_service']} high confidence)")
        print(f"   Scholarship: {summary['scholarship_files']} files ({summary['high_confidence_scholarship']} high confidence)")
        print(f"   Misc: {summary['misc_files']} files (the mystery category)")
        
        return categorized, summary
    
    def pass2_detailed_analysis(self, categorized_files, categories_to_process, output_dir):
        """Pass 2: Full text extraction and detailed analysis on selected categories (the deep dive)"""
        print(f"\\n🔬 Pass 2: Detailed Analysis (Now We Get Serious)")
        
        from extractors import extract_text
        from report import write_csv, write_summary, write_html
        
        # Build file list from selected categories
        files_to_process = []
        for category in categories_to_process:
            if category in categorized_files:
                files_to_process.extend([f['path'] for f in categorized_files[category]])
        
        print(f"Processing {len(files_to_process)} files from categories: {', '.join(categories_to_process)}")
        
        # Load full rules for detailed analysis
        compiled_rules = self._compile_rules(self.config['categories'])
        scoring = self.config.get('scoring', {})
        per_hit = scoring.get('per_hit_points', 1)
        cap = scoring.get('cap_per_file', 10)
        cat_weights = scoring.get('category_weights', {})
        bonus_keywords = scoring.get('bonus_keywords', {})
        
        rows = []
        stats = Counter(processed=0, text_extracted=0, matched=0)
        
        PROPRIETARY_HINTS = {".sib", ".musx", ".mus", ".ftmx", ".ftm", ".3dj", ".3dz", ".3da", ".prod"}
        
        pbar = tqdm(
            files_to_process,
            desc="Detailed analysis", 
            unit="file",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        
        for filepath in pbar:
            stats['processed'] += 1
            
            try:
                file_stats = os.stat(filepath)
                ext = os.path.splitext(filepath)[1].lower()
                
                # Extract text content
                text_content = extract_text(filepath)
                
                # Fallback for proprietary formats (when all else fails, use the filename)
                if not text_content and ext in PROPRIETARY_HINTS:
                    text_content = os.path.basename(filepath).lower()
                    # Add a comment for these files
                    if ext in self.metadata_analyzer.file_type_comments:
                        print(f"   {self.metadata_analyzer.file_type_comments[ext]}")
                
                if text_content and text_content.strip():
                    stats['text_extracted'] += 1
                    
                    # Score against detailed rules
                    file_matched = False
                    for category, subcategories in compiled_rules.items():
                        for subcategory, patterns in subcategories.items():
                            score, hits = self._score_text(text_content, patterns, per_hit, cap)
                            if score > 0:
                                file_matched = True
                                
                                # Apply category weights and bonuses
                                weighted_score = score * cat_weights.get(category, 1.0)
                                for keyword, bonus_points in bonus_keywords.items():
                                    if re.search(re.escape(keyword), text_content, re.IGNORECASE):
                                        weighted_score += bonus_points
                                
                                rows.append({
                                    'source': 'files',
                                    'path': filepath,
                                    'display': filepath,
                                    'category': category,
                                    'subcategory': subcategory,
                                    'hits': hits,
                                    'score': int(weighted_score) if weighted_score.is_integer() else weighted_score,
                                    'meta': f"mtime {datetime.fromtimestamp(file_stats.st_mtime, tz=timezone.utc).isoformat()}",
                                    'when': datetime.fromtimestamp(file_stats.st_mtime, tz=timezone.utc).date().isoformat()
                                })
                    
                    if file_matched:
                        stats['matched'] += 1
                
                pbar.set_postfix({
                    'extracted': f"{stats['text_extracted']}/{stats['processed']}", 
                    'matched': stats['matched']
                })
                        
            except Exception as e:
                continue
        
        # Generate reports
        if rows:
            rows.sort(key=lambda r: (r['source'], -float(r['score']), r['category'], r['subcategory']))
            
            evidence_csv = write_csv(rows, output_dir, 'evidence.csv')
            summary_csv = write_summary(rows, output_dir)  
            report_html = write_html(rows, output_dir)
            
            print(f"\\n✅ Pass 2 Complete (Mission Accomplished):")
            print(f"   Files processed: {stats['processed']}")
            print(f"   Text extracted: {stats['text_extracted']}")  
            print(f"   Files matched: {stats['matched']}")
            print(f"   Evidence entries: {len(rows)}")
            
            return evidence_csv, summary_csv, report_html
        else:
            print("❌ No matches found in detailed analysis (That's... unexpected)")
            return None, None, None
    
    def _compile_rules(self, categories_config):
        """Compile regex rules from config (the pattern factory)"""
        compiled = {}
        for cat, subs in categories_config.items():
            compiled[cat] = {}
            for sub, rule in subs.items():
                patterns = [re.compile(p, re.IGNORECASE) for p in rule.get('any', [])]
                compiled[cat][sub] = patterns
        return compiled
    
    def _score_text(self, text, patterns, per_hit, cap):
        """Score text content against patterns (the matching game)"""
        if not text:
            return 0, 0
        hits = 0
        for pattern in patterns:
            hits += len(set(m.span() for m in pattern.finditer(text)))
        return min(hits * per_hit, cap), hits


def load_path_list(path):
    """Load file paths from a text file (the directory reader)"""
    if not path or not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [ln.strip() for ln in f if ln.strip()]

def walk_directories(include_dirs, include_exts, exclude_dirs, since_ts=None, until_ts=None, max_bytes=0):
    """Walk through directories to find files (the file hunter)"""
    files = []
    for root_dir in include_dirs:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Filter out excluded directories
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                ext = os.path.splitext(filename.lower())[1]
                
                # Check extension filter
                if include_exts and ext not in include_exts:
                    continue
                
                try:
                    st = os.stat(filepath)
                except Exception:
                    continue
                
                # Check size filter
                if max_bytes and st.st_size > max_bytes:
                    continue
                
                # Check date filters
                if since_ts and st.st_mtime < since_ts:
                    continue
                if until_ts and st.st_mtime > until_ts + 86399:  # inclusive end-of-day
                    continue
                
                files.append(filepath)
    
    return files

def to_epoch(dstr):
    """Convert date string to epoch timestamp (time travel helper)"""
    if not dstr:
        return None
    return datetime.strptime(dstr, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()

def main():
    parser = argparse.ArgumentParser(description="Two-pass academic evidence scanner (The Smart Way)")
    parser.add_argument("--path-list", help="File with paths to scan")
    parser.add_argument("--include", nargs="*", help="Directories to scan")
    parser.add_argument("--include-file", help="File with directories to scan")  
    parser.add_argument("--rules", default="config/rules.yml", help="Rules configuration file")
    parser.add_argument("--out", default="out", help="Output directory")
    parser.add_argument("--pass1-only", action="store_true", help="Run only metadata analysis (quick survey)")
    parser.add_argument("--categories", nargs="+", default=["teaching", "service", "scholarship"], 
                       help="Categories to process in pass 2")
    parser.add_argument("--min-confidence", type=float, default=1.0, 
                       help="Minimum confidence threshold for pass 2")
    parser.add_argument("--modified-since", help="Only files modified after this date (YYYY-MM-DD)")
    parser.add_argument("--modified-until", help="Only files modified before this date (YYYY-MM-DD)")
    parser.add_argument("--max-bytes", type=int, default=50000000, help="Maximum file size to process")
    parser.add_argument("--only-ext", help="Comma-separated list of extensions to include")
    
    args = parser.parse_args()
    
    # Initialize scanner
    scanner = TwoPassScanner(args.rules)
    
    # Load configuration for file filters
    with open(args.rules) as f:
        config = yaml.safe_load(f)
    
    include_exts = set([e.lower() for e in config["file_filters"]["include_extensions"]])
    if args.only_ext:
        include_exts = set([e.strip().lower() for e in args.only_ext.split(",") if e.strip()])
    
    exclude_dirs = set(config["file_filters"].get("exclude_dirs", []))
    
    # Date filters
    since_ts = to_epoch(args.modified_since)
    until_ts = to_epoch(args.modified_until)
    
    # Load file paths
    file_paths = []
    if args.path_list:
        file_paths = load_path_list(args.path_list)
        print(f"Loaded {len(file_paths)} paths from {args.path_list}")
    else:
        include_dirs = []
        if args.include:
            include_dirs.extend(args.include)
        if args.include_file:
            with open(args.include_file) as f:
                include_dirs.extend([line.strip() for line in f if line.strip()])
        
        if include_dirs:
            print(f"Walking directories: {include_dirs}")
            file_paths = walk_directories(include_dirs, include_exts, exclude_dirs, since_ts, until_ts, args.max_bytes)
            print(f"Found {len(file_paths)} files to analyze")
    
    if not file_paths:
        print("❌ No files to process. Check your paths and try again.")
        return
    
    print(f"\\n🎯 Scanning {len(file_paths)} files with two-pass approach...")
    print("Pass 1 will categorize files quickly, Pass 2 will do detailed analysis.")
    
    # Pass 1: Metadata analysis
    categorized, summary = scanner.pass1_metadata_scan(file_paths, args.out)
    
    # Save pass 1 summary
    with open(os.path.join(args.out, 'pass1_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    if args.pass1_only:
        print("\\n✅ Pass 1 complete! Review results and run pass 2 with desired categories.")
        print(f"Results saved to: {args.out}/pass1_categorized.json")
        return
    
    # Pass 2: Detailed analysis
    evidence_csv, summary_csv, report_html = scanner.pass2_detailed_analysis(
        categorized, args.categories, args.out
    )
    
    if evidence_csv:
        print(f"\\n🎉 Two-pass scan complete! Reports generated:")
        print(f"  📊 {evidence_csv}")
        print(f"  📈 {summary_csv}") 
        print(f"  🌐 {report_html}")
        print("\\nNow you can bask in the glory of organized academic evidence!")
    else:
        print("\\n🤷 No evidence found. Maybe try different search criteria?")

if __name__ == "__main__":
    main()
