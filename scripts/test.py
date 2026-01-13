import ftplib
import os
from datetime import datetime
import humanize
import argparse
import time
import random
import sys
from collections import defaultdict
import re

class ArgoFTPAnalyzer:
    def __init__(self, host='ftp.ifremer.fr', path='ifremer/argo', sample_size=3):
        self.host = host
        self.path = path
        self.sample_size = sample_size
        self.ftp = None
        self.accessible_dirs = set()
        self.inaccessible_dirs = set()
        self.cache = {}
        self.directory_patterns = {}
        self.progress = {
            'total_dirs_scanned': 0,
            'total_files_sampled': 0,
            'similar_dirs_skipped': 0,
            'start_time': None,
            'current_task': None
        }
        # Store temporal information
        self.temporal_range = {
            'min_date': None,
            'max_date': None,
            'date_patterns_found': []
        }
        # Store feature information
        self.feature_info = {
            'parameters': set(),
            'platforms': set(),
            'data_types': set()
        }
        
    def log_task(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def connect(self):
        self.log_task("Starting FTP connection...")
        try:
            self.progress['start_time'] = time.time()
            self.ftp = ftplib.FTP(self.host, timeout=60)
            self.log_task("Connected to server, attempting login...")
            self.ftp.login()
            self.log_task("Login successful, changing to target directory...")
            self.ftp.cwd(self.path)
            self.log_task(f"Successfully connected to {self.host}/{self.path}")
            return True
        except Exception as e:
            self.log_task(f"Connection failed: {e}", "ERROR")
            return False
    
    def disconnect(self):
        if self.ftp:
            self.ftp.quit()
            self.log_task("Disconnected from FTP server")
    
    def parse_listing(self, line):
        parts = line.split()
        if len(parts) < 9:
            return None
        
        if parts[0].startswith('d'):
            return {
                'type': 'directory',
                'name': ' '.join(parts[8:]),
                'size': 0,
                'permissions': parts[0]
            }
        else:
            try:
                size = int(parts[4])
                return {
                    'type': 'file',
                    'name': ' '.join(parts[8:]),
                    'size': size,
                    'permissions': parts[0]
                }
            except (ValueError, IndexError):
                return None

    def extract_temporal_info(self, filename, path):
        """Extract temporal information from filenames and paths"""
        # Common Argo date patterns in filenames
        date_patterns = [
            r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
            r'(\d{4})_(\d{2})_(\d{2})',  # YYYY_MM_DD
            r'(\d{4})(\d{2})',  # YYYYMM
        ]
        
        full_path = os.path.join(path, filename).lower()
        
        for pattern in date_patterns:
            matches = re.findall(pattern, full_path)
            for match in matches:
                if len(match) == 3:  # YYYYMMDD
                    year, month, day = match
                    try:
                        date_obj = datetime(int(year), int(month), int(day))
                        if self.temporal_range['min_date'] is None or date_obj < self.temporal_range['min_date']:
                            self.temporal_range['min_date'] = date_obj
                        if self.temporal_range['max_date'] is None or date_obj > self.temporal_range['max_date']:
                            self.temporal_range['max_date'] = date_obj
                        self.temporal_range['date_patterns_found'].append(pattern)
                    except ValueError:
                        continue
                elif len(match) == 2:  # YYYYMM
                    year, month = match
                    try:
                        date_obj = datetime(int(year), int(month), 1)
                        if self.temporal_range['min_date'] is None or date_obj < self.temporal_range['min_date']:
                            self.temporal_range['min_date'] = date_obj
                        if self.temporal_range['max_date'] is None or date_obj > self.temporal_range['max_date']:
                            self.temporal_range['max_date'] = date_obj
                    except ValueError:
                        continue

    def extract_feature_info(self, filename, path):
        """Extract feature information from filenames and paths"""
        full_path = os.path.join(path, filename).lower()
        
        # Common Argo parameters in filenames
        parameters = ['temp', 'temperature', 'sal', 'salinity', 'pres', 'pressure', 
                     'doxy', 'oxygen', 'chlorophyll', 'bbp', 'cndc', 'ph', 'nitrate']
        
        # Platform types
        platforms = ['argo', 'float', 'drifter', 'moored', 'profile']
        
        # Data types
        data_types = ['rt', 'realtime', 'delayed', 'adjusted', 'profile', 'trajectory']
        
        for param in parameters:
            if param in full_path:
                self.feature_info['parameters'].add(param)
                
        for platform in platforms:
            if platform in full_path:
                self.feature_info['platforms'].add(platform)
                
        for data_type in data_types:
            if data_type in full_path:
                self.feature_info['data_types'].add(data_type)

    def can_access_directory(self, path):
        try:
            current = self.ftp.pwd()
            self.ftp.cwd(path)
            self.ftp.cwd(current)
            return True
        except Exception:
            return False
    
    def get_directory_listing(self, path):
        if path in self.cache:
            return self.cache[path]
            
        self.log_task(f"Scanning directory: {path}")
        try:
            current_dir = self.ftp.pwd()
            self.ftp.cwd(path)
            
            lines = []
            self.ftp.retrlines('LIST', lines.append)
            
            self.ftp.cwd(current_dir)
            
            items = []
            for line in lines:
                item = self.parse_listing(line)
                if item:
                    items.append(item)
            
            self.cache[path] = items
            self.progress['total_dirs_scanned'] += 1
            
            # Extract information from files in this directory
            for item in items:
                if item['type'] == 'file':
                    self.extract_temporal_info(item['name'], path)
                    self.extract_feature_info(item['name'], path)
            
            files = [item for item in items if item['type'] == 'file']
            dirs = [item for item in items if item['type'] == 'directory' and item['name'] not in ['.', '..']]
            
            if files or dirs:
                self.log_task(f"Found {len(files)} files and {len(dirs)} subdirectories in {path}")
            
            return items
            
        except ftplib.error_perm as e:
            self.log_task(f"Permission denied for directory: {path}", "WARNING")
            self.inaccessible_dirs.add(path)
            self.cache[path] = None
            return None
        except Exception as e:
            self.log_task(f"Error listing {path}: {e}", "ERROR")
            self.cache[path] = None
            return None

    def get_directory_pattern_signature(self, items):
        """Enhanced pattern detection with NetCDF awareness"""
        if not items:
            return None
            
        files = [item for item in items if item['type'] == 'file']
        dirs = [item for item in items if item['type'] == 'directory' and item['name'] not in ['.', '..']]
        
        file_extensions = defaultdict(int)
        total_files = len(files)
        total_dirs = len(dirs)
        
        # Check for NetCDF files specifically
        nc_files = [f for f in files if f['name'].lower().endswith(('.nc', '.nc4', '.cdf'))]
        has_nc_files = len(nc_files) > 0
        
        for file in files:
            ext = os.path.splitext(file['name'])[1].lower()
            file_extensions[ext] += 1
        
        ext_signature = tuple(sorted([(ext, count/total_files if total_files > 0 else 0) 
                                    for ext, count in file_extensions.items()]))
        
        return {
            'file_count': total_files,
            'dir_count': total_dirs,
            'extensions': ext_signature,
            'has_subdirs': total_dirs > 0,
            'has_nc_files': has_nc_files,
            'nc_file_count': len(nc_files)
        }

    def is_similar_directory(self, current_path, items):
        """Enhanced similarity detection - don't skip directories with NetCDF files"""
        signature = self.get_directory_pattern_signature(items)
        if not signature:
            return False
        
        # Don't skip directories that contain NetCDF files
        if signature['has_nc_files']:
            self.log_task(f"Directory contains NetCDF files, will scan individually: {current_path}")
            return False
        
        for pattern_path, pattern_sig in self.directory_patterns.items():
            if (pattern_sig['file_count'] == signature['file_count'] and
                pattern_sig['dir_count'] == signature['dir_count'] and
                pattern_sig['extensions'] == signature['extensions'] and
                pattern_sig['has_subdirs'] == signature['has_subdirs'] and
                not signature['has_nc_files']):  # Only skip if no NetCDF files
                
                self.log_task(f"Similar directory pattern detected: {current_path} matches {pattern_path}", "INFO")
                return pattern_path
        
        self.directory_patterns[current_path] = signature
        return False

    def estimate_directory_size(self, path='.', current_depth=0, max_depth=2):
        if current_depth > max_depth:
            return {
                'path': path,
                'estimated_size': 0,
                'file_count': 0,
                'dir_count': 0,
                'files_sampled': 0,
                'accessible': False,
                'max_depth_reached': True,
                'estimation_method': 'depth_limit',
                'subdirectories': {}
            }
        
        self.log_task(f"Estimating directory (depth {current_depth}): {path}")
        items = self.get_directory_listing(path)
        if items is None:
            return {
                'path': path,
                'estimated_size': 0,
                'file_count': 0,
                'dir_count': 0,
                'files_sampled': 0,
                'accessible': False,
                'estimation_method': 'inaccessible',
                'subdirectories': {}
            }
        
        similar_to = self.is_similar_directory(path, items)
        if similar_to and similar_to != path:
            self.progress['similar_dirs_skipped'] += 1
            return {
                'path': path,
                'estimated_size': 0,
                'file_count': 0,
                'dir_count': 0,
                'files_sampled': 0,
                'accessible': True,
                'estimation_method': 'pattern_match',
                'similar_to': similar_to,
                'note': f'Similar to {similar_to}',
                'subdirectories': {}
            }
        
        analysis = {
            'path': path,
            'estimated_size': 0,
            'file_count': 0,
            'dir_count': 0,
            'files_sampled': 0,
            'accessible': True,
            'subdirectories': {},
            'estimation_method': 'sampled',
            'sample_details': {}
        }
        
        # Process files in current directory
        current_files = [item for item in items if item['type'] == 'file']
        analysis['file_count'] = len(current_files)
        
        if current_files:
            # Prioritize sampling NetCDF files if present
            nc_files = [f for f in current_files if f['name'].lower().endswith(('.nc', '.nc4', '.cdf'))]
            other_files = [f for f in current_files if f not in nc_files]
            
            sample_files = []
            if nc_files:
                # Sample all NetCDF files or up to sample_size
                sample_files.extend(nc_files[:self.sample_size])
                remaining_samples = self.sample_size - len(sample_files)
                if remaining_samples > 0 and other_files:
                    if len(other_files) > remaining_samples:
                        sample_files.extend(random.sample(other_files, remaining_samples))
                    else:
                        sample_files.extend(other_files)
            else:
                # No NetCDF files, sample normally
                if len(current_files) > self.sample_size:
                    sample_files = random.sample(current_files, self.sample_size)
                else:
                    sample_files = current_files
            
            sampled_sizes = [f['size'] for f in sample_files]
            avg_file_size = sum(sampled_sizes) / len(sampled_sizes) if sampled_sizes else 0
            
            estimated_current_size = avg_file_size * len(current_files)
            analysis['estimated_size'] += estimated_current_size
            analysis['files_sampled'] += len(sample_files)
            self.progress['total_files_sampled'] += len(sample_files)
            
            analysis['sample_details'] = {
                'files_sampled': len(sample_files),
                'total_files': len(current_files),
                'average_file_size': avg_file_size,
                'sampled_files': [f['name'] for f in sample_files],
                'sampled_sizes': sampled_sizes,
                'nc_files_sampled': len([f for f in sample_files if f['name'].lower().endswith(('.nc', '.nc4', '.cdf'))])
            }
            
            self.log_task(f"Sampled {len(sample_files)} of {len(current_files)} files in {path} "
                         f"({len(nc_files)} NetCDF files found)")
        
        # Process subdirectories (rest of the function remains the same)
        subdirs = [item for item in items if item['type'] == 'directory' and item['name'] not in ['.', '..']]
        analysis['dir_count'] = len(subdirs)
        
        if subdirs:
            self.log_task(f"Processing {len(subdirs)} subdirectories in {path}")
        
        dir_groups = defaultdict(list)
        for subdir in subdirs:
            dir_name = subdir['name']
            if any(char.isdigit() for char in dir_name):
                base_name = ''.join([c for c in dir_name if not c.isdigit()])
                dir_groups[base_name].append(subdir)
            else:
                dir_groups[dir_name].append(subdir)
        
        for group_name, group_dirs in dir_groups.items():
            if len(group_dirs) > 1:
                self.log_task(f"Found {len(group_dirs)} similar directories in group '{group_name}'")
            
            first_dir = group_dirs[0]
            sub_path = os.path.join(path, first_dir['name'])
            
            if self.can_access_directory(sub_path):
                self.accessible_dirs.add(sub_path)
                sub_analysis = self.estimate_directory_size(sub_path, current_depth + 1, max_depth)
                analysis['subdirectories'][first_dir['name']] = sub_analysis
                analysis['estimated_size'] += sub_analysis['estimated_size']
                analysis['file_count'] += sub_analysis['file_count']
                analysis['dir_count'] += sub_analysis['dir_count']
                analysis['files_sampled'] += sub_analysis['files_sampled']
                
                for other_dir in group_dirs[1:]:
                    other_path = os.path.join(path, other_dir['name'])
                    analysis['subdirectories'][other_dir['name']] = {
                        'path': other_path,
                        'estimated_size': sub_analysis['estimated_size'],
                        'file_count': sub_analysis['file_count'],
                        'dir_count': sub_analysis['dir_count'],
                        'files_sampled': 0,
                        'accessible': True,
                        'estimation_method': 'pattern_reuse',
                        'similar_to': first_dir['name'],
                        'note': f'Pattern reused from {first_dir["name"]}',
                        'subdirectories': sub_analysis.get('subdirectories', {})
                    }
            else:
                for dir_item in group_dirs:
                    dir_path = os.path.join(path, dir_item['name'])
                    self.inaccessible_dirs.add(dir_path)
                    analysis['subdirectories'][dir_item['name']] = {
                        'path': dir_path,
                        'estimated_size': 0,
                        'file_count': 0,
                        'dir_count': 0,
                        'files_sampled': 0,
                        'accessible': False,
                        'estimation_method': 'inaccessible',
                        'subdirectories': {}
                    }
        
        return analysis

    def generate_detailed_stats(self, analysis):
        """Fixed statistics generation"""
        def collect_file_types(analysis):
            file_types = defaultdict(int)
            total_files = analysis['file_count']
            
            # Only count actual files, don't scale estimates
            if analysis.get('sample_details') and analysis.get('estimation_method') == 'sampled':
                for filename in analysis['sample_details'].get('sampled_files', []):
                    ext = os.path.splitext(filename)[1].lower() or 'no_extension'
                    file_types[ext] += 1
                # Scale based on actual sampling ratio
                sampled_count = analysis['sample_details']['files_sampled']
                if sampled_count > 0 and total_files > sampled_count:
                    scale_factor = total_files / sampled_count
                    for ext in list(file_types.keys()):
                        file_types[ext] = int(file_types[ext] * scale_factor)
            
            # Process subdirectories
            for sub_analysis in analysis.get('subdirectories', {}).values():
                sub_file_types = collect_file_types(sub_analysis)
                for ext, count in sub_file_types.items():
                    file_types[ext] += count
            
            return file_types
        
        file_types = collect_file_types(analysis)
        total_counted_files = sum(file_types.values())
        
        # Ensure total matches estimated files
        if total_counted_files != analysis['file_count'] and analysis['file_count'] > 0:
            scale_factor = analysis['file_count'] / total_counted_files if total_counted_files > 0 else 1
            for ext in file_types:
                file_types[ext] = int(file_types[ext] * scale_factor)
        
        # Recalculate total after scaling
        total_counted_files = sum(file_types.values())
        
        data_categories = {
            'NetCDF Files': sum(count for ext, count in file_types.items() if ext in ['.nc', '.nc4', '.cdf']),
            'Text Data': sum(count for ext, count in file_types.items() if ext in ['.txt', '.csv', '.dat', '.asc']),
            'Compressed Files': sum(count for ext, count in file_types.items() if ext in ['.gz', '.zip', '.tar', '.bz2']),
            'Metadata Files': sum(count for ext, count in file_types.items() if ext in ['.xml', '.json', '.yml', '.yaml']),
            'Binary Files': sum(count for ext, count in file_types.items() if ext in ['.bin', '.dat']),
            'Other Files': sum(count for ext, count in file_types.items() if ext not in ['.nc', '.nc4', '.cdf', '.txt', '.csv', '.dat', '.asc', '.gz', '.zip', '.tar', '.bz2', '.xml', '.json', '.yml', '.yaml', '.bin'])
        }
        
        max_depth = self.find_max_depth(analysis)
        
        return {
            'file_type_breakdown': dict(file_types),
            'data_categories': data_categories,
            'total_data_points': analysis['file_count'],  # This should now match estimated files
            'unique_file_extensions': len(file_types),
            'directory_structure': {
                'total_directories': analysis['dir_count'],
                'max_depth_reached': max_depth >= 3,
                'maximum_depth': max_depth,
                'average_files_per_directory': analysis['file_count'] / max(1, analysis['dir_count'])
            },
            'temporal_range': {
                'min_date': self.temporal_range['min_date'].strftime('%Y-%m-%d') if self.temporal_range['min_date'] else 'Unknown',
                'max_date': self.temporal_range['max_date'].strftime('%Y-%m-%d') if self.temporal_range['max_date'] else 'Unknown',
                'date_patterns_found': list(set(self.temporal_range['date_patterns_found']))
            },
            'feature_information': {
                'parameters_detected': list(self.feature_info['parameters']),
                'platform_types': list(self.feature_info['platforms']),
                'data_types': list(self.feature_info['data_types']),
                'total_parameters': len(self.feature_info['parameters']),
                'total_platforms': len(self.feature_info['platforms']),
                'total_data_types': len(self.feature_info['data_types'])
            }
        }

    def save_text_report(self, analysis, filename="argo_ftp_analysis_report.txt"):
        """Enhanced text report with temporal and feature information"""
        summary = self.generate_summary_report(analysis)
        stats = self.generate_detailed_stats(analysis)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("ARGO FTP DATA ANALYSIS REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-"*40 + "\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target: {summary['host']}{summary['path']}\n")
            f.write(f"Estimated Total Size: {summary['estimated_size_readable']}\n")
            f.write(f"Estimated Files: {summary['estimated_files']:,}\n")
            f.write(f"Estimated Directories: {summary['estimated_directories']:,}\n")
            f.write(f"Analysis Duration: {summary['analysis_duration_seconds']:.1f} seconds\n\n")
            
            # NEW: Temporal Information
            f.write("TEMPORAL COVERAGE\n")
            f.write("-"*40 + "\n")
            f.write(f"Data Start Date: {stats['temporal_range']['min_date']}\n")
            f.write(f"Data End Date: {stats['temporal_range']['max_date']}\n")
            f.write(f"Date Patterns Found: {', '.join(stats['temporal_range']['date_patterns_found'])}\n\n")
            
            # NEW: Feature Information
            f.write("DATA FEATURES DETECTED\n")
            f.write("-"*40 + "\n")
            f.write(f"Parameters: {', '.join(stats['feature_information']['parameters_detected'])}\n")
            f.write(f"Platform Types: {', '.join(stats['feature_information']['platform_types'])}\n")
            f.write(f"Data Types: {', '.join(stats['feature_information']['data_types'])}\n")
            f.write(f"Total Parameters: {stats['feature_information']['total_parameters']}\n")
            f.write(f"Total Platforms: {stats['feature_information']['total_platforms']}\n")
            f.write(f"Total Data Types: {stats['feature_information']['total_data_types']}\n\n")
            
            f.write("DATA STATISTICS\n")
            f.write("-"*40 + "\n")
            f.write(f"Total Data Points: {stats['total_data_points']:,}\n")
            f.write(f"Unique File Types: {stats['unique_file_extensions']}\n")
            f.write(f"Directories Scanned: {summary['directories_scanned']}\n")
            f.write(f"Files Sampled: {summary['optimization_metrics']['files_sampled_total']:,}\n")
            f.write(f"Estimation Accuracy: {summary['optimization_metrics']['estimation_accuracy_percentage']}%\n\n")
            
            f.write("DATA CATEGORIES BREAKDOWN\n")
            f.write("-"*40 + "\n")
            for category, count in stats['data_categories'].items():
                percentage = (count / stats['total_data_points'] * 100) if stats['total_data_points'] > 0 else 0
                f.write(f"{category:<20}: {count:>10,} files ({percentage:5.1f}%)\n")
            f.write("\n")
            
            f.write("FILE TYPE DETAILS\n")
            f.write("-"*40 + "\n")
            for file_type, count in sorted(stats['file_type_breakdown'].items(), 
                                         key=lambda x: x[1], reverse=True)[:20]:
                percentage = (count / stats['total_data_points'] * 100) if stats['total_data_points'] > 0 else 0
                f.write(f"{file_type or 'no_extension':<10}: {count:>10,} files ({percentage:5.1f}%)\n")
            f.write("\n")
            
            # Rest of the report remains the same...
            f.write("DIRECTORY STRUCTURE\n")
            f.write("-"*40 + "\n")
            f.write(f"Maximum Depth: {stats['directory_structure']['maximum_depth']}\n")
            f.write(f"Depth Limit Reached: {'Yes' if stats['directory_structure']['max_depth_reached'] else 'No'}\n")
            f.write(f"Average Files per Directory: {stats['directory_structure']['average_files_per_directory']:.1f}\n\n")
            
            f.write("OPTIMIZATION METRICS\n")
            f.write("-"*40 + "\n")
            f.write(f"Sample Size per Directory: {summary['optimization_metrics']['sample_size_per_directory']}\n")
            f.write(f"Similar Directories Skipped: {summary['optimization_metrics']['similar_directories_skipped']:,}\n")
            f.write(f"Unique Patterns Detected: {summary['optimization_metrics']['unique_patterns_detected']}\n")
            f.write(f"Performance Speed Factor: {summary['performance_metrics']['estimation_speed_factor']:.1f}x\n")
            f.write(f"Directories per Second: {summary['performance_metrics']['directories_per_second']:.1f}\n")
            f.write(f"Files Sampled per Second: {summary['performance_metrics']['files_sampled_per_second']:.1f}\n\n")
            
            f.write("NETCDF FILES ANALYSIS\n")
            f.write("-"*40 + "\n")
            nc_count = stats['data_categories']['NetCDF Files']
            nc_percentage = (nc_count / stats['total_data_points'] * 100) if stats['total_data_points'] > 0 else 0
            f.write(f"NetCDF Files Found: {nc_count:,} ({nc_percentage:.1f}% of total)\n")
            f.write("Note: Directories containing NetCDF files are always scanned individually\n")
            f.write("to ensure accurate representation of scientific data files.\n\n")
            
            f.write("METHODOLOGY\n")
            f.write("-"*40 + "\n")
            f.write("This analysis uses enhanced pattern detection with NetCDF awareness:\n")
            f.write("1. Prioritizes sampling of NetCDF files for scientific data accuracy\n")
            f.write("2. Extracts temporal information from filenames and paths\n")
            f.write("3. Identifies oceanographic parameters and platform types\n")
            f.write("4. Never skips directories containing NetCDF files\n")
            f.write("5. Uses statistical sampling with pattern reuse for efficiency\n\n")
            
            f.write("NOTE: This analysis prioritizes accuracy of scientific data files.\n")
            f.write("NetCDF file counts should be more representative of actual data content.\n")
        
        self.log_task(f"Enhanced analysis report saved to {filename}")
        return filename

# The main() function remains the same as your original code
def main():
    parser = argparse.ArgumentParser(description='Estimate Argo FTP data size using enhanced pattern detection')
    parser.add_argument('--max-depth', type=int, default=3,
                       help='Maximum recursion depth (default: 3)')
    parser.add_argument('--sample-size', type=int, default=3,
                       help='Number of files to sample per directory (default: 3)')
    parser.add_argument('--output', type=str, help='Output file for JSON report')
    parser.add_argument('--text-report', type=str, help='Output file for text report (.txt)')
    parser.add_argument('--quick-scan', action='store_true',
                       help='Only scan top-level structure for quick overview')
    args = parser.parse_args()
    
    analyzer = ArgoFTPAnalyzer(sample_size=args.sample_size)
    
    if not analyzer.connect():
        return
    
    try:
        # ... (rest of main function remains the same as your original code)
        print("="*80)
        print("ARGO FTP DATA ESTIMATION - ENHANCED PATTERN DETECTION")
        print("="*80)
        print(f"Sampling {args.sample_size} files per directory for estimation")
        print("🔄 Enhanced pattern detection: ACTIVE (NetCDF directories always scanned)")
        print("📊 Temporal information extraction: ACTIVE")
        print("🔍 Feature detection: ACTIVE")
        print()
        
        overview = analyzer.get_top_level_overview()
        analyzer.log_task(f"Top-level: {len(overview['directories'])} directories, {len(overview['files'])} files")
        
        if args.quick_scan:
            analyzer.log_task("Quick scan completed - use without --quick-scan for full estimation")
            return
        
        analyzer.log_task(f"Starting enhanced estimation analysis...")
        print()
        
        start_time = time.time()
        analysis = analyzer.estimate_directory_size(path='.', max_depth=args.max_depth)
        elapsed_time = time.time() - start_time
        
        print()
        analyzer.log_task("Enhanced estimation completed!")
        
        # Generate and display enhanced report
        stats = analyzer.generate_detailed_stats(analysis)
        
        print("="*80)
        print("ENHANCED ANALYSIS RESULTS")
        print("="*80)
        print(f"📅 Temporal Range: {stats['temporal_range']['min_date']} to {stats['temporal_range']['max_date']}")
        print(f"🔬 Parameters Detected: {', '.join(stats['feature_information']['parameters_detected'])}")
        print(f"🛰️  Platform Types: {', '.join(stats['feature_information']['platform_types'])}")
        print(f"💾 NetCDF Files: {stats['data_categories']['NetCDF Files']:,} "
              f"({stats['data_categories']['NetCDF Files']/stats['total_data_points']*100:.1f}% of total)")
        print()
        
        # Save enhanced report
        text_report_file = args.text_report or "argo_ftp_enhanced_analysis_report.txt"
        analyzer.save_text_report(analysis, text_report_file)
        
    except KeyboardInterrupt:
        analyzer.log_task("Estimation interrupted by user", "WARNING")
    except Exception as e:
        analyzer.log_task(f"Error during estimation: {e}", "ERROR")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.disconnect()

if __name__ == "__main__":
    main()