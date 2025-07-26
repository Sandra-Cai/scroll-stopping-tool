#!/usr/bin/env python3
"""
Enhanced Scroll Stopping Tool - Launch Script
Demonstrates the complete enhanced application with all advanced features.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print the application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  🚀 Enhanced Scroll Stopping Tool - Complete Edition 🚀     ║
    ║                                                              ║
    ║  A comprehensive digital wellbeing platform with advanced   ║
    ║  features, machine learning, and gamification.              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_installation():
    """Check if all required files are present"""
    print("🔍 Checking installation...")
    
    required_files = [
        'scroll_stopping_tool_enhanced.py',
        'advanced_features.py',
        'ml_analytics.py',
        'gamification.py',
        'requirements_complete.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        print("Please run the integration script first:")
        print("   python integrate_advanced_features.py")
        return False
    
    print("✅ All required files found")
    return True

def check_dependencies():
    """Check if dependencies are installed"""
    print("📦 Checking dependencies...")
    
    try:
        import psutil
        import matplotlib
        import tkinter
        print("✅ Core dependencies available")
        
        # Check optional dependencies
        optional_deps = {
            'ttkbootstrap': 'Enhanced UI themes',
            'pandas': 'Advanced analytics',
            'numpy': 'Data processing',
            'scikit-learn': 'Machine learning'
        }
        
        for dep, description in optional_deps.items():
            try:
                __import__(dep)
                print(f"✅ {dep} - {description}")
            except ImportError:
                print(f"⚠️  {dep} - {description} (optional)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing core dependency: {e}")
        print("Please install dependencies:")
        print("   pip install -r requirements_complete.txt")
        return False

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_enhanced.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("⚠️  Some tests failed")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def show_feature_summary():
    """Show a summary of available features"""
    print("\n🎯 Available Features:")
    print("=" * 50)
    
    features = [
        ("🏗️ Core Features", [
            "Real-time social media tracking",
            "Focus mode with productivity scoring",
            "Smart break reminders",
            "Cross-platform screen locking",
            "Daily usage limits and goals"
        ]),
        ("🤖 Advanced Analytics", [
            "Machine learning predictions",
            "Behavioral pattern recognition",
            "Productivity trend analysis",
            "Smart insights and recommendations",
            "Predictive analytics"
        ]),
        ("🏆 Gamification", [
            "Achievement system (20+ achievements)",
            "Streak tracking and rewards",
            "Level progression system",
            "Experience points and badges",
            "Motivational features"
        ]),
        ("💡 Smart Features", [
            "Adaptive goal setting",
            "AI-powered productivity coaching",
            "Context-aware notifications",
            "Personalized recommendations",
            "Behavioral analysis"
        ]),
        ("📊 Analytics & Reporting", [
            "Comprehensive usage analytics",
            "Focus session analysis",
            "Productivity metrics",
            "Data export (CSV, JSON, PDF)",
            "Visual charts and graphs"
        ])
    ]
    
    for category, feature_list in features:
        print(f"\n{category}:")
        for feature in feature_list:
            print(f"  • {feature}")

def launch_application():
    """Launch the enhanced application"""
    print("\n🚀 Launching Enhanced Scroll Stopping Tool...")
    print("=" * 50)
    
    try:
        # Launch the application
        process = subprocess.Popen([sys.executable, "scroll_stopping_tool_enhanced.py"])
        
        print("✅ Application launched successfully!")
        print("\n🎮 How to use:")
        print("1. Click 'Start Tracking' to begin monitoring")
        print("2. Use 'Focus Mode' for distraction-free work")
        print("3. Check 'Advanced Analytics' for insights")
        print("4. View achievements and progress")
        print("5. Export data for detailed analysis")
        
        print(f"\n📱 Process ID: {process.pid}")
        print("Press Ctrl+C to stop the application")
        
        # Wait for the process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n⏹️  Application stopped by user")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")

def show_demo_options():
    """Show demo options"""
    print("\n🎬 Demo Options:")
    print("=" * 30)
    print("1. Launch full application")
    print("2. Run feature demo")
    print("3. Run tests only")
    print("4. Show feature summary")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                launch_application()
                break
            elif choice == '2':
                print("🎬 Launching feature demo...")
                subprocess.run([sys.executable, "demo_advanced_features.py"])
                break
            elif choice == '3':
                run_tests()
                break
            elif choice == '4':
                show_feature_summary()
                show_demo_options()
                break
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def main():
    """Main launch function"""
    print_banner()
    
    print("🔧 Enhanced Scroll Stopping Tool - Launch Script")
    print("=" * 60)
    
    # Check installation
    if not check_installation():
        return False
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 To install missing dependencies:")
        print("   pip install -r requirements_complete.txt")
        print("   python install_complete.py")
        return False
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Some tests failed, but you can still try the application")
    
    # Show feature summary
    show_feature_summary()
    
    # Show demo options
    show_demo_options()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Launch failed: {e}")
        print("Please check the installation and try again.") 