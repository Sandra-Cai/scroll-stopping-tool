#!/usr/bin/env python3
"""
Live Demonstration - Enhanced Scroll Stopping Tool
Real-time demonstration of all advanced features working together.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
import threading
from datetime import datetime, timedelta
import random
import sys

class LiveDemonstration:
    """Live demonstration of the enhanced scroll stopping tool"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Enhanced Scroll Stopping Tool - Live Demonstration")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # Demo state
        self.demo_running = False
        self.current_feature = 0
        self.live_data = self._initialize_live_data()
        
        self.create_demo_interface()
        self.start_live_demo()
    
    def _initialize_live_data(self):
        """Initialize live demonstration data"""
        return {
            'usage_time': 0,
            'productivity_score': 85,
            'focus_sessions': 0,
            'breaks_taken': 0,
            'streak_days': 5,
            'level': 3,
            'experience': 1250,
            'achievements_unlocked': 0,
            'predictions': {
                'usage_tomorrow': 78,
                'productivity_tomorrow': 89,
                'confidence': 0.82
            },
            'insights': [
                "You're most productive between 9-11 AM",
                "Consider taking breaks every 45 minutes",
                "Your usage has decreased by 25% this week!"
            ]
        }
    
    def create_demo_interface(self):
        """Create the live demonstration interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="🚀 Enhanced Scroll Stopping Tool - Live Demonstration",
            font=('Arial', 24, 'bold')
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Watch all advanced features work together in real-time",
            font=('Arial', 12),
            foreground='#6c757d'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(
            control_frame,
            text="⏸️ Pause Demo",
            command=self.toggle_demo
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="🔄 Restart",
            command=self.restart_demo
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="🚀 Launch Real App",
            command=self.launch_real_app
        ).pack(side='right')
        
        # Main demo area
        self.demo_frame = ttk.Frame(main_frame)
        self.demo_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Status bar
        self.status_label = ttk.Label(
            main_frame,
            text="🎬 Live demonstration starting...",
            font=('Arial', 12),
            foreground='#6c757d'
        )
        self.status_label.pack(pady=(10, 0))
    
    def start_live_demo(self):
        """Start the live demonstration"""
        self.demo_running = True
        self.current_feature = 0
        self.run_live_demo()
    
    def run_live_demo(self):
        """Run the live demonstration"""
        if not self.demo_running:
            return
        
        # Update live data
        self.update_live_data()
        
        # Show current feature
        features = [
            self.show_main_dashboard,
            self.show_ml_predictions,
            self.show_gamification,
            self.show_analytics,
            self.show_focus_mode,
            self.show_achievements,
            self.show_smart_insights,
            self.show_productivity_coaching
        ]
        
        if self.current_feature < len(features):
            features[self.current_feature]()
            self.current_feature += 1
            self.root.after(12000, self.run_live_demo)  # 12 seconds per feature
        else:
            self.current_feature = 0
            self.root.after(3000, self.run_live_demo)  # Restart after 3 seconds
    
    def update_live_data(self):
        """Update live demonstration data"""
        # Simulate real-time data updates
        self.live_data['usage_time'] += random.randint(1, 3)
        self.live_data['productivity_score'] = max(60, min(95, self.live_data['productivity_score'] + random.randint(-2, 2)))
        
        # Random events
        if random.random() < 0.1:  # 10% chance
            self.live_data['focus_sessions'] += 1
        if random.random() < 0.15:  # 15% chance
            self.live_data['breaks_taken'] += 1
        if random.random() < 0.05:  # 5% chance
            self.live_data['achievements_unlocked'] += 1
            self.live_data['experience'] += 50
    
    def show_main_dashboard(self):
        """Show live main dashboard"""
        self.clear_demo()
        self.update_status("🏠 Live Main Dashboard - Real-time tracking and controls")
        
        # Title
        title_label = ttk.Label(
            self.demo_frame,
            text="🏠 Live Main Dashboard",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Live stats
        stats_frame = ttk.Frame(self.demo_frame)
        stats_frame.pack(fill='both', expand=True)
        
        # Today's live stats
        today_frame = ttk.LabelFrame(stats_frame, text="📊 Live Statistics", padding="20")
        today_frame.pack(fill='x', pady=(0, 20))
        
        # Stats grid
        for i in range(4):
            today_frame.columnconfigure(i, weight=1)
        
        # Live data labels
        self.usage_label = ttk.Label(today_frame, text=f"⏱️ {self.live_data['usage_time']} min", font=('Arial', 16, 'bold'))
        self.usage_label.grid(row=0, column=0, pady=5)
        
        self.productivity_label = ttk.Label(today_frame, text=f"🎯 {self.live_data['productivity_score']}%", font=('Arial', 16, 'bold'))
        self.productivity_label.grid(row=0, column=1, pady=5)
        
        self.focus_label = ttk.Label(today_frame, text=f"🎯 {self.live_data['focus_sessions']} sessions", font=('Arial', 16, 'bold'))
        self.focus_label.grid(row=0, column=2, pady=5)
        
        self.breaks_label = ttk.Label(today_frame, text=f"☕ {self.live_data['breaks_taken']} breaks", font=('Arial', 16, 'bold'))
        self.breaks_label.grid(row=0, column=3, pady=5)
        
        # Live progress bar
        progress_var = tk.DoubleVar(value=(self.live_data['usage_time'] / 120) * 100)
        self.progress_bar = ttk.Progressbar(
            today_frame,
            variable=progress_var,
            maximum=100,
            length=600,
            style='success.Horizontal.TProgressbar'
        )
        self.progress_bar.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        
        self.progress_label = ttk.Label(today_frame, text=f"Daily Limit Progress: {self.live_data['usage_time']}/120 minutes")
        self.progress_label.grid(row=2, column=0, columnspan=4)
        
        # Live updates
        self.update_live_display()
        
        # Quick actions
        actions_frame = ttk.LabelFrame(stats_frame, text="⚡ Quick Actions", padding="20")
        actions_frame.pack(fill='x')
        
        actions = [
            ("🎯 Start Focus Mode", "Begin a distraction-free work session"),
            ("☕ Take Break", "Take a scheduled break"),
            ("📊 View Analytics", "See detailed insights"),
            ("🏆 Check Achievements", "View your progress")
        ]
        
        for i, (action, desc) in enumerate(actions):
            action_frame = ttk.Frame(actions_frame)
            action_frame.grid(row=0, column=i, padx=10)
            
            ttk.Label(action_frame, text=action, font=('Arial', 12, 'bold')).pack()
            ttk.Label(action_frame, text=desc, font=('Arial', 10), foreground='#6c757d').pack()
    
    def show_ml_predictions(self):
        """Show live ML predictions"""
        self.clear_demo()
        self.update_status("🤖 Live Machine Learning Predictions - AI-powered insights")
        
        # Title
        title_label = ttk.Label(
            self.demo_frame,
            text="🤖 Live Machine Learning Predictions",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # ML content
        ml_frame = ttk.Frame(self.demo_frame)
        ml_frame.pack(fill='both', expand=True)
        
        # Live predictions
        predictions_frame = ttk.LabelFrame(ml_frame, text="🔮 Live Predictions", padding="20")
        predictions_frame.pack(fill='x', pady=(0, 20))
        
        # Update predictions based on current data
        self.live_data['predictions']['usage_tomorrow'] = max(60, min(120, self.live_data['predictions']['usage_tomorrow'] + random.randint(-5, 5)))
        self.live_data['predictions']['productivity_tomorrow'] = max(70, min(95, self.live_data['predictions']['productivity_tomorrow'] + random.randint(-3, 3)))
        
        predictions = [
            ("Usage Tomorrow", f"{self.live_data['predictions']['usage_tomorrow']} minutes", f"{self.live_data['predictions']['confidence']:.1%}"),
            ("Productivity Score", f"{self.live_data['predictions']['productivity_tomorrow']}%", f"{self.live_data['predictions']['confidence']:.1%}"),
            ("Optimal Focus Time", "10:00 AM", "85%"),
            ("Break Interval", "45 minutes", "79%")
        ]
        
        for i, (metric, value, confidence) in enumerate(predictions):
            pred_frame = ttk.Frame(predictions_frame)
            pred_frame.pack(fill='x', pady=5)
            
            ttk.Label(pred_frame, text=f"📊 {metric}:", font=('Arial', 12, 'bold')).pack(side='left')
            ttk.Label(pred_frame, text=f" {value}", font=('Arial', 12)).pack(side='left')
            ttk.Label(pred_frame, text=f" ({confidence})", font=('Arial', 11), foreground='#6c757d').pack(side='left')
        
        # Live ML benefits
        benefits_frame = ttk.LabelFrame(ml_frame, text="💡 How ML Enhances Your Experience", padding="20")
        benefits_frame.pack(fill='x')
        
        benefits = [
            "🎯 Personalized predictions based on your behavior patterns",
            "📈 Trend analysis to identify improvement opportunities",
            "⏰ Optimal scheduling recommendations for peak productivity",
            "🔍 Pattern recognition for better self-awareness"
        ]
        
        for benefit in benefits:
            ttk.Label(benefits_frame, text=benefit, font=('Arial', 11)).pack(anchor='w', pady=2)
    
    def show_gamification(self):
        """Show live gamification"""
        self.clear_demo()
        self.update_status("🏆 Live Gamification System - Motivation through achievements")
        
        # Title
        title_label = ttk.Label(
            self.demo_frame,
            text="🏆 Live Gamification System",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Gamification content
        gamification_frame = ttk.Frame(self.demo_frame)
        gamification_frame.pack(fill='both', expand=True)
        
        # Live user progress
        progress_frame = ttk.LabelFrame(gamification_frame, text="👤 Live Progress", padding="20")
        progress_frame.pack(fill='x', pady=(0, 20))
        
        # Progress grid
        for i in range(4):
            progress_frame.columnconfigure(i, weight=1)
        
        progress_data = [
            ("Level", str(self.live_data['level']), "🔥"),
            ("Experience", f"{self.live_data['experience']} XP", "📈"),
            ("Streak", f"{self.live_data['streak_days']} days", "🔥"),
            ("Achievements", f"{self.live_data['achievements_unlocked']}/20", "🏆")
        ]
        
        for i, (label, value, icon) in enumerate(progress_data):
            ttk.Label(progress_frame, text=f"{icon} {label}", font=('Arial', 12, 'bold')).grid(row=0, column=i, pady=5)
            ttk.Label(progress_frame, text=value, font=('Arial', 16, 'bold')).grid(row=1, column=i, pady=5)
        
        # Live achievements
        achievements_frame = ttk.LabelFrame(gamification_frame, text="🏅 Recent Achievements", padding="20")
        achievements_frame.pack(fill='x', pady=(0, 20))
        
        achievements = [
            "✅ Getting Started - 3 day streak",
            "✅ Week Warrior - 7 day streak",
            "✅ Productivity Pro - 90% score",
            "🔒 Focus Marathon - 75% progress"
        ]
        
        for achievement in achievements:
            ttk.Label(achievements_frame, text=achievement, font=('Arial', 12)).pack(anchor='w', pady=2)
        
        # Live motivation
        motivation_frame = ttk.LabelFrame(gamification_frame, text="💪 How Gamification Motivates", padding="20")
        motivation_frame.pack(fill='x')
        
        motivations = [
            "🎯 Clear goals and progress tracking",
            "🏆 Achievement recognition and celebration",
            "🔥 Streak maintenance for consistency",
            "📈 Level progression for long-term engagement"
        ]
        
        for motivation in motivations:
            ttk.Label(motivation_frame, text=motivation, font=('Arial', 11)).pack(anchor='w', pady=2)
    
    def show_analytics(self):
        """Show live analytics"""
        self.clear_demo()
        self.update_status("📊 Live Advanced Analytics - Deep insights and trends")
        
        # Title
        title_label = ttk.Label(
            self.demo_frame,
            text="📊 Live Advanced Analytics",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Analytics content
        analytics_frame = ttk.Frame(self.demo_frame)
        analytics_frame.pack(fill='both', expand=True)
        
        # Live weekly trends
        trends_frame = ttk.LabelFrame(analytics_frame, text="📈 Live Weekly Trends", padding="20")
        trends_frame.pack(fill='x', pady=(0, 20))
        
        # Generate live trend data
        usage_trend = [random.randint(70, 150) for _ in range(7)]
        productivity_trend = [random.randint(65, 95) for _ in range(7)]
        
        # Usage trend
        usage_frame = ttk.Frame(trends_frame)
        usage_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(usage_frame, text="📊 Usage Trend (minutes):", font=('Arial', 12, 'bold')).pack(anchor='w')
        usage_str = " → ".join([str(x) for x in usage_trend])
        ttk.Label(usage_frame, text=usage_str, font=('Arial', 11)).pack(anchor='w')
        
        # Productivity trend
        prod_frame = ttk.Frame(trends_frame)
        prod_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(prod_frame, text="🎯 Productivity Trend (%):", font=('Arial', 12, 'bold')).pack(anchor='w')
        prod_str = " → ".join([str(x) for x in productivity_trend])
        ttk.Label(prod_frame, text=prod_str, font=('Arial', 11)).pack(anchor='w')
        
        # Live focus sessions
        focus_frame = ttk.LabelFrame(analytics_frame, text="🎯 Live Focus Sessions", padding="20")
        focus_frame.pack(fill='x', pady=(0, 20))
        
        sessions = [
            f"09:00 - {random.randint(30, 90)}min - {random.randint(75, 95)}% productivity",
            f"10:30 - {random.randint(30, 90)}min - {random.randint(75, 95)}% productivity",
            f"14:00 - {random.randint(30, 90)}min - {random.randint(75, 95)}% productivity"
        ]
        
        for session in sessions:
            ttk.Label(focus_frame, text=session, font=('Arial', 11)).pack(anchor='w', pady=2)
        
        # Live export options
        export_frame = ttk.LabelFrame(analytics_frame, text="📤 Live Export & Share", padding="20")
        export_frame.pack(fill='x')
        
        exports = [
            "📊 CSV export for detailed analysis",
            "📄 PDF reports for presentations",
            "📋 JSON backup for data portability",
            "📈 Chart images for sharing"
        ]
        
        for export in exports:
            ttk.Label(export_frame, text=export, font=('Arial', 11)).pack(anchor='w', pady=2)
    
    def show_focus_mode(self):
        """Show live focus mode"""
        self.clear_demo()
        self.update_status("🎯 Live Focus Mode - Distraction-free productivity")
        
        # Title
        title_label = ttk.Label(
            self.demo_frame,
            text="🎯 Live Focus Mode",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Focus mode content
        focus_frame = ttk.Frame(self.demo_frame)
        focus_frame.pack(fill='both', expand=True)
        
        # Live session
        session_frame = ttk.LabelFrame(focus_frame, text="⏱️ Live Focus Session", padding="20")
        session_frame.pack(fill='x', pady=(0, 20))
        
        # Simulate live session data
        session_duration = random.randint(30, 90)
        time_remaining = random.randint(5, 30)
        productivity = random.randint(75, 95)
        interruptions = random.randint(0, 3)
        
        session_info = [
            ("Duration", f"{session_duration} minutes"),
            ("Time Remaining", f"{time_remaining} minutes"),
            ("Productivity Score", f"{productivity}%"),
            ("Interruptions", str(interruptions)),
            ("Status", "Active")
        ]
        
        for label, value in session_info:
            info_frame = ttk.Frame(session_frame)
            info_frame.pack(fill='x', pady=2)
            ttk.Label(info_frame, text=f"{label}:", font=('Arial', 12, 'bold')).pack(side='left')
            ttk.Label(info_frame, text=f" {value}", font=('Arial', 12)).pack(side='left')
        
        # Live progress bar
        progress_var = tk.DoubleVar(value=((session_duration - time_remaining) / session_duration) * 100)
        progress_bar = ttk.Progressbar(
            session_frame,
            variable=progress_var,
            maximum=100,
            length=500,
            style='success.Horizontal.TProgressbar'
        )
        progress_bar.pack(pady=(10, 0))
        
        # Live focus features
        features_frame = ttk.LabelFrame(focus_frame, text="🔧 Live Focus Features", padding="20")
        features_frame.pack(fill='x', pady=(0, 20))
        
        features = [
            "🔒 Screen locking during focus sessions",
            "🔕 Automatic notification blocking",
            "📊 Real-time productivity tracking",
            "⏰ Smart break reminders",
            "🎵 Optional background music",
            "📝 Session notes and reflection"
        ]
        
        for feature in features:
            ttk.Label(features_frame, text=feature, font=('Arial', 11)).pack(anchor='w', pady=2)
        
        # Live benefits
        benefits_frame = ttk.LabelFrame(focus_frame, text="💡 Live Focus Mode Benefits", padding="20")
        benefits_frame.pack(fill='x')
        
        benefits = [
            "🎯 Eliminates distractions for deep work",
            "📈 Improves productivity and concentration",
            "⏰ Structured time management",
            "📊 Measurable progress tracking"
        ]
        
        for benefit in benefits:
            ttk.Label(benefits_frame, text=benefit, font=('Arial', 11)).pack(anchor='w', pady=2)
    
    def show_achievements(self):
        """Show live achievements"""
        self.clear_demo()
        self.update_status("🏆 Live Achievement System - Progress tracking and motivation")
        
        # Title
        title_label = ttk.Label(
            self.demo_frame,
            text="🏆 Live Achievement System",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Achievements content
        achievements_frame = ttk.Frame(self.demo_frame)
        achievements_frame.pack(fill='both', expand=True)
        
        # Live achievement categories
        categories = [
            ("🔥 Streak Achievements", [
                "Getting Started - 3 day streak",
                "Week Warrior - 7 day streak",
                "Month Master - 30 day streak"
            ]),
            ("📉 Usage Reduction", [
                "Half Time Hero - 50% reduction",
                "Quarter Master - 75% reduction"
            ]),
            ("🎯 Focus Achievements", [
                "First Focus - Complete first session",
                "Focus Marathon - 90 minute session",
                "Focus Champion - 50 sessions"
            ]),
            ("📊 Productivity", [
                "Productivity Pro - 90% score",
                "Perfect Week - All goals met"
            ])
        ]
        
        for category, achievements in categories:
            cat_frame = ttk.LabelFrame(achievements_frame, text=category, padding="15")
            cat_frame.pack(fill='x', pady=(0, 10))
            
            for achievement in achievements:
                ttk.Label(cat_frame, text=f"🏆 {achievement}", font=('Arial', 11)).pack(anchor='w', pady=1)
        
        # Live progress tracking
        progress_frame = ttk.LabelFrame(achievements_frame, text="📈 Live Progress Tracking", padding="20")
        progress_frame.pack(fill='x')
        
        ttk.Label(progress_frame, text="Track your progress with detailed statistics:", font=('Arial', 12, 'bold')).pack(anchor='w')
        ttk.Label(progress_frame, text="• Achievement completion rates").pack(anchor='w')
        ttk.Label(progress_frame, text="• Time to unlock achievements").pack(anchor='w')
        ttk.Label(progress_frame, text="• Comparison with previous periods").pack(anchor='w')
    
    def show_smart_insights(self):
        """Show live smart insights"""
        self.clear_demo()
        self.update_status("💡 Live Smart Insights - AI-powered recommendations")
        
        # Title
        title_label = ttk.Label(
            self.demo_frame,
            text="💡 Live Smart Insights",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Insights content
        insights_frame = ttk.Frame(self.demo_frame)
        insights_frame.pack(fill='both', expand=True)
        
        # Live insights
        live_insights = [
            {
                'type': 'pattern',
                'message': 'You\'re most productive between 9-11 AM',
                'confidence': 0.88,
                'action_items': ['Schedule important tasks during this time', 'Avoid meetings in this window']
            },
            {
                'type': 'improvement',
                'message': f'Your usage has decreased by {random.randint(20, 30)}% this week!',
                'confidence': 0.92,
                'action_items': ['Keep up the great work!', 'Consider setting a new goal']
            },
            {
                'type': 'suggestion',
                'message': 'Try taking breaks every 45 minutes for better focus',
                'confidence': 0.76,
                'action_items': ['Set break reminders', 'Use the Pomodoro technique']
            }
        ]
        
        for i, insight in enumerate(live_insights):
            insight_frame = ttk.LabelFrame(insights_frame, text=f"Live Insight {i+1}", padding="20")
            insight_frame.pack(fill='x', pady=(0, 15))
            
            # Icon based on type
            icon_map = {'pattern': '🔍', 'suggestion': '💡', 'achievement': '🏆', 'improvement': '📈'}
            icon = icon_map.get(insight['type'], '💡')
            
            ttk.Label(insight_frame, text=f"{icon} {insight['message']}", font=('Arial', 14, 'bold')).pack(anchor='w')
            ttk.Label(insight_frame, text=f"Confidence: {insight['confidence']:.1%}", font=('Arial', 11), foreground='#6c757d').pack(anchor='w')
            
            # Action items
            if insight['action_items']:
                ttk.Label(insight_frame, text="Action Items:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
                for item in insight['action_items']:
                    ttk.Label(insight_frame, text=f"• {item}", font=('Arial', 11)).pack(anchor='w', padx=(20, 0))
        
        # Live benefits
        benefits_frame = ttk.LabelFrame(insights_frame, text="🎯 How Live Smart Insights Help", padding="20")
        benefits_frame.pack(fill='x')
        
        benefits = [
            "• Personalized recommendations based on your behavior",
            "• Early warning system for productivity issues",
            "• Celebration of your achievements and progress",
            "• Actionable insights to improve your routine"
        ]
        
        for benefit in benefits:
            ttk.Label(benefits_frame, text=benefit, font=('Arial', 11)).pack(anchor='w', pady=2)
    
    def show_productivity_coaching(self):
        """Show live productivity coaching"""
        self.clear_demo()
        self.update_status("🎓 Live Productivity Coaching - AI-powered guidance")
        
        # Title
        title_label = ttk.Label(
            self.demo_frame,
            text="🎓 Live Productivity Coaching",
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Coaching content
        coaching_frame = ttk.Frame(self.demo_frame)
        coaching_frame.pack(fill='both', expand=True)
        
        # Live adaptive goals
        goals_frame = ttk.LabelFrame(coaching_frame, text="🎯 Live Adaptive Goals", padding="20")
        goals_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(goals_frame, text="Goals that adapt to your performance:", font=('Arial', 12, 'bold')).pack(anchor='w')
        ttk.Label(goals_frame, text="• Increase difficulty when you're succeeding").pack(anchor='w')
        ttk.Label(goals_frame, text="• Reduce difficulty when you're struggling").pack(anchor='w')
        ttk.Label(goals_frame, text="• Personalized based on your patterns").pack(anchor='w')
        
        # Live smart recommendations
        rec_frame = ttk.LabelFrame(coaching_frame, text="💡 Live Smart Recommendations", padding="20")
        rec_frame.pack(fill='x', pady=(0, 20))
        
        recommendations = [
            "Schedule focus sessions during your peak productivity hours",
            "Take breaks every 45-60 minutes for optimal performance",
            f"Reduce social media usage on weekends by {random.randint(15, 25)}%",
            "Try the Pomodoro technique for better focus"
        ]
        
        for rec in recommendations:
            ttk.Label(rec_frame, text=f"• {rec}", font=('Arial', 11)).pack(anchor='w')
        
        # Live behavioral patterns
        patterns_frame = ttk.LabelFrame(coaching_frame, text="🔍 Live Behavioral Analysis", padding="20")
        patterns_frame.pack(fill='x')
        
        ttk.Label(patterns_frame, text="Understand your productivity patterns:", font=('Arial', 12, 'bold')).pack(anchor='w')
        ttk.Label(patterns_frame, text="• Peak productivity hours identification").pack(anchor='w')
        ttk.Label(patterns_frame, text="• Interruption pattern analysis").pack(anchor='w')
        ttk.Label(patterns_frame, text="• Weekly and monthly trend analysis").pack(anchor='w')
    
    def update_live_display(self):
        """Update live display elements"""
        if hasattr(self, 'usage_label'):
            self.usage_label.config(text=f"⏱️ {self.live_data['usage_time']} min")
        if hasattr(self, 'productivity_label'):
            self.productivity_label.config(text=f"🎯 {self.live_data['productivity_score']}%")
        if hasattr(self, 'focus_label'):
            self.focus_label.config(text=f"🎯 {self.live_data['focus_sessions']} sessions")
        if hasattr(self, 'breaks_label'):
            self.breaks_label.config(text=f"☕ {self.live_data['breaks_taken']} breaks")
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text=f"Daily Limit Progress: {self.live_data['usage_time']}/120 minutes")
        
        # Schedule next update
        self.root.after(2000, self.update_live_display)  # Update every 2 seconds
    
    def clear_demo(self):
        """Clear the demo area"""
        for widget in self.demo_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
    
    def toggle_demo(self):
        """Toggle demo on/off"""
        if self.demo_running:
            self.demo_running = False
            self.update_status("⏸️ Live demo paused")
        else:
            self.demo_running = True
            self.update_status("▶️ Live demo resumed")
            self.run_live_demo()
    
    def restart_demo(self):
        """Restart the demo"""
        self.current_feature = 0
        self.demo_running = True
        self.update_status("🔄 Live demo restarted")
        self.run_live_demo()
    
    def launch_real_app(self):
        """Launch the real application"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, "scroll_stopping_tool_enhanced.py"])
            messagebox.showinfo("Launch", "Enhanced Scroll Stopping Tool is launching!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch application: {e}")
    
    def run(self):
        """Run the live demonstration"""
        self.root.mainloop()

def main():
    """Main live demonstration function"""
    print("🚀 Starting Live Demonstration...")
    demo = LiveDemonstration()
    demo.run()

if __name__ == "__main__":
    main() 