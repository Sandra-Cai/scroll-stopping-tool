#!/usr/bin/env python3
"""
Scroll Stopping Tool
A Python application to help users break the habit of excessive social media scrolling.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import time
import threading
import psutil
import schedule
from datetime import datetime, timedelta
from plyer import notification
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import platform
import subprocess
import webbrowser
import urllib.parse
import csv
import sqlite3
import random
import winsound  # For Windows sound support
try:
    from matplotlib.backends.backend_pdf import PdfPages
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as pdf_canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
import smtplib
from email.mime.text import MIMEText
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

class ScrollStoppingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Scroll Stopping Tool - Advanced")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.data_file = "usage_data.json"
        self.settings_file = "settings.json"
        self.db_file = "productivity.db"
        self.load_data()
        self.load_settings()
        self.init_database()
        
        # Tracking variables
        self.is_tracking = False
        self.is_focus_mode = False
        self.tracking_thread = None
        self.blocking_thread = None
        self.focus_thread = None
        self.social_media_processes = [
            'chrome.exe', 'firefox.exe', 'safari.exe', 'msedge.exe',
            'instagram.exe', 'facebook.exe', 'twitter.exe', 'tiktok.exe'
        ]
        self.social_media_sites = [
            'facebook.com', 'instagram.com', 'twitter.com', 'tiktok.com',
            'youtube.com', 'reddit.com', 'snapchat.com', 'linkedin.com'
        ]
        
        # Website blocking
        self.blocked_sites = self.settings.get('blocked_sites', [])
        self.blocking_enabled = self.settings.get('blocking_enabled', False)
        
        # Scheduled breaks
        self.scheduled_breaks = self.settings.get('scheduled_breaks', [])
        
        # Productivity tracking
        self.productivity_sessions = []
        self.current_session = None
        
        # Goals
        self.goals = self.settings.get('goals', {
            'daily_limit': 120,
            'weekly_goal': 5,
            'monthly_goal': 20
        })
        
        # Streak tracking
        self.current_streak = self.usage_data.get('current_streak', 0)
        self.best_streak = self.usage_data.get('best_streak', 0)
        
        # Motivational quotes
        self.quotes = [
            "The secret of getting ahead is getting started. – Mark Twain",
            "Don't watch the clock; do what it does. Keep going. – Sam Levenson",
            "Success is the sum of small efforts, repeated day in and day out. – Robert Collier",
            "You don't have to be perfect to be amazing.",
            "Discipline is the bridge between goals and accomplishment. – Jim Rohn",
            "It always seems impossible until it's done. – Nelson Mandela",
            "The best way to get something done is to begin.",
            "Small steps every day."
        ]
        
        # Timer variables
        self.pomodoro_active = False
        self.pomodoro_work_time = 25 * 60  # 25 minutes in seconds
        self.pomodoro_break_time = 5 * 60  # 5 minutes in seconds
        self.pomodoro_current_time = self.pomodoro_work_time
        self.pomodoro_is_break = False
        self.pomodoro_thread = None
        
        # Custom timer presets
        self.custom_timers = self.settings.get('custom_timers', {
            'Pomodoro': {'work': 25, 'break': 5, 'name': 'Pomodoro'},
            'Deep Work': {'work': 45, 'break': 15, 'name': 'Deep Work'},
            'Quick Tasks': {'work': 15, 'break': 3, 'name': 'Quick Tasks'},
            'Study Session': {'work': 30, 'break': 10, 'name': 'Study Session'}
        })
        self.current_timer_preset = 'Pomodoro'
        
        # Achievement system
        self.achievements = self.usage_data.get('achievements', {})
        self.achievement_definitions = {
            'first_break': {'name': 'First Break', 'description': 'Take your first break', 'icon': '☕'},
            'streak_3': {'name': 'Getting Started', 'description': '3-day streak', 'icon': '🔥'},
            'streak_7': {'name': 'Week Warrior', 'description': '7-day streak', 'icon': '⚡'},
            'streak_30': {'name': 'Month Master', 'description': '30-day streak', 'icon': '👑'},
            'focus_5': {'name': 'Focus Novice', 'description': '5 focus sessions', 'icon': '🎯'},
            'focus_25': {'name': 'Focus Expert', 'description': '25 focus sessions', 'icon': '🧠'},
            'breaks_10': {'name': 'Break Taker', 'description': '10 breaks taken', 'icon': '🛑'},
            'breaks_50': {'name': 'Break Master', 'description': '50 breaks taken', 'icon': '⏰'},
            'pomodoro_5': {'name': 'Pomodoro Starter', 'description': '5 Pomodoro sessions', 'icon': '🍅'},
            'pomodoro_20': {'name': 'Pomodoro Pro', 'description': '20 Pomodoro sessions', 'icon': '⏱️'},
            'under_limit_week': {'name': 'Week Winner', 'description': 'Stay under limit for a week', 'icon': '📅'},
            'productivity_90': {'name': 'Productivity Guru', 'description': '90%+ productivity score', 'icon': '💎'}
        }
        
        # Sound notification system
        self.sound_enabled = self.settings.get('sound_enabled', True)
        self.sound_types = self.settings.get('sound_types', {
            'break': 'chime',
            'achievement': 'success',
            'warning': 'alert',
            'timer': 'notification'
        })
        self.sound_system = platform.system()
        
        # Calendar integration settings
        self.calendar_api_key = self.settings.get('calendar_api_key', '')
        self.calendar_id = self.settings.get('calendar_id', '')
        self.calendar_enabled = self.settings.get('calendar_enabled', False)
        self.upcoming_sessions = []
        
        # Email/SMS reminders settings
        self.reminder_email_enabled = self.settings.get('reminder_email_enabled', False)
        self.reminder_sms_enabled = self.settings.get('reminder_sms_enabled', False)
        self.reminder_email = self.settings.get('reminder_email', '')
        self.reminder_phone = self.settings.get('reminder_phone', '')
        
        # SMTP settings for email reminders
        self.smtp_server = self.settings.get('smtp_server', '')
        self.smtp_port = self.settings.get('smtp_port', 587)
        self.smtp_username = self.settings.get('smtp_username', '')
        self.smtp_password = self.settings.get('smtp_password', '')
        self.smtp_tls = self.settings.get('smtp_tls', True)
        
        # Twilio settings for SMS reminders
        self.twilio_sid = self.settings.get('twilio_sid', '')
        self.twilio_token = self.settings.get('twilio_token', '')
        self.twilio_from = self.settings.get('twilio_from', '')
        
        # Create GUI
        self.create_widgets()
        self.update_display()
        self.show_motivational_quote()
        
        # Start background tasks
        self.start_background_tasks()
        
        # Keyboard shortcuts
        self.root.bind('<Control-t>', lambda e: self.start_tracking())
        self.root.bind('<Control-s>', lambda e: self.stop_tracking())
        self.root.bind('<Control-b>', lambda e: self.take_break())
        self.root.bind('<Control-l>', lambda e: self.lock_screen())
        self.root.bind('<Control-p>', lambda e: self.start_pomodoro())
        self.root.bind('<Control-o>', lambda e: self.pause_pomodoro())
        self.root.bind('<Control-r>', lambda e: self.reset_pomodoro())
        self.root.bind('<Control-e>', lambda e: self.open_settings())
        self.root.bind('<Control-a>', lambda e: self.open_analytics_dashboard())
        
        # Add tooltips for shortcut hints
        self.add_tooltip(self.start_button, "Start Tracking (Ctrl+T)")
        self.add_tooltip(self.stop_button, "Stop Tracking (Ctrl+S)")
        self.add_tooltip(self.break_button, "Take Break (Ctrl+B)")
        self.add_tooltip(self.lock_button, "Lock Screen (Ctrl+L)")
        self.add_tooltip(self.focus_button, "Focus Mode")
        self.add_tooltip(self.settings_button, "Settings (Ctrl+E)")
        self.add_tooltip(self.export_button, "Export Data")
        self.add_tooltip(self.export_pdf_button, "Export PDF")
        self.add_tooltip(self.analytics_button, "Analytics (Ctrl+A)")
        self.add_tooltip(self.pomodoro_start_button, "Start Pomodoro (Ctrl+P)")
        self.add_tooltip(self.pomodoro_pause_button, "Pause Pomodoro (Ctrl+O)")
        self.add_tooltip(self.pomodoro_reset_button, "Reset Pomodoro (Ctrl+R)")
        self.add_tooltip(self.schedule_calendar_button, "Schedule Focus (Calendar)")
    
    def init_database(self):
        """Initialize SQLite database for productivity tracking"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productivity_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,
                end_time TEXT,
                duration INTEGER,
                focus_score INTEGER,
                notes TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def load_data(self):
        """Load usage data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.usage_data = json.load(f)
            else:
                self.usage_data = {
                    'daily_usage': {},
                    'total_time': 0,
                    'breaks_taken': 0,
                    'goals_met': 0,
                    'focus_sessions': 0,
                    'productivity_score': 0,
                    'current_streak': 0,
                    'best_streak': 0,
                    'achievements': {} # Initialize achievements
                }
        except:
            self.usage_data = {
                'daily_usage': {},
                'total_time': 0,
                'breaks_taken': 0,
                'goals_met': 0,
                'focus_sessions': 0,
                'productivity_score': 0,
                'current_streak': 0,
                'best_streak': 0,
                'achievements': {}
            }
    
    def save_data(self):
        """Save usage data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {
                    'daily_limit': 120,  # minutes
                    'break_reminder': 30,  # minutes
                    'block_hours': {'start': '22:00', 'end': '07:00'},
                    'notifications_enabled': True,
                    'auto_break': True,
                    'auto_lock': False,
                    'blocking_enabled': False,
                    'blocked_sites': [],
                    'scheduled_breaks': [],
                    'custom_notifications': [],
                    'focus_mode_enabled': False,
                    'theme': 'default',
                    'goals': {
                        'daily_limit': 120,
                        'weekly_goal': 5,
                        'monthly_goal': 20
                    },
                    'custom_timers': {
                        'Pomodoro': {'work': 25, 'break': 5, 'name': 'Pomodoro'},
                        'Deep Work': {'work': 45, 'break': 15, 'name': 'Deep Work'},
                        'Quick Tasks': {'work': 15, 'break': 3, 'name': 'Quick Tasks'},
                        'Study Session': {'work': 30, 'break': 10, 'name': 'Study Session'}
                    },
                    'sound_enabled': True,
                    'sound_types': {
                        'break': 'chime',
                        'achievement': 'success',
                        'warning': 'alert',
                        'timer': 'notification'
                    },
                    'calendar_api_key': '',
                    'calendar_id': '',
                    'calendar_enabled': False,
                    'reminder_email_enabled': False,
                    'reminder_sms_enabled': False,
                    'reminder_email': '',
                    'reminder_phone': '',
                    'smtp_server': '',
                    'smtp_port': 587,
                    'smtp_username': '',
                    'smtp_password': '',
                    'smtp_tls': True,
                    'twilio_sid': '',
                    'twilio_token': '',
                    'twilio_from': ''
                }
        except:
            self.settings = {
                'daily_limit': 120,
                'break_reminder': 30,
                'block_hours': {'start': '22:00', 'end': '07:00'},
                'notifications_enabled': True,
                'auto_break': True,
                'auto_lock': False,
                'blocking_enabled': False,
                'blocked_sites': [],
                'scheduled_breaks': [],
                'custom_notifications': [],
                'focus_mode_enabled': False,
                'theme': 'default',
                'goals': {
                    'daily_limit': 120,
                    'weekly_goal': 5,
                    'monthly_goal': 20
                },
                'custom_timers': {
                    'Pomodoro': {'work': 25, 'break': 5, 'name': 'Pomodoro'},
                    'Deep Work': {'work': 45, 'break': 15, 'name': 'Deep Work'},
                    'Quick Tasks': {'work': 15, 'break': 3, 'name': 'Quick Tasks'},
                    'Study Session': {'work': 30, 'break': 10, 'name': 'Study Session'}
                },
                'sound_enabled': True,
                'sound_types': {
                    'break': 'chime',
                    'achievement': 'success',
                    'warning': 'alert',
                    'timer': 'notification'
                },
                'calendar_api_key': '',
                'calendar_id': '',
                'calendar_enabled': False,
                'reminder_email_enabled': False,
                'reminder_sms_enabled': False,
                'reminder_email': '',
                'reminder_phone': '',
                'smtp_server': '',
                'smtp_port': 587,
                'smtp_username': '',
                'smtp_password': '',
                'smtp_tls': True,
                'twilio_sid': '',
                'twilio_token': '',
                'twilio_from': ''
            }
    
    def save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        self.apply_theme()  # Apply theme before creating widgets
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Scroll Stopping Tool - Advanced", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=6, pady=(0, 20))
        
        # Control buttons
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="Start Tracking", 
                                      command=self.start_tracking)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Tracking", 
                                     command=self.stop_tracking, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.focus_button = ttk.Button(control_frame, text="Focus Mode", 
                                      command=self.toggle_focus_mode)
        self.focus_button.grid(row=0, column=2, padx=(0, 10))
        
        self.settings_button = ttk.Button(control_frame, text="Settings", 
                                         command=self.open_settings)
        self.settings_button.grid(row=0, column=3, padx=(0, 10))
        
        self.break_button = ttk.Button(control_frame, text="Take Break", 
                                      command=self.take_break)
        self.break_button.grid(row=0, column=4, padx=(0, 10))
        
        self.lock_button = ttk.Button(control_frame, text="Lock Screen", 
                                      command=self.lock_screen)
        self.lock_button.grid(row=0, column=5, padx=(0, 10))
        
        self.block_button = ttk.Button(control_frame, text="Block Sites", 
                                      command=self.open_blocking_dialog)
        self.block_button.grid(row=0, column=6, padx=(0, 10))
        
        self.export_button = ttk.Button(control_frame, text="Export Data", 
                                       command=self.export_data)
        self.export_button.grid(row=0, column=7, padx=(0, 10))
        
        self.export_pdf_button = ttk.Button(control_frame, text="Export PDF", 
                                           command=self.export_pdf_report)
        self.export_pdf_button.grid(row=0, column=9)
        
        self.analytics_button = ttk.Button(control_frame, text="Analytics", 
                                          command=self.open_analytics_dashboard)
        self.analytics_button.grid(row=0, column=8)
        
        # Calendar integration button
        self.schedule_calendar_button = ttk.Button(control_frame, text="Schedule Focus (Calendar)", command=self.schedule_focus_session)
        self.schedule_calendar_button.grid(row=0, column=10)
        self.add_tooltip(self.schedule_calendar_button, "Schedule next focus session in Google Calendar")
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="Today's Statistics", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Today's usage
        self.today_usage_label = ttk.Label(stats_frame, text="Today's Usage: 0 minutes")
        self.today_usage_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        # Daily limit progress
        self.limit_progress_label = ttk.Label(stats_frame, text="Daily Limit: 0/120 minutes")
        self.limit_progress_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Breaks taken
        self.breaks_label = ttk.Label(stats_frame, text="Breaks Taken: 0")
        self.breaks_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        
        # Focus sessions
        self.focus_label = ttk.Label(stats_frame, text="Focus Sessions: 0")
        self.focus_label.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        # Productivity score
        self.productivity_label = ttk.Label(stats_frame, text="Productivity: 0%")
        self.productivity_label.grid(row=0, column=4, sticky=tk.W)
        
        # Streak labels
        self.streak_label = ttk.Label(stats_frame, text="Current Streak: 0 days")
        self.streak_label.grid(row=0, column=5, sticky=tk.W, padx=(0, 20))
        self.best_streak_label = ttk.Label(stats_frame, text="Best Streak: 0 days")
        self.best_streak_label.grid(row=0, column=6, sticky=tk.W)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(stats_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Alternative activities frame
        activities_frame = ttk.LabelFrame(main_frame, text="Alternative Activities", padding="10")
        activities_frame.grid(row=3, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(0, 10))
        
        activities = [
            "Read a book", "Go for a walk", "Call a friend", "Exercise",
            "Meditate", "Write in a journal", "Cook a meal", "Learn something new"
        ]
        
        for i, activity in enumerate(activities):
            btn = ttk.Button(activities_frame, text=activity, 
                           command=lambda a=activity: self.suggest_activity(a))
            btn.grid(row=i//4, column=i%4, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Chart frame
        chart_frame = ttk.LabelFrame(main_frame, text="Weekly Usage Chart", padding="10")
        chart_frame.grid(row=4, column=0, columnspan=6, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to start tracking")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(10, 0))
        # Smart Suggestions
        self.suggestion_var = tk.StringVar()
        self.suggestion_label = ttk.Label(main_frame, textvariable=self.suggestion_var, font=("Arial", 11, "italic"), foreground="#0077cc")
        self.suggestion_label.grid(row=6, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Pomodoro timer frame
        pomodoro_frame = ttk.LabelFrame(main_frame, text="Pomodoro Timer", padding="10")
        pomodoro_frame.grid(row=7, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Timer display
        self.timer_var = tk.StringVar()
        self.timer_var.set("25:00")
        timer_label = ttk.Label(pomodoro_frame, textvariable=self.timer_var, font=("Arial", 24, "bold"))
        timer_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Timer preset selector
        ttk.Label(pomodoro_frame, text="Timer Preset:").grid(row=1, column=0, padx=(0, 5), pady=5)
        self.timer_preset_var = tk.StringVar(value=self.current_timer_preset)
        self.timer_preset_combo = ttk.Combobox(pomodoro_frame, textvariable=self.timer_preset_var, 
                                              values=list(self.custom_timers.keys()), state="readonly", width=15)
        self.timer_preset_combo.grid(row=1, column=1, padx=5, pady=5)
        self.timer_preset_combo.bind('<<ComboboxSelected>>', self.on_timer_preset_change)
        
        # Custom timer button
        self.custom_timer_button = ttk.Button(pomodoro_frame, text="Custom Timers", command=self.open_custom_timers)
        self.custom_timer_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Timer controls
        self.pomodoro_start_button = ttk.Button(pomodoro_frame, text="Start", command=self.start_pomodoro)
        self.pomodoro_start_button.grid(row=2, column=0, padx=5, pady=5)
        
        self.pomodoro_pause_button = ttk.Button(pomodoro_frame, text="Pause", command=self.pause_pomodoro, state='disabled')
        self.pomodoro_pause_button.grid(row=2, column=1, padx=5, pady=5)
        
        self.pomodoro_reset_button = ttk.Button(pomodoro_frame, text="Reset", command=self.reset_pomodoro)
        self.pomodoro_reset_button.grid(row=2, column=2, padx=5, pady=5)
        
        # Timer status
        self.timer_status_var = tk.StringVar()
        self.timer_status_var.set("Ready to start")
        timer_status = ttk.Label(pomodoro_frame, textvariable=self.timer_status_var, font=("Arial", 10))
        timer_status.grid(row=2, column=0, columnspan=3, pady=(5, 0))
        
        # Achievements frame
        achievements_frame = ttk.LabelFrame(main_frame, text="Achievements", padding="10")
        achievements_frame.grid(row=8, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Achievement display
        self.achievement_text = tk.Text(achievements_frame, height=4, width=80, wrap=tk.WORD, state='disabled')
        self.achievement_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Share achievement button
        self.share_achievement_button = ttk.Button(achievements_frame, text="Share Achievement", command=self.share_achievement)
        self.share_achievement_button.pack(side=tk.LEFT, padx=10)
        self.add_tooltip(self.share_achievement_button, "Share your latest achievement (copies to clipboard)")
        
        # Scrollbar for achievements
        achievement_scrollbar = ttk.Scrollbar(achievements_frame, orient=tk.VERTICAL, command=self.achievement_text.yview)
        achievement_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.achievement_text.config(yscrollcommand=achievement_scrollbar.set)
        
        # Sound settings
        sound_var = tk.BooleanVar(value=self.settings.get('sound_enabled', True))
        sound_check = ttk.Checkbutton(general_frame, text="Enable Sound Notifications", 
                                     variable=sound_var)
        sound_check.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
        
        # Sound type selectors
        ttk.Label(general_frame, text="Break Sound:").grid(row=8, column=0, padx=10, pady=5)
        break_sound_var = tk.StringVar(value=self.sound_types.get('break', 'chime'))
        break_sound_combo = ttk.Combobox(general_frame, textvariable=break_sound_var, 
                                        values=["chime", "bell", "ding", "success"], state="readonly")
        break_sound_combo.grid(row=8, column=1, padx=10, pady=5)
        
        ttk.Label(general_frame, text="Achievement Sound:").grid(row=9, column=0, padx=10, pady=5)
        achievement_sound_var = tk.StringVar(value=self.sound_types.get('achievement', 'success'))
        achievement_sound_combo = ttk.Combobox(general_frame, textvariable=achievement_sound_var, 
                                              values=["success", "fanfare", "chime", "bell"], state="readonly")
        achievement_sound_combo.grid(row=9, column=1, padx=10, pady=5)
        
        ttk.Label(general_frame, text="Warning Sound:").grid(row=10, column=0, padx=10, pady=5)
        warning_sound_var = tk.StringVar(value=self.sound_types.get('warning', 'alert'))
        warning_sound_combo = ttk.Combobox(general_frame, textvariable=warning_sound_var, 
                                          values=["alert", "warning", "error", "ding"], state="readonly")
        warning_sound_combo.grid(row=10, column=1, padx=10, pady=5)
        
        ttk.Label(general_frame, text="Timer Sound:").grid(row=11, column=0, padx=10, pady=5)
        timer_sound_var = tk.StringVar(value=self.sound_types.get('timer', 'notification'))
        timer_sound_combo = ttk.Combobox(general_frame, textvariable=timer_sound_var, 
                                        values=["notification", "chime", "bell", "ding"], state="readonly")
        timer_sound_combo.grid(row=11, column=1, padx=10, pady=5)
    
    def apply_theme(self):
        """Apply the selected theme to the app"""
        theme = self.settings.get('theme', 'default')
        if theme == 'dark':
            style = ttk.Style()
            self.root.tk_setPalette(background='#222', foreground='#eee', activeBackground='#333', activeForeground='#fff')
            style.theme_use('clam')
            style.configure('.', background='#222', foreground='#eee')
            style.configure('TLabel', background='#222', foreground='#eee')
            style.configure('TButton', background='#333', foreground='#eee')
            style.configure('TFrame', background='#222')
            style.configure('TNotebook', background='#222')
            style.configure('TNotebook.Tab', background='#333', foreground='#eee')
        else:
            style = ttk.Style()
            self.root.tk_setPalette(background='#f0f0f0', foreground='#222', activeBackground='#e0e0e0', activeForeground='#222')
            style.theme_use('default')
            style.configure('.', background='#f0f0f0', foreground='#222')
            style.configure('TLabel', background='#f0f0f0', foreground='#222')
            style.configure('TButton', background='#e0e0e0', foreground='#222')
            style.configure('TFrame', background='#f0f0f0')
            style.configure('TNotebook', background='#f0f0f0')
            style.configure('TNotebook.Tab', background='#e0e0e0', foreground='#222')

    def start_tracking(self):
        """Start tracking social media usage"""
        self.is_tracking = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_var.set("Tracking active - monitoring social media usage")
        
        # Start tracking thread
        self.tracking_thread = threading.Thread(target=self.tracking_loop, daemon=True)
        self.tracking_thread.start()
        
        # Start website blocking if enabled
        if self.blocking_enabled:
            self.start_website_blocking()
    
    def stop_tracking(self):
        """Stop tracking social media usage"""
        self.is_tracking = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("Tracking stopped")
        
        # Stop website blocking
        self.stop_website_blocking()
        
        # End current focus session if active
        if self.current_session:
            self.end_focus_session()
    
    def toggle_focus_mode(self):
        """Toggle focus mode on/off"""
        if not self.is_focus_mode:
            self.start_focus_mode()
        else:
            self.stop_focus_mode()
    
    def start_focus_mode(self):
        """Start focus mode"""
        self.is_focus_mode = True
        self.focus_button.config(text="Exit Focus Mode")
        self.status_var.set("Focus mode active - enhanced blocking enabled")
        
        # Start focus mode thread
        self.focus_thread = threading.Thread(target=self.focus_mode_loop, daemon=True)
        self.focus_thread.start()
        
        # Start focus session
        self.start_focus_session()
        
        if self.settings['notifications_enabled']:
            notification.notify(
                title='Focus Mode Started!',
                message='Enhanced blocking enabled. Stay focused!',
                timeout=5
            )
    
    def stop_focus_mode(self):
        """Stop focus mode"""
        self.is_focus_mode = False
        self.focus_button.config(text="Focus Mode")
        self.status_var.set("Focus mode disabled")
        
        # End focus session
        if self.current_session:
            self.end_focus_session()
        
        if self.settings['notifications_enabled']:
            notification.notify(
                title='Focus Mode Ended',
                message='Great job staying focused!',
                timeout=5
            )
    
    def start_focus_session(self):
        """Start a new focus session"""
        self.current_session = {
            'start_time': datetime.now(),
            'focus_score': 0,
            'interruptions': 0
        }
    
    def end_focus_session(self):
        """End the current focus session"""
        if self.current_session:
            duration = (datetime.now() - self.current_session['start_time']).total_seconds()
            focus_score = max(0, 100 - (self.current_session['interruptions'] * 10))
            
            # Save to database
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO productivity_sessions (start_time, end_time, duration, focus_score, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.current_session['start_time'].isoformat(),
                datetime.now().isoformat(),
                int(duration),
                focus_score,
                f"Focus session with {self.current_session['interruptions']} interruptions"
            ))
            conn.commit()
            conn.close()
            
            self.usage_data['focus_sessions'] += 1
            self.usage_data['productivity_score'] = focus_score
            self.save_data()
            self.check_achievements()  # Check for new achievements
            self.current_session = None
    
    def focus_mode_loop(self):
        """Focus mode monitoring loop"""
        while self.is_focus_mode and self.is_tracking:
            try:
                # Check for any social media activity
                if self.is_social_media_active():
                    if self.current_session:
                        self.current_session['interruptions'] += 1
                    
                    # More aggressive blocking in focus mode
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if proc.info['cmdline']:
                                cmdline = ' '.join(proc.info['cmdline']).lower()
                                if any(site in cmdline for site in self.social_media_sites):
                                    proc.terminate()
                                    if self.settings['notifications_enabled']:
                                        notification.notify(
                                            title='Focus Mode: Site Blocked!',
                                            message='Stay focused - social media blocked.',
                                            timeout=3
                                        )
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
            except:
                pass
            time.sleep(2)  # Check every 2 seconds in focus mode
    
    def tracking_loop(self):
        """Main tracking loop"""
        start_time = time.time()
        last_break_reminder = time.time()
        
        while self.is_tracking:
            # Check for social media processes
            if self.is_social_media_active():
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Update daily usage
                today = datetime.now().strftime('%Y-%m-%d')
                if today not in self.usage_data['daily_usage']:
                    self.usage_data['daily_usage'][today] = 0
                
                self.usage_data['daily_usage'][today] += 1  # Add 1 second
                self.usage_data['total_time'] += 1
                
                # Check for break reminder
                if (self.settings['auto_break'] and 
                    current_time - last_break_reminder > self.settings['break_reminder'] * 60):
                    self.send_break_reminder()
                    last_break_reminder = current_time
                
                # Check daily limit
                if self.usage_data['daily_usage'][today] >= self.settings['daily_limit'] * 60:
                    self.send_limit_reached_notification()
                
                self.save_data()
                self.root.after(0, self.update_display)
            
            time.sleep(1)
    
    def is_social_media_active(self):
        """Check if social media is currently being used"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Check process names
                    if proc.info['name'] in self.social_media_processes:
                        return True
                    
                    # Check command line for social media sites
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline']).lower()
                        if any(site in cmdline for site in self.social_media_sites):
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass
        return False
    
    def take_break(self):
        """Manually take a break"""
        self.usage_data['breaks_taken'] += 1
        self.save_data()
        self.update_display()
        self.check_achievements()
        
        # Play break sound
        self.play_sound('break')
        
        if self.settings['notifications_enabled']:
            notification.notify(
                title='Break Time!',
                message='Great job taking a break! Consider doing something offline.',
                timeout=10
            )
        
        self.status_var.set("Break taken - good job!")
        self.show_motivational_quote()
    
    def suggest_activity(self, activity):
        """Suggest an alternative activity"""
        messagebox.showinfo("Alternative Activity", 
                           f"Great idea! Here are some suggestions for {activity}:\n\n"
                           f"• Set a timer for 15-30 minutes\n"
                           f"• Put your phone in another room\n"
                           f"• Focus on the activity completely\n"
                           f"• Notice how you feel afterward")
    
    def send_break_reminder(self):
        """Send a break reminder notification"""
        if self.settings['notifications_enabled']:
            notification.notify(
                title='Time for a Break!',
                message='You\'ve been scrolling for a while. Consider taking a short break.',
                timeout=10
            )
    
    def send_limit_reached_notification(self):
        """Send notification when daily limit is reached"""
        # Play warning sound
        self.play_sound('warning')
        
        if self.settings['notifications_enabled']:
            notification.notify(
                title='Daily Limit Reached!',
                message='You\'ve reached your daily social media limit. Time to disconnect!',
                timeout=10
            )
        if self.settings.get('auto_lock', False):
            self.lock_screen()
        self.suggestion_var.set(self.get_smart_suggestion())
    
    def lock_screen(self):
        """Lock the user's screen (cross-platform)"""
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["/System/Library/CoreServices/Menu\u20Bar.app/Contents/Resources/CGSession", "-suspend"])
            elif system == "Windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            elif system == "Linux":
                # Try common Linux lock commands
                if subprocess.call(["which", "gnome-screensaver-command"]) == 0:
                    subprocess.run(["gnome-screensaver-command", "--lock"])
                elif subprocess.call(["which", "loginctl"]) == 0:
                    subprocess.run(["loginctl", "lock-session"])
                else:
                    messagebox.showwarning("Screen Lock", "No supported screen lock command found.")
                    return
            else:
                messagebox.showwarning("Screen Lock", f"Screen lock not supported on {system}.")
                return
            self.status_var.set("Screen locked!")
        except Exception as e:
            messagebox.showerror("Screen Lock Error", f"Failed to lock screen: {e}")
    
    def export_data(self):
        """Export usage data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Date', 'Usage (minutes)', 'Breaks Taken', 'Focus Sessions', 'Productivity Score'])
                    
                    for date, usage in self.usage_data['daily_usage'].items():
                        writer.writerow([
                            date,
                            usage // 60,
                            self.usage_data.get('breaks_taken', 0),
                            self.usage_data.get('focus_sessions', 0),
                            self.usage_data.get('productivity_score', 0)
                        ])
                
                messagebox.showinfo("Export", f"Data exported successfully to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def export_pdf_report(self):
        """Export analytics and reports as a PDF file"""
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("PDF Export", "ReportLab is not installed. Please install it to enable PDF export.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not filename:
            return
        # Create PDF
        c = pdf_canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 40, "Scroll Stopping Tool - Analytics Report")
        c.setFont("Helvetica", 12)
        c.drawString(40, height - 70, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(40, height - 90, f"Total Days Tracked: {len(self.usage_data['daily_usage'])}")
        c.drawString(40, height - 110, f"Total Usage Time: {self.usage_data['total_time']//60} minutes")
        c.drawString(40, height - 130, f"Focus Sessions: {self.usage_data.get('focus_sessions', 0)}")
        c.drawString(40, height - 150, f"Breaks Taken: {self.usage_data.get('breaks_taken', 0)}")
        c.drawString(40, height - 170, f"Current Streak: {self.usage_data.get('current_streak', 0)} days")
        c.drawString(40, height - 190, f"Best Streak: {self.usage_data.get('best_streak', 0)} days")
        c.drawString(40, height - 210, f"Achievements Unlocked: {len(self.achievements)}")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 240, "Weekly Usage Chart:")
        # Save weekly chart as image and embed
        import tempfile
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 3))
        self.create_weekly_chart(ax)
        tmp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        fig.savefig(tmp_img.name)
        plt.close(fig)
        c.drawImage(tmp_img.name, 40, height - 420, width=500, height=150)
        # Focus session summary
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 440, "Focus Session Summary:")
        c.setFont("Helvetica", 11)
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT start_time, duration, focus_score FROM productivity_sessions ORDER BY start_time DESC LIMIT 10")
        sessions = cursor.fetchall()
        conn.close()
        y = height - 460
        for s in sessions:
            start, duration, score = s
            mins = int(duration) // 60
            c.drawString(50, y, f"{start[:16]} | {mins} min | Score: {score}%")
            y -= 18
            if y < 80:
                c.showPage()
                y = height - 40
        c.save()
        os.unlink(tmp_img.name)
        messagebox.showinfo("Export PDF", f"PDF report exported successfully to {filename}")
    
    def open_blocking_dialog(self):
        """Open website blocking configuration dialog"""
        blocking_window = tk.Toplevel(self.root)
        blocking_window.title("Website Blocking")
        blocking_window.geometry("500x400")
        blocking_window.transient(self.root)
        blocking_window.grab_set()
        
        # Enable/disable blocking
        blocking_var = tk.BooleanVar(value=self.blocking_enabled)
        blocking_check = ttk.Checkbutton(blocking_window, text="Enable Website Blocking", 
                                        variable=blocking_var)
        blocking_check.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
        
        # Blocked sites list
        ttk.Label(blocking_window, text="Blocked Websites:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        
        # Listbox for blocked sites
        sites_frame = ttk.Frame(blocking_window)
        sites_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        sites_listbox = tk.Listbox(sites_frame, height=8)
        sites_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(sites_frame, orient=tk.VERTICAL, command=sites_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        sites_listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate listbox
        for site in self.blocked_sites:
            sites_listbox.insert(tk.END, site)
        
        # Add site entry
        ttk.Label(blocking_window, text="Add site (e.g., facebook.com):").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        site_entry = ttk.Entry(blocking_window, width=30)
        site_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        
        def add_site():
            site = site_entry.get().strip()
            if site and site not in self.blocked_sites:
                self.blocked_sites.append(site)
                sites_listbox.insert(tk.END, site)
                site_entry.delete(0, tk.END)
        
        def remove_site():
            selection = sites_listbox.curselection()
            if selection:
                site = sites_listbox.get(selection[0])
                self.blocked_sites.remove(site)
                sites_listbox.delete(selection[0])
        
        # Buttons
        button_frame = ttk.Frame(blocking_window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Site", command=add_site).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Site", command=remove_site).pack(side=tk.LEFT, padx=5)
        
        def save_blocking():
            self.blocking_enabled = blocking_var.get()
            self.settings['blocking_enabled'] = self.blocking_enabled
            self.settings['blocked_sites'] = self.blocked_sites
            self.save_settings()
            self.update_blocking_status()
            blocking_window.destroy()
            messagebox.showinfo("Blocking", "Website blocking settings saved!")
        
        ttk.Button(button_frame, text="Save", command=save_blocking).pack(side=tk.LEFT, padx=5)
    
    def start_website_blocking(self):
        """Start website blocking thread"""
        if self.blocking_enabled and not self.blocking_thread:
            self.blocking_thread = threading.Thread(target=self.blocking_loop, daemon=True)
            self.blocking_thread.start()
    
    def stop_website_blocking(self):
        """Stop website blocking"""
        self.blocking_thread = None
    
    def blocking_loop(self):
        """Website blocking loop"""
        while self.blocking_thread and self.is_tracking:
            try:
                # Check for browser processes and block access to social media sites
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline']).lower()
                            for site in self.blocked_sites:
                                if site in cmdline:
                                    # Try to close the browser tab/window
                                    proc.terminate()
                                    if self.settings['notifications_enabled']:
                                        notification.notify(
                                            title='Site Blocked!',
                                            message=f'Access to {site} has been blocked.',
                                            timeout=5
                                        )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except:
                pass
            time.sleep(5)  # Check every 5 seconds
    
    def update_blocking_status(self):
        """Update the blocking status display"""
        status = "Enabled" if self.blocking_enabled else "Disabled"
        count = len(self.blocked_sites) if self.blocked_sites else 0
        self.blocking_status_label.config(text=f"Blocking: {status} ({count} sites)")
    
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Advanced Settings")
        settings_window.geometry("600x600")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General settings tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        # Daily limit
        ttk.Label(general_frame, text="Daily Limit (minutes):").grid(row=0, column=0, padx=10, pady=10)
        limit_var = tk.StringVar(value=str(self.settings['daily_limit']))
        limit_entry = ttk.Entry(general_frame, textvariable=limit_var)
        limit_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Break reminder
        ttk.Label(general_frame, text="Break Reminder (minutes):").grid(row=1, column=0, padx=10, pady=10)
        reminder_var = tk.StringVar(value=str(self.settings['break_reminder']))
        reminder_entry = ttk.Entry(general_frame, textvariable=reminder_var)
        reminder_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Notifications
        notif_var = tk.BooleanVar(value=self.settings['notifications_enabled'])
        notif_check = ttk.Checkbutton(general_frame, text="Enable Notifications", 
                                     variable=notif_var)
        notif_check.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        
        # Auto break
        auto_break_var = tk.BooleanVar(value=self.settings['auto_break'])
        auto_break_check = ttk.Checkbutton(general_frame, text="Auto Break Reminders", 
                                          variable=auto_break_var)
        auto_break_check.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
        # Auto lock
        auto_lock_var = tk.BooleanVar(value=self.settings.get('auto_lock', False))
        auto_lock_check = ttk.Checkbutton(general_frame, text="Auto Lock Screen on Limit", 
                                          variable=auto_lock_var)
        auto_lock_check.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        
        # Focus mode
        focus_var = tk.BooleanVar(value=self.settings.get('focus_mode_enabled', False))
        focus_check = ttk.Checkbutton(general_frame, text="Enable Focus Mode", 
                                     variable=focus_var)
        focus_check.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        # Theme selector
        ttk.Label(general_frame, text="Theme:").grid(row=6, column=0, padx=10, pady=10)
        theme_var = tk.StringVar(value=self.settings.get('theme', 'default'))
        theme_combo = ttk.Combobox(general_frame, textvariable=theme_var, values=["default", "dark"], state="readonly")
        theme_combo.grid(row=6, column=1, padx=10, pady=10)
        
        # Scheduled breaks tab
        breaks_frame = ttk.Frame(notebook)
        notebook.add(breaks_frame, text="Scheduled Breaks")
        
        ttk.Label(breaks_frame, text="Scheduled Breaks:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        
        breaks_listbox = tk.Listbox(breaks_frame, height=6)
        breaks_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        for break_time in self.scheduled_breaks:
            breaks_listbox.insert(tk.END, break_time)
        
        ttk.Label(breaks_frame, text="Add break time (HH:MM):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        break_entry = ttk.Entry(breaks_frame, width=10)
        break_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        
        def add_break():
            break_time = break_entry.get().strip()
            if break_time and break_time not in self.scheduled_breaks:
                self.scheduled_breaks.append(break_time)
                breaks_listbox.insert(tk.END, break_time)
                break_entry.delete(0, tk.END)
        
        def remove_break():
            selection = breaks_listbox.curselection()
            if selection:
                break_time = breaks_listbox.get(selection[0])
                self.scheduled_breaks.remove(break_time)
                breaks_listbox.delete(selection[0])
        
        ttk.Button(breaks_frame, text="Add Break", command=add_break).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(breaks_frame, text="Remove Break", command=remove_break).grid(row=3, column=1, padx=5, pady=5)
        
        # Goals tab
        goals_frame = ttk.Frame(notebook)
        notebook.add(goals_frame, text="Goals")
        
        ttk.Label(goals_frame, text="Daily Limit (minutes):").grid(row=0, column=0, padx=10, pady=10)
        daily_goal_var = tk.StringVar(value=str(self.goals['daily_limit']))
        daily_goal_entry = ttk.Entry(goals_frame, textvariable=daily_goal_var)
        daily_goal_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(goals_frame, text="Weekly Goal (days under limit):").grid(row=1, column=0, padx=10, pady=10)
        weekly_goal_var = tk.StringVar(value=str(self.goals['weekly_goal']))
        weekly_goal_entry = ttk.Entry(goals_frame, textvariable=weekly_goal_var)
        weekly_goal_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(goals_frame, text="Monthly Goal (days under limit):").grid(row=2, column=0, padx=10, pady=10)
        monthly_goal_var = tk.StringVar(value=str(self.goals['monthly_goal']))
        monthly_goal_entry = ttk.Entry(goals_frame, textvariable=monthly_goal_var)
        monthly_goal_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Session History tab
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="Session History")
        ttk.Label(history_frame, text="Focus Session History:").pack(anchor=tk.W, padx=10, pady=5)
        columns = ("Start", "End", "Duration (min)", "Score", "Notes")
        tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        # Load data from database
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT start_time, end_time, duration, focus_score, notes FROM productivity_sessions ORDER BY id DESC LIMIT 100")
        for row in cursor.fetchall():
            start, end, duration, score, notes = row
            mins = int(duration) // 60
            tree.insert("", tk.END, values=(start[:16], end[:16], mins, score, notes))
        conn.close()
        
        # Calendar integration tab
        calendar_frame = ttk.Frame(notebook)
        notebook.add(calendar_frame, text="Calendar")
        
        cal_enabled_var = tk.BooleanVar(value=self.calendar_enabled)
        cal_enabled_check = ttk.Checkbutton(calendar_frame, text="Enable Google Calendar Integration", variable=cal_enabled_var)
        cal_enabled_check.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
        
        ttk.Label(calendar_frame, text="API Key:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        cal_api_var = tk.StringVar(value=self.calendar_api_key)
        cal_api_entry = ttk.Entry(calendar_frame, textvariable=cal_api_var, width=40)
        cal_api_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(calendar_frame, text="Calendar ID:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        cal_id_var = tk.StringVar(value=self.calendar_id)
        cal_id_entry = ttk.Entry(calendar_frame, textvariable=cal_id_var, width=40)
        cal_id_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        
        def save_calendar_settings():
            self.calendar_enabled = cal_enabled_var.get()
            self.calendar_api_key = cal_api_var.get()
            self.calendar_id = cal_id_var.get()
            self.settings['calendar_enabled'] = self.calendar_enabled
            self.settings['calendar_api_key'] = self.calendar_api_key
            self.settings['calendar_id'] = self.calendar_id
            self.save_settings()
            messagebox.showinfo("Calendar Settings", "Calendar integration settings saved!")
        
        ttk.Button(calendar_frame, text="Save", command=save_calendar_settings).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Save button
        def save_settings():
            try:
                self.settings['daily_limit'] = int(limit_var.get())
                self.settings['break_reminder'] = int(reminder_var.get())
                self.settings['notifications_enabled'] = notif_var.get()
                self.settings['auto_break'] = auto_break_var.get()
                self.settings['auto_lock'] = auto_lock_var.get()
                self.settings['focus_mode_enabled'] = focus_var.get()
                self.settings['scheduled_breaks'] = self.scheduled_breaks
                self.settings['theme'] = theme_var.get()
                
                # Save sound settings
                self.settings['sound_enabled'] = sound_var.get()
                self.settings['sound_types'] = {
                    'break': break_sound_var.get(),
                    'achievement': achievement_sound_var.get(),
                    'warning': warning_sound_var.get(),
                    'timer': timer_sound_var.get()
                }
                
                # Update goals
                self.goals['daily_limit'] = int(daily_goal_var.get())
                self.goals['weekly_goal'] = int(weekly_goal_var.get())
                self.goals['monthly_goal'] = int(monthly_goal_var.get())
                self.settings['goals'] = self.goals
                
                self.save_settings()
                self.apply_theme()
                settings_window.destroy()
                self.update_display()
                messagebox.showinfo("Settings", "Settings saved successfully!")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for limits and goals.")
        
        ttk.Button(settings_window, text="Save", command=save_settings).pack(pady=20)
        
        # Backup & Sync buttons in settings
        backup_frame = ttk.LabelFrame(settings_window, text="Backup & Sync", padding="10")
        backup_frame.pack(fill=tk.X, padx=10, pady=10)
        
        export_backup_btn = ttk.Button(backup_frame, text="Export Backup", command=self.export_backup)
        export_backup_btn.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(export_backup_btn, "Export all your data as a JSON backup")
        
        import_backup_btn = ttk.Button(backup_frame, text="Import Backup", command=self.import_backup)
        import_backup_btn.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(import_backup_btn, "Import a JSON backup to restore your data")
        
        sync_btn = ttk.Button(backup_frame, text="Sync (Cloud)", command=self.sync_cloud)
        sync_btn.pack(side=tk.LEFT, padx=5)
        self.add_tooltip(sync_btn, "(Stub) Sync your data to the cloud")
        
        # Email/SMS Reminders section in settings
        reminders_frame = ttk.LabelFrame(settings_window, text="Reminders (Email/SMS)", padding="10")
        reminders_frame.pack(fill=tk.X, padx=10, pady=10)
        
        email_enabled_var = tk.BooleanVar(value=self.reminder_email_enabled)
        email_check = ttk.Checkbutton(reminders_frame, text="Enable Email Reminders", variable=email_enabled_var)
        email_check.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(reminders_frame, text="Email:").grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        email_var = tk.StringVar(value=self.reminder_email)
        email_entry = ttk.Entry(reminders_frame, textvariable=email_var, width=30)
        email_entry.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        
        sms_enabled_var = tk.BooleanVar(value=self.reminder_sms_enabled)
        sms_check = ttk.Checkbutton(reminders_frame, text="Enable SMS Reminders", variable=sms_enabled_var)
        sms_check.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(reminders_frame, text="Phone:").grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        phone_var = tk.StringVar(value=self.reminder_phone)
        phone_entry = ttk.Entry(reminders_frame, textvariable=phone_var, width=20)
        phone_entry.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
        
        def save_reminder_settings():
            self.reminder_email_enabled = email_enabled_var.get()
            self.reminder_sms_enabled = sms_enabled_var.get()
            self.reminder_email = email_var.get()
            self.reminder_phone = phone_var.get()
            self.settings['reminder_email_enabled'] = self.reminder_email_enabled
            self.settings['reminder_sms_enabled'] = self.reminder_sms_enabled
            self.settings['reminder_email'] = self.reminder_email
            self.settings['reminder_phone'] = self.reminder_phone
            self.save_settings()
            messagebox.showinfo("Reminders", "Reminder settings saved!")
        
        ttk.Button(reminders_frame, text="Save", command=save_reminder_settings).grid(row=2, column=0, pady=10)
        ttk.Button(reminders_frame, text="Test Email Reminder", command=self.test_email_reminder).grid(row=2, column=1, pady=10)
        ttk.Button(reminders_frame, text="Test SMS Reminder", command=self.test_sms_reminder).grid(row=2, column=2, pady=10)
        self.add_tooltip(email_check, "Enable/disable email reminders for breaks, limits, etc.")
        self.add_tooltip(sms_check, "Enable/disable SMS reminders for breaks, limits, etc.")
        self.add_tooltip(email_entry, "Enter your email address for reminders")
        self.add_tooltip(phone_entry, "Enter your phone number for SMS reminders")
        self.add_tooltip(reminders_frame, "Reminders are sent for breaks, limits, and scheduled events (stub)")
        
        # SMTP settings for email reminders
        smtp_frame = ttk.LabelFrame(reminders_frame, text="SMTP Settings (for Email)", padding="10")
        smtp_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W)
        
        ttk.Label(smtp_frame, text="SMTP Server:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        smtp_server_var = tk.StringVar(value=self.smtp_server)
        smtp_server_entry = ttk.Entry(smtp_frame, textvariable=smtp_server_var, width=20)
        smtp_server_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(smtp_frame, text="Port:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        smtp_port_var = tk.StringVar(value=str(self.smtp_port))
        smtp_port_entry = ttk.Entry(smtp_frame, textvariable=smtp_port_var, width=6)
        smtp_port_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(smtp_frame, text="Username:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        smtp_user_var = tk.StringVar(value=self.smtp_username)
        smtp_user_entry = ttk.Entry(smtp_frame, textvariable=smtp_user_var, width=20)
        smtp_user_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(smtp_frame, text="Password:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        smtp_pass_var = tk.StringVar(value=self.smtp_password)
        smtp_pass_entry = ttk.Entry(smtp_frame, textvariable=smtp_pass_var, width=20, show='*')
        smtp_pass_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        
        smtp_tls_var = tk.BooleanVar(value=self.smtp_tls)
        smtp_tls_check = ttk.Checkbutton(smtp_frame, text="Use TLS", variable=smtp_tls_var)
        smtp_tls_check.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        def save_smtp_settings():
            self.smtp_server = smtp_server_var.get()
            self.smtp_port = int(smtp_port_var.get())
            self.smtp_username = smtp_user_var.get()
            self.smtp_password = smtp_pass_var.get()
            self.smtp_tls = smtp_tls_var.get()
            self.settings['smtp_server'] = self.smtp_server
            self.settings['smtp_port'] = self.smtp_port
            self.settings['smtp_username'] = self.smtp_username
            self.settings['smtp_password'] = self.smtp_password
            self.settings['smtp_tls'] = self.smtp_tls
            self.save_settings()
            messagebox.showinfo("SMTP Settings", "SMTP settings saved!")
        
        ttk.Button(smtp_frame, text="Save SMTP Settings", command=save_smtp_settings).grid(row=2, column=1, pady=10)
        
        # Twilio settings for SMS reminders
        twilio_frame = ttk.LabelFrame(reminders_frame, text="Twilio Settings (for SMS)", padding="10")
        twilio_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W)
        
        ttk.Label(twilio_frame, text="Account SID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        twilio_sid_var = tk.StringVar(value=self.twilio_sid)
        twilio_sid_entry = ttk.Entry(twilio_frame, textvariable=twilio_sid_var, width=30)
        twilio_sid_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(twilio_frame, text="Auth Token:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        twilio_token_var = tk.StringVar(value=self.twilio_token)
        twilio_token_entry = ttk.Entry(twilio_frame, textvariable=twilio_token_var, width=30, show='*')
        twilio_token_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(twilio_frame, text="From Number:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        twilio_from_var = tk.StringVar(value=self.twilio_from)
        twilio_from_entry = ttk.Entry(twilio_frame, textvariable=twilio_from_var, width=20)
        twilio_from_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save_twilio_settings():
            self.twilio_sid = twilio_sid_var.get()
            self.twilio_token = twilio_token_var.get()
            self.twilio_from = twilio_from_var.get()
            self.settings['twilio_sid'] = self.twilio_sid
            self.settings['twilio_token'] = self.twilio_token
            self.settings['twilio_from'] = self.twilio_from
            self.save_settings()
            messagebox.showinfo("Twilio Settings", "Twilio settings saved!")
        
        ttk.Button(twilio_frame, text="Save Twilio Settings", command=save_twilio_settings).grid(row=3, column=1, pady=10)
    
    def update_display(self):
        """Update the display with current data"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_usage = self.usage_data['daily_usage'].get(today, 0) // 60  # Convert to minutes
        
        # Update labels
        self.today_usage_label.config(text=f"Today's Usage: {today_usage} minutes")
        self.limit_progress_label.config(text=f"Daily Limit: {today_usage}/{self.settings['daily_limit']} minutes")
        self.breaks_label.config(text=f"Breaks Taken: {self.usage_data['breaks_taken']}")
        self.focus_label.config(text=f"Focus Sessions: {self.usage_data['focus_sessions']}")
        self.productivity_label.config(text=f"Productivity: {self.usage_data.get('productivity_score', 0)}%")
        self.streak_label.config(text=f"Current Streak: {self.usage_data.get('current_streak', 0)} days")
        self.best_streak_label.config(text=f"Best Streak: {self.usage_data.get('best_streak', 0)} days")
        
        # Update progress bar
        progress = min(100, (today_usage / self.settings['daily_limit']) * 100)
        self.progress_var.set(progress)
        
        # Update blocking status
        self.update_blocking_status()
        
        # Update chart
        self.update_chart()
        self.suggestion_var.set(self.get_smart_suggestion())
        self.update_achievement_display()
    
    def update_chart(self):
        """Update the weekly usage chart"""
        self.ax.clear()
        
        # Get last 7 days
        dates = []
        usage = []
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            dates.insert(0, date)
            usage.insert(0, self.usage_data['daily_usage'].get(date, 0) // 60)
        
        # Create bar chart
        bars = self.ax.bar(range(len(dates)), usage, color='skyblue', alpha=0.7)
        
        # Add limit line
        limit_line = [self.settings['daily_limit']] * len(dates)
        self.ax.plot(range(len(dates)), limit_line, 'r--', label='Daily Limit', linewidth=2)
        
        # Customize chart
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Minutes')
        self.ax.set_title('Weekly Social Media Usage')
        self.ax.set_xticks(range(len(dates)))
        self.ax.set_xticklabels([d[5:] for d in dates], rotation=45)
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, usage):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value}m', ha='center', va='bottom')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def show_motivational_quote(self):
        quote = random.choice(self.quotes)
        messagebox.showinfo("Motivation", quote)
    
    def start_background_tasks(self):
        """Start background tasks like scheduling"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        # Schedule daily reset
        schedule.every().day.at("00:00").do(self.daily_reset)
        
        # Schedule breaks
        for break_time in self.scheduled_breaks:
            schedule.every().day.at(break_time).do(self.scheduled_break)
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def daily_reset(self):
        """Reset daily counters and update streaks"""
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        # Check if yesterday met the goal
        if (yesterday in self.usage_data['daily_usage'] and
            self.usage_data['daily_usage'][yesterday] <= self.settings['daily_limit'] * 60):
            self.current_streak += 1
        else:
            self.current_streak = 0
        if self.current_streak > self.best_streak:
            self.best_streak = self.current_streak
        self.usage_data['current_streak'] = self.current_streak
        self.usage_data['best_streak'] = self.best_streak
        self.usage_data['goals_met'] += 1
        self.save_data()
        self.update_display()
        self.suggestion_var.set(self.get_smart_suggestion())
    
    def scheduled_break(self):
        """Trigger a scheduled break"""
        if self.settings['notifications_enabled']:
            notification.notify(
                title='Scheduled Break!',
                message='It\'s time for your scheduled break. Step away from the screen!',
                timeout=10
            )
        self.take_break()

    def start_pomodoro(self):
        """Start the Pomodoro timer"""
        if not self.pomodoro_active:
            self.pomodoro_active = True
            self.pomodoro_start_button.config(state='disabled')
            self.pomodoro_pause_button.config(state='normal')
            self.timer_status_var.set("Work session in progress")
            
            # Start focus mode if not already active
            if not self.is_focus_mode:
                self.start_focus_mode()
            
            # Start timer thread
            self.pomodoro_thread = threading.Thread(target=self.pomodoro_timer_loop, daemon=True)
            self.pomodoro_thread.start()
    
    def pause_pomodoro(self):
        """Pause the Pomodoro timer"""
        if self.pomodoro_active:
            self.pomodoro_active = False
            self.pomodoro_start_button.config(state='normal')
            self.pomodoro_pause_button.config(state='disabled')
            self.timer_status_var.set("Timer paused")
    
    def reset_pomodoro(self):
        """Reset the Pomodoro timer"""
        self.pomodoro_active = False
        preset = self.custom_timers[self.current_timer_preset]
        self.pomodoro_work_time = preset['work'] * 60
        self.pomodoro_break_time = preset['break'] * 60
        self.pomodoro_current_time = self.pomodoro_work_time
        self.pomodoro_is_break = False
        self.pomodoro_start_button.config(state='normal')
        self.pomodoro_pause_button.config(state='disabled')
        self.timer_var.set(f"{preset['work']:02d}:00")
        self.timer_status_var.set(f"Ready to start {preset['name']}")
    
    def pomodoro_timer_loop(self):
        """Pomodoro timer loop"""
        while self.pomodoro_active and self.pomodoro_current_time > 0:
            minutes = self.pomodoro_current_time // 60
            seconds = self.pomodoro_current_time % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            # Update timer display
            self.root.after(0, lambda: self.timer_var.set(time_str))
            
            time.sleep(1)
            self.pomodoro_current_time -= 1
        
        # Timer finished
        if self.pomodoro_current_time <= 0:
            self.root.after(0, self.pomodoro_finished)
    
    def pomodoro_finished(self):
        """Handle Pomodoro timer completion"""
        if not self.pomodoro_is_break:
            # Work session finished, start break
            self.pomodoro_is_break = True
            self.pomodoro_current_time = self.pomodoro_break_time
            self.timer_status_var.set("Break time!")
            
            # Play timer sound
            self.play_sound('timer')
            
            # Take a break
            self.take_break()
            
            # Show notification
            if self.settings['notifications_enabled']:
                notification.notify(
                    title='Pomodoro Break!',
                    message='Great work! Take a 5-minute break.',
                    timeout=10
                )
            
            # Start break timer
            self.pomodoro_thread = threading.Thread(target=self.pomodoro_timer_loop, daemon=True)
            self.pomodoro_thread.start()
        else:
            # Break finished, reset to work session
            self.pomodoro_is_break = False
            self.pomodoro_current_time = self.pomodoro_work_time
            self.timer_status_var.set("Break finished - ready for next session")
            
            # Play timer sound
            self.play_sound('timer')
            
            # Show notification
            if self.settings['notifications_enabled']:
                notification.notify(
                    title='Break Finished!',
                    message='Ready for your next 25-minute work session.',
                    timeout=5
                )
            
            # Reset timer display
            self.timer_var.set("25:00")
            self.pomodoro_active = False
            self.pomodoro_start_button.config(state='normal')
            self.pomodoro_pause_button.config(state='disabled')
            
            # Track Pomodoro sessions
            pomodoro_sessions = self.usage_data.get('pomodoro_sessions', 0) + 1
            self.usage_data['pomodoro_sessions'] = pomodoro_sessions
            self.save_data()
            self.check_achievements()  # Check for new achievements
    
    def check_achievements(self):
        """Check and award achievements based on current stats"""
        new_achievements = []
        
        # Check streak achievements
        streak = self.usage_data.get('current_streak', 0)
        if streak >= 3 and 'streak_3' not in self.achievements:
            self.achievements['streak_3'] = datetime.now().isoformat()
            new_achievements.append('streak_3')
        if streak >= 7 and 'streak_7' not in self.achievements:
            self.achievements['streak_7'] = datetime.now().isoformat()
            new_achievements.append('streak_7')
        if streak >= 30 and 'streak_30' not in self.achievements:
            self.achievements['streak_30'] = datetime.now().isoformat()
            new_achievements.append('streak_30')
        
        # Check focus session achievements
        focus_sessions = self.usage_data.get('focus_sessions', 0)
        if focus_sessions >= 5 and 'focus_5' not in self.achievements:
            self.achievements['focus_5'] = datetime.now().isoformat()
            new_achievements.append('focus_5')
        if focus_sessions >= 25 and 'focus_25' not in self.achievements:
            self.achievements['focus_25'] = datetime.now().isoformat()
            new_achievements.append('focus_25')
        
        # Check break achievements
        breaks = self.usage_data.get('breaks_taken', 0)
        if breaks >= 1 and 'first_break' not in self.achievements:
            self.achievements['first_break'] = datetime.now().isoformat()
            new_achievements.append('first_break')
        if breaks >= 10 and 'breaks_10' not in self.achievements:
            self.achievements['breaks_10'] = datetime.now().isoformat()
            new_achievements.append('breaks_10')
        if breaks >= 50 and 'breaks_50' not in self.achievements:
            self.achievements['breaks_50'] = datetime.now().isoformat()
            new_achievements.append('breaks_50')
        
        # Check productivity achievements
        productivity = self.usage_data.get('productivity_score', 0)
        if productivity >= 90 and 'productivity_90' not in self.achievements:
            self.achievements['productivity_90'] = datetime.now().isoformat()
            new_achievements.append('productivity_90')
        
        # Save achievements
        self.usage_data['achievements'] = self.achievements
        self.save_data()
        
        # Show notifications for new achievements
        for achievement_id in new_achievements:
            achievement = self.achievement_definitions[achievement_id]
            
            # Play achievement sound
            self.play_sound('achievement')
            
            if self.settings['notifications_enabled']:
                notification.notify(
                    title=f'Achievement Unlocked! {achievement["icon"]}',
                    message=f'{achievement["name"]}: {achievement["description"]}',
                    timeout=10
                )
        
        # Update achievement display
        self.update_achievement_display()
    
    def update_achievement_display(self):
        """Update the achievement display"""
        self.achievement_text.config(state='normal')
        self.achievement_text.delete(1.0, tk.END)
        
        if not self.achievements:
            self.achievement_text.insert(tk.END, "No achievements yet. Keep using the app to unlock badges!")
        else:
            for achievement_id, unlock_date in self.achievements.items():
                if achievement_id in self.achievement_definitions:
                    achievement = self.achievement_definitions[achievement_id]
                    date_str = unlock_date[:10] if len(unlock_date) >= 10 else unlock_date
                    self.achievement_text.insert(tk.END, f"{achievement['icon']} {achievement['name']} - {achievement['description']} (Unlocked: {date_str})\n")
        
        self.achievement_text.config(state='disabled')
    
    def get_smart_suggestion(self):
        """Generate a smart suggestion based on recent usage patterns"""
        today = datetime.now().strftime('%Y-%m-%d')
        streak = self.usage_data.get('current_streak', 0)
        best_streak = self.usage_data.get('best_streak', 0)
        breaks = self.usage_data.get('breaks_taken', 0)
        today_usage = self.usage_data['daily_usage'].get(today, 0) // 60
        limit = self.settings['daily_limit']
        suggestions = []
        
        # Add Pomodoro suggestions
        if not self.pomodoro_active:
            suggestions.append("Try the Pomodoro timer for focused work sessions!")
        
        if streak >= 3:
            suggestions.append(f"Great job! You've met your goal {streak} days in a row.")
        if today_usage > limit:
            suggestions.append("You exceeded your daily limit. Try scheduling an extra break tomorrow.")
        if breaks == 0 and today_usage > 0:
            suggestions.append("Remember to take breaks for better focus and wellbeing.")
        if best_streak >= 7:
            suggestions.append(f"Amazing! Your best streak is {best_streak} days. Keep it up!")
        if not suggestions:
            suggestions.append("Tip: Use Focus Mode for deep work or try reducing your daily limit by 10 minutes.")
        return random.choice(suggestions)

    def on_timer_preset_change(self, event=None):
        """Handle timer preset selection change"""
        self.current_timer_preset = self.timer_preset_var.get()
        preset = self.custom_timers[self.current_timer_preset]
        self.pomodoro_work_time = preset['work'] * 60
        self.pomodoro_break_time = preset['break'] * 60
        self.pomodoro_current_time = self.pomodoro_work_time
        self.timer_var.set(f"{preset['work']:02d}:00")
        self.timer_status_var.set(f"Ready to start {preset['name']}")
    
    def open_custom_timers(self):
        """Open custom timer configuration dialog"""
        timer_window = tk.Toplevel(self.root)
        timer_window.title("Custom Timer Presets")
        timer_window.geometry("500x400")
        timer_window.transient(self.root)
        timer_window.grab_set()
        
        # Timer list
        ttk.Label(timer_window, text="Custom Timer Presets:").pack(anchor=tk.W, padx=10, pady=5)
        
        # Listbox for timers
        timer_frame = ttk.Frame(timer_window)
        timer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        timer_listbox = tk.Listbox(timer_frame, height=8)
        timer_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(timer_frame, orient=tk.VERTICAL, command=timer_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        timer_listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate listbox
        for name, preset in self.custom_timers.items():
            timer_listbox.insert(tk.END, f"{name}: {preset['work']}min work / {preset['break']}min break")
        
        # Add new timer frame
        add_frame = ttk.LabelFrame(timer_window, text="Add New Timer", padding="10")
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(add_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(add_frame, width=20)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Work (min):").grid(row=0, column=2, padx=5, pady=5)
        work_entry = ttk.Entry(add_frame, width=10)
        work_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Break (min):").grid(row=0, column=4, padx=5, pady=5)
        break_entry = ttk.Entry(add_frame, width=10)
        break_entry.grid(row=0, column=5, padx=5, pady=5)
        
        def add_timer():
            name = name_entry.get().strip()
            try:
                work = int(work_entry.get())
                break_time = int(break_entry.get())
                if name and work > 0 and break_time > 0:
                    self.custom_timers[name] = {'work': work, 'break': break_time, 'name': name}
                    timer_listbox.insert(tk.END, f"{name}: {work}min work / {break_time}min break")
                    name_entry.delete(0, tk.END)
                    work_entry.delete(0, tk.END)
                    break_entry.delete(0, tk.END)
                    # Update combo box
                    self.timer_preset_combo['values'] = list(self.custom_timers.keys())
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for work and break times.")
        
        def remove_timer():
            selection = timer_listbox.curselection()
            if selection:
                timer_name = timer_listbox.get(selection[0]).split(':')[0]
                if timer_name in self.custom_timers:
                    del self.custom_timers[timer_name]
                    timer_listbox.delete(selection[0])
                    # Update combo box
                    self.timer_preset_combo['values'] = list(self.custom_timers.keys())
                    if self.current_timer_preset == timer_name:
                        self.current_timer_preset = 'Pomodoro'
                        self.timer_preset_var.set('Pomodoro')
                        self.on_timer_preset_change()
        
        # Buttons
        button_frame = ttk.Frame(timer_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Add Timer", command=add_timer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Timer", command=remove_timer).pack(side=tk.LEFT, padx=5)
        
        def save_timers():
            self.settings['custom_timers'] = self.custom_timers
            self.save_settings()
            timer_window.destroy()
            messagebox.showinfo("Timers", "Custom timers saved successfully!")
        
        ttk.Button(button_frame, text="Save", command=save_timers).pack(side=tk.LEFT, padx=5)

    def open_analytics_dashboard(self):
        """Open advanced analytics dashboard"""
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Advanced Analytics Dashboard")
        analytics_window.geometry("1200x800")
        analytics_window.transient(self.root)
        analytics_window.grab_set()
        
        # Create notebook for different analytics views
        notebook = ttk.Notebook(analytics_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Overview tab
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Overview")
        self.create_overview_tab(overview_frame)
        
        # Productivity tab
        productivity_frame = ttk.Frame(notebook)
        notebook.add(productivity_frame, text="Productivity")
        self.create_productivity_tab(productivity_frame)
        
        # Focus Sessions tab
        focus_frame = ttk.Frame(notebook)
        notebook.add(focus_frame, text="Focus Sessions")
        self.create_focus_tab(focus_frame)
        
        # Trends tab
        trends_frame = ttk.Frame(notebook)
        notebook.add(trends_frame, text="Trends")
        self.create_trends_tab(trends_frame)
        
        # Upcoming sessions display (stub)
        upcoming_frame = ttk.LabelFrame(overview_frame, text="Upcoming Scheduled Focus Sessions (Calendar)", padding="10")
        upcoming_frame.pack(fill=tk.X, padx=10, pady=10)
        if self.calendar_enabled:
            if self.upcoming_sessions:
                for sess in self.upcoming_sessions:
                    ttk.Label(upcoming_frame, text=sess).pack(anchor=tk.W)
            else:
                ttk.Label(upcoming_frame, text="(Stub) No upcoming sessions found.").pack(anchor=tk.W)
        else:
            ttk.Label(upcoming_frame, text="Calendar integration is disabled.").pack(anchor=tk.W)
    
    def create_overview_tab(self, parent):
        """Create overview analytics tab"""
        # Key metrics frame
        metrics_frame = ttk.LabelFrame(parent, text="Key Metrics", padding="10")
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Calculate metrics
        total_days = len(self.usage_data['daily_usage'])
        total_time = self.usage_data['total_time'] // 60  # Convert to minutes
        avg_daily = total_time // total_days if total_days > 0 else 0
        focus_sessions = self.usage_data.get('focus_sessions', 0)
        breaks_taken = self.usage_data.get('breaks_taken', 0)
        current_streak = self.usage_data.get('current_streak', 0)
        best_streak = self.usage_data.get('best_streak', 0)
        achievements_count = len(self.achievements)
        
        # Display metrics in grid
        metrics = [
            ("Total Days Tracked", f"{total_days} days"),
            ("Total Usage Time", f"{total_time} minutes"),
            ("Average Daily Usage", f"{avg_daily} minutes"),
            ("Focus Sessions", f"{focus_sessions} sessions"),
            ("Breaks Taken", f"{breaks_taken} breaks"),
            ("Current Streak", f"{current_streak} days"),
            ("Best Streak", f"{best_streak} days"),
            ("Achievements Unlocked", f"{achievements_count} badges")
        ]
        
        for i, (label, value) in enumerate(metrics):
            row = i // 4
            col = i % 4
            ttk.Label(metrics_frame, text=label, font=("Arial", 10, "bold")).grid(row=row*2, column=col, padx=10, pady=5)
            ttk.Label(metrics_frame, text=value, font=("Arial", 12)).grid(row=row*2+1, column=col, padx=10, pady=5)
        
        # Weekly usage chart
        chart_frame = ttk.LabelFrame(parent, text="Weekly Usage Overview", padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        self.create_weekly_chart(ax)
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_productivity_tab(self, parent):
        """Create productivity analytics tab"""
        # Productivity score over time
        score_frame = ttk.LabelFrame(parent, text="Productivity Score Trends", padding="10")
        score_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get productivity data from database
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT start_time, focus_score FROM productivity_sessions ORDER BY start_time")
        data = cursor.fetchall()
        conn.close()
        
        if data:
            dates = [row[0][:10] for row in data]
            scores = [row[1] for row in data]
            
            ax.plot(range(len(dates)), scores, marker='o', linewidth=2, markersize=6)
            ax.set_xlabel('Session Number')
            ax.set_ylabel('Productivity Score (%)')
            ax.set_title('Productivity Score Over Time')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 100)
            
            # Add average line
            avg_score = sum(scores) / len(scores)
            ax.axhline(y=avg_score, color='r', linestyle='--', label=f'Average: {avg_score:.1f}%')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No productivity data available yet', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Productivity Score Over Time')
        
        canvas = FigureCanvasTkAgg(fig, score_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_focus_tab(self, parent):
        """Create focus sessions analytics tab"""
        # Focus session statistics
        stats_frame = ttk.LabelFrame(parent, text="Focus Session Statistics", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Get focus session data
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT duration, focus_score, notes FROM productivity_sessions")
        sessions = cursor.fetchall()
        conn.close()
        
        if sessions:
            durations = [s[0] for s in sessions]
            scores = [s[1] for s in sessions]
            
            avg_duration = sum(durations) / len(durations)
            avg_score = sum(scores) / len(scores)
            total_focus_time = sum(durations) // 60  # Convert to minutes
            
            stats_text = f"""
            Total Focus Sessions: {len(sessions)}
            Total Focus Time: {total_focus_time} minutes
            Average Session Duration: {avg_duration//60} minutes {avg_duration%60} seconds
            Average Productivity Score: {avg_score:.1f}%
            Best Session Score: {max(scores)}%
            """
        else:
            stats_text = "No focus session data available yet."
        
        stats_label = ttk.Label(stats_frame, text=stats_text, font=("Arial", 11))
        stats_label.pack(anchor=tk.W)
        
        # Focus session distribution chart
        chart_frame = ttk.LabelFrame(parent, text="Focus Session Distribution", padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        if sessions:
            # Duration distribution
            ax1.hist(durations, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
            ax1.set_xlabel('Duration (seconds)')
            ax1.set_ylabel('Number of Sessions')
            ax1.set_title('Session Duration Distribution')
            ax1.grid(True, alpha=0.3)
            
            # Score distribution
            ax2.hist(scores, bins=10, alpha=0.7, color='lightgreen', edgecolor='black')
            ax2.set_xlabel('Productivity Score (%)')
            ax2.set_ylabel('Number of Sessions')
            ax2.set_title('Productivity Score Distribution')
            ax2.grid(True, alpha=0.3)
        else:
            ax1.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax1.transAxes)
            ax2.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax2.transAxes)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_trends_tab(self, parent):
        """Create trends analytics tab"""
        # Daily usage trends
        trends_frame = ttk.LabelFrame(parent, text="Daily Usage Trends", padding="10")
        trends_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Get last 30 days of data
        dates = []
        usage = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            dates.insert(0, date)
            usage.insert(0, self.usage_data['daily_usage'].get(date, 0) // 60)
        
        # Daily usage line chart
        ax1.plot(range(len(dates)), usage, marker='o', linewidth=2, markersize=4)
        ax1.set_xlabel('Days Ago')
        ax1.set_ylabel('Usage (minutes)')
        ax1.set_title('Daily Usage Over Last 30 Days')
        ax1.grid(True, alpha=0.3)
        
        # Add limit line
        limit_line = [self.settings['daily_limit']] * len(dates)
        ax1.plot(range(len(dates)), limit_line, 'r--', label='Daily Limit', linewidth=2)
        ax1.legend()
        
        # Weekly average chart
        weekly_avgs = []
        week_labels = []
        for i in range(0, len(usage), 7):
            week_usage = usage[i:i+7]
            if week_usage:
                weekly_avgs.append(sum(week_usage) / len(week_usage))
                week_labels.append(f"Week {len(weekly_avgs)}")
        
        if weekly_avgs:
            ax2.bar(week_labels, weekly_avgs, alpha=0.7, color='orange')
            ax2.set_xlabel('Week')
            ax2.set_ylabel('Average Daily Usage (minutes)')
            ax2.set_title('Weekly Average Usage')
            ax2.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, v in enumerate(weekly_avgs):
                ax2.text(i, v + 1, f'{v:.0f}m', ha='center', va='bottom')
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, trends_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_weekly_chart(self, ax):
        """Create enhanced weekly usage chart"""
        # Get last 7 days
        dates = []
        usage = []
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            dates.insert(0, date)
            usage.insert(0, self.usage_data['daily_usage'].get(date, 0) // 60)
        
        # Create enhanced bar chart
        bars = ax.bar(range(len(dates)), usage, color='skyblue', alpha=0.7, edgecolor='navy')
        
        # Add limit line
        limit_line = [self.settings['daily_limit']] * len(dates)
        ax.plot(range(len(dates)), limit_line, 'r--', label='Daily Limit', linewidth=2)
        
        # Customize chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Minutes')
        ax.set_title('Weekly Social Media Usage')
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels([d[5:] for d in dates], rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, usage):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value}m', ha='center', va='bottom')
        
        # Color bars based on limit
        for i, (bar, value) in enumerate(zip(bars, usage)):
            if value > self.settings['daily_limit']:
                bar.set_color('lightcoral')
            elif value < self.settings['daily_limit'] * 0.8:
                bar.set_color('lightgreen')

    def play_sound(self, sound_type):
        """Play a sound notification based on type"""
        if not self.sound_enabled:
            return
        
        sound_name = self.sound_types.get(sound_type, 'chime')
        
        try:
            if self.sound_system == "Windows":
                # Windows system sounds
                sound_map = {
                    'chime': winsound.MB_ICONASTERISK,
                    'bell': winsound.MB_ICONEXCLAMATION,
                    'ding': winsound.MB_ICONINFORMATION,
                    'success': winsound.MB_ICONASTERISK,
                    'fanfare': winsound.MB_ICONASTERISK,
                    'alert': winsound.MB_ICONEXCLAMATION,
                    'warning': winsound.MB_ICONEXCLAMATION,
                    'error': winsound.MB_ICONHAND,
                    'notification': winsound.MB_ICONINFORMATION
                }
                winsound.MessageBeep(sound_map.get(sound_name, winsound.MB_ICONINFORMATION))
            
            elif self.sound_system == "Darwin":  # macOS
                # macOS system sounds
                sound_map = {
                    'chime': 'Glass',
                    'bell': 'Basso',
                    'ding': 'Ping',
                    'success': 'Glass',
                    'fanfare': 'Hero',
                    'alert': 'Sosumi',
                    'warning': 'Sosumi',
                    'error': 'Basso',
                    'notification': 'Ping'
                }
                sound_file = sound_map.get(sound_name, 'Ping')
                subprocess.run(['afplay', f'/System/Library/Sounds/{sound_file}.aiff'])
            
            elif self.sound_system == "Linux":
                # Linux system sounds (using aplay or paplay)
                sound_map = {
                    'chime': 'message-new-instant',
                    'bell': 'bell-window-system',
                    'ding': 'message',
                    'success': 'complete',
                    'fanfare': 'complete',
                    'alert': 'dialog-warning',
                    'warning': 'dialog-warning',
                    'error': 'dialog-error',
                    'notification': 'message'
                }
                sound_file = sound_map.get(sound_name, 'message')
                try:
                    subprocess.run(['paplay', f'/usr/share/sounds/freedesktop/stereo/{sound_file}.oga'])
                except FileNotFoundError:
                    try:
                        subprocess.run(['aplay', f'/usr/share/sounds/{sound_file}.wav'])
                    except FileNotFoundError:
                        # Fallback to simple beep
                        print('\a')
        except Exception as e:
            # Fallback to simple beep if sound system fails
            print('\a')

    def add_tooltip(self, widget, text):
        """Add a tooltip to a widget"""
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        label = tk.Label(tooltip, text=text, background="#ffffe0", relief=tk.SOLID, borderwidth=1, font=("Arial", 9))
        label.pack(ipadx=2)
        
        def enter(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
        def leave(event):
            tooltip.withdraw()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def schedule_focus_session(self):
        """Stub: Schedule the next focus session in Google Calendar"""
        if not self.calendar_enabled or not self.calendar_api_key or not self.calendar_id:
            messagebox.showwarning("Calendar Integration", "Please enable calendar integration and provide API key and calendar ID in settings.")
            return
        # Here you would use Google Calendar API to create an event
        # For now, just show a stub message
        messagebox.showinfo("Calendar Integration", "(Stub) Focus session scheduled in Google Calendar!")

    def share_achievement(self):
        """Share the latest achievement (copies to clipboard)"""
        if not self.achievements:
            messagebox.showinfo("Share Achievement", "No achievements to share yet!")
            return
        # Get the most recent achievement
        latest = max(self.achievements.items(), key=lambda x: x[1])
        achievement_id, unlock_date = latest
        if achievement_id in self.achievement_definitions:
            achievement = self.achievement_definitions[achievement_id]
            msg = f"I just unlocked '{achievement['name']}' in the Scroll Stopping Tool! {achievement['icon']} ({achievement['description']}) #ScrollStoppingTool"
            self.root.clipboard_clear()
            self.root.clipboard_append(msg)
            messagebox.showinfo("Share Achievement", "Achievement copied to clipboard! Paste it anywhere to share.")
        else:
            messagebox.showinfo("Share Achievement", "Achievement not found.")

    def compare_progress(self):
        """Stub: Compare progress with a friend's exported stats"""
        messagebox.showinfo("Compare Progress", "(Stub) This will allow you to import a friend's stats and compare side-by-side.")

    def export_backup(self):
        """Export all user data as a JSON backup"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filename:
            return
        backup = {
            'usage_data': self.usage_data,
            'settings': self.settings
        }
        try:
            with open(filename, 'w') as f:
                import json
                json.dump(backup, f, indent=2)
            messagebox.showinfo("Export Backup", f"Backup exported successfully to {filename}")
        except Exception as e:
            messagebox.showerror("Export Backup", f"Failed to export backup: {e}")

    def import_backup(self):
        """Import user data from a JSON backup"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            with open(filename, 'r') as f:
                import json
                backup = json.load(f)
            if 'usage_data' in backup and 'settings' in backup:
                self.usage_data = backup['usage_data']
                self.settings = backup['settings']
                self.save_data()
                self.save_settings()
                self.update_display()
                messagebox.showinfo("Import Backup", "Backup imported successfully!")
            else:
                messagebox.showerror("Import Backup", "Invalid backup file.")
        except Exception as e:
            messagebox.showerror("Import Backup", f"Failed to import backup: {e}")

    def sync_cloud(self):
        """Stub: Sync data to the cloud"""
        messagebox.showinfo("Sync (Cloud)", "(Stub) This will sync your data to the cloud in a future update.")

    def test_email_reminder(self):
        """Send a test email reminder using SMTP"""
        if not self.reminder_email_enabled or not self.reminder_email:
            messagebox.showwarning("Test Email Reminder", "Please enable email reminders and enter your email address.")
            return
        if not self.smtp_server or not self.smtp_username or not self.smtp_password:
            messagebox.showwarning("Test Email Reminder", "Please enter your SMTP settings.")
            return
        try:
            msg = MIMEText("This is a test reminder from the Scroll Stopping Tool.")
            msg['Subject'] = "Test Reminder - Scroll Stopping Tool"
            msg['From'] = self.smtp_username
            msg['To'] = self.reminder_email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            if self.smtp_tls:
                server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.smtp_username, [self.reminder_email], msg.as_string())
            server.quit()
            messagebox.showinfo("Test Email Reminder", f"Test email sent to {self.reminder_email}!")
        except Exception as e:
            messagebox.showerror("Test Email Reminder", f"Failed to send test email: {e}")

    def test_sms_reminder(self):
        """Send a test SMS reminder using Twilio"""
        if not self.reminder_sms_enabled or not self.reminder_phone:
            messagebox.showwarning("Test SMS Reminder", "Please enable SMS reminders and enter your phone number.")
            return
        if not TWILIO_AVAILABLE:
            messagebox.showerror("Test SMS Reminder", "Twilio is not installed. Please install the twilio package.")
            return
        if not self.twilio_sid or not self.twilio_token or not self.twilio_from:
            messagebox.showwarning("Test SMS Reminder", "Please enter your Twilio settings.")
            return
        try:
            client = TwilioClient(self.twilio_sid, self.twilio_token)
            message = client.messages.create(
                body="This is a test SMS reminder from the Scroll Stopping Tool.",
                from_=self.twilio_from,
                to=self.reminder_phone
            )
            messagebox.showinfo("Test SMS Reminder", f"Test SMS sent to {self.reminder_phone}!")
        except Exception as e:
            messagebox.showerror("Test SMS Reminder", f"Failed to send test SMS: {e}")

    def customize_dashboard(self):
        """Stub: Customize dashboard layout (show/hide sections)"""
        # For now, just show a dialog with checkboxes and save preferences
        layout_prefs = self.settings.get('dashboard_layout', {
            'weekly_chart': True,
            'focus_stats': True,
            'achievements': True,
            'trends': True
        })
        win = tk.Toplevel(self.root)
        win.title("Customize Dashboard")
        win.geometry("350x250")
        win.transient(self.root)
        win.grab_set()
        
        vars = {}
        row = 0
        for section, enabled in layout_prefs.items():
            var = tk.BooleanVar(value=enabled)
            vars[section] = var
            ttk.Checkbutton(win, text=f"Show {section.replace('_', ' ').title()}", variable=var).grid(row=row, column=0, sticky=tk.W, padx=20, pady=10)
            row += 1
        
        def save_layout():
            self.settings['dashboard_layout'] = {k: v.get() for k, v in vars.items()}
            self.save_settings()
            win.destroy()
            messagebox.showinfo("Customize Dashboard", "Dashboard layout preferences saved! (Stub: sections will be shown/hidden in a future update)")
        
        ttk.Button(win, text="Save", command=save_layout).grid(row=row, column=0, pady=20)

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = ScrollStoppingTool(root)
    
    # Handle window close
    def on_closing():
        if app.is_tracking:
            app.stop_tracking()
        app.save_data()
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 