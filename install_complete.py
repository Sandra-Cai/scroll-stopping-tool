#!/usr/bin/env python3
"""
Complete Installation Script for Enhanced Scroll Stopping Tool with Advanced Features
"""

import subprocess
import sys
import os
from pathlib import Path

def install_complete():
    """Install all dependencies including advanced features"""
    
    print("🚀 Installing Enhanced Scroll Stopping Tool with Advanced Features")
    print("=" * 70)
    
    # Install core requirements
    print("📦 Installing core dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_complete.txt"], check=True)
        print("✅ Core dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install core dependencies: {e}")
        return False
    
    # Install optional ML dependencies
    print("🤖 Installing machine learning dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "scikit-learn", "pandas", "numpy"], check=True)
        print("✅ ML dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  ML dependencies failed (optional): {e}")
    
    # Test the installation
    print("🧪 Testing installation...")
    try:
        result = subprocess.run([sys.executable, "test_enhanced.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Installation test passed")
        else:
            print("⚠️  Installation test had issues")
    except Exception as e:
        print(f"⚠️  Could not run installation test: {e}")
    
    print("\n🎉 Installation completed!")
    print("\n🎯 To run the enhanced version with advanced features:")
    print("   python scroll_stopping_tool_enhanced.py")
    print("\n📊 Advanced features include:")
    print("   • Machine Learning Predictions")
    print("   • Advanced Analytics Dashboard")
    print("   • Gamification System")
    print("   • Smart Insights")
    print("   • Achievement Tracking")
    
    return True

if __name__ == "__main__":
    install_complete()
