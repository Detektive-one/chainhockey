"""
Build script for web version using pygbag.
Run with: python build_web.py
"""

import subprocess
import sys
import os



def build_web():
    """Build the game for web using pygbag"""
    print("Building Chain Hockey for web...")
    print("This will create a web-compatible build in the build/web directory")
    
    # Check if pygbag is installed
    try:
        import pygbag
    except ImportError:
        print("Error: pygbag is not installed. Install it with: pip install pygbag")
        sys.exit(1)
    
    # Build command
    # pygbag will compile main.py and create web build
    cmd = [sys.executable, "-m", "pygbag", "--build", "main.py"]
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild complete! Check the build/web directory for output.")
        print("You can test it by opening index.html in a web browser.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_web()

