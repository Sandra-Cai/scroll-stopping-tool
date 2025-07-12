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
            "Don’t watch the clock; do what it does. Keep going. – Sam Levenson",
            "Success is the sum of small efforts, repeated day in and day out. – Robert Collier",
            "You don’t have to be perfect to be amazing.",
            "Discipline is the bridge between goals and accomplishment. – Jim Rohn",
            "It always seems impossible until it’s done. – Nelson Mandela",
            "The best way to get something done is to begin.",
            "Small steps every day."
        ]
        
        # Create GUI
        self.create_widgets()
        self.update_display()
        self.show_motivational_quote()
        
        # Start background tasks
        self.start_background_tasks()
    
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
                    'best_streak': 0
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
                'best_streak': 0
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
                    }
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
                }
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
        self.export_button.grid(row=0, column=7)
        
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
        if self.settings['notifications_enabled']:
            notification.notify(
                title='Daily Limit Reached!',
                message='You\'ve reached your daily social media limit. Time to disconnect!',
                timeout=10
            )
        if self.settings.get('auto_lock', False):
            self.lock_screen()
    
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
    
    def scheduled_break(self):
        """Trigger a scheduled break"""
        if self.settings['notifications_enabled']:
            notification.notify(
                title='Scheduled Break!',
                message='It\'s time for your scheduled break. Step away from the screen!',
                timeout=10
            )
        self.take_break()

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