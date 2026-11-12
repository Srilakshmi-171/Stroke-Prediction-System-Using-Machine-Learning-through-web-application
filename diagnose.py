"""
Diagnostic script to check the gradcam.py file
"""

import os
import sys
import inspect

print("="*60)
print("NEUROCARDIOAI - DIAGNOSTIC SCRIPT")
print("="*60)

# Check current directory
print(f"\nCurrent directory: {os.getcwd()}")

# Check if utils directory exists
utils_path = os.path.join(os.getcwd(), 'utils')
print(f"Utils path: {utils_path}")
print(f"Utils exists: {os.path.exists(utils_path)}")

if os.path.exists(utils_path):
    # List files in utils
    print("\nFiles in utils directory:")
    for file in os.listdir(utils_path):
        if file.endswith('.py'):
            size = os.path.getsize(os.path.join(utils_path, file))
            print(f"  - {file} ({size} bytes)")

# Check gradcam.py specifically
gradcam_path = os.path.join(utils_path, 'gradcam.py')
print(f"\nGradCAM path: {gradcam_path}")
print(f"GradCAM exists: {os.path.exists(gradcam_path)}")

if os.path.exists(gradcam_path):
    # Read and display file content (first few lines)
    print("\nFile content (first 20 lines):")
    print("-" * 40)
    with open(gradcam_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:20]):
            print(f"{i+1:2d}: {line.rstrip()}")
    print("-" * 40)
    
    # Check for function definitions
    print("\nChecking for function definitions:")
    with open(gradcam_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        if 'def process_mri_scan' in content:
            print("✓ 'process_mri_scan' function found")
        else:
            print("✗ 'process_mri_scan' function NOT found")
            
        if 'def generate_gradcam' in content:
            print("✓ 'generate_gradcam' function found")
        else:
            print("✗ 'generate_gradcam' function NOT found")
        
        if 'class GradCAMProcessor' in content:
            print("✓ 'GradCAMProcessor' class found")
        else:
            print("✗ 'GradCAMProcessor' class NOT found")

# Try to import directly
print("\n" + "="*60)
print("Attempting direct import")
print("="*60)

try:
    # Add current directory to path
    sys.path.insert(0, os.getcwd())
    
    # Try to import the module
    import utils.gradcam
    print(f"✓ Module imported: {utils.gradcam}")
    
    # Check what's in the module
    print("\nAttributes in module:")
    for name in dir(utils.gradcam):
        if not name.startswith('_'):
            print(f"  - {name}")
    
    # Try to access the function
    if hasattr(utils.gradcam, 'process_mri_scan'):
        print("\n✓ 'process_mri_scan' is available in module")
    else:
        print("\n✗ 'process_mri_scan' is NOT available in module")
        
except Exception as e:
    print(f"✗ Import failed: {e}")

print("\n" + "="*60)