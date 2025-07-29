#!/usr/bin/env python3
"""
Advanced Security and Privacy Module for Scroll Stopping Tool
Comprehensive security features including encryption, access controls, audit logging, and privacy compliance
"""

import hashlib
import hmac
import secrets
import base64
import json
import sqlite3
import threading
import time
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import pickle
import tempfile
import shutil

# Security libraries
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logging.warning("Cryptography not available - advanced security features will be disabled")

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logging.warning("Bcrypt not available - password hashing will use fallback")

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    encryption_enabled: bool = True
    password_required: bool = True
    session_timeout: int = 3600  # 1 hour
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes
    audit_logging: bool = True
    data_retention_days: int = 365
    auto_wipe_on_compromise: bool = False
    privacy_mode: bool = False
    gdpr_compliance: bool = True

@dataclass
class UserSession:
    """User session information"""
    user_id: str
    session_id: str
    login_time: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    permissions: List[str]
    is_active: bool = True

@dataclass
class AuditEvent:
    """Audit log event"""
    timestamp: datetime
    event_type: str
    user_id: str
    action: str
    resource: str
    ip_address: str
    user_agent: str
    success: bool
    details: Dict
    session_id: str

@dataclass
class PrivacySettings:
    """Privacy settings for GDPR compliance"""
    data_collection_enabled: bool = True
    analytics_enabled: bool = True
    third_party_sharing: bool = False
    data_export_enabled: bool = True
    data_deletion_enabled: bool = True
    anonymization_enabled: bool = False
    consent_given: bool = False
    consent_date: Optional[datetime] = None

class PasswordManager:
    """Secure password management"""
    
    def __init__(self):
        self.salt_rounds = 12 if BCRYPT_AVAILABLE else 100000
    
    def hash_password(self, password: str) -> str:
        """Hash password securely"""
        if BCRYPT_AVAILABLE:
            salt = bcrypt.gensalt(rounds=self.salt_rounds)
            return bcrypt.hashpw(password.encode(), salt).decode()
        else:
            # Fallback to PBKDF2
            salt = secrets.token_hex(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=self.salt_rounds,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return f"{salt}:{key.decode()}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            if BCRYPT_AVAILABLE:
                return bcrypt.checkpw(password.encode(), hashed_password.encode())
            else:
                # Fallback verification
                salt, key = hashed_password.split(':', 1)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt.encode(),
                    iterations=self.salt_rounds,
                )
                test_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
                return hmac.compare_digest(key, test_key.decode())
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def generate_strong_password(self, length: int = 16) -> str:
        """Generate a strong password"""
        import string
        
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]
        
        # Fill remaining length
        all_chars = lowercase + uppercase + digits + symbols
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # Shuffle password
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        return ''.join(password_list)

class EncryptionManager:
    """Advanced encryption management"""
    
    def __init__(self, master_key: str = None):
        self.master_key = master_key or self._generate_master_key()
        self.key_derivation_salt = secrets.token_hex(16)
        self.fernet_key = self._derive_fernet_key()
        self.cipher = Fernet(self.fernet_key)
    
    def _generate_master_key(self) -> str:
        """Generate a master encryption key"""
        return secrets.token_hex(32)
    
    def _derive_fernet_key(self) -> bytes:
        """Derive Fernet key from master key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.key_derivation_salt.encode(),
            iterations=100000,
        )
        key = kdf.derive(self.master_key.encode())
        return base64.urlsafe_b64encode(key)
    
    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using Fernet"""
        return self.cipher.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using Fernet"""
        return self.cipher.decrypt(encrypted_data)
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> str:
        """Encrypt a file"""
        if output_path is None:
            output_path = file_path + '.encrypted'
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.encrypt_data(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        
        return output_path
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str = None) -> str:
        """Decrypt a file"""
        if output_path is None:
            output_path = encrypted_file_path.replace('.encrypted', '')
        
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.decrypt_data(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        return output_path
    
    def encrypt_database(self, db_path: str) -> str:
        """Encrypt entire database"""
        encrypted_db_path = db_path + '.encrypted'
        
        # Create temporary copy
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        # Copy database
        shutil.copy2(db_path, temp_db.name)
        
        # Encrypt the copy
        self.encrypt_file(temp_db.name, encrypted_db_path)
        
        # Clean up
        os.unlink(temp_db.name)
        
        return encrypted_db_path
    
    def decrypt_database(self, encrypted_db_path: str, output_path: str = None) -> str:
        """Decrypt database"""
        if output_path is None:
            output_path = encrypted_db_path.replace('.encrypted', '')
        
        return self.decrypt_file(encrypted_db_path, output_path)

class AccessControlManager:
    """Access control and session management"""
    
    def __init__(self, db_path: str = 'security.db'):
        self.db_path = db_path
        self.active_sessions: Dict[str, UserSession] = {}
        self.login_attempts: Dict[str, List[datetime]] = {}
        self.lockouts: Dict[str, datetime] = {}
        
        self.init_database()
    
    def init_database(self):
        """Initialize security database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'user',
                    created_date TEXT NOT NULL,
                    last_login TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    permissions TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN,
                    details TEXT,
                    session_id TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    ip_address TEXT,
                    user_id TEXT,
                    resolved BOOLEAN DEFAULT 0
                )
            ''')
            
            conn.commit()
    
    def create_user(self, username: str, password: str, email: str = None, role: str = 'user') -> bool:
        """Create a new user"""
        try:
            password_manager = PasswordManager()
            password_hash = password_manager.hash_password(password)
            
            user_id = secrets.token_hex(16)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO users (id, username, password_hash, email, role, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, username, password_hash, email, role, datetime.now().isoformat()))
                conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str, ip_address: str, user_agent: str) -> Optional[UserSession]:
        """Authenticate user and create session"""
        # Check for lockout
        if username in self.lockouts:
            if datetime.now() < self.lockouts[username]:
                self.log_security_event("failed_login", "high", f"Account locked: {username}", ip_address)
                return None
            else:
                del self.lockouts[username]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, password_hash, role, permissions FROM users 
                    WHERE username = ? AND is_active = 1
                ''', (username,))
                row = cursor.fetchone()
                
                if not row:
                    self._record_failed_login(username, ip_address)
                    return None
                
                user_id, password_hash, role, permissions = row
                
                # Verify password
                password_manager = PasswordManager()
                if not password_manager.verify_password(password, password_hash):
                    self._record_failed_login(username, ip_address)
                    return None
                
                # Create session
                session = UserSession(
                    user_id=user_id,
                    session_id=secrets.token_hex(32),
                    login_time=datetime.now(),
                    last_activity=datetime.now(),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    permissions=json.loads(permissions) if permissions else []
                )
                
                self.active_sessions[session.session_id] = session
                
                # Update last login
                conn.execute('''
                    UPDATE users SET last_login = ? WHERE id = ?
                ''', (datetime.now().isoformat(), user_id))
                conn.commit()
                
                # Log successful login
                self.log_audit_event("login", user_id, "login", "authentication", ip_address, user_agent, True, {})
                
                return session
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def _record_failed_login(self, username: str, ip_address: str):
        """Record failed login attempt"""
        if username not in self.login_attempts:
            self.login_attempts[username] = []
        
        self.login_attempts[username].append(datetime.now())
        
        # Remove old attempts (older than 1 hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.login_attempts[username] = [
            attempt for attempt in self.login_attempts[username] 
            if attempt > cutoff_time
        ]
        
        # Check if account should be locked
        if len(self.login_attempts[username]) >= 5:
            self.lockouts[username] = datetime.now() + timedelta(minutes=15)
            self.log_security_event("account_locked", "high", f"Account locked due to failed attempts: {username}", ip_address)
        
        self.log_audit_event("login", username, "login", "authentication", ip_address, "", False, {})
    
    def validate_session(self, session_id: str) -> Optional[UserSession]:
        """Validate and update session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        # Check session timeout
        if datetime.now() - session.last_activity > timedelta(hours=1):
            self.logout_user(session_id)
            return None
        
        # Update last activity
        session.last_activity = datetime.now()
        
        return session
    
    def logout_user(self, session_id: str):
        """Logout user and invalidate session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            self.log_audit_event("logout", session.user_id, "logout", "authentication", 
                               session.ip_address, session.user_agent, True, {})
            del self.active_sessions[session_id]
    
    def check_permission(self, session_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        session = self.validate_session(session_id)
        if not session:
            return False
        
        return permission in session.permissions
    
    def log_audit_event(self, event_type: str, user_id: str, action: str, resource: str, 
                       ip_address: str, user_agent: str, success: bool, details: Dict):
        """Log audit event"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO audit_log 
                    (timestamp, event_type, user_id, action, resource, ip_address, user_agent, success, details, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    event_type,
                    user_id,
                    action,
                    resource,
                    ip_address,
                    user_agent,
                    success,
                    json.dumps(details),
                    ""  # session_id would be passed if available
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
    
    def log_security_event(self, event_type: str, severity: str, description: str, 
                          ip_address: str, user_id: str = None):
        """Log security event"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO security_events 
                    (timestamp, event_type, severity, description, ip_address, user_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    event_type,
                    severity,
                    description,
                    ip_address,
                    user_id
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging security event: {e}")

class PrivacyManager:
    """Privacy and GDPR compliance management"""
    
    def __init__(self, db_path: str = 'privacy.db'):
        self.db_path = db_path
        self.privacy_settings = PrivacySettings()
        
        self.init_database()
        self.load_settings()
    
    def init_database(self):
        """Initialize privacy database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS privacy_consent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    consent_type TEXT NOT NULL,
                    consent_given BOOLEAN NOT NULL,
                    consent_date TEXT NOT NULL,
                    consent_version TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS data_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    request_type TEXT NOT NULL,
                    request_date TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    completed_date TEXT,
                    data_path TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS data_retention (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_type TEXT NOT NULL,
                    retention_days INTEGER NOT NULL,
                    last_cleanup TEXT,
                    records_cleaned INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
    
    def load_settings(self):
        """Load privacy settings"""
        settings_file = Path('privacy_settings.json')
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings_data = json.load(f)
                    self.privacy_settings = PrivacySettings(**settings_data)
            except Exception as e:
                logger.error(f"Error loading privacy settings: {e}")
    
    def save_settings(self):
        """Save privacy settings"""
        try:
            with open('privacy_settings.json', 'w') as f:
                json.dump(asdict(self.privacy_settings), f, default=str, indent=2)
        except Exception as e:
            logger.error(f"Error saving privacy settings: {e}")
    
    def record_consent(self, user_id: str, consent_type: str, consent_given: bool, 
                      ip_address: str = None, user_agent: str = None):
        """Record user consent"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO privacy_consent 
                    (user_id, consent_type, consent_given, consent_date, consent_version, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    consent_type,
                    consent_given,
                    datetime.now().isoformat(),
                    "1.0",
                    ip_address,
                    user_agent
                ))
                conn.commit()
            
            # Update privacy settings
            if consent_type == "general":
                self.privacy_settings.consent_given = consent_given
                self.privacy_settings.consent_date = datetime.now()
                self.save_settings()
                
        except Exception as e:
            logger.error(f"Error recording consent: {e}")
    
    def request_data_export(self, user_id: str) -> str:
        """Request data export for GDPR compliance"""
        try:
            request_id = secrets.token_hex(16)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO data_requests 
                    (user_id, request_type, request_date)
                    VALUES (?, ?, ?)
                ''', (user_id, "export", datetime.now().isoformat()))
                conn.commit()
            
            # Generate export
            export_path = self._generate_data_export(user_id)
            
            # Update request status
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE data_requests 
                    SET status = ?, completed_date = ?, data_path = ?
                    WHERE user_id = ? AND request_type = ? AND status = 'pending'
                ''', ("completed", datetime.now().isoformat(), export_path, user_id, "export"))
                conn.commit()
            
            return export_path
            
        except Exception as e:
            logger.error(f"Error requesting data export: {e}")
            return None
    
    def _generate_data_export(self, user_id: str) -> str:
        """Generate data export for user"""
        export_dir = Path('data_exports')
        export_dir.mkdir(exist_ok=True)
        
        export_file = export_dir / f"user_data_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'user_id': user_id,
            'export_date': datetime.now().isoformat(),
            'usage_data': self._get_user_usage_data(user_id),
            'privacy_consent': self._get_user_consent_data(user_id),
            'audit_log': self._get_user_audit_data(user_id)
        }
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return str(export_file)
    
    def _get_user_usage_data(self, user_id: str) -> Dict:
        """Get user usage data"""
        try:
            with sqlite3.connect('productivity.db') as conn:
                cursor = conn.execute('''
                    SELECT * FROM usage_data WHERE user_id = ?
                ''', (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting usage data: {e}")
            return {}
    
    def _get_user_consent_data(self, user_id: str) -> List[Dict]:
        """Get user consent data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM privacy_consent WHERE user_id = ?
                ''', (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting consent data: {e}")
            return []
    
    def _get_user_audit_data(self, user_id: str) -> List[Dict]:
        """Get user audit data"""
        try:
            with sqlite3.connect('security.db') as conn:
                cursor = conn.execute('''
                    SELECT * FROM audit_log WHERE user_id = ?
                ''', (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting audit data: {e}")
            return []
    
    def request_data_deletion(self, user_id: str) -> bool:
        """Request data deletion for GDPR compliance"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO data_requests 
                    (user_id, request_type, request_date)
                    VALUES (?, ?, ?)
                ''', (user_id, "deletion", datetime.now().isoformat()))
                conn.commit()
            
            # Perform data deletion
            success = self._delete_user_data(user_id)
            
            # Update request status
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE data_requests 
                    SET status = ?, completed_date = ?
                    WHERE user_id = ? AND request_type = ? AND status = 'pending'
                ''', ("completed" if success else "failed", datetime.now().isoformat(), user_id, "deletion"))
                conn.commit()
            
            return success
            
        except Exception as e:
            logger.error(f"Error requesting data deletion: {e}")
            return False
    
    def _delete_user_data(self, user_id: str) -> bool:
        """Delete all user data"""
        try:
            # Delete from productivity database
            with sqlite3.connect('productivity.db') as conn:
                conn.execute('DELETE FROM usage_data WHERE user_id = ?', (user_id,))
                conn.execute('DELETE FROM focus_sessions WHERE user_id = ?', (user_id,))
                conn.commit()
            
            # Delete from security database
            with sqlite3.connect('security.db') as conn:
                conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.execute('DELETE FROM audit_log WHERE user_id = ?', (user_id,))
                conn.commit()
            
            # Delete from privacy database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM privacy_consent WHERE user_id = ?', (user_id,))
                conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False
    
    def cleanup_expired_data(self):
        """Clean up expired data based on retention policies"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT * FROM data_retention')
                retention_policies = cursor.fetchall()
            
            for policy in retention_policies:
                data_type = policy[1]
                retention_days = policy[2]
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                
                # Clean up based on data type
                if data_type == "usage_data":
                    self._cleanup_usage_data(cutoff_date)
                elif data_type == "audit_log":
                    self._cleanup_audit_log(cutoff_date)
                elif data_type == "security_events":
                    self._cleanup_security_events(cutoff_date)
                    
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {e}")
    
    def _cleanup_usage_data(self, cutoff_date: datetime):
        """Clean up old usage data"""
        try:
            with sqlite3.connect('productivity.db') as conn:
                conn.execute('DELETE FROM usage_data WHERE date < ?', (cutoff_date.date().isoformat(),))
                conn.commit()
        except Exception as e:
            logger.error(f"Error cleaning up usage data: {e}")
    
    def _cleanup_audit_log(self, cutoff_date: datetime):
        """Clean up old audit log entries"""
        try:
            with sqlite3.connect('security.db') as conn:
                conn.execute('DELETE FROM audit_log WHERE timestamp < ?', (cutoff_date.isoformat(),))
                conn.commit()
        except Exception as e:
            logger.error(f"Error cleaning up audit log: {e}")
    
    def _cleanup_security_events(self, cutoff_date: datetime):
        """Clean up old security events"""
        try:
            with sqlite3.connect('security.db') as conn:
                conn.execute('DELETE FROM security_events WHERE timestamp < ?', (cutoff_date.isoformat(),))
                conn.commit()
        except Exception as e:
            logger.error(f"Error cleaning up security events: {e}")

class SecurityManager:
    """Main security manager"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.access_control = AccessControlManager()
        self.privacy_manager = PrivacyManager()
        self.encryption_manager = EncryptionManager()
        self.password_manager = PasswordManager()
        
        # Initialize default admin user if needed
        self._initialize_default_admin()
    
    def _initialize_default_admin(self):
        """Initialize default admin user"""
        try:
            # Check if admin user exists
            with sqlite3.connect(self.access_control.db_path) as conn:
                cursor = conn.execute('SELECT id FROM users WHERE username = ?', ('admin',))
                if not cursor.fetchone():
                    # Create default admin user
                    self.access_control.create_user(
                        username='admin',
                        password='admin123',  # Should be changed on first login
                        email='admin@scrollstopping.com',
                        role='admin'
                    )
                    logger.info("Default admin user created")
        except Exception as e:
            logger.error(f"Error initializing default admin: {e}")
    
    def authenticate_and_create_session(self, username: str, password: str, 
                                      ip_address: str, user_agent: str) -> Optional[UserSession]:
        """Authenticate user and create session"""
        return self.access_control.authenticate_user(username, password, ip_address, user_agent)
    
    def validate_session(self, session_id: str) -> Optional[UserSession]:
        """Validate user session"""
        return self.access_control.validate_session(session_id)
    
    def logout_user(self, session_id: str):
        """Logout user"""
        self.access_control.logout_user(session_id)
    
    def check_permission(self, session_id: str, permission: str) -> bool:
        """Check user permission"""
        return self.access_control.check_permission(session_id, permission)
    
    def encrypt_sensitive_data(self, data: bytes) -> bytes:
        """Encrypt sensitive data"""
        if self.config.encryption_enabled:
            return self.encryption_manager.encrypt_data(data)
        return data
    
    def decrypt_sensitive_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt sensitive data"""
        if self.config.encryption_enabled:
            return self.encryption_manager.decrypt_data(encrypted_data)
        return encrypted_data
    
    def log_audit_event(self, event_type: str, user_id: str, action: str, resource: str,
                       ip_address: str, user_agent: str, success: bool, details: Dict):
        """Log audit event"""
        if self.config.audit_logging:
            self.access_control.log_audit_event(event_type, user_id, action, resource,
                                              ip_address, user_agent, success, details)
    
    def log_security_event(self, event_type: str, severity: str, description: str,
                          ip_address: str, user_id: str = None):
        """Log security event"""
        self.access_control.log_security_event(event_type, severity, description, ip_address, user_id)
    
    def request_data_export(self, user_id: str) -> str:
        """Request data export"""
        return self.privacy_manager.request_data_export(user_id)
    
    def request_data_deletion(self, user_id: str) -> bool:
        """Request data deletion"""
        return self.privacy_manager.request_data_deletion(user_id)
    
    def record_privacy_consent(self, user_id: str, consent_type: str, consent_given: bool,
                              ip_address: str = None, user_agent: str = None):
        """Record privacy consent"""
        self.privacy_manager.record_consent(user_id, consent_type, consent_given, ip_address, user_agent)
    
    def cleanup_expired_data(self):
        """Clean up expired data"""
        self.privacy_manager.cleanup_expired_data()
    
    def generate_strong_password(self, length: int = 16) -> str:
        """Generate strong password"""
        return self.password_manager.generate_strong_password(length)
    
    def get_security_report(self) -> Dict:
        """Generate security report"""
        try:
            with sqlite3.connect(self.access_control.db_path) as conn:
                # Get user statistics
                user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
                active_users = conn.execute('SELECT COUNT(*) FROM users WHERE is_active = 1').fetchone()[0]
                
                # Get recent security events
                recent_events = conn.execute('''
                    SELECT event_type, severity, description, timestamp 
                    FROM security_events 
                    WHERE timestamp > ? 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                ''', ((datetime.now() - timedelta(days=7)).isoformat(),)).fetchall()
                
                # Get failed login attempts
                failed_logins = conn.execute('''
                    SELECT COUNT(*) FROM audit_log 
                    WHERE event_type = 'login' AND success = 0 
                    AND timestamp > ?
                ''', ((datetime.now() - timedelta(days=7)).isoformat(),)).fetchone()[0]
                
                return {
                    'total_users': user_count,
                    'active_users': active_users,
                    'recent_security_events': len(recent_events),
                    'failed_login_attempts_7d': failed_logins,
                    'encryption_enabled': self.config.encryption_enabled,
                    'audit_logging_enabled': self.config.audit_logging,
                    'gdpr_compliance': self.config.gdpr_compliance
                }
                
        except Exception as e:
            logger.error(f"Error generating security report: {e}")
            return {}

def main():
    """Main function for testing security features"""
    # Create security configuration
    config = SecurityConfig(
        encryption_enabled=True,
        password_required=True,
        session_timeout=3600,
        max_login_attempts=5,
        lockout_duration=900,
        audit_logging=True,
        data_retention_days=365,
        auto_wipe_on_compromise=False,
        privacy_mode=False,
        gdpr_compliance=True
    )
    
    # Initialize security manager
    security_manager = SecurityManager(config)
    
    # Test authentication
    print("Testing authentication...")
    session = security_manager.authenticate_and_create_session(
        username='admin',
        password='admin123',
        ip_address='127.0.0.1',
        user_agent='Test Client'
    )
    
    if session:
        print(f"Authentication successful. Session ID: {session.session_id}")
        
        # Test session validation
        valid_session = security_manager.validate_session(session.session_id)
        if valid_session:
            print("Session validation successful")
        
        # Test permissions
        has_permission = security_manager.check_permission(session.session_id, "admin")
        print(f"Has admin permission: {has_permission}")
        
        # Logout
        security_manager.logout_user(session.session_id)
        print("User logged out")
    else:
        print("Authentication failed")
    
    # Test password generation
    strong_password = security_manager.generate_strong_password()
    print(f"Generated strong password: {strong_password}")
    
    # Test security report
    security_report = security_manager.get_security_report()
    print(f"Security report: {security_report}")
    
    # Test data export
    export_path = security_manager.request_data_export("test_user")
    if export_path:
        print(f"Data export created: {export_path}")

if __name__ == "__main__":
    main() 