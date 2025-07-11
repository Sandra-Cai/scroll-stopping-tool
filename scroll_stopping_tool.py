#!/usr/bin/env python3
"""
Scroll Stopping Tool
A Python application to help users break the habit of excessive social media scrolling.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
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

class ScrollStoppingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Scroll Stopping Tool")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.data_file = "usage_data.json"
        self.settings_file = "settings.json"
        self.load_data()
        self.load_settings()
        
        # Tracking variables
        self.is_tracking = False
        self.tracking_thread = None
        self.blocking_thread = None
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
        
        # Create GUI
        self.create_widgets()
        self.update_display()
        
        # Start background tasks
        self.start_background_tasks()
    
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
                    'goals_met': 0
                }
        except:
            self.usage_data = {
                'daily_usage': {},
                'total_time': 0,
                'breaks_taken': 0,
                'goals_met': 0
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
                    'auto_lock': False,  # New setting
                    'blocking_enabled': False,
                    'blocked_sites': [],
                    'scheduled_breaks': [],
                    'custom_notifications': []
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
                'custom_notifications': []
            }
    
    def save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Scroll Stopping Tool", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=5, pady=(0, 20))
        
        # Control buttons
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="Start Tracking", 
                                      command=self.start_tracking)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Tracking", 
                                     command=self.stop_tracking, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.settings_button = ttk.Button(control_frame, text="Settings", 
                                         command=self.open_settings)
        self.settings_button.grid(row=0, column=2, padx=(0, 10))
        
        self.break_button = ttk.Button(control_frame, text="Take Break", 
                                      command=self.take_break)
        self.break_button.grid(row=0, column=3, padx=(0, 10))
        
        self.lock_button = ttk.Button(control_frame, text="Lock Screen Now", 
                                      command=self.lock_screen)
        self.lock_button.grid(row=0, column=4, padx=(0, 10))
        
        self.block_button = ttk.Button(control_frame, text="Block Sites", 
                                      command=self.open_blocking_dialog)
        self.block_button.grid(row=0, column=5)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="Today's Statistics", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Today's usage
        self.today_usage_label = ttk.Label(stats_frame, text="Today's Usage: 0 minutes")
        self.today_usage_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        # Daily limit progress
        self.limit_progress_label = ttk.Label(stats_frame, text="Daily Limit: 0/120 minutes")
        self.limit_progress_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Breaks taken
        self.breaks_label = ttk.Label(stats_frame, text="Breaks Taken: 0")
        self.breaks_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        
        # Blocking status
        self.blocking_status_label = ttk.Label(stats_frame, text="Blocking: Disabled")
        self.blocking_status_label.grid(row=0, column=3, sticky=tk.W)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(stats_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Alternative activities frame
        activities_frame = ttk.LabelFrame(main_frame, text="Alternative Activities", padding="10")
        activities_frame.grid(row=3, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        chart_frame.grid(row=4, column=0, columnspan=5, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to start tracking")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 0))
    
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
        settings_window.title("Settings")
        settings_window.geometry("500x500")
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
        
        # Save button
        def save_settings():
            try:
                self.settings['daily_limit'] = int(limit_var.get())
                self.settings['break_reminder'] = int(reminder_var.get())
                self.settings['notifications_enabled'] = notif_var.get()
                self.settings['auto_break'] = auto_break_var.get()
                self.settings['auto_lock'] = auto_lock_var.get()
                self.settings['scheduled_breaks'] = self.scheduled_breaks
                self.save_settings()
                settings_window.destroy()
                self.update_display()
                messagebox.showinfo("Settings", "Settings saved successfully!")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for limits and reminders.")
        
        ttk.Button(settings_window, text="Save", command=save_settings).pack(pady=20)
    
    def update_display(self):
        """Update the display with current data"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_usage = self.usage_data['daily_usage'].get(today, 0) // 60  # Convert to minutes
        
        # Update labels
        self.today_usage_label.config(text=f"Today's Usage: {today_usage} minutes")
        self.limit_progress_label.config(text=f"Daily Limit: {today_usage}/{self.settings['daily_limit']} minutes")
        self.breaks_label.config(text=f"Breaks Taken: {self.usage_data['breaks_taken']}")
        
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
        """Reset daily counters"""
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