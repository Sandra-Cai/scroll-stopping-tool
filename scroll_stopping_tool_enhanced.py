#!/usr/bin/env python3
"""
Scroll Stopping Tool - Enhanced Version
A Python application to help users break the habit of excessive social media scrolling.
Enhanced version with improved UI, performance, and features.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import time
import threading
import psutil
import schedule
from datetime import datetime, timedelta
import logging
import sys
import os
import platform
import subprocess
import webbrowser
import urllib.parse
import csv
import sqlite3
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scroll_stopping_tool.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Optional imports with better error handling
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    logger.warning("Plyer not available - notifications will be disabled")

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib not available - charts will be disabled")

try:
    from matplotlib.backends.backend_pdf import PdfPages
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as pdf_canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not available - PDF export will be disabled")

try:
    import smtplib
    from email.mime.text import MIMEText
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False
    logger.warning("SMTP not available - email notifications will be disabled")

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not available - SMS notifications will be disabled")

try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    logger.warning("Google API not available - calendar integration will be disabled")

try:
    import qrcode
    from PIL import Image, ImageTk
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    logger.warning("QRCode/PIL not available - QR code features will be disabled")

try:
    from flask import Flask, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask not available - web API will be disabled")

try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logger.warning("Speech recognition not available - voice features will be disabled")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("Pygame not available - audio features will be disabled")

try:
    import ttkbootstrap as tb
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    logger.warning("ttkbootstrap not available - using default tkinter theme")

# Platform-specific imports
if platform.system() == "Windows":
    try:
        import winsound
        WINSOUND_AVAILABLE = True
    except ImportError:
        WINSOUND_AVAILABLE = False
else:
    WINSOUND_AVAILABLE = False

# Data classes for better type safety
@dataclass
class UsageData:
    """Data class for usage statistics"""
    date: str
    total_time: int
    breaks_taken: int
    focus_sessions: int
    productivity_score: float
    goals_met: bool

@dataclass
class FocusSession:
    """Data class for focus session data"""
    start_time: datetime
    end_time: Optional[datetime]
    duration: int
    interruptions: int
    productivity_score: float
    notes: str = ""

@dataclass
class Settings:
    """Data class for application settings"""
    daily_limit: int = 120
    break_reminder: int = 30
    notifications_enabled: bool = True
    auto_break: bool = True
    auto_lock: bool = False
    blocking_enabled: bool = False
    focus_mode_enabled: bool = True
    theme: str = "flatly"
    language: str = "en"

class Theme(Enum):
    """Available themes"""
    FLATLY = "flatly"
    DARKLY = "darkly"
    LITERA = "litera"
    COSMOS = "cosmos"
    SIMPLEX = "simplex"

class NotificationType(Enum):
    """Notification types"""
    BREAK_REMINDER = "break_reminder"
    LIMIT_REACHED = "limit_reached"
    FOCUS_START = "focus_start"
    FOCUS_END = "focus_end"
    ACHIEVEMENT = "achievement"

# Configuration constants
CONFIG_DIR = Path.home() / ".scroll_stopping_tool"
DATA_DIR = CONFIG_DIR / "data"
BACKUP_DIR = CONFIG_DIR / "backups"
LOG_DIR = CONFIG_DIR / "logs"

# Ensure directories exist
for directory in [CONFIG_DIR, DATA_DIR, BACKUP_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
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
    }
}

# Social media detection patterns
SOCIAL_MEDIA_PATTERNS = {
    "processes": [
        'chrome.exe', 'firefox.exe', 'safari.exe', 'msedge.exe',
        'instagram.exe', 'facebook.exe', 'twitter.exe', 'tiktok.exe'
    ],
    "sites": [
        'facebook.com', 'instagram.com', 'twitter.com', 'tiktok.com',
        'youtube.com', 'reddit.com', 'snapchat.com', 'linkedin.com',
        'pinterest.com', 'whatsapp.com', 'telegram.org', 'discord.com'
    ],
    "keywords": [
        'social', 'media', 'feed', 'scroll', 'post', 'share', 'like'
    ]
}

class DataManager:
    """Manages data persistence and database operations"""
    
    def __init__(self):
        self.db_path = DATA_DIR / "productivity.db"
        self.data_file = DATA_DIR / "usage_data.json"
        self.settings_file = DATA_DIR / "settings.json"
        self.init_database()
        self.load_settings()
    
    def init_database(self):
        """Initialize SQLite database with proper schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create focus sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS focus_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        duration INTEGER,
                        interruptions INTEGER DEFAULT 0,
                        productivity_score REAL DEFAULT 0.0,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create usage statistics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usage_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT UNIQUE NOT NULL,
                        total_time INTEGER DEFAULT 0,
                        breaks_taken INTEGER DEFAULT 0,
                        focus_sessions INTEGER DEFAULT 0,
                        productivity_score REAL DEFAULT 0.0,
                        goals_met BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create achievements table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        type TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file with fallback to defaults"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    logger.info("Settings loaded successfully")
                    return settings
            else:
                logger.info("No settings file found, using defaults")
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return DEFAULT_CONFIG.copy()
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def save_focus_session(self, session: FocusSession):
        """Save focus session to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO focus_sessions 
                    (start_time, end_time, duration, interruptions, productivity_score, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session.start_time.isoformat(),
                    session.end_time.isoformat() if session.end_time else None,
                    session.duration,
                    session.interruptions,
                    session.productivity_score,
                    session.notes
                ))
                conn.commit()
                logger.info("Focus session saved successfully")
        except Exception as e:
            logger.error(f"Failed to save focus session: {e}")
    
    def get_focus_sessions(self, days: int = 30) -> List[FocusSession]:
        """Get focus sessions from the last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT start_time, end_time, duration, interruptions, productivity_score, notes
                    FROM focus_sessions
                    WHERE start_time >= date('now', '-{} days')
                    ORDER BY start_time DESC
                '''.format(days))
                
                sessions = []
                for row in cursor.fetchall():
                    start_time = datetime.fromisoformat(row[0])
                    end_time = datetime.fromisoformat(row[1]) if row[1] else None
                    sessions.append(FocusSession(
                        start_time=start_time,
                        end_time=end_time,
                        duration=row[2],
                        interruptions=row[3],
                        productivity_score=row[4],
                        notes=row[5]
                    ))
                return sessions
        except Exception as e:
            logger.error(f"Failed to get focus sessions: {e}")
            return []

class NotificationManager:
    """Manages all notification types and delivery methods"""
    
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.notification_queue = queue.Queue()
        self.start_notification_thread()
    
    def start_notification_thread(self):
        """Start background thread for notification processing"""
        def notification_worker():
            while True:
                try:
                    notification_data = self.notification_queue.get(timeout=1)
                    self.send_notification(notification_data)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Notification error: {e}")
        
        thread = threading.Thread(target=notification_worker, daemon=True)
        thread.start()
    
    def send_notification(self, notification_data: Dict[str, Any]):
        """Send notification using available methods"""
        title = notification_data.get('title', 'Scroll Stopping Tool')
        message = notification_data.get('message', '')
        notification_type = notification_data.get('type', NotificationType.BREAK_REMINDER)
        
        # System notification
        if PLYER_AVAILABLE and self.settings.get('notifications_enabled', True):
            try:
                notification.notify(
                    title=title,
                    message=message,
                    timeout=10
                )
            except Exception as e:
                logger.error(f"Failed to send system notification: {e}")
        
        # Sound notification
        self.play_notification_sound(notification_type)
        
        # Log notification
        logger.info(f"Notification sent: {title} - {message}")
    
    def play_notification_sound(self, notification_type: NotificationType):
        """Play appropriate sound for notification type"""
        try:
            if WINSOUND_AVAILABLE and platform.system() == "Windows":
                if notification_type == NotificationType.LIMIT_REACHED:
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                else:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
            elif PYGAME_AVAILABLE:
                # Play custom sound files
                pass
        except Exception as e:
            logger.error(f"Failed to play notification sound: {e}")
    
    def queue_notification(self, title: str, message: str, notification_type: NotificationType = NotificationType.BREAK_REMINDER):
        """Queue a notification for sending"""
        self.notification_queue.put({
            'title': title,
            'message': message,
            'type': notification_type
        })

class ProcessMonitor:
    """Monitors system processes for social media activity"""
    
    def __init__(self, patterns: Dict[str, List[str]]):
        self.patterns = patterns
        self.active_processes = set()
        self.last_check = time.time()
    
    def is_social_media_active(self) -> bool:
        """Check if social media processes are currently active"""
        try:
            current_time = time.time()
            # Cache results for 1 second to avoid excessive CPU usage
            if current_time - self.last_check < 1.0:
                return len(self.active_processes) > 0
            
            self.last_check = current_time
            self.active_processes.clear()
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    # Check process names
                    for pattern in self.patterns['processes']:
                        if pattern.lower() in proc_name:
                            self.active_processes.add(proc.pid)
                            return True
                    
                    # Check command line for social media sites
                    cmdline = proc_info.get('cmdline', [])
                    if cmdline:
                        cmdline_str = ' '.join(cmdline).lower()
                        for site in self.patterns['sites']:
                            if site in cmdline_str:
                                self.active_processes.add(proc.pid)
                                return True
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return len(self.active_processes) > 0
            
        except Exception as e:
            logger.error(f"Error checking social media activity: {e}")
            return False
    
    def get_active_processes(self) -> List[str]:
        """Get list of currently active social media processes"""
        try:
            processes = []
            for pid in self.active_processes:
                try:
                    proc = psutil.Process(pid)
                    processes.append(proc.name())
                except psutil.NoSuchProcess:
                    continue
            return processes
        except Exception as e:
            logger.error(f"Error getting active processes: {e}")
            return []



# Advanced Features Integration
try:
    from advanced_features import AdvancedFeatures
    from ml_analytics import PredictiveAnalytics
    from gamification import GamificationEngine
    ADVANCED_FEATURES_AVAILABLE = True
    logger.info("Advanced features loaded successfully")
except ImportError as e:
    ADVANCED_FEATURES_AVAILABLE = False
    logger.warning(f"Advanced features not available: {e}")

class EnhancedScrollStoppingTool:
    """Enhanced version of the Scroll Stopping Tool with improved architecture"""
    
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.setup_managers()
        self.setup_variables()
        self.create_widgets()
        self.start_background_tasks()
        logger.info("Enhanced Scroll Stopping Tool initialized")
    
    def setup_ui(self):
        """Setup the main UI window"""
        if TTKBOOTSTRAP_AVAILABLE:
            self.style = tb.Style('flatly')
        else:
            self.style = ttk.Style()
        
        self.root.title("Scroll Stopping Tool - Enhanced")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f8f9fa')
        
        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def setup_managers(self):
        """Initialize all manager classes"""
        self.data_manager = DataManager()
        self.settings = self.data_manager.load_settings()
        self.notification_manager = NotificationManager(self.settings)
        self.process_monitor = ProcessMonitor(SOCIAL_MEDIA_PATTERNS)
        
        # Advanced features integration
        self.advanced_features = None
        self.ml_analytics = None
        self.gamification = None
        
        if ADVANCED_FEATURES_AVAILABLE:
            self.setup_advanced_features()
    
        # Advanced features integration
        self.advanced_features = None
        self.ml_analytics = None
        self.gamification = None
        
        if ADVANCED_FEATURES_AVAILABLE:
            self.setup_advanced_features()

    def setup_variables(self):
        """Initialize tracking variables"""
        self.is_tracking = False
        self.is_focus_mode = False
        self.tracking_thread = None
        self.focus_thread = None
        self.current_session = None
        self.today_usage = 0
        self.breaks_taken = 0
        self.focus_sessions = 0
        self.productivity_score = 0.0
        self.streak_days = 0
        self.best_streak = 0
        
        # Load today's data
        self.load_today_data()
    
    def create_widgets(self):
        """Create the main GUI widgets with modern design"""
        # Main container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.columnconfigure(0, weight=1)
        
        # Header
        self.create_header(main_container)
        
        # Control panel
        self.create_control_panel(main_container)
        
        # Statistics panel
        self.create_stats_panel(main_container)
        
        # Progress and charts
        self.create_progress_panel(main_container)
        
        # Quick actions
        self.create_quick_actions(main_container)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create the application header"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            header_frame, 
            text="🎯 Enhanced Scroll Stopping Tool", 
            font=('Arial', 24, 'bold')
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Break the habit, boost your productivity",
            font=('Arial', 12),
            foreground='#6c757d'
        )
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Settings button
        settings_btn = ttk.Button(
            header_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            style='secondary.TButton'
        )
        settings_btn.grid(row=0, column=2, rowspan=2, padx=(20, 0))
    
    def create_control_panel(self, parent):
        """Create the main control panel"""
        control_frame = ttk.LabelFrame(parent, text="🎮 Controls", padding="15")
        control_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Primary controls
        primary_frame = ttk.Frame(control_frame)
        primary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.start_button = ttk.Button(
            primary_frame,
            text="▶️ Start Tracking",
            command=self.start_tracking,
            style='success.TButton',
            width=15
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            primary_frame,
            text="⏹️ Stop Tracking",
            command=self.stop_tracking,
            state='disabled',
            style='danger.TButton',
            width=15
        )
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.focus_button = ttk.Button(
            primary_frame,
            text="🎯 Focus Mode",
            command=self.toggle_focus_mode,
            style='info.TButton',
            width=15
        )
        self.focus_button.grid(row=0, column=2, padx=(0, 10))
        
        # Secondary controls
        secondary_frame = ttk.Frame(control_frame)
        secondary_frame.grid(row=1, column=0, sticky="ew")
        
        # Advanced Analytics button
        self.advanced_button = ttk.Button(
            secondary_frame,
            text="🤖 Advanced Analytics",
            command=self.show_advanced_dashboard,
            width=15
        )
        self.advanced_button.grid(row=0, column=4, padx=(0, 10))
        
        ttk.Button(
            secondary_frame,
            text="☕ Take Break",
            command=self.take_break,
            width=12
        ).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(
            secondary_frame,
            text="🔒 Lock Screen",
            command=self.lock_screen,
            width=12
        ).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(
            secondary_frame,
            text="📊 Analytics",
            command=self.open_analytics,
            width=12
        ).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(
            secondary_frame,
            text="📤 Export Data",
            command=self.export_data,
            width=12
        ).grid(row=0, column=3, padx=(0, 10))
    
    def create_stats_panel(self, parent):
        """Create the statistics display panel"""
        stats_frame = ttk.LabelFrame(parent, text="📈 Today's Statistics", padding="15")
        stats_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        # Create a grid for stats
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)
        
        # Usage stats
        self.usage_label = ttk.Label(
            stats_frame,
            text="⏱️ Usage: 0 minutes",
            font=('Arial', 14, 'bold')
        )
        self.usage_label.grid(row=0, column=0, pady=5)
        
        self.limit_label = ttk.Label(
            stats_frame,
            text="🎯 Limit: 0/120 min",
            font=('Arial', 14, 'bold')
        )
        self.limit_label.grid(row=0, column=1, pady=5)
        
        self.breaks_label = ttk.Label(
            stats_frame,
            text="☕ Breaks: 0",
            font=('Arial', 14, 'bold')
        )
        self.breaks_label.grid(row=0, column=2, pady=5)
        
        self.focus_label = ttk.Label(
            stats_frame,
            text="🎯 Focus: 0 sessions",
            font=('Arial', 14, 'bold')
        )
        self.focus_label.grid(row=0, column=3, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            stats_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            style='success.Horizontal.TProgressbar'
        )
        self.progress_bar.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 0))
    
    def create_progress_panel(self, parent):
        """Create progress and achievement panel"""
        progress_frame = ttk.LabelFrame(parent, text="🏆 Progress & Achievements", padding="15")
        progress_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        # Streak information
        streak_frame = ttk.Frame(progress_frame)
        streak_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.streak_label = ttk.Label(
            streak_frame,
            text="🔥 Current Streak: 0 days",
            font=('Arial', 12, 'bold'),
            foreground='#dc3545'
        )
        self.streak_label.grid(row=0, column=0, padx=(0, 20))
        
        self.best_streak_label = ttk.Label(
            streak_frame,
            text="🏆 Best Streak: 0 days",
            font=('Arial', 12, 'bold'),
            foreground='#28a745'
        )
        self.best_streak_label.grid(row=0, column=1)
        
        # Productivity score
        self.productivity_label = ttk.Label(
            progress_frame,
            text="📊 Productivity Score: 0%",
            font=('Arial', 16, 'bold'),
            foreground='#007bff'
        )
        self.productivity_label.grid(row=1, column=0, pady=(10, 0))
    
    def create_quick_actions(self, parent):
        """Create quick action buttons"""
        actions_frame = ttk.LabelFrame(parent, text="⚡ Quick Actions", padding="15")
        actions_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        
        # Quick action buttons
        actions = [
            ("🎵 Music Player", self.open_music_player),
            ("📅 Schedule Focus", self.schedule_focus),
            ("🎯 Custom Timers", self.open_custom_timers),
            ("📱 Mobile Sync", self.open_mobile_sync),
            ("☁️ Cloud Backup", self.backup_data),
            ("🔄 Import Data", self.import_data)
        ]
        
        for i, (text, command) in enumerate(actions):
            btn = ttk.Button(
                actions_frame,
                text=text,
                command=command,
                width=15
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=5, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready to start tracking your productivity!",
            font=('Arial', 10),
            foreground='#6c757d'
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # Update display
        self.update_display()
    
    def load_today_data(self):
        """Load today's usage data"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            # Load from database or create new entry
            # This is a simplified version - in full implementation, load from database
            self.today_usage = 0
            self.breaks_taken = 0
            self.focus_sessions = 0
            self.productivity_score = 0.0
        except Exception as e:
            logger.error(f"Failed to load today's data: {e}")
    
    def start_tracking(self):
        """Start tracking social media usage"""
        if not self.is_tracking:
            self.is_tracking = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_label.config(text="Tracking active - monitoring social media usage...")
            
            # Start tracking thread
            self.tracking_thread = threading.Thread(target=self.tracking_loop, daemon=True)
            self.tracking_thread.start()
            
            logger.info("Started tracking social media usage")
    
    def stop_tracking(self):
        """Stop tracking social media usage"""
        if self.is_tracking:
            self.is_tracking = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.status_label.config(text="Tracking stopped")
            
            logger.info("Stopped tracking social media usage")
    
    def tracking_loop(self):
        """Main tracking loop"""
        while self.is_tracking:
            try:
                if self.process_monitor.is_social_media_active():
                    self.today_usage += 1  # Increment by 1 minute
                    
                    # Check if daily limit reached
                    if self.today_usage >= self.settings.get('daily_limit', 120):
                        self.notification_manager.queue_notification(
                            "Daily Limit Reached!",
                            "You've reached your daily social media limit. Time to take a break!",
                            NotificationType.LIMIT_REACHED
                        )
                        
                        if self.settings.get('auto_lock', False):
                            self.lock_screen()
                
                # Update display every minute
                if self.today_usage % 60 == 0:
                    self.root.after(0, self.update_display)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}")
                time.sleep(60)
    
    def toggle_focus_mode(self):
        """Toggle focus mode on/off"""
        if not self.is_focus_mode:
            self.start_focus_mode()
        else:
            self.stop_focus_mode()
    
    def start_focus_mode(self):
        """Start focus mode"""
        self.is_focus_mode = True
        self.focus_button.config(text="⏹️ Exit Focus", style='danger.TButton')
        self.current_session = FocusSession(
            start_time=datetime.now(),
            end_time=None,
            duration=0,
            interruptions=0,
            productivity_score=100.0
        )
        
        self.notification_manager.queue_notification(
            "Focus Mode Started",
            "Stay focused! Social media is now blocked.",
            NotificationType.FOCUS_START
        )
        
        # Start focus monitoring thread
        self.focus_thread = threading.Thread(target=self.focus_mode_loop, daemon=True)
        self.focus_thread.start()
        
        logger.info("Focus mode started")
    
    def stop_focus_mode(self):
        """Stop focus mode"""
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.duration = int(
                (self.current_session.end_time - self.current_session.start_time).total_seconds() / 60
            )
            
            # Calculate productivity score
            if self.current_session.duration > 0:
                self.current_session.productivity_score = max(0, 100 - (self.current_session.interruptions * 10))
            
            # Save session
            self.data_manager.save_focus_session(self.current_session)
            
            self.focus_sessions += 1
            self.productivity_score = (
                (self.productivity_score * (self.focus_sessions - 1) + self.current_session.productivity_score) 
                / self.focus_sessions
            )
        
        self.is_focus_mode = False
        self.focus_button.config(text="🎯 Focus Mode", style='info.TButton')
        self.current_session = None
        
        self.notification_manager.queue_notification(
            "Focus Mode Ended",
            f"Great job! You completed a {self.current_session.duration if self.current_session else 0} minute focus session.",
            NotificationType.FOCUS_END
        )
        
        logger.info("Focus mode stopped")
    
    def focus_mode_loop(self):
        """Focus mode monitoring loop"""
        while self.is_focus_mode:
            try:
                if self.process_monitor.is_social_media_active():
                    self.current_session.interruptions += 1
                    
                    self.notification_manager.queue_notification(
                        "Focus Interrupted!",
                        "You accessed social media during focus mode. Stay focused!",
                        NotificationType.BREAK_REMINDER
                    )
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in focus mode loop: {e}")
                time.sleep(30)
    
    def take_break(self):
        """Manually trigger a break"""
        self.breaks_taken += 1
        self.notification_manager.queue_notification(
            "Break Time!",
            "Take a 5-minute break. Stretch, walk around, or do some eye exercises.",
            NotificationType.BREAK_REMINDER
        )
        self.update_display()
        logger.info("Manual break triggered")
    
    def lock_screen(self):
        """Lock the computer screen"""
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
            elif system == "Darwin":  # macOS
                subprocess.run(['pmset', 'displaysleepnow'])
            elif system == "Linux":
                subprocess.run(['gnome-screensaver-command', '--lock'])
            
            logger.info("Screen locked")
        except Exception as e:
            logger.error(f"Failed to lock screen: {e}")
    
    def update_display(self):
        """Update all display elements"""
        try:
            # Update usage labels
            self.usage_label.config(text=f"⏱️ Usage: {self.today_usage} minutes")
            
            daily_limit = self.settings.get('daily_limit', 120)
            self.limit_label.config(text=f"🎯 Limit: {self.today_usage}/{daily_limit} min")
            
            self.breaks_label.config(text=f"☕ Breaks: {self.breaks_taken}")
            self.focus_label.config(text=f"🎯 Focus: {self.focus_sessions} sessions")
            
            # Update progress bar
            progress = min(100, (self.today_usage / daily_limit) * 100)
            self.progress_var.set(progress)
            
            # Update productivity score
            self.productivity_label.config(text=f"📊 Productivity Score: {self.productivity_score:.1f}%")
            
            # Update streak information
            self.streak_label.config(text=f"🔥 Current Streak: {self.streak_days} days")
            self.best_streak_label.config(text=f"🏆 Best Streak: {self.best_streak} days")
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    def start_background_tasks(self):
        """Start background tasks like scheduled breaks"""
        def background_worker():
            while True:
                try:
                    # Check for scheduled breaks
                    current_time = datetime.now().strftime('%H:%M')
                    scheduled_breaks = self.settings.get('scheduled_breaks', [])
                    
                    if current_time in scheduled_breaks:
                        self.notification_manager.queue_notification(
                            "Scheduled Break",
                            "It's time for your scheduled break!",
                            NotificationType.BREAK_REMINDER
                        )
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"Error in background tasks: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
    
    # Placeholder methods for additional features
    def open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog will be implemented in the next iteration")
    
    def open_analytics(self):
        """Open analytics dashboard"""
        messagebox.showinfo("Analytics", "Analytics dashboard will be implemented in the next iteration")
    
    def export_data(self):
        """Export usage data"""
        messagebox.showinfo("Export", "Data export will be implemented in the next iteration")
    
    def open_music_player(self):
        """Open music player"""
        messagebox.showinfo("Music Player", "Music player will be implemented in the next iteration")
    
    def schedule_focus(self):
        """Schedule focus session"""
        messagebox.showinfo("Schedule Focus", "Focus scheduling will be implemented in the next iteration")
    
    def open_custom_timers(self):
        """Open custom timers"""
        messagebox.showinfo("Custom Timers", "Custom timers will be implemented in the next iteration")
    
    def open_mobile_sync(self):
        """Open mobile sync"""
        messagebox.showinfo("Mobile Sync", "Mobile sync will be implemented in the next iteration")
    
    def backup_data(self):
        """Backup data to cloud"""
        messagebox.showinfo("Backup", "Cloud backup will be implemented in the next iteration")
    
    def import_data(self):
        """Import data from backup"""
        messagebox.showinfo("Import", "Data import will be implemented in the next iteration")
    
    def setup_advanced_features(self):
        """Setup advanced features if available"""
        try:
            if ADVANCED_FEATURES_AVAILABLE:
                self.advanced_features = AdvancedFeatures()
                self.ml_analytics = PredictiveAnalytics()
                self.gamification = GamificationEngine()
                
                # Initialize with existing data
                user_data = {
                    'goals': [],
                    'usage_history': []
                }
                self.advanced_features.initialize_advanced_features(user_data)
                
                logger.info("Advanced features initialized successfully")
        except Exception as e:
            logger.error(f"Failed to setup advanced features: {e}")
    
    def get_advanced_insights(self) -> Dict[str, Any]:
        """Get advanced insights and recommendations"""
        if not self.advanced_features:
            return {'error': 'Advanced features not available'}
        
        try:
            # Get current data
            current_data = {
                'daily_usage': self.today_usage,
                'productivity_score': self.productivity_score,
                'focus_sessions': self.focus_sessions,
                'breaks_taken': self.breaks_taken,
                'daily_limit_met': self.today_usage <= self.settings.get('daily_limit', 120)
            }
            
            # Get ML predictions
            predictions = {}
            if self.ml_analytics:
                predictions = self.ml_analytics.get_predictions(current_data)
            
            # Get gamification updates
            gamification_results = {}
            if self.gamification:
                gamification_results = self.gamification.process_daily_update(current_data)
            
            # Get advanced insights
            insights = []
            if self.advanced_features:
                insights = self.advanced_features.get_daily_insights(current_data)
            
            return {
                'predictions': predictions,
                'gamification': gamification_results,
                'insights': [vars(insight) for insight in insights],
                'advanced_summary': self.advanced_features.get_gamification_summary() if self.gamification else {}
            }
        except Exception as e:
            logger.error(f"Failed to get advanced insights: {e}")
            return {'error': str(e)}
    
    def show_advanced_dashboard(self):
        """Show advanced analytics dashboard"""
        if not self.advanced_features:
            messagebox.showinfo("Advanced Features", "Advanced features are not available. Please install additional dependencies.")
            return
        
        try:
            insights = self.get_advanced_insights()
            
            # Create advanced dashboard window
            dashboard_window = tk.Toplevel(self.root)
            dashboard_window.title("Advanced Analytics Dashboard")
            dashboard_window.geometry("800x600")
            
            # Create notebook for tabs
            notebook = ttk.Notebook(dashboard_window)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # ML Predictions tab
            predictions_frame = ttk.Frame(notebook)
            notebook.add(predictions_frame, text="🤖 ML Predictions")
            self.create_predictions_tab(predictions_frame, insights.get('predictions', {}))
            
            # Gamification tab
            gamification_frame = ttk.Frame(notebook)
            notebook.add(gamification_frame, text="🏆 Gamification")
            self.create_gamification_tab(gamification_frame, insights.get('gamification', {}))
            
            # Insights tab
            insights_frame = ttk.Frame(notebook)
            notebook.add(insights_frame, text="💡 Insights")
            self.create_insights_tab(insights_frame, insights.get('insights', []))
            
        except Exception as e:
            logger.error(f"Failed to show advanced dashboard: {e}")
            messagebox.showerror("Error", f"Failed to show advanced dashboard: {e}")
    
    def create_predictions_tab(self, parent, predictions):
        """Create ML predictions tab"""
        # Title
        title_label = ttk.Label(parent, text="Machine Learning Predictions", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Predictions display
        if predictions:
            for pred_type, prediction in predictions.items():
                if hasattr(prediction, 'value'):
                    frame = ttk.LabelFrame(parent, text=pred_type.replace('_', ' ').title())
                    frame.pack(fill='x', padx=10, pady=5)
                    
                    ttk.Label(frame, text=f"Predicted Value: {prediction.value:.1f}").pack(anchor='w', padx=5)
                    ttk.Label(frame, text=f"Confidence: {prediction.confidence:.1%}").pack(anchor='w', padx=5)
                    ttk.Label(frame, text=f"Factors: {', '.join(prediction.factors)}").pack(anchor='w', padx=5)
        else:
            ttk.Label(parent, text="No predictions available yet. More data needed.").pack(pady=20)
    
    def create_gamification_tab(self, parent, gamification_data):
        """Create gamification tab"""
        # Title
        title_label = ttk.Label(parent, text="Gamification & Achievements", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        if gamification_data:
            # Level and points
            level_frame = ttk.LabelFrame(parent, text="Progress")
            level_frame.pack(fill='x', padx=10, pady=5)
            
            if self.gamification:
                summary = self.gamification.get_gamification_summary()
                ttk.Label(level_frame, text=f"Level: {summary.get('level', 1)}").pack(anchor='w', padx=5)
                ttk.Label(level_frame, text=f"Experience: {summary.get('experience', 0)}").pack(anchor='w', padx=5)
                ttk.Label(level_frame, text=f"Points: {summary.get('points', 0)}").pack(anchor='w', padx=5)
            
            # Recent achievements
            achievements_frame = ttk.LabelFrame(parent, text="Recent Achievements")
            achievements_frame.pack(fill='x', padx=10, pady=5)
            
            new_achievements = gamification_data.get('achievements_unlocked', [])
            if new_achievements:
                for achievement in new_achievements:
                    ttk.Label(achievements_frame, text=f"🏆 {achievement.name}").pack(anchor='w', padx=5)
            else:
                ttk.Label(achievements_frame, text="No new achievements yet").pack(padx=5)
        else:
            ttk.Label(parent, text="Gamification data not available").pack(pady=20)
    
    def create_insights_tab(self, parent, insights):
        """Create insights tab"""
        # Title
        title_label = ttk.Label(parent, text="Smart Insights", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        if insights:
            for insight in insights:
                frame = ttk.LabelFrame(parent, text=insight.get('type', 'Insight').title())
                frame.pack(fill='x', padx=10, pady=5)
                
                ttk.Label(frame, text=insight.get('message', 'No message')).pack(anchor='w', padx=5)
                ttk.Label(frame, text=f"Confidence: {insight.get('confidence', 0):.1%}").pack(anchor='w', padx=5)
                
                action_items = insight.get('action_items', [])
                if action_items:
                    ttk.Label(frame, text="Action Items:").pack(anchor='w', padx=5)
                    for item in action_items:
                        ttk.Label(frame, text=f"• {item}").pack(anchor='w', padx=15)
        else:
            ttk.Label(parent, text="No insights available yet").pack(pady=20)

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = EnhancedScrollStoppingTool(root)
        
        def on_closing():
            """Handle application closing"""
            if app.is_tracking:
                app.stop_tracking()
            if app.is_focus_mode:
                app.stop_focus_mode()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Error", f"Application failed to start: {e}")
    def setup_advanced_features(self):
        """Setup advanced features if available"""
        try:
            if ADVANCED_FEATURES_AVAILABLE:
                self.advanced_features = AdvancedFeatures()
                self.ml_analytics = PredictiveAnalytics()
                self.gamification = GamificationEngine()
                
                # Initialize with existing data
                user_data = {
                    'goals': [],
                    'usage_history': []
                }
                self.advanced_features.initialize_advanced_features(user_data)
                
                logger.info("Advanced features initialized successfully")
        except Exception as e:
            logger.error(f"Failed to setup advanced features: {e}")
    
    def get_advanced_insights(self) -> Dict[str, Any]:
        """Get advanced insights and recommendations"""
        if not self.advanced_features:
            return {'error': 'Advanced features not available'}
        
        try:
            # Get current data
            current_data = {
                'daily_usage': self.today_usage,
                'productivity_score': self.productivity_score,
                'focus_sessions': self.focus_sessions,
                'breaks_taken': self.breaks_taken,
                'daily_limit_met': self.today_usage <= self.settings.get('daily_limit', 120)
            }
            
            # Get ML predictions
            predictions = {}
            if self.ml_analytics:
                predictions = self.ml_analytics.get_predictions(current_data)
            
            # Get gamification updates
            gamification_results = {}
            if self.gamification:
                gamification_results = self.gamification.process_daily_update(current_data)
            
            # Get advanced insights
            insights = []
            if self.advanced_features:
                insights = self.advanced_features.get_daily_insights(current_data)
            
            return {
                'predictions': predictions,
                'gamification': gamification_results,
                'insights': [vars(insight) for insight in insights],
                'advanced_summary': self.advanced_features.get_gamification_summary() if self.gamification else {}
            }
        except Exception as e:
            logger.error(f"Failed to get advanced insights: {e}")
            return {'error': str(e)}
    
    def show_advanced_dashboard(self):
        """Show advanced analytics dashboard"""
        if not self.advanced_features:
            messagebox.showinfo("Advanced Features", "Advanced features are not available. Please install additional dependencies.")
            return
        
        try:
            insights = self.get_advanced_insights()
            
            # Create advanced dashboard window
            dashboard_window = tk.Toplevel(self.root)
            dashboard_window.title("Advanced Analytics Dashboard")
            dashboard_window.geometry("800x600")
            
            # Create notebook for tabs
            notebook = ttk.Notebook(dashboard_window)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # ML Predictions tab
            predictions_frame = ttk.Frame(notebook)
            notebook.add(predictions_frame, text="🤖 ML Predictions")
            self.create_predictions_tab(predictions_frame, insights.get('predictions', {}))
            
            # Gamification tab
            gamification_frame = ttk.Frame(notebook)
            notebook.add(gamification_frame, text="🏆 Gamification")
            self.create_gamification_tab(gamification_frame, insights.get('gamification', {}))
            
            # Insights tab
            insights_frame = ttk.Frame(notebook)
            notebook.add(insights_frame, text="💡 Insights")
            self.create_insights_tab(insights_frame, insights.get('insights', []))
            
        except Exception as e:
            logger.error(f"Failed to show advanced dashboard: {e}")
            messagebox.showerror("Error", f"Failed to show advanced dashboard: {e}")
    
    def create_predictions_tab(self, parent, predictions):
        """Create ML predictions tab"""
        # Title
        title_label = ttk.Label(parent, text="Machine Learning Predictions", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Predictions display
        if predictions:
            for pred_type, prediction in predictions.items():
                if hasattr(prediction, 'value'):
                    frame = ttk.LabelFrame(parent, text=pred_type.replace('_', ' ').title())
                    frame.pack(fill='x', padx=10, pady=5)
                    
                    ttk.Label(frame, text=f"Predicted Value: {prediction.value:.1f}").pack(anchor='w', padx=5)
                    ttk.Label(frame, text=f"Confidence: {prediction.confidence:.1%}").pack(anchor='w', padx=5)
                    ttk.Label(frame, text=f"Factors: {', '.join(prediction.factors)}").pack(anchor='w', padx=5)
        else:
            ttk.Label(parent, text="No predictions available yet. More data needed.").pack(pady=20)
    
    def create_gamification_tab(self, parent, gamification_data):
        """Create gamification tab"""
        # Title
        title_label = ttk.Label(parent, text="Gamification & Achievements", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        if gamification_data:
            # Level and points
            level_frame = ttk.LabelFrame(parent, text="Progress")
            level_frame.pack(fill='x', padx=10, pady=5)
            
            if self.gamification:
                summary = self.gamification.get_gamification_summary()
                ttk.Label(level_frame, text=f"Level: {summary.get('level', 1)}").pack(anchor='w', padx=5)
                ttk.Label(level_frame, text=f"Experience: {summary.get('experience', 0)}").pack(anchor='w', padx=5)
                ttk.Label(level_frame, text=f"Points: {summary.get('points', 0)}").pack(anchor='w', padx=5)
            
            # Recent achievements
            achievements_frame = ttk.LabelFrame(parent, text="Recent Achievements")
            achievements_frame.pack(fill='x', padx=10, pady=5)
            
            new_achievements = gamification_data.get('achievements_unlocked', [])
            if new_achievements:
                for achievement in new_achievements:
                    ttk.Label(achievements_frame, text=f"🏆 {achievement.name}").pack(anchor='w', padx=5)
            else:
                ttk.Label(achievements_frame, text="No new achievements yet").pack(padx=5)
        else:
            ttk.Label(parent, text="Gamification data not available").pack(pady=20)
    
    def create_insights_tab(self, parent, insights):
        """Create insights tab"""
        # Title
        title_label = ttk.Label(parent, text="Smart Insights", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        if insights:
            for insight in insights:
                frame = ttk.LabelFrame(parent, text=insight.get('type', 'Insight').title())
                frame.pack(fill='x', padx=10, pady=5)
                
                ttk.Label(frame, text=insight.get('message', 'No message')).pack(anchor='w', padx=5)
                ttk.Label(frame, text=f"Confidence: {insight.get('confidence', 0):.1%}").pack(anchor='w', padx=5)
                
                action_items = insight.get('action_items', [])
                if action_items:
                    ttk.Label(frame, text="Action Items:").pack(anchor='w', padx=5)
                    for item in action_items:
                        ttk.Label(frame, text=f"• {item}").pack(anchor='w', padx=15)
        else:
            ttk.Label(parent, text="No insights available yet").pack(pady=20)



if __name__ == "__main__":
    main() 