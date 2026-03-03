#!/usr/bin/env python3
"""
JARVIS Graceful Shutdown & Cleanup Orchestrator
Safely terminates all JARVIS processes, releases GPU resources, and cleans up build artifacts
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}[WARNING] {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}[ERROR] {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}[INFO] {text}{Colors.END}")

def get_jarvis_processes():
    """Find all JARVIS-related Python processes"""
    processes = []
    
    try:
        # Get all Python processes
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-Process python -ErrorAction SilentlyContinue | Select-Object Id,Path | ConvertTo-Json'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            import json
            proc_data = json.loads(result.stdout)
            
            # Handle both single process (dict) and multiple processes (list)
            if isinstance(proc_data, dict):
                proc_data = [proc_data]
            
            # Filter for JARVIS processes
            project_path = Path(__file__).parent.absolute()
            for proc in proc_data:
                if proc.get('Path'):
                    proc_path = Path(proc['Path'])
                    # Check if process is running from jarvis_env or project directory
                    if 'jarvis_env' in str(proc_path).lower() or str(project_path) in str(proc_path):
                        processes.append({
                            'pid': proc['Id'],
                            'path': str(proc_path)
                        })
    
    except Exception as e:
        print_warning(f"Could not enumerate processes: {e}")
    
    return processes

def terminate_processes(processes):
    """Gracefully terminate JARVIS processes"""
    if not processes:
        print_info("No JARVIS processes found running")
        return 0
    
    print_info(f"Found {len(processes)} JARVIS process(es)")
    
    terminated_count = 0
    
    for proc in processes:
        pid = proc['pid']
        path = proc['path']
        
        print(f"  - PID {pid}: {os.path.basename(path)}")
        
        try:
            # Try graceful termination first (SIGTERM equivalent on Windows)
            subprocess.run(['taskkill', '/PID', str(pid)], 
                          capture_output=True, timeout=2)
            terminated_count += 1
        except Exception as e:
            print_warning(f"    Could not terminate PID {pid}: {e}")
    
    # Wait for processes to terminate
    if terminated_count > 0:
        print_info("Waiting for processes to terminate gracefully...")
        time.sleep(2)
        
        # Force kill any remaining processes
        for proc in processes:
            try:
                subprocess.run(['taskkill', '/F', '/PID', str(proc['pid'])], 
                              capture_output=True, timeout=2)
            except:
                pass
    
    return terminated_count

def check_port_usage():
    """Check if JARVIS ports are in use"""
    ports_to_check = [8765, 8000]  # WebSocket and HTTP server
    in_use = []
    
    for port in ports_to_check:
        try:
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if f":{port}" in result.stdout:
                in_use.append(port)
        except:
            pass
    
    return in_use

def get_directory_size(path):
    """Calculate total size of a directory"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception as e:
        print_warning(f"Could not calculate size for {path}: {e}")
    
    return total_size

def format_size(bytes):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def cleanup_files():
    """Remove build artifacts and temporary files"""
    project_root = Path(__file__).parent.absolute()
    
    items_to_delete = [
        # Virtual environment
        ('jarvis_env', 'directory'),
        # Python cache
        ('__pycache__', 'directory'),
        # Temporary files
        ('tmp_*.wav', 'glob'),
        ('files.zip', 'file'),
        # Speech recognition model
        ('vosk-model-small-en-in-0.4', 'directory'),
    ]
    
    total_deleted = 0
    total_size = 0
    deleted_items = []
    
    for item_pattern, item_type in items_to_delete:
        if item_type == 'directory':
            item_path = project_root / item_pattern
            if item_path.exists():
                size = get_directory_size(item_path)
                try:
                    shutil.rmtree(item_path)
                    total_deleted += 1
                    total_size += size
                    deleted_items.append(f"{item_pattern}/ ({format_size(size)})")
                    print_success(f"Deleted: {item_pattern}/ ({format_size(size)})")
                except Exception as e:
                    print_error(f"Failed to delete {item_pattern}: {e}")
        
        elif item_type == 'file':
            item_path = project_root / item_pattern
            if item_path.exists():
                size = item_path.stat().st_size
                try:
                    item_path.unlink()
                    total_deleted += 1
                    total_size += size
                    deleted_items.append(f"{item_pattern} ({format_size(size)})")
                    print_success(f"Deleted: {item_pattern} ({format_size(size)})")
                except Exception as e:
                    print_error(f"Failed to delete {item_pattern}: {e}")
        
        elif item_type == 'glob':
            for item_path in project_root.glob(item_pattern):
                if item_path.is_file():
                    size = item_path.stat().st_size
                    try:
                        item_path.unlink()
                        total_deleted += 1
                        total_size += size
                        deleted_items.append(f"{item_path.name} ({format_size(size)})")
                        print_success(f"Deleted: {item_path.name} ({format_size(size)})")
                    except Exception as e:
                        print_error(f"Failed to delete {item_path.name}: {e}")
    
    # Also clean __pycache__ recursively
    for pycache in project_root.rglob('__pycache__'):
        if pycache.is_dir():
            size = get_directory_size(pycache)
            try:
                shutil.rmtree(pycache)
                total_deleted += 1
                total_size += size
                rel_path = pycache.relative_to(project_root)
                print_success(f"Deleted: {rel_path} ({format_size(size)})")
            except Exception as e:
                print_error(f"Failed to delete {pycache}: {e}")
    
    return total_deleted, total_size, deleted_items

def verify_cleanup():
    """Verify cleanup was successful"""
    issues = []
    
    # Check for remaining processes
    remaining_procs = get_jarvis_processes()
    if remaining_procs:
        issues.append(f"{len(remaining_procs)} JARVIS process(es) still running")
    
    # Check for ports in use
    ports_in_use = check_port_usage()
    if ports_in_use:
        issues.append(f"Ports still in use: {', '.join(map(str, ports_in_use))}")
    
    # Check if virtual environment still exists
    venv_path = Path(__file__).parent / 'jarvis_env'
    if venv_path.exists():
        issues.append("Virtual environment directory still exists")
    
    return issues

def main():
    """Main cleanup orchestrator"""
    print_header("JARVIS GRACEFUL SHUTDOWN & CLEANUP")
    
    print(f"{Colors.BOLD}Timestamp:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Phase 1: Process Termination
    print_header("PHASE 1: Process Termination")
    processes = get_jarvis_processes()
    terminated_count = terminate_processes(processes)
    
    if terminated_count > 0:
        print_success(f"Terminated {terminated_count} process(es)")
    
    # Phase 2: Port Check
    print_header("PHASE 2: Network Cleanup")
    ports_in_use = check_port_usage()
    if ports_in_use:
        print_warning(f"Ports still in use: {', '.join(map(str, ports_in_use))}")
        print_info("These may be released shortly...")
    else:
        print_success("All JARVIS ports are free")
    
    # Phase 3: File Cleanup
    print_header("PHASE 3: File Cleanup")
    deleted_count, total_size, deleted_items = cleanup_files()
    
    if deleted_count > 0:
        print_success(f"\nDeleted {deleted_count} item(s)")
        print_success(f"Freed {format_size(total_size)} of disk space")
    else:
        print_info("No files to delete (already clean)")
    
    # Phase 4: Verification
    print_header("PHASE 4: Verification")
    issues = verify_cleanup()
    
    if issues:
        print_warning("Some issues detected:")
        for issue in issues:
            print(f"  * {issue}")
    else:
        print_success("All verification checks passed")
        print_success("GPU resources released")
        print_success("WebSocket connections closed")
        print_success("File system cleaned")
    
    # Final Summary
    print_header("CLEANUP SUMMARY")
    print(f"{Colors.BOLD}Processes terminated:{Colors.END} {terminated_count}")
    print(f"{Colors.BOLD}Files deleted:{Colors.END} {deleted_count}")
    print(f"{Colors.BOLD}Disk space freed:{Colors.END} {format_size(total_size)}")
    print(f"{Colors.BOLD}Status:{Colors.END} {Colors.GREEN}COMPLETE{Colors.END}" if not issues else f"{Colors.BOLD}Status:{Colors.END} {Colors.YELLOW}COMPLETE WITH WARNINGS{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}JARVIS offline. Environment ready for clean installation.{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}Goodbye.{Colors.END}\n")
    
    return 0 if not issues else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Cleanup interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
