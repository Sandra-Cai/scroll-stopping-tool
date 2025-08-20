#!/usr/bin/env python3
"""
Mobile Integration System
Comprehensive mobile integration for the scroll stopping tool including
mobile app support, push notifications, cross-platform sync, and mobile-specific features.
"""

import json
import time
import threading
import requests
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from enum import Enum
import sqlite3
import uuid
import hashlib
from pathlib import Path
import queue
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, messaging, firestore
import jwt
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class MobilePlatform(Enum):
    """Mobile platforms"""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    DESKTOP = "desktop"

class NotificationType(Enum):
    """Mobile notification types"""
    BREAK_REMINDER = "break_reminder"
    LIMIT_REACHED = "limit_reached"
    ACHIEVEMENT = "achievement"
    CHALLENGE = "challenge"
    GOAL_UPDATE = "goal_update"
    MOTIVATION = "motivation"
    SYSTEM = "system"

class SyncStatus(Enum):
    """Data synchronization status"""
    PENDING = "pending"
    SYNCED = "synced"
    CONFLICT = "conflict"
    ERROR = "error"

@dataclass
class MobileDevice:
    """Mobile device information"""
    device_id: str
    user_id: str
    platform: MobilePlatform
    device_token: str
    app_version: str
    os_version: str
    last_sync: datetime
    is_active: bool
    push_enabled: bool
    sync_enabled: bool

@dataclass
class MobileNotification:
    """Mobile notification definition"""
    id: str
    user_id: str
    device_id: str
    type: NotificationType
    title: str
    body: str
    data: Dict[str, Any]
    scheduled_time: datetime
    sent_time: Optional[datetime]
    is_read: bool
    action_taken: bool

@dataclass
class SyncData:
    """Data synchronization object"""
    id: str
    user_id: str
    device_id: str
    data_type: str
    data: Dict[str, Any]
    timestamp: datetime
    status: SyncStatus
    conflict_resolution: Optional[str]

class MobileIntegrationSystem:
    """Mobile integration system"""
    
    def __init__(self, db_path: str = "productivity.db", firebase_config: str = None):
        self.db_path = db_path
        self.devices = {}
        self.notifications = {}
        self.sync_queue = queue.Queue()
        self.notification_queue = queue.Queue()
        
        # Initialize Firebase (if configured)
        self.firebase_app = None
        self.firestore_db = None
        if firebase_config:
            self._initialize_firebase(firebase_config)
        
        # Initialize Flask app for mobile API
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'mobile_integration_secret'
        
        # Initialize API routes
        self._initialize_api_routes()
        
        # Start background processing
        self.processing_thread = threading.Thread(target=self._background_processing, daemon=True)
        self.processing_thread.start()
        
        print("📱 Mobile Integration System initialized!")
        print("🔔 Push notifications enabled!")
        print("🔄 Cross-platform sync active!")
    
    def _initialize_firebase(self, firebase_config: str):
        """Initialize Firebase for push notifications"""
        try:
            cred = credentials.Certificate(firebase_config)
            self.firebase_app = firebase_admin.initialize_app(cred)
            self.firestore_db = firestore.client()
            print("🔥 Firebase initialized successfully!")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
    
    def _initialize_api_routes(self):
        """Initialize API routes for mobile integration"""
        
        @self.app.route('/api/mobile/register', methods=['POST'])
        def register_device():
            """Register a mobile device"""
            data = request.get_json()
            
            device_id = data.get('device_id')
            user_id = data.get('user_id')
            platform = data.get('platform')
            device_token = data.get('device_token')
            app_version = data.get('app_version')
            os_version = data.get('os_version')
            
            if not all([device_id, user_id, platform, device_token]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            device = self.register_device(
                device_id=device_id,
                user_id=user_id,
                platform=MobilePlatform(platform),
                device_token=device_token,
                app_version=app_version,
                os_version=os_version
            )
            
            return jsonify({
                'success': True,
                'device_id': device.device_id,
                'sync_enabled': device.sync_enabled,
                'push_enabled': device.push_enabled
            })
        
        @self.app.route('/api/mobile/sync', methods=['POST'])
        def sync_data():
            """Sync data with mobile device"""
            data = request.get_json()
            
            user_id = data.get('user_id')
            device_id = data.get('device_id')
            sync_data_list = data.get('data', [])
            
            if not all([user_id, device_id]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            sync_results = self.sync_data(user_id, device_id, sync_data_list)
            
            return jsonify({
                'success': True,
                'synced_items': len(sync_results),
                'conflicts': len([r for r in sync_results if r.status == SyncStatus.CONFLICT])
            })
        
        @self.app.route('/api/mobile/notifications', methods=['GET'])
        def get_notifications():
            """Get notifications for a user"""
            user_id = request.args.get('user_id')
            device_id = request.args.get('device_id')
            limit = int(request.args.get('limit', 20))
            
            if not user_id:
                return jsonify({'error': 'Missing user_id'}), 400
            
            notifications = self.get_user_notifications(user_id, device_id, limit)
            
            return jsonify({
                'notifications': [
                    {
                        'id': n.id,
                        'type': n.type.value,
                        'title': n.title,
                        'body': n.body,
                        'data': n.data,
                        'timestamp': n.scheduled_time.isoformat(),
                        'is_read': n.is_read
                    }
                    for n in notifications
                ]
            })
        
        @self.app.route('/api/mobile/notifications/<notification_id>/read', methods=['POST'])
        def mark_notification_read(notification_id):
            """Mark notification as read"""
            success = self.mark_notification_read(notification_id)
            
            return jsonify({'success': success})
    
    def register_device(self, device_id: str, user_id: str, platform: MobilePlatform,
                       device_token: str, app_version: str = "1.0.0", 
                       os_version: str = "Unknown") -> MobileDevice:
        """Register a mobile device"""
        device = MobileDevice(
            device_id=device_id,
            user_id=user_id,
            platform=platform,
            device_token=device_token,
            app_version=app_version,
            os_version=os_version,
            last_sync=datetime.now(),
            is_active=True,
            push_enabled=True,
            sync_enabled=True
        )
        
        self.devices[device_id] = device
        self._save_device(device)
        
        print(f"📱 Device registered: {device_id} ({platform.value})")
        return device
    
    def unregister_device(self, device_id: str) -> bool:
        """Unregister a mobile device"""
        if device_id in self.devices:
            device = self.devices[device_id]
            device.is_active = False
            self._save_device(device)
            
            print(f"📱 Device unregistered: {device_id}")
            return True
        
        return False
    
    def send_push_notification(self, user_id: str, notification_type: NotificationType,
                             title: str, body: str, data: Dict[str, Any] = None,
                             scheduled_time: datetime = None) -> bool:
        """Send push notification to user's devices"""
        if not self.firebase_app:
            logger.warning("Firebase not configured - push notifications disabled")
            return False
        
        # Get user's active devices
        user_devices = [d for d in self.devices.values() 
                       if d.user_id == user_id and d.is_active and d.push_enabled]
        
        if not user_devices:
            logger.warning(f"No active devices found for user {user_id}")
            return False
        
        # Create notification
        notification_id = str(uuid.uuid4())
        notification = MobileNotification(
            id=notification_id,
            user_id=user_id,
            device_id=user_devices[0].device_id,  # Send to first device
            type=notification_type,
            title=title,
            body=body,
            data=data or {},
            scheduled_time=scheduled_time or datetime.now(),
            sent_time=None,
            is_read=False,
            action_taken=False
        )
        
        self.notifications[notification_id] = notification
        self._save_notification(notification)
        
        # Add to notification queue
        self.notification_queue.put(notification)
        
        print(f"🔔 Push notification queued: {title}")
        return True
    
    def send_break_reminder(self, user_id: str, break_duration: int = 5) -> bool:
        """Send break reminder notification"""
        return self.send_push_notification(
            user_id=user_id,
            notification_type=NotificationType.BREAK_REMINDER,
            title="Time for a Break! ☕",
            body=f"Take a {break_duration}-minute break to refresh your mind.",
            data={
                'break_duration': break_duration,
                'action': 'take_break'
            }
        )
    
    def send_limit_reached(self, user_id: str, platform: str = "social media") -> bool:
        """Send limit reached notification"""
        return self.send_push_notification(
            user_id=user_id,
            notification_type=NotificationType.LIMIT_REACHED,
            title="Daily Limit Reached! ⏰",
            body=f"You've reached your daily {platform} limit. Time to focus on other activities!",
            data={
                'platform': platform,
                'action': 'lock_screen'
            }
        )
    
    def send_achievement_notification(self, user_id: str, achievement_name: str,
                                    achievement_description: str) -> bool:
        """Send achievement notification"""
        return self.send_push_notification(
            user_id=user_id,
            notification_type=NotificationType.ACHIEVEMENT,
            title=f"🏆 Achievement Unlocked: {achievement_name}",
            body=achievement_description,
            data={
                'achievement_name': achievement_name,
                'action': 'view_achievement'
            }
        )
    
    def send_challenge_notification(self, user_id: str, challenge_name: str,
                                  challenge_description: str) -> bool:
        """Send challenge notification"""
        return self.send_push_notification(
            user_id=user_id,
            notification_type=NotificationType.CHALLENGE,
            title=f"🎯 New Challenge: {challenge_name}",
            body=challenge_description,
            data={
                'challenge_name': challenge_name,
                'action': 'join_challenge'
            }
        )
    
    def sync_data(self, user_id: str, device_id: str, 
                 sync_data_list: List[Dict[str, Any]]) -> List[SyncData]:
        """Sync data with mobile device"""
        sync_results = []
        
        for data_item in sync_data_list:
            sync_id = str(uuid.uuid4())
            
            sync_data = SyncData(
                id=sync_id,
                user_id=user_id,
                device_id=device_id,
                data_type=data_item.get('type'),
                data=data_item.get('data', {}),
                timestamp=datetime.now(),
                status=SyncStatus.PENDING,
                conflict_resolution=None
            )
            
            # Check for conflicts
            if self._check_data_conflict(user_id, data_item):
                sync_data.status = SyncStatus.CONFLICT
                sync_data.conflict_resolution = self._resolve_conflict(user_id, data_item)
            else:
                # Apply the data
                self._apply_sync_data(user_id, data_item)
                sync_data.status = SyncStatus.SYNCED
            
            sync_results.append(sync_data)
            self._save_sync_data(sync_data)
        
        # Update device last sync time
        if device_id in self.devices:
            self.devices[device_id].last_sync = datetime.now()
            self._save_device(self.devices[device_id])
        
        print(f"🔄 Synced {len(sync_results)} items for user {user_id}")
        return sync_results
    
    def get_user_notifications(self, user_id: str, device_id: str = None,
                             limit: int = 20) -> List[MobileNotification]:
        """Get notifications for a user"""
        user_notifications = [n for n in self.notifications.values() if n.user_id == user_id]
        
        if device_id:
            user_notifications = [n for n in user_notifications if n.device_id == device_id]
        
        # Sort by scheduled time (newest first)
        user_notifications.sort(key=lambda x: x.scheduled_time, reverse=True)
        
        return user_notifications[:limit]
    
    def mark_notification_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        if notification_id in self.notifications:
            notification = self.notifications[notification_id]
            notification.is_read = True
            self._save_notification(notification)
            return True
        
        return False
    
    def get_device_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get device analytics for a user"""
        user_devices = [d for d in self.devices.values() if d.user_id == user_id]
        
        if not user_devices:
            return {"error": "No devices found"}
        
        # Calculate analytics
        total_devices = len(user_devices)
        active_devices = len([d for d in user_devices if d.is_active])
        push_enabled_devices = len([d for d in user_devices if d.push_enabled])
        sync_enabled_devices = len([d for d in user_devices if d.sync_enabled])
        
        # Platform distribution
        platform_counts = {}
        for device in user_devices:
            platform = device.platform.value
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Recent sync activity
        recent_syncs = [d.last_sync for d in user_devices if d.last_sync]
        avg_sync_frequency = None
        if recent_syncs:
            recent_syncs.sort(reverse=True)
            if len(recent_syncs) > 1:
                time_diffs = [(recent_syncs[i] - recent_syncs[i+1]).total_seconds() 
                             for i in range(len(recent_syncs)-1)]
                avg_sync_frequency = sum(time_diffs) / len(time_diffs)
        
        analytics = {
            "devices": {
                "total": total_devices,
                "active": active_devices,
                "push_enabled": push_enabled_devices,
                "sync_enabled": sync_enabled_devices
            },
            "platforms": platform_counts,
            "sync_activity": {
                "avg_frequency_hours": avg_sync_frequency / 3600 if avg_sync_frequency else None,
                "last_sync": max([d.last_sync for d in user_devices]).isoformat() if user_devices else None
            },
            "notifications": {
                "total_sent": len([n for n in self.notifications.values() if n.user_id == user_id]),
                "unread": len([n for n in self.notifications.values() 
                             if n.user_id == user_id and not n.is_read])
            }
        }
        
        return analytics
    
    def _check_data_conflict(self, user_id: str, data_item: Dict[str, Any]) -> bool:
        """Check if there's a data conflict"""
        # This is a simplified conflict detection
        # In a real implementation, you'd check for actual conflicts
        return False
    
    def _resolve_conflict(self, user_id: str, data_item: Dict[str, Any]) -> str:
        """Resolve data conflict"""
        # Simple conflict resolution: use the most recent data
        return "use_latest"
    
    def _apply_sync_data(self, user_id: str, data_item: Dict[str, Any]):
        """Apply synced data"""
        data_type = data_item.get('type')
        data = data_item.get('data', {})
        
        # Apply different types of data
        if data_type == 'usage_data':
            self._apply_usage_data(user_id, data)
        elif data_type == 'focus_session':
            self._apply_focus_session(user_id, data)
        elif data_type == 'goal_update':
            self._apply_goal_update(user_id, data)
        elif data_type == 'settings':
            self._apply_settings_update(user_id, data)
    
    def _apply_usage_data(self, user_id: str, data: Dict[str, Any]):
        """Apply usage data from mobile"""
        # Save usage data to database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mobile_usage_data 
                    (user_id, platform, duration, timestamp, source)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user_id,
                    data.get('platform'),
                    data.get('duration'),
                    datetime.now().isoformat(),
                    'mobile'
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error applying usage data: {e}")
    
    def _apply_focus_session(self, user_id: str, data: Dict[str, Any]):
        """Apply focus session from mobile"""
        # Save focus session to database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mobile_focus_sessions 
                    (user_id, duration, start_time, end_time, interruptions, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    data.get('duration'),
                    data.get('start_time'),
                    data.get('end_time'),
                    data.get('interruptions', 0),
                    'mobile'
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error applying focus session: {e}")
    
    def _apply_goal_update(self, user_id: str, data: Dict[str, Any]):
        """Apply goal update from mobile"""
        # Update goal progress
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_goals 
                    SET current_progress = ?, last_updated = ?
                    WHERE user_id = ? AND goal_id = ?
                """, (
                    data.get('progress'),
                    datetime.now().isoformat(),
                    user_id,
                    data.get('goal_id')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error applying goal update: {e}")
    
    def _apply_settings_update(self, user_id: str, data: Dict[str, Any]):
        """Apply settings update from mobile"""
        # Update user settings
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_settings 
                    SET settings_data = ?, last_updated = ?
                    WHERE user_id = ?
                """, (
                    json.dumps(data),
                    datetime.now().isoformat(),
                    user_id
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error applying settings update: {e}")
    
    def _background_processing(self):
        """Background processing for mobile integration"""
        while True:
            try:
                # Process notification queue
                while not self.notification_queue.empty():
                    notification = self.notification_queue.get_nowait()
                    self._send_push_notification(notification)
                
                # Process sync queue
                while not self.sync_queue.empty():
                    sync_data = self.sync_queue.get_nowait()
                    # Process sync data
                
                # Clean up old notifications
                self._cleanup_old_notifications()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in mobile background processing: {e}")
                time.sleep(30)
    
    def _send_push_notification(self, notification: MobileNotification):
        """Send push notification via Firebase"""
        if not self.firebase_app:
            return
        
        try:
            # Get device token
            device = self.devices.get(notification.device_id)
            if not device or not device.is_active:
                return
            
            # Create message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.body
                ),
                data=notification.data,
                token=device.device_token
            )
            
            # Send message
            response = messaging.send(message)
            
            # Update notification
            notification.sent_time = datetime.now()
            self._save_notification(notification)
            
            print(f"🔔 Push notification sent: {response}")
            
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
    
    def _cleanup_old_notifications(self):
        """Clean up old notifications (keep last 100 per user)"""
        for user_id in set(n.user_id for n in self.notifications.values()):
            user_notifications = [n for n in self.notifications.values() if n.user_id == user_id]
            if len(user_notifications) > 100:
                # Sort by scheduled time and keep only the most recent 100
                user_notifications.sort(key=lambda x: x.scheduled_time)
                notifications_to_remove = user_notifications[:-100]
                
                for notification in notifications_to_remove:
                    del self.notifications[notification.id]
    
    def _save_device(self, device: MobileDevice):
        """Save device to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO mobile_devices 
                    (device_id, user_id, platform, device_token, app_version, os_version,
                     last_sync, is_active, push_enabled, sync_enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    device.device_id,
                    device.user_id,
                    device.platform.value,
                    device.device_token,
                    device.app_version,
                    device.os_version,
                    device.last_sync.isoformat(),
                    device.is_active,
                    device.push_enabled,
                    device.sync_enabled
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving device: {e}")
    
    def _save_notification(self, notification: MobileNotification):
        """Save notification to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO mobile_notifications 
                    (id, user_id, device_id, type, title, body, data, scheduled_time,
                     sent_time, is_read, action_taken)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    notification.id,
                    notification.user_id,
                    notification.device_id,
                    notification.type.value,
                    notification.title,
                    notification.body,
                    json.dumps(notification.data),
                    notification.scheduled_time.isoformat(),
                    notification.sent_time.isoformat() if notification.sent_time else None,
                    notification.is_read,
                    notification.action_taken
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving notification: {e}")
    
    def _save_sync_data(self, sync_data: SyncData):
        """Save sync data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mobile_sync_data 
                    (id, user_id, device_id, data_type, data, timestamp, status, conflict_resolution)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sync_data.id,
                    sync_data.user_id,
                    sync_data.device_id,
                    sync_data.data_type,
                    json.dumps(sync_data.data),
                    sync_data.timestamp.isoformat(),
                    sync_data.status.value,
                    sync_data.conflict_resolution
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving sync data: {e}")
    
    def run_server(self, host: str = '0.0.0.0', port: int = 5002):
        """Run the mobile integration server"""
        print(f"🚀 Starting Mobile Integration Server on {host}:{port}")
        self.app.run(host=host, port=port, debug=False)

# Initialize database tables
def initialize_mobile_database(db_path: str = "productivity.db"):
    """Initialize database tables for mobile integration"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Mobile devices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mobile_devices (
                    device_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    platform TEXT,
                    device_token TEXT,
                    app_version TEXT,
                    os_version TEXT,
                    last_sync TEXT,
                    is_active BOOLEAN,
                    push_enabled BOOLEAN,
                    sync_enabled BOOLEAN
                )
            """)
            
            # Mobile notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mobile_notifications (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    device_id TEXT,
                    type TEXT,
                    title TEXT,
                    body TEXT,
                    data TEXT,
                    scheduled_time TEXT,
                    sent_time TEXT,
                    is_read BOOLEAN,
                    action_taken BOOLEAN
                )
            """)
            
            # Mobile sync data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mobile_sync_data (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    device_id TEXT,
                    data_type TEXT,
                    data TEXT,
                    timestamp TEXT,
                    status TEXT,
                    conflict_resolution TEXT
                )
            """)
            
            # Mobile usage data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mobile_usage_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    platform TEXT,
                    duration INTEGER,
                    timestamp TEXT,
                    source TEXT
                )
            """)
            
            # Mobile focus sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mobile_focus_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    duration INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    interruptions INTEGER,
                    source TEXT
                )
            """)
            
            conn.commit()
            print("📱 Mobile database tables initialized successfully!")
            
    except Exception as e:
        logger.error(f"Error initializing mobile database: {e}")

if __name__ == "__main__":
    # Initialize database
    initialize_mobile_database()
    
    # Create mobile integration system
    mobile_integration = MobileIntegrationSystem()
    
    # Example usage
    device = mobile_integration.register_device(
        device_id="mobile_123",
        user_id="user1",
        platform=MobilePlatform.ANDROID,
        device_token="firebase_token_123",
        app_version="1.2.0",
        os_version="Android 12"
    )
    
    # Send example notifications
    mobile_integration.send_break_reminder("user1", 5)
    mobile_integration.send_achievement_notification(
        "user1", 
        "First Focus", 
        "You completed your first focus session!"
    )
    
    print("📱 Mobile integration system ready!")
    print("🔔 Starting mobile API server...")
    
    # Run the server
    mobile_integration.run_server()
