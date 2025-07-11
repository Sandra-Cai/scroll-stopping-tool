#!/usr/bin/env python3
"""
Installation script for the Scroll Stopping Tool
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut (optional)"""
    try:
        import platform
        system = platform.system()
        
        if system == "Windows":
            # Create Windows shortcut
            shortcut_content = f'''@echo off
cd /d "{os.path.dirname(os.path.abspath(__file__))}"
python run.py
pause'''
            with open("Scroll Stopping Tool.bat", "w") as f:
                f.write(shortcut_content)
            print("✓ Created Windows shortcut: 'Scroll Stopping Tool.bat'")
            
        elif system == "Darwin":  # macOS
            # Create macOS app launcher
            app_content = f'''#!/bin/bash
cd "{os.path.dirname(os.path.abspath(__file__))}"
python3 run.py'''
            with open("Scroll Stopping Tool.command", "w") as f:
                f.write(app_content)
            os.chmod("Scroll Stopping Tool.command", 0o755)
            print("✓ Created macOS launcher: 'Scroll Stopping Tool.command'")
            
        elif system == "Linux":
            # Create Linux desktop file
            desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Scroll Stopping Tool
Comment=Monitor and limit social media usage
Exec=python3 {os.path.join(os.path.abspath('.'), 'run.py')}
Icon=applications-internet
Terminal=true
Categories=Utility;"""
            
            desktop_file = os.path.expanduser("~/Desktop/scroll-stopping-tool.desktop")
            with open(desktop_file, "w") as f:
                f.write(desktop_content)
            os.chmod(desktop_file, 0o755)
            print(f"✓ Created Linux desktop shortcut: {desktop_file}")
            
    except Exception as e:
        print(f"Note: Could not create desktop shortcut: {e}")

def main():
    """Main installation function"""
    print("Scroll Stopping Tool - Installation")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create desktop shortcut
    create_shortcut = input("\nWould you like to create a desktop shortcut? (y/n): ").lower().strip()
    if create_shortcut in ['y', 'yes']:
        create_desktop_shortcut()
    
    print("\n" + "=" * 40)
    print("Installation completed successfully!")
    print("\nTo run the application:")
    print("  python run.py")
    print("\nOr double-click the created shortcut.")
    print("\nHappy mindful browsing! 📱➡️🌱")

if __name__ == "__main__":
    main() 