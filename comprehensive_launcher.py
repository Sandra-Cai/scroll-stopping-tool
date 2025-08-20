#!/usr/bin/env python3
"""
Comprehensive Integration Launcher
Unified launcher that integrates all advanced features of the scroll stopping tool including
AI engine, gamification, analytics, collaboration, mobile integration, security, voice control, and ML analytics.
"""

import json
import time
import threading
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from enum import Enum
import sqlite3
import uuid
from pathlib import Path
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import queue

# Import all advanced systems
try:
    from ai_productivity_engine import AIProductivityEngine, initialize_ai_database
    from gamification_system import GamificationSystem, initialize_gamification_database
    from advanced_analytics_dashboard import AdvancedAnalyticsDashboard, initialize_analytics_database
    from real_time_collaboration_system import RealTimeCollaborationSystem, initialize_collaboration_database
    from mobile_integration import MobileIntegrationSystem, initialize_mobile_database
    from security_privacy_system import SecurityPrivacySystem, initialize_security_database
    from voice_control_system import VoiceControlSystem, initialize_voice_database
    from advanced_ml_analytics import AdvancedMLAnalytics, initialize_ml_database
    ALL_SYSTEMS_AVAILABLE = True
except ImportError as e:
    ALL_SYSTEMS_AVAILABLE = False
    print(f"⚠️ Some systems not available: {e}")

logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    """System status"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    STOPPING = "stopping"

class IntegrationLevel(Enum):
    """Integration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    COMPREHENSIVE = "comprehensive"

@dataclass
class SystemInfo:
    """System information"""
    name: str
    status: SystemStatus
    port: int
    description: str
    dependencies: List[str]
    auto_start: bool
    last_started: Optional[datetime]
    error_message: Optional[str]

class ComprehensiveLauncher:
    """Comprehensive integration launcher"""
    
    def __init__(self, db_path: str = "productivity.db"):
        self.db_path = db_path
        self.systems = {}
        self.status_queue = queue.Queue()
        self.integration_level = IntegrationLevel.COMPREHENSIVE
        
        # Initialize all systems
        self._initialize_systems()
        
        # Create GUI
        self.root = None
        self._create_gui()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitor_systems, daemon=True)
        self.monitoring_thread.start()
        
        print("🚀 Comprehensive Integration Launcher initialized!")
        print("🔗 All advanced systems integrated!")
        print("🎛️ Unified control interface ready!")
    
    def _initialize_systems(self):
        """Initialize all advanced systems"""
        self.systems = {
            "ai_engine": SystemInfo(
                name="AI Productivity Engine",
                status=SystemStatus.STOPPED,
                port=5000,
                description="AI-powered productivity analysis and recommendations",
                dependencies=["scikit-learn", "numpy", "pandas"],
                auto_start=True,
                last_started=None,
                error_message=None
            ),
            "gamification": SystemInfo(
                name="Gamification System",
                status=SystemStatus.STOPPED,
                port=5001,
                description="Achievements, challenges, and rewards system",
                dependencies=[],
                auto_start=True,
                last_started=None,
                error_message=None
            ),
            "analytics": SystemInfo(
                name="Advanced Analytics Dashboard",
                status=SystemStatus.STOPPED,
                port=5002,
                description="Real-time analytics and visualization dashboard",
                dependencies=["dash", "plotly", "pandas"],
                auto_start=True,
                last_started=None,
                error_message=None
            ),
            "collaboration": SystemInfo(
                name="Real-time Collaboration System",
                status=SystemStatus.STOPPED,
                port=5003,
                description="Team collaboration and shared goals",
                dependencies=["flask", "flask-socketio"],
                auto_start=False,
                last_started=None,
                error_message=None
            ),
            "mobile": SystemInfo(
                name="Mobile Integration System",
                status=SystemStatus.STOPPED,
                port=5004,
                description="Mobile app support and push notifications",
                dependencies=["flask", "firebase-admin"],
                auto_start=False,
                last_started=None,
                error_message=None
            ),
            "security": SystemInfo(
                name="Security & Privacy System",
                status=SystemStatus.STOPPED,
                port=5005,
                description="Data encryption and privacy controls",
                dependencies=["cryptography", "bcrypt", "jwt"],
                auto_start=True,
                last_started=None,
                error_message=None
            ),
            "voice": SystemInfo(
                name="Voice Control System",
                status=SystemStatus.STOPPED,
                port=5006,
                description="Voice commands and accessibility features",
                dependencies=["speech_recognition", "pyttsx3"],
                auto_start=False,
                last_started=None,
                error_message=None
            ),
            "ml_analytics": SystemInfo(
                name="Advanced ML Analytics",
                status=SystemStatus.STOPPED,
                port=5007,
                description="Machine learning predictions and insights",
                dependencies=["scikit-learn", "xgboost", "lightgbm"],
                auto_start=True,
                last_started=None,
                error_message=None
            )
        }
    
    def _create_gui(self):
        """Create the main GUI"""
        self.root = tk.Tk()
        self.root.title("Scroll Stopping Tool - Comprehensive Launcher")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 Comprehensive Integration Launcher", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Status overview
        self._create_status_overview(main_frame)
        
        # System controls
        self._create_system_controls(main_frame)
        
        # Integration level selector
        self._create_integration_selector(main_frame)
        
        # Quick actions
        self._create_quick_actions(main_frame)
        
        # Log area
        self._create_log_area(main_frame)
    
    def _create_status_overview(self, parent):
        """Create status overview section"""
        status_frame = ttk.LabelFrame(parent, text="System Status Overview", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Status grid
        self.status_labels = {}
        row = 0
        col = 0
        for system_id, system in self.systems.items():
            frame = ttk.Frame(status_frame)
            frame.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
            
            # System name
            name_label = ttk.Label(frame, text=system.name, font=('Arial', 10, 'bold'))
            name_label.pack()
            
            # Status indicator
            status_label = ttk.Label(frame, text="●", font=('Arial', 16))
            status_label.pack()
            self.status_labels[system_id] = status_label
            
            # Update status
            self._update_status_indicator(system_id, system.status)
            
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(4):
            status_frame.columnconfigure(i, weight=1)
    
    def _create_system_controls(self, parent):
        """Create system control buttons"""
        controls_frame = ttk.LabelFrame(parent, text="System Controls", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Control buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Start All Systems", 
                  command=self.start_all_systems).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop All Systems", 
                  command=self.stop_all_systems).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Restart All Systems", 
                  command=self.restart_all_systems).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Check Status", 
                  command=self.check_all_status).pack(side=tk.LEFT, padx=5)
        
        # Individual system controls
        self.system_buttons = {}
        for system_id, system in self.systems.items():
            system_frame = ttk.Frame(controls_frame)
            system_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(system_frame, text=f"{system.name}:").pack(side=tk.LEFT, padx=(0, 10))
            
            start_btn = ttk.Button(system_frame, text="Start", 
                                 command=lambda s=system_id: self.start_system(s))
            start_btn.pack(side=tk.LEFT, padx=2)
            
            stop_btn = ttk.Button(system_frame, text="Stop", 
                                command=lambda s=system_id: self.stop_system(s))
            stop_btn.pack(side=tk.LEFT, padx=2)
            
            open_btn = ttk.Button(system_frame, text="Open", 
                                command=lambda s=system_id: self.open_system(s))
            open_btn.pack(side=tk.LEFT, padx=2)
            
            self.system_buttons[system_id] = {
                'start': start_btn,
                'stop': stop_btn,
                'open': open_btn
            }
    
    def _create_integration_selector(self, parent):
        """Create integration level selector"""
        integration_frame = ttk.LabelFrame(parent, text="Integration Level", padding=10)
        integration_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Integration level variable
        self.integration_var = tk.StringVar(value=self.integration_level.value)
        
        # Radio buttons
        for level in IntegrationLevel:
            ttk.Radiobutton(integration_frame, text=level.value.title(), 
                           variable=self.integration_var, value=level.value,
                           command=self._on_integration_change).pack(anchor=tk.W)
    
    def _create_quick_actions(self, parent):
        """Create quick action buttons"""
        actions_frame = ttk.LabelFrame(parent, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Action buttons
        ttk.Button(actions_frame, text="Open Analytics Dashboard", 
                  command=self.open_analytics_dashboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Start Voice Control", 
                  command=self.start_voice_control).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Show ML Insights", 
                  command=self.show_ml_insights).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Export Data", 
                  command=self.export_all_data).pack(side=tk.LEFT, padx=5)
    
    def _create_log_area(self, parent):
        """Create log display area"""
        log_frame = ttk.LabelFrame(parent, text="System Logs", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log text area
        self.log_text = tk.Text(log_frame, height=10, bg='#1e1e1e', fg='#ffffff')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def start_all_systems(self):
        """Start all systems"""
        self.log("🚀 Starting all systems...")
        
        for system_id in self.systems.keys():
            if self.systems[system_id].auto_start:
                self.start_system(system_id)
        
        self.log("✅ All auto-start systems initiated")
    
    def stop_all_systems(self):
        """Stop all systems"""
        self.log("🛑 Stopping all systems...")
        
        for system_id in self.systems.keys():
            self.stop_system(system_id)
        
        self.log("✅ All systems stopped")
    
    def restart_all_systems(self):
        """Restart all systems"""
        self.log("🔄 Restarting all systems...")
        self.stop_all_systems()
        time.sleep(2)
        self.start_all_systems()
    
    def check_all_status(self):
        """Check status of all systems"""
        self.log("🔍 Checking system status...")
        
        for system_id, system in self.systems.items():
            self._check_system_status(system_id)
    
    def start_system(self, system_id: str):
        """Start a specific system"""
        try:
            system = self.systems[system_id]
            system.status = SystemStatus.STARTING
            self._update_status_indicator(system_id, system.status)
            
            self.log(f"🔄 Starting {system.name}...")
            
            # Start system based on type
            if system_id == "ai_engine":
                self._start_ai_engine()
            elif system_id == "gamification":
                self._start_gamification()
            elif system_id == "analytics":
                self._start_analytics()
            elif system_id == "collaboration":
                self._start_collaboration()
            elif system_id == "mobile":
                self._start_mobile()
            elif system_id == "security":
                self._start_security()
            elif system_id == "voice":
                self._start_voice()
            elif system_id == "ml_analytics":
                self._start_ml_analytics()
            
            system.status = SystemStatus.RUNNING
            system.last_started = datetime.now()
            self._update_status_indicator(system_id, system.status)
            
            self.log(f"✅ {system.name} started successfully")
            
        except Exception as e:
            system.status = SystemStatus.ERROR
            system.error_message = str(e)
            self._update_status_indicator(system_id, system.status)
            self.log(f"❌ Error starting {system.name}: {e}")
    
    def stop_system(self, system_id: str):
        """Stop a specific system"""
        try:
            system = self.systems[system_id]
            system.status = SystemStatus.STOPPING
            self._update_status_indicator(system_id, system.status)
            
            self.log(f"🛑 Stopping {system.name}...")
            
            # Stop system based on type
            if system_id == "ai_engine":
                self._stop_ai_engine()
            elif system_id == "gamification":
                self._stop_gamification()
            elif system_id == "analytics":
                self._stop_analytics()
            elif system_id == "collaboration":
                self._stop_collaboration()
            elif system_id == "mobile":
                self._stop_mobile()
            elif system_id == "security":
                self._stop_security()
            elif system_id == "voice":
                self._stop_voice()
            elif system_id == "ml_analytics":
                self._stop_ml_analytics()
            
            system.status = SystemStatus.STOPPED
            self._update_status_indicator(system_id, system.status)
            
            self.log(f"✅ {system.name} stopped")
            
        except Exception as e:
            system.status = SystemStatus.ERROR
            system.error_message = str(e)
            self._update_status_indicator(system_id, system.status)
            self.log(f"❌ Error stopping {system.name}: {e}")
    
    def open_system(self, system_id: str):
        """Open a system's interface"""
        try:
            system = self.systems[system_id]
            
            if system.status == SystemStatus.RUNNING:
                url = f"http://localhost:{system.port}"
                webbrowser.open(url)
                self.log(f"🌐 Opened {system.name} at {url}")
            else:
                messagebox.showwarning("System Not Running", 
                                     f"{system.name} is not currently running. Please start it first.")
                
        except Exception as e:
            self.log(f"❌ Error opening {system.name}: {e}")
    
    def _start_ai_engine(self):
        """Start AI productivity engine"""
        if not ALL_SYSTEMS_AVAILABLE:
            raise Exception("AI engine not available")
        
        # Initialize database
        initialize_ai_database(self.db_path)
        
        # Create and start AI engine
        self.ai_engine = AIProductivityEngine(self.db_path)
        self.log("🤖 AI Productivity Engine initialized")
    
    def _start_gamification(self):
        """Start gamification system"""
        if not ALL_SYSTEMS_AVAILABLE:
            raise Exception("Gamification system not available")
        
        # Initialize database
        initialize_gamification_database(self.db_path)
        
        # Create gamification system
        self.gamification = GamificationSystem(self.db_path)
        self.log("🎮 Gamification System initialized")
    
    def _start_analytics(self):
        """Start analytics dashboard"""
        if not ALL_SYSTEMS_AVAILABLE:
            raise Exception("Analytics dashboard not available")
        
        # Initialize database
        initialize_analytics_database(self.db_path)
        
        # Create analytics dashboard
        self.analytics = AdvancedAnalyticsDashboard(self.db_path)
        
        # Start dashboard in background
        dashboard_thread = threading.Thread(target=self._run_analytics_dashboard, daemon=True)
        dashboard_thread.start()
        
        self.log("📊 Analytics Dashboard started")
    
    def _start_collaboration(self):
        """Start collaboration system"""
        if not ALL_SYSTEMS_AVAILABLE:
            raise Exception("Collaboration system not available")
        
        # Initialize database
        initialize_collaboration_database(self.db_path)
        
        # Create collaboration system
        self.collaboration = RealTimeCollaborationSystem(self.db_path)
        
        # Start server in background
        server_thread = threading.Thread(target=self._run_collaboration_server, daemon=True)
        server_thread.start()
        
        self.log("👥 Collaboration System started")
    
    def _start_mobile(self):
        """Start mobile integration"""
        if not ALL_SYSTEMS_AVAILABLE:
            raise Exception("Mobile integration not available")
        
        # Initialize database
        initialize_mobile_database(self.db_path)
        
        # Create mobile integration
        self.mobile = MobileIntegrationSystem(self.db_path)
        
        # Start server in background
        server_thread = threading.Thread(target=self._run_mobile_server, daemon=True)
        server_thread.start()
        
        self.log("📱 Mobile Integration started")
    
    def _start_security(self):
        """Start security system"""
        if not ALL_SYSTEMS_AVAILABLE:
            raise Exception("Security system not available")
        
        # Initialize database
        initialize_security_database(self.db_path)
        
        # Create security system
        self.security = SecurityPrivacySystem(self.db_path)
        
        # Start server in background
        server_thread = threading.Thread(target=self._run_security_server, daemon=True)
        server_thread.start()
        
        self.log("🔒 Security System started")
    
    def _start_voice(self):
        """Start voice control system"""
        if not ALL_SYSTEMS_AVAILABLE:
            raise Exception("Voice control not available")
        
        # Initialize database
        initialize_voice_database(self.db_path)
        
        # Create voice control system
        self.voice = VoiceControlSystem(self.db_path)
        
        # Start voice session
        self.voice_session_id = self.voice.start_voice_session("launcher_user")
        
        self.log("🎤 Voice Control System started")
    
    def _start_ml_analytics(self):
        """Start ML analytics system"""
        if not ALL_SYSTEMS_AVAILABLE:
            raise Exception("ML analytics not available")
        
        # Initialize database
        initialize_ml_database(self.db_path)
        
        # Create ML analytics system
        self.ml_analytics = AdvancedMLAnalytics(self.db_path)
        
        # Train models
        self.ml_analytics.train_models()
        
        self.log("🤖 ML Analytics System started")
    
    def _stop_ai_engine(self):
        """Stop AI engine"""
        if hasattr(self, 'ai_engine'):
            delattr(self, 'ai_engine')
    
    def _stop_gamification(self):
        """Stop gamification system"""
        if hasattr(self, 'gamification'):
            delattr(self, 'gamification')
    
    def _stop_analytics(self):
        """Stop analytics dashboard"""
        if hasattr(self, 'analytics'):
            delattr(self, 'analytics')
    
    def _stop_collaboration(self):
        """Stop collaboration system"""
        if hasattr(self, 'collaboration'):
            delattr(self, 'collaboration')
    
    def _stop_mobile(self):
        """Stop mobile integration"""
        if hasattr(self, 'mobile'):
            delattr(self, 'mobile')
    
    def _stop_security(self):
        """Stop security system"""
        if hasattr(self, 'security'):
            delattr(self, 'security')
    
    def _stop_voice(self):
        """Stop voice control system"""
        if hasattr(self, 'voice') and hasattr(self, 'voice_session_id'):
            self.voice.stop_voice_session(self.voice_session_id)
            delattr(self, 'voice')
            delattr(self, 'voice_session_id')
    
    def _stop_ml_analytics(self):
        """Stop ML analytics system"""
        if hasattr(self, 'ml_analytics'):
            delattr(self, 'ml_analytics')
    
    def _run_analytics_dashboard(self):
        """Run analytics dashboard server"""
        try:
            self.analytics.run_server(port=5002)
        except Exception as e:
            self.log(f"❌ Analytics dashboard error: {e}")
    
    def _run_collaboration_server(self):
        """Run collaboration server"""
        try:
            self.collaboration.run_server(port=5003)
        except Exception as e:
            self.log(f"❌ Collaboration server error: {e}")
    
    def _run_mobile_server(self):
        """Run mobile integration server"""
        try:
            self.mobile.run_server(port=5004)
        except Exception as e:
            self.log(f"❌ Mobile server error: {e}")
    
    def _run_security_server(self):
        """Run security server"""
        try:
            self.security.run_server(port=5005)
        except Exception as e:
            self.log(f"❌ Security server error: {e}")
    
    def open_analytics_dashboard(self):
        """Open analytics dashboard"""
        webbrowser.open("http://localhost:5002")
        self.log("📊 Opening Analytics Dashboard")
    
    def start_voice_control(self):
        """Start voice control session"""
        if hasattr(self, 'voice'):
            self.voice.speak("Voice control activated. How can I help you?")
            self.log("🎤 Voice control activated")
        else:
            messagebox.showwarning("Voice Control", "Voice control system is not running")
    
    def show_ml_insights(self):
        """Show ML insights"""
        if hasattr(self, 'ml_analytics'):
            insights = self.ml_analytics.get_ml_insights("launcher_user")
            self.log("🧠 ML Insights:")
            for key, value in insights.items():
                if key != "user_id":
                    self.log(f"  {key}: {value}")
        else:
            messagebox.showwarning("ML Analytics", "ML Analytics system is not running")
    
    def export_all_data(self):
        """Export all system data"""
        try:
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export database
            import shutil
            shutil.copy2(self.db_path, export_dir / f"productivity_data_{timestamp}.db")
            
            # Export configuration
            config_data = {
                "export_date": datetime.now().isoformat(),
                "integration_level": self.integration_level.value,
                "systems": {
                    system_id: {
                        "name": system.name,
                        "status": system.status.value,
                        "port": system.port,
                        "auto_start": system.auto_start
                    }
                    for system_id, system in self.systems.items()
                }
            }
            
            with open(export_dir / f"launcher_config_{timestamp}.json", 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.log(f"📤 Data exported to {export_dir}")
            messagebox.showinfo("Export Complete", f"Data exported to {export_dir}")
            
        except Exception as e:
            self.log(f"❌ Export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def _on_integration_change(self):
        """Handle integration level change"""
        new_level = IntegrationLevel(self.integration_var.get())
        self.integration_level = new_level
        
        # Update auto-start settings based on level
        if new_level == IntegrationLevel.BASIC:
            for system_id, system in self.systems.items():
                system.auto_start = system_id in ["ai_engine", "gamification"]
        elif new_level == IntegrationLevel.STANDARD:
            for system_id, system in self.systems.items():
                system.auto_start = system_id in ["ai_engine", "gamification", "analytics"]
        elif new_level == IntegrationLevel.ADVANCED:
            for system_id, system in self.systems.items():
                system.auto_start = system_id in ["ai_engine", "gamification", "analytics", "security", "ml_analytics"]
        elif new_level == IntegrationLevel.COMPREHENSIVE:
            for system_id, system in self.systems.items():
                system.auto_start = system_id in ["ai_engine", "gamification", "analytics", "security", "ml_analytics"]
        
        self.log(f"🔧 Integration level changed to {new_level.value}")
    
    def _update_status_indicator(self, system_id: str, status: SystemStatus):
        """Update status indicator in GUI"""
        if system_id in self.status_labels:
            label = self.status_labels[system_id]
            
            if status == SystemStatus.RUNNING:
                label.configure(text="🟢", foreground="green")
            elif status == SystemStatus.STARTING:
                label.configure(text="🟡", foreground="orange")
            elif status == SystemStatus.STOPPING:
                label.configure(text="🟡", foreground="orange")
            elif status == SystemStatus.ERROR:
                label.configure(text="🔴", foreground="red")
            else:  # STOPPED
                label.configure(text="⚫", foreground="gray")
    
    def _check_system_status(self, system_id: str):
        """Check status of a specific system"""
        try:
            system = self.systems[system_id]
            
            # Simple port check
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', system.port))
            sock.close()
            
            if result == 0:
                if system.status != SystemStatus.RUNNING:
                    system.status = SystemStatus.RUNNING
                    self._update_status_indicator(system_id, system.status)
            else:
                if system.status == SystemStatus.RUNNING:
                    system.status = SystemStatus.STOPPED
                    self._update_status_indicator(system_id, system.status)
                    
        except Exception as e:
            self.log(f"❌ Error checking {system.name} status: {e}")
    
    def _monitor_systems(self):
        """Monitor system status"""
        while True:
            try:
                # Check status every 30 seconds
                time.sleep(30)
                
                for system_id in self.systems.keys():
                    self._check_system_status(system_id)
                    
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(60)
    
    def log(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Update GUI log
        if self.root:
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
        
        # Also print to console
        print(log_message.strip())
    
    def run(self):
        """Run the launcher GUI"""
        if self.root:
            self.log("🚀 Comprehensive Launcher started")
            self.root.mainloop()

def main():
    """Main function"""
    print("🚀 Starting Comprehensive Integration Launcher...")
    
    # Create launcher
    launcher = ComprehensiveLauncher()
    
    # Start auto-start systems
    launcher.start_all_systems()
    
    # Run GUI
    launcher.run()

if __name__ == "__main__":
    main()
