#!/usr/bin/env python3
"""
Security and Privacy System
Comprehensive security and privacy features for the scroll stopping tool including
data encryption, user authentication, privacy controls, and compliance features.
"""

import json
import time
import threading
import hashlib
import hmac
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from enum import Enum
import sqlite3
import uuid
from pathlib import Path
import queue
from flask import Flask, request, jsonify, session
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import jwt
import bcrypt
import re

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"

class PrivacyLevel(Enum):
    """Privacy levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"

class DataCategory(Enum):
    """Data categories for privacy control"""
    USAGE_DATA = "usage_data"
    PERSONAL_INFO = "personal_info"
    ANALYTICS = "analytics"
    COLLABORATION = "collaboration"
    SYSTEM_LOGS = "system_logs"

class ComplianceType(Enum):
    """Compliance types"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    ISO27001 = "iso27001"

@dataclass
class UserSecurityProfile:
    """User security profile"""
    user_id: str
    password_hash: str
    salt: str
    security_level: SecurityLevel
    privacy_level: PrivacyLevel
    two_factor_enabled: bool
    two_factor_secret: Optional[str]
    last_password_change: datetime
    failed_login_attempts: int
    account_locked: bool
    lockout_until: Optional[datetime]
    session_tokens: List[str]
    api_keys: List[str]

@dataclass
class PrivacySettings:
    """User privacy settings"""
    user_id: str
    data_retention_days: int
    data_sharing_enabled: bool
    analytics_enabled: bool
    collaboration_enabled: bool
    data_categories: Dict[DataCategory, bool]
    compliance_settings: Dict[ComplianceType, bool]
    data_export_enabled: bool
    data_deletion_enabled: bool

@dataclass
class SecurityEvent:
    """Security event log"""
    id: str
    user_id: str
    event_type: str
    description: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    severity: str
    resolved: bool

@dataclass
class DataRequest:
    """Data privacy request"""
    id: str
    user_id: str
    request_type: str  # export, deletion, access
    status: str  # pending, processing, completed, failed
    created_date: datetime
    completed_date: Optional[datetime]
    data_size: Optional[int]
    file_path: Optional[str]

class SecurityPrivacySystem:
    """Security and privacy system"""
    
    def __init__(self, db_path: str = "productivity.db", encryption_key: str = None):
        self.db_path = db_path
        self.security_profiles = {}
        self.privacy_settings = {}
        self.security_events = {}
        self.data_requests = {}
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.event_queue = queue.Queue()
        
        # Initialize Flask app for security API
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = secrets.token_hex(32)
        
        # Initialize API routes
        self._initialize_api_routes()
        
        # Start background processing
        self.processing_thread = threading.Thread(target=self._background_processing, daemon=True)
        self.processing_thread.start()
        
        print("🔒 Security and Privacy System initialized!")
        print("🔐 Data encryption enabled!")
        print("🛡️ Privacy controls active!")
    
    def _initialize_api_routes(self):
        """Initialize API routes for security and privacy"""
        
        @self.app.route('/api/security/register', methods=['POST'])
        def register_user():
            """Register a new user with security"""
            data = request.get_json()
            
            user_id = data.get('user_id')
            password = data.get('password')
            email = data.get('email')
            
            if not all([user_id, password, email]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            success = self.register_user(user_id, password, email)
            
            return jsonify({'success': success})
        
        @self.app.route('/api/security/login', methods=['POST'])
        def login_user():
            """Authenticate user login"""
            data = request.get_json()
            
            user_id = data.get('user_id')
            password = data.get('password')
            
            if not all([user_id, password]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            auth_result = self.authenticate_user(user_id, password)
            
            if auth_result['success']:
                return jsonify({
                    'success': True,
                    'token': auth_result['token'],
                    'security_level': auth_result['security_level']
                })
            else:
                return jsonify({'error': auth_result['error']}), 401
        
        @self.app.route('/api/privacy/settings', methods=['GET'])
        def get_privacy_settings():
            """Get user privacy settings"""
            user_id = request.args.get('user_id')
            
            if not user_id:
                return jsonify({'error': 'Missing user_id'}), 400
            
            settings = self.get_privacy_settings(user_id)
            
            return jsonify(settings)
        
        @self.app.route('/api/privacy/settings', methods=['PUT'])
        def update_privacy_settings():
            """Update user privacy settings"""
            data = request.get_json()
            
            user_id = data.get('user_id')
            settings = data.get('settings', {})
            
            if not user_id:
                return jsonify({'error': 'Missing user_id'}), 400
            
            success = self.update_privacy_settings(user_id, settings)
            
            return jsonify({'success': success})
        
        @self.app.route('/api/privacy/request', methods=['POST'])
        def create_data_request():
            """Create a data privacy request"""
            data = request.get_json()
            
            user_id = data.get('user_id')
            request_type = data.get('request_type')
            
            if not all([user_id, request_type]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            request_id = self.create_data_request(user_id, request_type)
            
            return jsonify({'request_id': request_id})
    
    def register_user(self, user_id: str, password: str, email: str) -> bool:
        """Register a new user with security"""
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # Create security profile
            security_profile = UserSecurityProfile(
                user_id=user_id,
                password_hash=password_hash.decode('utf-8'),
                salt=salt.decode('utf-8'),
                security_level=SecurityLevel.STANDARD,
                privacy_level=PrivacyLevel.STANDARD,
                two_factor_enabled=False,
                two_factor_secret=None,
                last_password_change=datetime.now(),
                failed_login_attempts=0,
                account_locked=False,
                lockout_until=None,
                session_tokens=[],
                api_keys=[]
            )
            
            # Create privacy settings
            privacy_settings = PrivacySettings(
                user_id=user_id,
                data_retention_days=365,
                data_sharing_enabled=False,
                analytics_enabled=True,
                collaboration_enabled=True,
                data_categories={
                    DataCategory.USAGE_DATA: True,
                    DataCategory.PERSONAL_INFO: True,
                    DataCategory.ANALYTICS: True,
                    DataCategory.COLLABORATION: True,
                    DataCategory.SYSTEM_LOGS: False
                },
                compliance_settings={
                    ComplianceType.GDPR: True,
                    ComplianceType.CCPA: True,
                    ComplianceType.HIPAA: False,
                    ComplianceType.SOX: False,
                    ComplianceType.ISO27001: False
                },
                data_export_enabled=True,
                data_deletion_enabled=True
            )
            
            self.security_profiles[user_id] = security_profile
            self.privacy_settings[user_id] = privacy_settings
            
            self._save_security_profile(security_profile)
            self._save_privacy_settings(privacy_settings)
            
            # Log security event
            self._log_security_event(
                user_id=user_id,
                event_type="user_registration",
                description=f"New user registered: {user_id}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                severity="info"
            )
            
            print(f"🔐 User registered: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False
    
    def authenticate_user(self, user_id: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            if user_id not in self.security_profiles:
                return {'success': False, 'error': 'User not found'}
            
            profile = self.security_profiles[user_id]
            
            # Check if account is locked
            if profile.account_locked and profile.lockout_until:
                if datetime.now() < profile.lockout_until:
                    return {'success': False, 'error': 'Account temporarily locked'}
                else:
                    # Unlock account
                    profile.account_locked = False
                    profile.failed_login_attempts = 0
                    profile.lockout_until = None
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), profile.password_hash.encode('utf-8')):
                # Successful login
                profile.failed_login_attempts = 0
                profile.account_locked = False
                profile.lockout_until = None
                
                # Generate session token
                token = self._generate_session_token(user_id)
                profile.session_tokens.append(token)
                
                self._save_security_profile(profile)
                
                # Log security event
                self._log_security_event(
                    user_id=user_id,
                    event_type="successful_login",
                    description=f"Successful login for user: {user_id}",
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    severity="info"
                )
                
                return {
                    'success': True,
                    'token': token,
                    'security_level': profile.security_level.value
                }
            else:
                # Failed login
                profile.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts
                if profile.failed_login_attempts >= 5:
                    profile.account_locked = True
                    profile.lockout_until = datetime.now() + timedelta(minutes=30)
                
                self._save_security_profile(profile)
                
                # Log security event
                self._log_security_event(
                    user_id=user_id,
                    event_type="failed_login",
                    description=f"Failed login attempt for user: {user_id}",
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    severity="warning"
                )
                
                return {'success': False, 'error': 'Invalid credentials'}
                
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return {'success': False, 'error': 'Authentication error'}
    
    def validate_session_token(self, token: str) -> Optional[str]:
        """Validate session token and return user_id"""
        try:
            # Decode token
            payload = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            expiry = payload.get('exp')
            
            if not user_id or not expiry:
                return None
            
            # Check if token is expired
            if datetime.now().timestamp() > expiry:
                return None
            
            # Check if token exists in user's session tokens
            if user_id in self.security_profiles:
                profile = self.security_profiles[user_id]
                if token in profile.session_tokens:
                    return user_id
            
            return None
            
        except jwt.InvalidTokenError:
            return None
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            return encrypted_data
    
    def get_privacy_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user privacy settings"""
        if user_id not in self.privacy_settings:
            return {"error": "User not found"}
        
        settings = self.privacy_settings[user_id]
        
        return {
            "user_id": settings.user_id,
            "data_retention_days": settings.data_retention_days,
            "data_sharing_enabled": settings.data_sharing_enabled,
            "analytics_enabled": settings.analytics_enabled,
            "collaboration_enabled": settings.collaboration_enabled,
            "data_categories": {k.value: v for k, v in settings.data_categories.items()},
            "compliance_settings": {k.value: v for k, v in settings.compliance_settings.items()},
            "data_export_enabled": settings.data_export_enabled,
            "data_deletion_enabled": settings.data_deletion_enabled
        }
    
    def update_privacy_settings(self, user_id: str, new_settings: Dict[str, Any]) -> bool:
        """Update user privacy settings"""
        try:
            if user_id not in self.privacy_settings:
                return False
            
            settings = self.privacy_settings[user_id]
            
            # Update settings
            if 'data_retention_days' in new_settings:
                settings.data_retention_days = new_settings['data_retention_days']
            
            if 'data_sharing_enabled' in new_settings:
                settings.data_sharing_enabled = new_settings['data_sharing_enabled']
            
            if 'analytics_enabled' in new_settings:
                settings.analytics_enabled = new_settings['analytics_enabled']
            
            if 'collaboration_enabled' in new_settings:
                settings.collaboration_enabled = new_settings['collaboration_enabled']
            
            if 'data_categories' in new_settings:
                for category_str, enabled in new_settings['data_categories'].items():
                    try:
                        category = DataCategory(category_str)
                        settings.data_categories[category] = enabled
                    except ValueError:
                        continue
            
            if 'compliance_settings' in new_settings:
                for compliance_str, enabled in new_settings['compliance_settings'].items():
                    try:
                        compliance = ComplianceType(compliance_str)
                        settings.compliance_settings[compliance] = enabled
                    except ValueError:
                        continue
            
            self._save_privacy_settings(settings)
            
            # Log privacy settings change
            self._log_security_event(
                user_id=user_id,
                event_type="privacy_settings_updated",
                description=f"Privacy settings updated for user: {user_id}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                severity="info"
            )
            
            print(f"🔒 Privacy settings updated for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating privacy settings: {e}")
            return False
    
    def create_data_request(self, user_id: str, request_type: str) -> str:
        """Create a data privacy request"""
        try:
            request_id = str(uuid.uuid4())
            
            data_request = DataRequest(
                id=request_id,
                user_id=user_id,
                request_type=request_type,
                status="pending",
                created_date=datetime.now(),
                completed_date=None,
                data_size=None,
                file_path=None
            )
            
            self.data_requests[request_id] = data_request
            self._save_data_request(data_request)
            
            # Log data request
            self._log_security_event(
                user_id=user_id,
                event_type="data_request_created",
                description=f"Data request created: {request_type}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                severity="info"
            )
            
            print(f"📋 Data request created: {request_type} for user {user_id}")
            return request_id
            
        except Exception as e:
            logger.error(f"Error creating data request: {e}")
            return ""
    
    def process_data_request(self, request_id: str) -> bool:
        """Process a data privacy request"""
        try:
            if request_id not in self.data_requests:
                return False
            
            request = self.data_requests[request_id]
            request.status = "processing"
            self._save_data_request(request)
            
            if request.request_type == "export":
                success = self._export_user_data(request)
            elif request.request_type == "deletion":
                success = self._delete_user_data(request)
            elif request.request_type == "access":
                success = self._provide_data_access(request)
            else:
                success = False
            
            if success:
                request.status = "completed"
                request.completed_date = datetime.now()
            else:
                request.status = "failed"
            
            self._save_data_request(request)
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing data request: {e}")
            return False
    
    def _export_user_data(self, request: DataRequest) -> bool:
        """Export user data for GDPR compliance"""
        try:
            user_id = request.user_id
            
            # Collect user data
            export_data = {
                "user_id": user_id,
                "export_date": datetime.now().isoformat(),
                "security_profile": self._get_user_security_data(user_id),
                "privacy_settings": self._get_user_privacy_data(user_id),
                "usage_data": self._get_user_usage_data(user_id),
                "focus_sessions": self._get_user_focus_data(user_id),
                "achievements": self._get_user_achievement_data(user_id)
            }
            
            # Create export file
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            file_path = export_dir / f"user_data_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            # Update request
            request.file_path = str(file_path)
            request.data_size = file_path.stat().st_size
            
            print(f"📤 Data exported for user {user_id}: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return False
    
    def _delete_user_data(self, request: DataRequest) -> bool:
        """Delete user data for GDPR compliance"""
        try:
            user_id = request.user_id
            
            # Delete user data from all tables
            tables_to_clean = [
                'usage_data', 'focus_sessions', 'achievements', 'goals',
                'mobile_devices', 'mobile_notifications', 'mobile_sync_data',
                'collaboration_messages', 'teams', 'shared_goals'
            ]
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for table in tables_to_clean:
                    cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
                
                conn.commit()
            
            # Remove from memory
            if user_id in self.security_profiles:
                del self.security_profiles[user_id]
            if user_id in self.privacy_settings:
                del self.privacy_settings[user_id]
            
            print(f"🗑️ Data deleted for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False
    
    def _provide_data_access(self, request: DataRequest) -> bool:
        """Provide data access information"""
        try:
            user_id = request.user_id
            
            # Create access report
            access_data = {
                "user_id": user_id,
                "access_date": datetime.now().isoformat(),
                "data_summary": self._get_data_summary(user_id),
                "data_categories": self._get_data_categories(user_id),
                "retention_info": self._get_retention_info(user_id)
            }
            
            # Save access report
            access_dir = Path("access_reports")
            access_dir.mkdir(exist_ok=True)
            
            file_path = access_dir / f"access_report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(file_path, 'w') as f:
                json.dump(access_data, f, indent=2, default=str)
            
            request.file_path = str(file_path)
            
            print(f"📋 Access report created for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error providing data access: {e}")
            return False
    
    def _generate_session_token(self, user_id: str) -> str:
        """Generate a session token for user"""
        payload = {
            'user_id': user_id,
            'exp': datetime.now().timestamp() + (24 * 60 * 60),  # 24 hours
            'iat': datetime.now().timestamp()
        }
        
        return jwt.encode(payload, self.app.config['SECRET_KEY'], algorithm='HS256')
    
    def _log_security_event(self, user_id: str, event_type: str, description: str,
                           ip_address: str, user_agent: str, severity: str):
        """Log a security event"""
        try:
            event_id = str(uuid.uuid4())
            
            event = SecurityEvent(
                id=event_id,
                user_id=user_id,
                event_type=event_type,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.now(),
                severity=severity,
                resolved=False
            )
            
            self.security_events[event_id] = event
            self._save_security_event(event)
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    def _background_processing(self):
        """Background processing for security and privacy"""
        while True:
            try:
                # Process event queue
                while not self.event_queue.empty():
                    event = self.event_queue.get_nowait()
                    # Process security events
                
                # Clean up old data based on retention policies
                self._cleanup_expired_data()
                
                # Process pending data requests
                self._process_pending_requests()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in security background processing: {e}")
                time.sleep(300)
    
    def _cleanup_expired_data(self):
        """Clean up expired data based on retention policies"""
        try:
            for user_id, settings in self.privacy_settings.items():
                retention_days = settings.data_retention_days
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                
                # Clean up old data
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Clean up old usage data
                    cursor.execute("""
                        DELETE FROM usage_data 
                        WHERE user_id = ? AND date < ?
                    """, (user_id, cutoff_date.isoformat()))
                    
                    # Clean up old security events
                    cursor.execute("""
                        DELETE FROM security_events 
                        WHERE user_id = ? AND timestamp < ?
                    """, (user_id, cutoff_date.isoformat()))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {e}")
    
    def _process_pending_requests(self):
        """Process pending data requests"""
        try:
            pending_requests = [r for r in self.data_requests.values() if r.status == "pending"]
            
            for request in pending_requests[:5]:  # Process up to 5 at a time
                self.process_data_request(request.id)
                
        except Exception as e:
            logger.error(f"Error processing pending requests: {e}")
    
    def _get_user_security_data(self, user_id: str) -> Dict[str, Any]:
        """Get user security data for export"""
        if user_id not in self.security_profiles:
            return {}
        
        profile = self.security_profiles[user_id]
        return {
            "security_level": profile.security_level.value,
            "privacy_level": profile.privacy_level.value,
            "two_factor_enabled": profile.two_factor_enabled,
            "last_password_change": profile.last_password_change.isoformat(),
            "account_locked": profile.account_locked
        }
    
    def _get_user_privacy_data(self, user_id: str) -> Dict[str, Any]:
        """Get user privacy data for export"""
        if user_id not in self.privacy_settings:
            return {}
        
        settings = self.privacy_settings[user_id]
        return {
            "data_retention_days": settings.data_retention_days,
            "data_sharing_enabled": settings.data_sharing_enabled,
            "analytics_enabled": settings.analytics_enabled,
            "collaboration_enabled": settings.collaboration_enabled
        }
    
    def _get_user_usage_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user usage data for export"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM usage_data WHERE user_id = ?", (user_id,))
                rows = cursor.fetchall()
                
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user usage data: {e}")
            return []
    
    def _get_user_focus_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user focus data for export"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM focus_sessions WHERE user_id = ?", (user_id,))
                rows = cursor.fetchall()
                
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user focus data: {e}")
            return []
    
    def _get_user_achievement_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user achievement data for export"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM achievements WHERE user_id = ?", (user_id,))
                rows = cursor.fetchall()
                
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user achievement data: {e}")
            return []
    
    def _get_data_summary(self, user_id: str) -> Dict[str, Any]:
        """Get data summary for access report"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records in each table
                tables = ['usage_data', 'focus_sessions', 'achievements', 'goals']
                summary = {}
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id = ?", (user_id,))
                    count = cursor.fetchone()[0]
                    summary[table] = count
                
                return summary
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {}
    
    def _get_data_categories(self, user_id: str) -> Dict[str, Any]:
        """Get data categories for access report"""
        if user_id not in self.privacy_settings:
            return {}
        
        settings = self.privacy_settings[user_id]
        return {k.value: v for k, v in settings.data_categories.items()}
    
    def _get_retention_info(self, user_id: str) -> Dict[str, Any]:
        """Get retention information for access report"""
        if user_id not in self.privacy_settings:
            return {}
        
        settings = self.privacy_settings[user_id]
        return {
            "data_retention_days": settings.data_retention_days,
            "data_export_enabled": settings.data_export_enabled,
            "data_deletion_enabled": settings.data_deletion_enabled
        }
    
    def _save_security_profile(self, profile: UserSecurityProfile):
        """Save security profile to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO security_profiles 
                    (user_id, password_hash, salt, security_level, privacy_level,
                     two_factor_enabled, two_factor_secret, last_password_change,
                     failed_login_attempts, account_locked, lockout_until, session_tokens, api_keys)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    profile.password_hash,
                    profile.salt,
                    profile.security_level.value,
                    profile.privacy_level.value,
                    profile.two_factor_enabled,
                    profile.two_factor_secret,
                    profile.last_password_change.isoformat(),
                    profile.failed_login_attempts,
                    profile.account_locked,
                    profile.lockout_until.isoformat() if profile.lockout_until else None,
                    json.dumps(profile.session_tokens),
                    json.dumps(profile.api_keys)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving security profile: {e}")
    
    def _save_privacy_settings(self, settings: PrivacySettings):
        """Save privacy settings to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO privacy_settings 
                    (user_id, data_retention_days, data_sharing_enabled, analytics_enabled,
                     collaboration_enabled, data_categories, compliance_settings,
                     data_export_enabled, data_deletion_enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    settings.user_id,
                    settings.data_retention_days,
                    settings.data_sharing_enabled,
                    settings.analytics_enabled,
                    settings.collaboration_enabled,
                    json.dumps({k.value: v for k, v in settings.data_categories.items()}),
                    json.dumps({k.value: v for k, v in settings.compliance_settings.items()}),
                    settings.data_export_enabled,
                    settings.data_deletion_enabled
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving privacy settings: {e}")
    
    def _save_security_event(self, event: SecurityEvent):
        """Save security event to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO security_events 
                    (id, user_id, event_type, description, ip_address, user_agent,
                     timestamp, severity, resolved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.id,
                    event.user_id,
                    event.event_type,
                    event.description,
                    event.ip_address,
                    event.user_agent,
                    event.timestamp.isoformat(),
                    event.severity,
                    event.resolved
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving security event: {e}")
    
    def _save_data_request(self, request: DataRequest):
        """Save data request to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO data_requests 
                    (id, user_id, request_type, status, created_date, completed_date,
                     data_size, file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    request.id,
                    request.user_id,
                    request.request_type,
                    request.status,
                    request.created_date.isoformat(),
                    request.completed_date.isoformat() if request.completed_date else None,
                    request.data_size,
                    request.file_path
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving data request: {e}")
    
    def run_server(self, host: str = '0.0.0.0', port: int = 5003):
        """Run the security and privacy server"""
        print(f"🚀 Starting Security and Privacy Server on {host}:{port}")
        self.app.run(host=host, port=port, debug=False)

# Initialize database tables
def initialize_security_database(db_path: str = "productivity.db"):
    """Initialize database tables for security and privacy"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Security profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_profiles (
                    user_id TEXT PRIMARY KEY,
                    password_hash TEXT,
                    salt TEXT,
                    security_level TEXT,
                    privacy_level TEXT,
                    two_factor_enabled BOOLEAN,
                    two_factor_secret TEXT,
                    last_password_change TEXT,
                    failed_login_attempts INTEGER,
                    account_locked BOOLEAN,
                    lockout_until TEXT,
                    session_tokens TEXT,
                    api_keys TEXT
                )
            """)
            
            # Privacy settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS privacy_settings (
                    user_id TEXT PRIMARY KEY,
                    data_retention_days INTEGER,
                    data_sharing_enabled BOOLEAN,
                    analytics_enabled BOOLEAN,
                    collaboration_enabled BOOLEAN,
                    data_categories TEXT,
                    compliance_settings TEXT,
                    data_export_enabled BOOLEAN,
                    data_deletion_enabled BOOLEAN
                )
            """)
            
            # Security events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    event_type TEXT,
                    description TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TEXT,
                    severity TEXT,
                    resolved BOOLEAN
                )
            """)
            
            # Data requests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_requests (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    request_type TEXT,
                    status TEXT,
                    created_date TEXT,
                    completed_date TEXT,
                    data_size INTEGER,
                    file_path TEXT
                )
            """)
            
            conn.commit()
            print("🔒 Security database tables initialized successfully!")
            
    except Exception as e:
        logger.error(f"Error initializing security database: {e}")

if __name__ == "__main__":
    # Initialize database
    initialize_security_database()
    
    # Create security and privacy system
    security_system = SecurityPrivacySystem()
    
    # Example usage
    success = security_system.register_user(
        user_id="test_user",
        password="secure_password123",
        email="test@example.com"
    )
    
    if success:
        auth_result = security_system.authenticate_user("test_user", "secure_password123")
        print(f"Authentication result: {auth_result}")
    
    print("🔒 Security and privacy system ready!")
    print("🛡️ Starting security API server...")
    
    # Run the server
    security_system.run_server()
