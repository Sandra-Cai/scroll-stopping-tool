#!/usr/bin/env python3
"""
Test script for Enhanced Scroll Stopping Tool
Verifies core functionality and dependencies.
"""

import sys
import os
import importlib
import subprocess
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    required_modules = [
        'tkinter',
        'psutil',
        'matplotlib',
        'json',
        'threading',
        'datetime',
        'logging',
        'pathlib',
        'typing',
        'dataclasses',
        'enum'
    ]
    
    optional_modules = [
        'plyer',
        'ttkbootstrap',
        'schedule',
        'qrcode',
        'PIL',
        'Flask',
        'pygame',
        'speech_recognition',
        'pyttsx3'
    ]
    
    failed_required = []
    failed_optional = []
    
    # Test required modules
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed_required.append(module)
    
    # Test optional modules
    for module in optional_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module} (optional)")
        except ImportError:
            print(f"  ⚠️  {module} (optional, not available)")
            failed_optional.append(module)
    
    if failed_required:
        print(f"\n❌ Failed to import required modules: {failed_required}")
        return False
    else:
        print("\n✅ All required modules imported successfully")
        return True

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'scroll_stopping_tool_enhanced.py',
        'requirements_enhanced.txt',
        'README_enhanced.md',
        'install_enhanced.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All required files found")
        return True

def test_python_version():
    """Test Python version compatibility"""
    print("\n🐍 Testing Python version...")
    
    version = sys.version_info
    print(f"  Current version: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("  ✅ Python version is compatible")
        return True
    else:
        print("  ❌ Python 3.8+ required")
        return False

def test_application_startup():
    """Test if the application can start"""
    print("\n🚀 Testing application startup...")
    
    try:
        # Try to import the main application
        sys.path.insert(0, str(Path.cwd()))
        
        # Import the main module
        import scroll_stopping_tool_enhanced
        
        print("  ✅ Application module imported successfully")
        
        # Test if we can create the main class (without GUI)
        try:
            # Create a mock root for testing
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            # Test creating the application instance
            app = scroll_stopping_tool_enhanced.EnhancedScrollStoppingTool(root)
            print("  ✅ Application instance created successfully")
            
            # Clean up
            root.destroy()
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to create application instance: {e}")
            return False
            
    except ImportError as e:
        print(f"  ❌ Failed to import application: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Application startup error: {e}")
        return False

def test_configuration():
    """Test configuration management"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from pathlib import Path
        import json
        
        # Test if config directory can be created
        config_dir = Path.home() / ".scroll_stopping_tool"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Test creating a sample config
        sample_config = {
            "daily_limit": 120,
            "break_reminder": 30,
            "notifications_enabled": True
        }
        
        config_file = config_dir / "test_settings.json"
        with open(config_file, 'w') as f:
            json.dump(sample_config, f)
        
        # Test reading the config
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        
        # Clean up test file
        config_file.unlink()
        
        if loaded_config == sample_config:
            print("  ✅ Configuration management works")
            return True
        else:
            print("  ❌ Configuration mismatch")
            return False
            
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_process_monitoring():
    """Test process monitoring functionality"""
    print("\n🔍 Testing process monitoring...")
    
    try:
        import psutil
        
        # Test getting process list
        processes = list(psutil.process_iter(['pid', 'name']))
        
        if len(processes) > 0:
            print(f"  ✅ Process monitoring works ({len(processes)} processes found)")
            return True
        else:
            print("  ❌ No processes found")
            return False
            
    except Exception as e:
        print(f"  ❌ Process monitoring test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🧪 Enhanced Scroll Stopping Tool - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Process Monitoring", test_process_monitoring),
        ("Application Startup", test_application_startup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced version is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

def main():
    """Main test function"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Testing cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 