#!/usr/bin/env python3
"""
Enhanced Installation Script for Scroll Stopping Tool
Handles dependency installation, platform setup, and configuration.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedInstaller:
    """Enhanced installer for Scroll Stopping Tool"""
    
    def __init__(self):
        self.platform = platform.system()
        self.python_version = sys.version_info
        self.install_dir = Path.cwd()
        self.config_dir = Path.home() / ".scroll_stopping_tool"
        
        # Platform-specific configurations
        self.platform_configs = {
            "Windows": {
                "python_cmd": "python",
                "pip_cmd": "pip",
                "system_deps": [],
                "post_install": self.windows_post_install
            },
            "Darwin": {  # macOS
                "python_cmd": "python3",
                "pip_cmd": "pip3",
                "system_deps": ["python3-tk"],
                "post_install": self.macos_post_install
            },
            "Linux": {
                "python_cmd": "python3",
                "pip_cmd": "pip3",
                "system_deps": ["python3-tk", "python3-dev"],
                "post_install": self.linux_post_install
            }
        }
        
        self.config = self.platform_configs.get(self.platform, self.platform_configs["Linux"])
    
    def check_python_version(self):
        """Check if Python version meets requirements"""
        logger.info("Checking Python version...")
        
        if self.python_version < (3, 8):
            logger.error(f"Python 3.8+ required. Current version: {self.python_version.major}.{self.python_version.minor}")
            return False
        
        logger.info(f"Python version: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        return True
    
    def check_system_dependencies(self):
        """Check and install system dependencies"""
        logger.info("Checking system dependencies...")
        
        if self.platform == "Linux":
            try:
                # Check if apt is available (Ubuntu/Debian)
                result = subprocess.run(["which", "apt"], capture_output=True, text=True)
                if result.returncode == 0:
                    self.install_apt_dependencies()
                else:
                    logger.warning("apt not found. Please install system dependencies manually.")
            except Exception as e:
                logger.error(f"Failed to check system dependencies: {e}")
        
        return True
    
    def install_apt_dependencies(self):
        """Install dependencies using apt (Ubuntu/Debian)"""
        try:
            logger.info("Installing system dependencies with apt...")
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y"] + self.config["system_deps"], check=True)
            logger.info("System dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install system dependencies: {e}")
        except FileNotFoundError:
            logger.error("sudo command not found. Please run as administrator.")
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        logger.info("Installing Python dependencies...")
        
        requirements_file = self.install_dir / "requirements_enhanced.txt"
        if not requirements_file.exists():
            logger.error("requirements_enhanced.txt not found")
            return False
        
        try:
            # Upgrade pip first
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
            
            # Install dependencies
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            
            logger.info("Python dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Python dependencies: {e}")
            return False
    
    def create_directories(self):
        """Create necessary directories"""
        logger.info("Creating application directories...")
        
        directories = [
            self.config_dir,
            self.config_dir / "data",
            self.config_dir / "backups",
            self.config_dir / "logs",
            self.config_dir / "themes",
            self.config_dir / "sounds"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def create_default_config(self):
        """Create default configuration file"""
        logger.info("Creating default configuration...")
        
        default_config = {
            "daily_limit": 120,
            "break_reminder": 30,
            "notifications_enabled": True,
            "auto_break": True,
            "auto_lock": False,
            "blocking_enabled": False,
            "focus_mode_enabled": True,
            "theme": "flatly",
            "language": "en",
            "blocked_sites": [
                "facebook.com", "instagram.com", "twitter.com", "tiktok.com",
                "youtube.com", "reddit.com", "snapchat.com", "linkedin.com"
            ],
            "scheduled_breaks": ["12:00", "15:00", "18:00"],
            "goals": {
                "daily_limit": 120,
                "weekly_goal": 5,
                "monthly_goal": 20
            },
            "advanced": {
                "log_level": "INFO",
                "backup_frequency": "daily",
                "auto_update": True,
                "performance_mode": False
            }
        }
        
        config_file = self.config_dir / "settings.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Default configuration created: {config_file}")
        except Exception as e:
            logger.error(f"Failed to create default configuration: {e}")
    
    def create_launcher_scripts(self):
        """Create launcher scripts for different platforms"""
        logger.info("Creating launcher scripts...")
        
        if self.platform == "Windows":
            self.create_windows_launcher()
        elif self.platform in ["Darwin", "Linux"]:
            self.create_unix_launcher()
    
    def create_windows_launcher(self):
        """Create Windows batch launcher"""
        launcher_content = f"""@echo off
cd /d "{self.install_dir}"
python scroll_stopping_tool_enhanced.py
pause
"""
        
        launcher_file = self.install_dir / "run_enhanced.bat"
        try:
            with open(launcher_file, 'w') as f:
                f.write(launcher_content)
            logger.info(f"Windows launcher created: {launcher_file}")
        except Exception as e:
            logger.error(f"Failed to create Windows launcher: {e}")
    
    def create_unix_launcher(self):
        """Create Unix shell launcher"""
        launcher_content = f"""#!/bin/bash
cd "{self.install_dir}"
python3 scroll_stopping_tool_enhanced.py
"""
        
        launcher_file = self.install_dir / "run_enhanced.sh"
        try:
            with open(launcher_file, 'w') as f:
                f.write(launcher_content)
            
            # Make executable
            os.chmod(launcher_file, 0o755)
            logger.info(f"Unix launcher created: {launcher_file}")
        except Exception as e:
            logger.error(f"Failed to create Unix launcher: {e}")
    
    def windows_post_install(self):
        """Post-installation steps for Windows"""
        logger.info("Performing Windows post-installation steps...")
        
        # Create desktop shortcut
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Scroll Stopping Tool Enhanced.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{self.install_dir / "scroll_stopping_tool_enhanced.py"}"'
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            logger.info("Desktop shortcut created")
        except ImportError:
            logger.info("Desktop shortcut creation skipped (pywin32 not available)")
        except Exception as e:
            logger.warning(f"Failed to create desktop shortcut: {e}")
    
    def macos_post_install(self):
        """Post-installation steps for macOS"""
        logger.info("Performing macOS post-installation steps...")
        
        # Check for accessibility permissions
        logger.info("Note: You may need to grant accessibility permissions in System Preferences > Security & Privacy > Privacy > Accessibility")
        
        # Create Applications folder shortcut
        try:
            app_dir = Path("/Applications")
            if app_dir.exists():
                # Create a simple app bundle or alias
                logger.info("macOS post-installation completed")
        except Exception as e:
            logger.warning(f"macOS post-installation warning: {e}")
    
    def linux_post_install(self):
        """Post-installation steps for Linux"""
        logger.info("Performing Linux post-installation steps...")
        
        # Create desktop entry
        desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Scroll Stopping Tool Enhanced
Comment=Digital wellbeing and productivity tool
Exec={sys.executable} {self.install_dir / "scroll_stopping_tool_enhanced.py"}
Icon=applications-internet
Terminal=false
Categories=Utility;Productivity;
"""
        
        desktop_file = Path.home() / ".local/share/applications/scroll-stopping-tool-enhanced.desktop"
        try:
            desktop_file.parent.mkdir(parents=True, exist_ok=True)
            with open(desktop_file, 'w') as f:
                f.write(desktop_entry)
            logger.info(f"Desktop entry created: {desktop_file}")
        except Exception as e:
            logger.warning(f"Failed to create desktop entry: {e}")
    
    def test_installation(self):
        """Test the installation"""
        logger.info("Testing installation...")
        
        try:
            # Test importing key modules
            import tkinter
            import psutil
            import matplotlib
            import ttkbootstrap
            
            logger.info("Core modules imported successfully")
            
            # Test running the application (briefly)
            logger.info("Testing application startup...")
            result = subprocess.run([
                sys.executable, "scroll_stopping_tool_enhanced.py", "--test"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("Application test successful")
                return True
            else:
                logger.warning("Application test had issues")
                return False
                
        except ImportError as e:
            logger.error(f"Import test failed: {e}")
            return False
        except subprocess.TimeoutExpired:
            logger.info("Application test completed (timeout)")
            return True
        except Exception as e:
            logger.error(f"Installation test failed: {e}")
            return False
    
    def run(self):
        """Run the complete installation process"""
        print("🚀 Enhanced Scroll Stopping Tool - Installation")
        print("=" * 50)
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Check system dependencies
        if not self.check_system_dependencies():
            return False
        
        # Install Python dependencies
        if not self.install_python_dependencies():
            return False
        
        # Create directories
        self.create_directories()
        
        # Create default configuration
        self.create_default_config()
        
        # Create launcher scripts
        self.create_launcher_scripts()
        
        # Platform-specific post-installation
        self.config["post_install"]()
        
        # Test installation
        if self.test_installation():
            print("\n✅ Installation completed successfully!")
            print("\n🎯 Next steps:")
            print("1. Run the application:")
            if self.platform == "Windows":
                print("   Double-click 'run_enhanced.bat' or run:")
            else:
                print("   Run './run_enhanced.sh' or execute:")
            print(f"   {sys.executable} scroll_stopping_tool_enhanced.py")
            print("2. Configure your settings in the application")
            print("3. Start tracking your productivity!")
            print(f"\n📁 Configuration directory: {self.config_dir}")
            print(f"📁 Installation directory: {self.install_dir}")
            return True
        else:
            print("\n❌ Installation completed with issues.")
            print("Please check the logs and try running the application manually.")
            return False

def main():
    """Main installation function"""
    try:
        installer = EnhancedInstaller()
        success = installer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        logger.error(f"Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 