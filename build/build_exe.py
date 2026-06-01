#!/usr/bin/env python3
"""
Build Script for AI Microscope Application
Creates a single executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller."""
    basedir = Path(__file__).resolve().parent.parent
    spec_file = basedir / "build" / "build_exe_file.spec"
    
    print("=" * 60)
    print("Building AI Microscope Executable")
    print("=" * 60)
    print(f"Base directory: {basedir}")
    print(f"Spec file: {spec_file}")
    
    # Verify spec file exists
    if not spec_file.exists():
        print(f"ERROR: Spec file not found: {spec_file}")
        sys.exit(1)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean previous builds
    dist_dir = basedir / "dist"
    build_dir = basedir / "build" / "build_exe"
    
    if dist_dir.exists():
        print(f"Cleaning previous dist directory...")
        shutil.rmtree(dist_dir, ignore_errors=True)
    
    if build_dir.exists():
        print(f"Cleaning previous build directory...")
        shutil.rmtree(build_dir, ignore_errors=True)
    
    # Build the executable
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]
    
    print(f"\nRunning: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        subprocess.check_call(cmd)
        print("-" * 60)
        print("\n✓ Build completed successfully!")
        
        exe_path = basedir / 'dist' / 'DMB_AI_Microscope.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✓ Executable: {exe_path}")
            print(f"✓ Size: {size_mb:.1f} MB")
        else:
            print(f"⚠ Warning: Expected executable not found at {exe_path}")
            
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Build failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
