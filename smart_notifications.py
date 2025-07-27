#!/usr/bin/env python3
"""
Smart Notifications Module for Enhanced Scroll Stopping Tool
Intelligent timing, personalized messages, and multiple notification channels.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import random
import queue

logger = logging.getLogger(__name__)

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationType(Enum):
    """Notification types"""
    BREAK_REMINDER = "break_reminder"
    USAGE_LIMIT = "usage_limit"
    FOCUS_START = "focus_start"
    FOCUS_END = "focus_end"
    ACHIEVEMENT = "achievement"
    MOTIVATION = "motivation"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    PRODUCTIVITY_TIP = "productivity_tip"
    STREAK_REMINDER = "streak_reminder"

class NotificationChannel(Enum):
    """Notification channels"""
    DESKTOP = "desktop"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SOUND = "sound"
    VISUAL = "visual"

@dataclass
class Notification:
    """Notification data structure"""
    id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    timestamp: datetime
    expires_at: Optional[datetime] = None
    user_data: Optional[Dict] = None
    action_required: bool = False
    dismissed: bool = False

class SmartNotificationEngine:
    """Smart notification engine with intelligent timing and personalization"""
    
    def __init__(self):
        self.notifications = []
        self.notification_queue = queue.Queue()
        self.user_preferences = {}
        self.notification_history = []
        self.smart_timing = SmartTiming()
        self.personalization = NotificationPersonalization()
        self.channel_manager = NotificationChannelManager()
        
        # Start notification processing thread
        self.processing_thread = threading.Thread(target=self._process_notifications, daemon=True)
        self.processing_thread.start()
    
    def set_user_preferences(self, preferences: Dict):
        """Set user notification preferences"""
        self.user_preferences = preferences
        logger.info("User notification preferences updated")
    
    def create_notification(self, notification_type: NotificationType, user_data: Dict, 
                          custom_message: Optional[str] = None) -> Notification:
        """Create a smart notification"""
        # Generate notification content
        title, message = self.personalization.generate_notification_content(
            notification_type, user_data, custom_message
        )
        
        # Determine priority
        priority = self._determine_priority(notification_type, user_data)
        
        # Determine channels
        channels = self._determine_channels(notification_type, priority)
        
        # Determine timing
        timestamp = self.smart_timing.get_optimal_timing(notification_type, user_data)
        
        # Create notification
        notification = Notification(
            id=f"{notification_type.value}_{int(time.time())}",
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
            channels=channels,
            timestamp=timestamp,
            user_data=user_data,
            action_required=self._requires_action(notification_type)
        )
        
        # Add to queue
        self.notification_queue.put(notification)
        
        return notification
    
    def _determine_priority(self, notification_type: NotificationType, user_data: Dict) -> NotificationPriority:
        """Determine notification priority based on type and user data"""
        priority_map = {
            NotificationType.USAGE_LIMIT: NotificationPriority.HIGH,
            NotificationType.FOCUS_START: NotificationPriority.MEDIUM,
            NotificationType.FOCUS_END: NotificationPriority.MEDIUM,
            NotificationType.ACHIEVEMENT: NotificationPriority.MEDIUM,
            NotificationType.BREAK_REMINDER: NotificationPriority.LOW,
            NotificationType.MOTIVATION: NotificationPriority.LOW,
            NotificationType.DAILY_SUMMARY: NotificationPriority.LOW,
            NotificationType.WEEKLY_REPORT: NotificationPriority.LOW,
            NotificationType.PRODUCTIVITY_TIP: NotificationPriority.LOW,
            NotificationType.STREAK_REMINDER: NotificationPriority.MEDIUM
        }
        
        base_priority = priority_map.get(notification_type, NotificationPriority.MEDIUM)
        
        # Adjust priority based on user data
        if notification_type == NotificationType.USAGE_LIMIT:
            usage_time = user_data.get('usage_time', 0)
            if usage_time > 150:
                return NotificationPriority.URGENT
            elif usage_time > 120:
                return NotificationPriority.HIGH
        
        return base_priority
    
    def _determine_channels(self, notification_type: NotificationType, priority: NotificationPriority) -> List[NotificationChannel]:
        """Determine notification channels based on type and priority"""
        # Base channels for each priority
        base_channels = {
            NotificationPriority.LOW: [NotificationChannel.DESKTOP],
            NotificationPriority.MEDIUM: [NotificationChannel.DESKTOP, NotificationChannel.SOUND],
            NotificationPriority.HIGH: [NotificationChannel.DESKTOP, NotificationChannel.SOUND, NotificationChannel.VISUAL],
            NotificationPriority.URGENT: [NotificationChannel.DESKTOP, NotificationChannel.SOUND, NotificationChannel.VISUAL, NotificationChannel.EMAIL]
        }
        
        channels = base_channels.get(priority, [NotificationChannel.DESKTOP])
        
        # Add type-specific channels
        if notification_type == NotificationType.ACHIEVEMENT:
            channels.append(NotificationChannel.PUSH)
        elif notification_type == NotificationType.WEEKLY_REPORT:
            channels.append(NotificationChannel.EMAIL)
        
        return channels
    
    def _requires_action(self, notification_type: NotificationType) -> bool:
        """Determine if notification requires user action"""
        action_required_types = [
            NotificationType.FOCUS_START,
            NotificationType.FOCUS_END,
            NotificationType.USAGE_LIMIT
        ]
        
        return notification_type in action_required_types
    
    def _process_notifications(self):
        """Process notifications in background thread"""
        while True:
            try:
                notification = self.notification_queue.get(timeout=1)
                
                # Check if notification should be sent now
                if datetime.now() >= notification.timestamp:
                    self._send_notification(notification)
                else:
                    # Re-queue for later
                    time.sleep((notification.timestamp - datetime.now()).total_seconds())
                    self.notification_queue.put(notification)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing notification: {e}")
    
    def _send_notification(self, notification: Notification):
        """Send notification through specified channels"""
        try:
            # Send through each channel
            for channel in notification.channels:
                self.channel_manager.send_notification(notification, channel)
            
            # Add to history
            self.notification_history.append(notification)
            
            # Keep only last 100 notifications
            if len(self.notification_history) > 100:
                self.notification_history = self.notification_history[-100:]
            
            logger.info(f"Notification sent: {notification.title}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    def get_notification_history(self) -> List[Notification]:
        """Get notification history"""
        return self.notification_history
    
    def dismiss_notification(self, notification_id: str):
        """Dismiss a notification"""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.dismissed = True
                break
    
    def create_smart_reminder(self, user_data: Dict) -> Notification:
        """Create a smart reminder based on user behavior"""
        # Analyze user behavior to determine best reminder type
        usage_time = user_data.get('usage_time', 0)
        productivity_score = user_data.get('productivity_score', 70)
        streak_days = user_data.get('streak_days', 0)
        
        if usage_time > 120:
            return self.create_notification(NotificationType.USAGE_LIMIT, user_data)
        elif productivity_score < 60:
            return self.create_notification(NotificationType.MOTIVATION, user_data)
        elif streak_days > 0 and streak_days % 7 == 0:
            return self.create_notification(NotificationType.STREAK_REMINDER, user_data)
        else:
            return self.create_notification(NotificationType.BREAK_REMINDER, user_data)

class SmartTiming:
    """Smart timing for notifications"""
    
    def __init__(self):
        self.user_patterns = {}
        self.optimal_times = {}
    
    def get_optimal_timing(self, notification_type: NotificationType, user_data: Dict) -> datetime:
        """Get optimal timing for notification"""
        now = datetime.now()
        
        # Type-specific timing
        if notification_type == NotificationType.BREAK_REMINDER:
            return self._get_break_timing(user_data)
        elif notification_type == NotificationType.USAGE_LIMIT:
            return now  # Immediate
        elif notification_type == NotificationType.FOCUS_START:
            return self._get_focus_start_timing(user_data)
        elif notification_type == NotificationType.MOTIVATION:
            return self._get_motivation_timing(user_data)
        else:
            return now
    
    def _get_break_timing(self, user_data: Dict) -> datetime:
        """Get optimal break timing"""
        now = datetime.now()
        usage_time = user_data.get('usage_time', 0)
        
        # Suggest break every 45-60 minutes
        if usage_time >= 45 and usage_time % 45 == 0:
            return now
        
        # Default: suggest break in 15 minutes
        return now + timedelta(minutes=15)
    
    def _get_focus_start_timing(self, user_data: Dict) -> datetime:
        """Get optimal focus start timing"""
        now = datetime.now()
        hour = now.hour
        
        # Optimal focus hours: 9-11 AM, 2-4 PM
        if 9 <= hour <= 11 or 14 <= hour <= 16:
            return now
        else:
            # Suggest focus session in next optimal hour
            if hour < 9:
                return now.replace(hour=9, minute=0, second=0, microsecond=0)
            elif 11 < hour < 14:
                return now.replace(hour=14, minute=0, second=0, microsecond=0)
            else:
                return now + timedelta(hours=1)
    
    def _get_motivation_timing(self, user_data: Dict) -> datetime:
        """Get optimal motivation timing"""
        now = datetime.now()
        productivity_score = user_data.get('productivity_score', 70)
        
        # Send motivation when productivity is low
        if productivity_score < 60:
            return now
        else:
            # Send motivation in 30 minutes
            return now + timedelta(minutes=30)

class NotificationPersonalization:
    """Personalize notification content"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.user_tone = "supportive"
    
    def _load_templates(self) -> Dict:
        """Load notification templates"""
        return {
            NotificationType.BREAK_REMINDER: {
                "titles": [
                    "Time for a break! ☕",
                    "Take a moment to recharge ⚡",
                    "Break time - you've earned it! 🎉"
                ],
                "messages": [
                    "You've been working hard. Take a 5-minute break to refresh your mind.",
                    "Great work! Time to step away and come back stronger.",
                    "Your brain needs a break. Stretch, walk, or just breathe."
                ]
            },
            NotificationType.USAGE_LIMIT: {
                "titles": [
                    "Usage limit reached! ⚠️",
                    "Time to take control 🎯",
                    "Social media break needed 📱"
                ],
                "messages": [
                    "You've reached your daily social media limit. Time to focus on other activities.",
                    "Your usage is above your goal. Let's get back on track!",
                    "Social media can wait. Your productivity goals are calling!"
                ]
            },
            NotificationType.FOCUS_START: {
                "titles": [
                    "Focus mode activated! 🎯",
                    "Time to get things done! 💪",
                    "Deep work session starting 🧠"
                ],
                "messages": [
                    "Focus mode is on. Distractions are blocked. You've got this!",
                    "Your focus session is ready. Let's make the most of this time.",
                    "Time to dive deep into your work. Stay focused and productive!"
                ]
            },
            NotificationType.ACHIEVEMENT: {
                "titles": [
                    "Achievement unlocked! 🏆",
                    "Congratulations! 🎉",
                    "You did it! 🌟"
                ],
                "messages": [
                    "Amazing work! You've unlocked a new achievement.",
                    "Your hard work is paying off! Keep up the great progress.",
                    "Another milestone reached! You're on fire!"
                ]
            },
            NotificationType.MOTIVATION: {
                "titles": [
                    "You've got this! 💪",
                    "Keep pushing forward! 🚀",
                    "Believe in yourself! ✨"
                ],
                "messages": [
                    "Every small step counts. You're making progress!",
                    "Challenges make you stronger. Keep going!",
                    "Your future self will thank you for today's efforts."
                ]
            }
        }
    
    def generate_notification_content(self, notification_type: NotificationType, 
                                    user_data: Dict, custom_message: Optional[str] = None) -> Tuple[str, str]:
        """Generate personalized notification content"""
        if custom_message:
            return self._generate_custom_content(notification_type, custom_message)
        
        templates = self.templates.get(notification_type, {})
        titles = templates.get("titles", ["Notification"])
        messages = templates.get("messages", ["You have a new notification."])
        
        # Select random template
        title = random.choice(titles)
        message = random.choice(messages)
        
        # Personalize based on user data
        title = self._personalize_title(title, user_data)
        message = self._personalize_message(message, user_data)
        
        return title, message
    
    def _personalize_title(self, title: str, user_data: Dict) -> str:
        """Personalize notification title"""
        # Add user-specific elements
        streak_days = user_data.get('streak_days', 0)
        if streak_days > 0:
            title = title.replace("!", f" (Day {streak_days})!")
        
        return title
    
    def _personalize_message(self, message: str, user_data: Dict) -> str:
        """Personalize notification message"""
        # Add user-specific information
        usage_time = user_data.get('usage_time', 0)
        productivity_score = user_data.get('productivity_score', 70)
        
        if "usage" in message.lower():
            message = message.replace("your daily social media limit", f"{usage_time} minutes of usage")
        
        if "productivity" in message.lower():
            message = message.replace("productivity goals", f"your {productivity_score}% productivity goal")
        
        return message
    
    def _generate_custom_content(self, notification_type: NotificationType, custom_message: str) -> Tuple[str, str]:
        """Generate content for custom message"""
        type_titles = {
            NotificationType.BREAK_REMINDER: "Break Reminder",
            NotificationType.USAGE_LIMIT: "Usage Alert",
            NotificationType.FOCUS_START: "Focus Mode",
            NotificationType.ACHIEVEMENT: "Achievement",
            NotificationType.MOTIVATION: "Motivation"
        }
        
        title = type_titles.get(notification_type, "Notification")
        return title, custom_message

class NotificationChannelManager:
    """Manage different notification channels"""
    
    def __init__(self):
        self.channels = {}
        self._setup_channels()
    
    def _setup_channels(self):
        """Setup available notification channels"""
        # Desktop notifications
        try:
            from plyer import notification as plyer_notification
            self.channels[NotificationChannel.DESKTOP] = self._send_desktop_notification
        except ImportError:
            logger.warning("Plyer not available - desktop notifications disabled")
        
        # Sound notifications
        self.channels[NotificationChannel.SOUND] = self._send_sound_notification
        
        # Visual notifications
        self.channels[NotificationChannel.VISUAL] = self._send_visual_notification
        
        # Email notifications (placeholder)
        self.channels[NotificationChannel.EMAIL] = self._send_email_notification
        
        # Push notifications (placeholder)
        self.channels[NotificationChannel.PUSH] = self._send_push_notification
    
    def send_notification(self, notification: Notification, channel: NotificationChannel):
        """Send notification through specific channel"""
        channel_func = self.channels.get(channel)
        if channel_func:
            try:
                channel_func(notification)
            except Exception as e:
                logger.error(f"Error sending notification through {channel.value}: {e}")
        else:
            logger.warning(f"Channel {channel.value} not available")
    
    def _send_desktop_notification(self, notification: Notification):
        """Send desktop notification"""
        try:
            from plyer import notification as plyer_notification
            plyer_notification.notify(
                title=notification.title,
                message=notification.message,
                timeout=10
            )
        except Exception as e:
            logger.error(f"Desktop notification failed: {e}")
    
    def _send_sound_notification(self, notification: Notification):
        """Send sound notification"""
        try:
            import platform
            if platform.system() == "Windows":
                import winsound
                winsound.MessageBeep()
            elif platform.system() == "Darwin":  # macOS
                import os
                os.system("afplay /System/Library/Sounds/Glass.aiff")
            else:  # Linux
                import os
                os.system("paplay /usr/share/sounds/freedesktop/stereo/complete.oga")
        except Exception as e:
            logger.error(f"Sound notification failed: {e}")
    
    def _send_visual_notification(self, notification: Notification):
        """Send visual notification (flashing window, etc.)"""
        # This would be implemented in the main application
        # to flash the window or show a visual indicator
        logger.info(f"Visual notification: {notification.title}")
    
    def _send_email_notification(self, notification: Notification):
        """Send email notification"""
        # Placeholder for email notification
        logger.info(f"Email notification would be sent: {notification.title}")
    
    def _send_push_notification(self, notification: Notification):
        """Send push notification"""
        # Placeholder for push notification
        logger.info(f"Push notification would be sent: {notification.title}")

class ReminderScheduler:
    """Schedule and manage reminders"""
    
    def __init__(self, notification_engine: SmartNotificationEngine):
        self.notification_engine = notification_engine
        self.scheduled_reminders = {}
        self.reminder_thread = None
        self.running = False
    
    def start_scheduler(self):
        """Start the reminder scheduler"""
        self.running = True
        self.reminder_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.reminder_thread.start()
        logger.info("Reminder scheduler started")
    
    def stop_scheduler(self):
        """Stop the reminder scheduler"""
        self.running = False
        if self.reminder_thread:
            self.reminder_thread.join()
        logger.info("Reminder scheduler stopped")
    
    def schedule_reminder(self, reminder_type: str, user_data: Dict, 
                         interval_minutes: int = 30):
        """Schedule a recurring reminder"""
        reminder_id = f"{reminder_type}_{int(time.time())}"
        
        self.scheduled_reminders[reminder_id] = {
            'type': reminder_type,
            'user_data': user_data,
            'interval': interval_minutes,
            'last_sent': None,
            'next_send': datetime.now() + timedelta(minutes=interval_minutes)
        }
        
        logger.info(f"Reminder scheduled: {reminder_type} every {interval_minutes} minutes")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                now = datetime.now()
                
                # Check for due reminders
                for reminder_id, reminder in list(self.scheduled_reminders.items()):
                    if reminder['next_send'] <= now:
                        # Send reminder
                        self._send_scheduled_reminder(reminder)
                        
                        # Update next send time
                        reminder['last_sent'] = now
                        reminder['next_send'] = now + timedelta(minutes=reminder['interval'])
                
                # Sleep for 1 minute
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
    
    def _send_scheduled_reminder(self, reminder: Dict):
        """Send a scheduled reminder"""
        try:
            reminder_type = reminder['type']
            user_data = reminder['user_data']
            
            if reminder_type == 'break':
                self.notification_engine.create_notification(
                    NotificationType.BREAK_REMINDER, user_data
                )
            elif reminder_type == 'motivation':
                self.notification_engine.create_notification(
                    NotificationType.MOTIVATION, user_data
                )
            elif reminder_type == 'focus':
                self.notification_engine.create_notification(
                    NotificationType.FOCUS_START, user_data
                )
            
            logger.info(f"Scheduled reminder sent: {reminder_type}")
            
        except Exception as e:
            logger.error(f"Error sending scheduled reminder: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize smart notification engine
    notification_engine = SmartNotificationEngine()
    
    # Set user preferences
    preferences = {
        'desktop_notifications': True,
        'sound_notifications': True,
        'email_notifications': False,
        'quiet_hours': {'start': '22:00', 'end': '08:00'}
    }
    notification_engine.set_user_preferences(preferences)
    
    # Sample user data
    user_data = {
        'usage_time': 95,
        'productivity_score': 78,
        'streak_days': 5,
        'focus_sessions': 3
    }
    
    # Create notifications
    notification_engine.create_notification(NotificationType.BREAK_REMINDER, user_data)
    notification_engine.create_notification(NotificationType.MOTIVATION, user_data)
    
    # Create smart reminder
    smart_reminder = notification_engine.create_smart_reminder(user_data)
    
    print("Smart Notifications module loaded successfully!")
    print(f"Created {len(notification_engine.notifications)} notifications") 