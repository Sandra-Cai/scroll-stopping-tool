#!/usr/bin/env python3
"""
Launcher script for the Scroll Stopping Tool
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from scroll_stopping_tool import main
    main()
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install the required dependencies:")
    print("pip install -r requirements.txt")
except Exception as e:
    print(f"Error running the application: {e}") 