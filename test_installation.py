#!/usr/bin/env python3
"""
Test script to verify the Scroll Stopping Tool installation
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported"""
    required_modules = [
        'tkinter',
        'json',
        'time',
        'threading',
        'psutil',
        'schedule',
        'datetime',
        'plyer',
        'matplotlib',
        'os'
    ]
    
    print("Testing module imports...")
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_main_application():
    """Test if the main application can be imported"""
    try:
        from scroll_stopping_tool import ScrollStoppingTool
        print("✓ Main application class imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import main application: {e}")
        return False

def test_gui_creation():
    """Test if GUI can be created (without showing it)"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        from scroll_stopping_tool import ScrollStoppingTool
        app = ScrollStoppingTool(root)
        
        # Test basic functionality
        assert hasattr(app, 'is_tracking')
        assert hasattr(app, 'settings')
        assert hasattr(app, 'usage_data')
        
        root.destroy()
        print("✓ GUI creation test passed")
        return True
    except Exception as e:
        print(f"✗ GUI creation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Scroll Stopping Tool - Installation Test")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    print()
    
    # Test main application
    app_ok = test_main_application()
    print()
    
    # Test GUI creation
    gui_ok = test_gui_creation()
    print()
    
    # Summary
    print("=" * 40)
    if imports_ok and app_ok and gui_ok:
        print("🎉 All tests passed! The application is ready to use.")
        print("\nYou can now run the application with:")
        print("  python run.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nTry reinstalling dependencies:")
        print("  pip install -r requirements.txt")
    
    return imports_ok and app_ok and gui_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 