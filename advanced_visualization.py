#!/usr/bin/env python3
"""
Advanced Visualization Module for Enhanced Scroll Stopping Tool
Interactive charts, real-time dashboards, and comprehensive analytics displays.
"""

import tkinter as tk
from tkinter import ttk
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import random

# Optional imports for advanced visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

class AdvancedVisualization:
    """Advanced data visualization system"""
    
    def __init__(self):
        self.charts = {}
        self.dashboards = {}
        self.real_time_data = {}
        self.animation_running = False
    
    def create_interactive_dashboard(self, parent, user_data: Dict) -> tk.Frame:
        """Create interactive dashboard with multiple charts"""
        dashboard_frame = ttk.Frame(parent)
        dashboard_frame.pack(fill='both', expand=True)
        
        # Create notebook for different dashboard views
        notebook = ttk.Notebook(dashboard_frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Overview tab
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="📊 Overview")
        self.create_overview_dashboard(overview_frame, user_data)
        
        # Trends tab
        trends_frame = ttk.Frame(notebook)
        notebook.add(trends_frame, text="📈 Trends")
        self.create_trends_dashboard(trends_frame, user_data)
        
        # Focus tab
        focus_frame = ttk.Frame(notebook)
        notebook.add(focus_frame, text="🎯 Focus")
        self.create_focus_dashboard(focus_frame, user_data)
        
        # Achievements tab
        achievements_frame = ttk.Frame(notebook)
        notebook.add(achievements_frame, text="🏆 Achievements")
        self.create_achievements_dashboard(achievements_frame, user_data)
        
        return dashboard_frame
    
    def create_overview_dashboard(self, parent, user_data: Dict):
        """Create overview dashboard"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(
            header_frame,
            text="📊 Productivity Overview",
            font=('Arial', 18, 'bold')
        ).pack()
        
        # Key metrics grid
        metrics_frame = ttk.Frame(parent)
        metrics_frame.pack(fill='x', padx=10, pady=10)
        
        # Create metric cards
        metrics = [
            ("⏱️ Today's Usage", f"{user_data.get('usage_time', 0)} min", "#FF6B6B"),
            ("🎯 Productivity", f"{user_data.get('productivity_score', 0)}%", "#4ECDC4"),
            ("🎯 Focus Sessions", f"{user_data.get('focus_sessions', 0)}", "#45B7D1"),
            ("🔥 Streak", f"{user_data.get('streak_days', 0)} days", "#96CEB4")
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            metric_frame = ttk.LabelFrame(metrics_frame, text=label, padding="15")
            metric_frame.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            metrics_frame.columnconfigure(i, weight=1)
            
            ttk.Label(
                metric_frame,
                text=value,
                font=('Arial', 20, 'bold'),
                foreground=color
            ).pack()
        
        # Progress visualization
        progress_frame = ttk.LabelFrame(parent, text="📈 Progress Visualization", padding="15")
        progress_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        if MATPLOTLIB_AVAILABLE:
            self.create_progress_chart(progress_frame, user_data)
        else:
            self.create_simple_progress_display(progress_frame, user_data)
    
    def create_trends_dashboard(self, parent, user_data: Dict):
        """Create trends dashboard"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(
            header_frame,
            text="📈 Usage & Productivity Trends",
            font=('Arial', 18, 'bold')
        ).pack()
        
        # Trends visualization
        trends_frame = ttk.Frame(parent)
        trends_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        if MATPLOTLIB_AVAILABLE:
            self.create_trends_chart(trends_frame, user_data)
        else:
            self.create_simple_trends_display(trends_frame, user_data)
    
    def create_focus_dashboard(self, parent, user_data: Dict):
        """Create focus dashboard"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(
            header_frame,
            text="🎯 Focus Session Analytics",
            font=('Arial', 18, 'bold')
        ).pack()
        
        # Focus metrics
        focus_metrics_frame = ttk.Frame(parent)
        focus_metrics_frame.pack(fill='x', padx=10, pady=10)
        
        focus_metrics = [
            ("Total Sessions", f"{user_data.get('total_focus_sessions', 0)}"),
            ("Avg Duration", f"{user_data.get('avg_focus_duration', 0)} min"),
            ("Best Session", f"{user_data.get('best_focus_score', 0)}%"),
            ("Today's Sessions", f"{user_data.get('focus_sessions', 0)}")
        ]
        
        for i, (label, value) in enumerate(focus_metrics):
            metric_frame = ttk.LabelFrame(focus_metrics_frame, text=label, padding="15")
            metric_frame.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            focus_metrics_frame.columnconfigure(i, weight=1)
            
            ttk.Label(
                metric_frame,
                text=value,
                font=('Arial', 16, 'bold')
            ).pack()
        
        # Focus visualization
        focus_viz_frame = ttk.LabelFrame(parent, text="📊 Focus Performance", padding="15")
        focus_viz_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        if MATPLOTLIB_AVAILABLE:
            self.create_focus_chart(focus_viz_frame, user_data)
        else:
            self.create_simple_focus_display(focus_viz_frame, user_data)
    
    def create_achievements_dashboard(self, parent, user_data: Dict):
        """Create achievements dashboard"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(
            header_frame,
            text="🏆 Achievement Progress",
            font=('Arial', 18, 'bold')
        ).pack()
        
        # Achievement stats
        achievement_stats_frame = ttk.Frame(parent)
        achievement_stats_frame.pack(fill='x', padx=10, pady=10)
        
        achievement_stats = [
            ("Unlocked", f"{user_data.get('achievements_unlocked', 0)}"),
            ("Total Available", "20"),
            ("Completion Rate", f"{(user_data.get('achievements_unlocked', 0) / 20) * 100:.1f}%"),
            ("Next Achievement", "Focus Marathon")
        ]
        
        for i, (label, value) in enumerate(achievement_stats):
            stat_frame = ttk.LabelFrame(achievement_stats_frame, text=label, padding="15")
            stat_frame.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            achievement_stats_frame.columnconfigure(i, weight=1)
            
            ttk.Label(
                stat_frame,
                text=value,
                font=('Arial', 16, 'bold')
            ).pack()
        
        # Achievement visualization
        achievement_viz_frame = ttk.LabelFrame(parent, text="🏅 Achievement Categories", padding="15")
        achievement_viz_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        if MATPLOTLIB_AVAILABLE:
            self.create_achievements_chart(achievement_viz_frame, user_data)
        else:
            self.create_simple_achievements_display(achievement_viz_frame, user_data)
    
    def create_progress_chart(self, parent, user_data: Dict):
        """Create progress chart using matplotlib"""
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Generate sample data
        days = list(range(1, 8))
        usage_data = [random.randint(70, 150) for _ in range(7)]
        productivity_data = [random.randint(60, 95) for _ in range(7)]
        
        # Create dual-axis chart
        ax2 = ax.twinx()
        
        # Plot usage data
        line1 = ax.plot(days, usage_data, 'b-', label='Usage (min)', linewidth=2, marker='o')
        ax.set_xlabel('Days')
        ax.set_ylabel('Usage (minutes)', color='b')
        ax.tick_params(axis='y', labelcolor='b')
        
        # Plot productivity data
        line2 = ax2.plot(days, productivity_data, 'r-', label='Productivity (%)', linewidth=2, marker='s')
        ax2.set_ylabel('Productivity (%)', color='r')
        ax2.tick_params(axis='y', labelcolor='r')
        
        # Add grid and title
        ax.grid(True, alpha=0.3)
        ax.set_title('Weekly Progress Overview', fontsize=14, fontweight='bold')
        
        # Add legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_trends_chart(self, parent, user_data: Dict):
        """Create trends chart"""
        fig = Figure(figsize=(12, 8))
        
        # Create subplots
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, 3)
        ax4 = fig.add_subplot(2, 2, 4)
        
        # Generate sample data
        hours = list(range(24))
        usage_by_hour = [random.randint(0, 20) for _ in range(24)]
        productivity_by_hour = [random.randint(50, 95) for _ in range(24)]
        
        # Hourly usage pattern
        ax1.bar(hours, usage_by_hour, color='skyblue', alpha=0.7)
        ax1.set_title('Hourly Usage Pattern')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Usage (minutes)')
        
        # Hourly productivity
        ax2.plot(hours, productivity_by_hour, 'g-', linewidth=2, marker='o')
        ax2.set_title('Hourly Productivity')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Productivity (%)')
        ax2.grid(True, alpha=0.3)
        
        # Weekly comparison
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekly_usage = [random.randint(80, 140) for _ in range(7)]
        weekly_productivity = [random.randint(65, 90) for _ in range(7)]
        
        x = range(len(days))
        ax3.bar(x, weekly_usage, color='lightcoral', alpha=0.7)
        ax3.set_title('Weekly Usage Comparison')
        ax3.set_xlabel('Day of Week')
        ax3.set_ylabel('Usage (minutes)')
        ax3.set_xticks(x)
        ax3.set_xticklabels(days)
        
        # Productivity vs Usage scatter
        ax4.scatter(weekly_usage, weekly_productivity, s=100, alpha=0.6, color='purple')
        ax4.set_title('Productivity vs Usage')
        ax4.set_xlabel('Usage (minutes)')
        ax4.set_ylabel('Productivity (%)')
        ax4.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_focus_chart(self, parent, user_data: Dict):
        """Create focus chart"""
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Generate sample focus session data
        sessions = list(range(1, 11))
        durations = [random.randint(25, 90) for _ in range(10)]
        productivity_scores = [random.randint(70, 95) for _ in range(10)]
        
        # Create scatter plot
        scatter = ax.scatter(durations, productivity_scores, s=100, alpha=0.6, c=sessions, cmap='viridis')
        ax.set_xlabel('Session Duration (minutes)')
        ax.set_ylabel('Productivity Score (%)')
        ax.set_title('Focus Session Performance')
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label('Session Number')
        
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_achievements_chart(self, parent, user_data: Dict):
        """Create achievements chart"""
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Achievement categories
        categories = ['Streak', 'Usage', 'Focus', 'Productivity', 'Consistency']
        unlocked = [3, 2, 1, 1, 1]  # Sample data
        total = [5, 4, 3, 3, 5]
        
        # Calculate percentages
        percentages = [(u/t)*100 for u, t in zip(unlocked, total)]
        
        # Create horizontal bar chart
        bars = ax.barh(categories, percentages, color='lightgreen', alpha=0.7)
        ax.set_xlabel('Completion Percentage (%)')
        ax.set_title('Achievement Progress by Category')
        ax.set_xlim(0, 100)
        
        # Add value labels on bars
        for i, (bar, pct) in enumerate(zip(bars, percentages)):
            ax.text(pct + 1, bar.get_y() + bar.get_height()/2, f'{pct:.1f}%', 
                   va='center', fontweight='bold')
        
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_simple_progress_display(self, parent, user_data: Dict):
        """Create simple progress display without matplotlib"""
        # Weekly progress table
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill='both', expand=True)
        
        # Header
        ttk.Label(progress_frame, text="Weekly Progress", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Create table
        tree = ttk.Treeview(progress_frame, columns=('Day', 'Usage', 'Productivity', 'Focus'), show='headings')
        tree.heading('Day', text='Day')
        tree.heading('Usage', text='Usage (min)')
        tree.heading('Productivity', text='Productivity (%)')
        tree.heading('Focus', text='Focus Sessions')
        
        # Add sample data
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days:
            usage = random.randint(70, 150)
            productivity = random.randint(60, 95)
            focus = random.randint(0, 4)
            tree.insert('', 'end', values=(day, usage, productivity, focus))
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_simple_trends_display(self, parent, user_data: Dict):
        """Create simple trends display"""
        trends_frame = ttk.Frame(parent)
        trends_frame.pack(fill='both', expand=True)
        
        # Usage trends
        usage_frame = ttk.LabelFrame(trends_frame, text="Usage Trends", padding="15")
        usage_frame.pack(fill='x', padx=10, pady=5)
        
        usage_data = [random.randint(70, 150) for _ in range(7)]
        usage_str = " → ".join([str(x) for x in usage_data])
        ttk.Label(usage_frame, text=f"Weekly Usage: {usage_str} minutes").pack()
        
        # Productivity trends
        prod_frame = ttk.LabelFrame(trends_frame, text="Productivity Trends", padding="15")
        prod_frame.pack(fill='x', padx=10, pady=5)
        
        prod_data = [random.randint(60, 95) for _ in range(7)]
        prod_str = " → ".join([str(x) for x in prod_data])
        ttk.Label(prod_frame, text=f"Weekly Productivity: {prod_str}%").pack()
    
    def create_simple_focus_display(self, parent, user_data: Dict):
        """Create simple focus display"""
        focus_frame = ttk.Frame(parent)
        focus_frame.pack(fill='both', expand=True)
        
        # Focus session list
        sessions_frame = ttk.LabelFrame(focus_frame, text="Recent Focus Sessions", padding="15")
        sessions_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create listbox
        listbox = tk.Listbox(sessions_frame, font=('Arial', 11))
        listbox.pack(fill='both', expand=True)
        
        # Add sample sessions
        sessions = [
            "09:00 - 45min - 92% productivity",
            "10:30 - 60min - 88% productivity",
            "14:00 - 30min - 85% productivity",
            "16:00 - 75min - 94% productivity"
        ]
        
        for session in sessions:
            listbox.insert(tk.END, session)
    
    def create_simple_achievements_display(self, parent, user_data: Dict):
        """Create simple achievements display"""
        achievements_frame = ttk.Frame(parent)
        achievements_frame.pack(fill='both', expand=True)
        
        # Achievement categories
        categories = [
            ("🔥 Streak Achievements", ["Getting Started", "Week Warrior", "Month Master"]),
            ("📉 Usage Reduction", ["Half Time Hero", "Quarter Master"]),
            ("🎯 Focus Achievements", ["First Focus", "Focus Marathon", "Focus Champion"]),
            ("📊 Productivity", ["Productivity Pro", "Perfect Week"])
        ]
        
        for category, achievements in categories:
            cat_frame = ttk.LabelFrame(achievements_frame, text=category, padding="15")
            cat_frame.pack(fill='x', padx=10, pady=5)
            
            for achievement in achievements:
                status = "✅" if random.choice([True, False]) else "🔒"
                ttk.Label(cat_frame, text=f"{status} {achievement}").pack(anchor='w')
    
    def create_real_time_chart(self, parent, data_callback):
        """Create real-time updating chart"""
        if not MATPLOTLIB_AVAILABLE:
            return self.create_simple_real_time_display(parent)
        
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Initialize data
        x_data = []
        y_data = []
        line, = ax.plot(x_data, y_data, 'b-', linewidth=2)
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Usage (minutes)')
        ax.set_title('Real-time Usage Tracking')
        ax.grid(True, alpha=0.3)
        
        def animate(frame):
            # Get new data
            new_data = data_callback()
            if new_data:
                x_data.append(len(x_data))
                y_data.append(new_data)
                
                # Keep only last 50 points
                if len(x_data) > 50:
                    x_data.pop(0)
                    y_data.pop(0)
                
                line.set_data(x_data, y_data)
                ax.relim()
                ax.autoscale_view()
            
            return line,
        
        # Create animation
        ani = animation.FuncAnimation(fig, animate, interval=1000, blit=True)
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        return ani
    
    def create_simple_real_time_display(self, parent):
        """Create simple real-time display without matplotlib"""
        real_time_frame = ttk.LabelFrame(parent, text="Real-time Usage", padding="15")
        real_time_frame.pack(fill='both', expand=True)
        
        # Current usage label
        self.current_usage_label = ttk.Label(
            real_time_frame,
            text="Current Usage: 0 minutes",
            font=('Arial', 16, 'bold')
        )
        self.current_usage_label.pack(pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            real_time_frame,
            variable=self.progress_var,
            maximum=120,
            length=400
        )
        self.progress_bar.pack(pady=10)
        
        # Update function
        def update_display():
            current_usage = random.randint(0, 120)
            self.current_usage_label.config(text=f"Current Usage: {current_usage} minutes")
            self.progress_var.set(current_usage)
            parent.after(2000, update_display)
        
        update_display()

class InteractiveDashboard:
    """Interactive dashboard with real-time updates"""
    
    def __init__(self, parent):
        self.parent = parent
        self.visualization = AdvancedVisualization()
        self.update_interval = 5000  # 5 seconds
        self.dashboard_running = False
    
    def create_dashboard(self, user_data: Dict) -> tk.Frame:
        """Create interactive dashboard"""
        dashboard_frame = ttk.Frame(self.parent)
        dashboard_frame.pack(fill='both', expand=True)
        
        # Control panel
        control_frame = ttk.Frame(dashboard_frame)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=lambda: self.refresh_dashboard(user_data)
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="⏸️ Pause Updates",
            command=self.toggle_updates
        ).pack(side='left', padx=(0, 10))
        
        # Create visualization
        self.viz_frame = self.visualization.create_interactive_dashboard(dashboard_frame, user_data)
        
        # Start real-time updates
        self.start_real_time_updates(user_data)
        
        return dashboard_frame
    
    def refresh_dashboard(self, user_data: Dict):
        """Refresh dashboard with new data"""
        # Clear existing visualization
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        # Recreate visualization
        self.visualization.create_interactive_dashboard(self.viz_frame, user_data)
    
    def toggle_updates(self):
        """Toggle real-time updates"""
        if self.dashboard_running:
            self.dashboard_running = False
        else:
            self.dashboard_running = True
            self.start_real_time_updates({})
    
    def start_real_time_updates(self, user_data: Dict):
        """Start real-time dashboard updates"""
        self.dashboard_running = True
        
        def update_loop():
            if self.dashboard_running:
                # Update user data with new values
                updated_data = self.generate_updated_data(user_data)
                self.refresh_dashboard(updated_data)
                self.parent.after(self.update_interval, update_loop)
        
        update_loop()
    
    def generate_updated_data(self, user_data: Dict) -> Dict:
        """Generate updated user data for real-time simulation"""
        updated_data = user_data.copy()
        
        # Simulate real-time updates
        updated_data['usage_time'] = user_data.get('usage_time', 0) + random.randint(1, 3)
        updated_data['productivity_score'] = max(60, min(95, user_data.get('productivity_score', 70) + random.randint(-2, 2)))
        
        return updated_data

# Example usage
if __name__ == "__main__":
    # Sample user data
    user_data = {
        'usage_time': 95,
        'productivity_score': 78,
        'focus_sessions': 3,
        'streak_days': 5,
        'achievements_unlocked': 6,
        'total_focus_sessions': 25,
        'avg_focus_duration': 45,
        'best_focus_score': 94
    }
    
    # Create visualization
    viz = AdvancedVisualization()
    
    print("Advanced Visualization module loaded successfully!")
    print(f"Matplotlib available: {MATPLOTLIB_AVAILABLE}")
    print(f"Seaborn available: {SEABORN_AVAILABLE}") 