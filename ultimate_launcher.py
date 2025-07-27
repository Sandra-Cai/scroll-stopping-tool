#!/usr/bin/env python3
"""
Ultimate Launcher - Enhanced Scroll Stopping Tool
Launches the complete application with all features.
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def launch_ultimate_application():
    """Launch the ultimate application with all features"""
    
    print("🚀 LAUNCHING ULTIMATE ENHANCED SCROLL STOPPING TOOL")
    print("=" * 60)
    
    # Check if main application exists
    if not os.path.exists('scroll_stopping_tool_enhanced.py'):
        print("❌ Main application not found!")
        return False
    
    # Check for optional modules
    optional_modules = [
        'ai_assistant.py',
        'advanced_visualization.py',
        'smart_notifications.py',
        'voice_control.py',
        'web_api.py'
    ]
    
    available_modules = []
    for module in optional_modules:
        if os.path.exists(module):
            available_modules.append(module)
    
    print(f"✅ Main application: scroll_stopping_tool_enhanced.py")
    print(f"✅ Available advanced modules: {len(available_modules)}")
    
    # Launch web API in background
    if 'web_api.py' in available_modules:
        print("🌐 Starting Web API server...")
        web_api_thread = threading.Thread(
            target=lambda: subprocess.run([sys.executable, 'web_api.py']),
            daemon=True
        )
        web_api_thread.start()
        time.sleep(2)
    
    # Launch main application
    print("🎯 Launching main application...")
    try:
        subprocess.run([sys.executable, 'scroll_stopping_tool_enhanced.py'])
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = launch_ultimate_application()
    if success:
        print("✅ Ultimate application launched successfully!")
    else:
        print("❌ Failed to launch ultimate application")
