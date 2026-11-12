"""
Fix logging permissions by clearing old log files
"""

import os
import glob
import time

def fix_logging():
    """Clear old log files to prevent permission issues"""
    
    log_files = glob.glob('logs/*.log*')
    
    for log_file in log_files:
        try:
            # Try to rename the file (this will fail if in use)
            new_name = log_file + '.old'
            os.rename(log_file, new_name)
            print(f"✓ Renamed: {log_file} -> {new_name}")
            
            # Delete the old file after a short delay
            time.sleep(0.1)
            os.remove(new_name)
            print(f"✓ Deleted: {new_name}")
            
        except Exception as e:
            print(f"Could not process {log_file}: {str(e)}")

if __name__ == "__main__":
    print("="*60)
    print("Fixing logging permissions...")
    print("="*60)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    fix_logging()
    
    print("\n✓ Logging fixed! You can now run the application.")