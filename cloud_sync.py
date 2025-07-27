#!/usr/bin/env python3
"""
Cloud Synchronization Module for Scroll Stopping Tool
Enables data backup, multi-device sync, and remote access
"""

import json
import sqlite3
import threading
import time
import hashlib
import base64
import zlib
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import logging
import queue
import requests
from pathlib import Path
import pickle
import tempfile

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class SyncConfig:
    """Configuration for cloud synchronization"""
    enabled: bool = False
    sync_interval: int = 300  # 5 minutes
    auto_backup: bool = True
    backup_interval: int = 86400  # 24 hours
    cloud_provider: str = "local"  # local, dropbox, google_drive, aws
    encryption_enabled: bool = True
    compression_enabled: bool = True
    conflict_resolution: str = "latest"  # latest, manual, merge

@dataclass
class SyncStatus:
    """Status of synchronization operations"""
    last_sync: Optional[datetime] = None
    last_backup: Optional[datetime] = None
    sync_in_progress: bool = False
    backup_in_progress: bool = False
    pending_changes: int = 0
    conflicts: List[Dict] = None
    error_count: int = 0
    last_error: Optional[str] = None

@dataclass
class SyncData:
    """Data structure for synchronization"""
    data_type: str  # usage, settings, analytics, models
    data_hash: str
    timestamp: datetime
    device_id: str
    data: Any
    version: int = 1

class DataEncryption:
    """Data encryption utilities"""
    
    def __init__(self, encryption_key: str = None):
        self.encryption_key = encryption_key or self._generate_key()
    
    def _generate_key(self) -> str:
        """Generate a random encryption key"""
        import secrets
        return secrets.token_hex(32)
    
    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'scroll_stopping_salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))
            
            # Create Fernet cipher
            cipher = Fernet(key)
            return cipher.encrypt(data)
        except ImportError:
            logger.warning("Cryptography not available, using simple encoding")
            return base64.b64encode(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'scroll_stopping_salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))
            
            # Create Fernet cipher
            cipher = Fernet(key)
            return cipher.decrypt(encrypted_data)
        except ImportError:
            logger.warning("Cryptography not available, using simple decoding")
            return base64.b64decode(encrypted_data)

class DataCompression:
    """Data compression utilities"""
    
    @staticmethod
    def compress_data(data: bytes) -> bytes:
        """Compress data using zlib"""
        return zlib.compress(data, level=9)
    
    @staticmethod
    def decompress_data(compressed_data: bytes) -> bytes:
        """Decompress data using zlib"""
        return zlib.decompress(compressed_data)

class LocalCloudProvider:
    """Local file-based cloud provider"""
    
    def __init__(self, sync_dir: str = "cloud_sync"):
        self.sync_dir = Path(sync_dir)
        self.sync_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.sync_dir / "data").mkdir(exist_ok=True)
        (self.sync_dir / "backups").mkdir(exist_ok=True)
        (self.sync_dir / "metadata").mkdir(exist_ok=True)
    
    def upload_data(self, data_type: str, data: bytes, metadata: Dict) -> bool:
        """Upload data to local cloud storage"""
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{data_type}_{timestamp}.dat"
            filepath = self.sync_dir / "data" / filename
            
            # Write data
            with open(filepath, 'wb') as f:
                f.write(data)
            
            # Write metadata
            metadata_file = self.sync_dir / "metadata" / f"{filename}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Error uploading data: {e}")
            return False
    
    def download_data(self, data_type: str, timestamp: str = None) -> Tuple[bytes, Dict]:
        """Download data from local cloud storage"""
        try:
            # Find latest file if timestamp not specified
            if timestamp is None:
                files = list((self.sync_dir / "data").glob(f"{data_type}_*.dat"))
                if not files:
                    return None, {}
                filepath = max(files, key=lambda x: x.stat().st_mtime)
            else:
                filepath = self.sync_dir / "data" / f"{data_type}_{timestamp}.dat"
            
            # Read data
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # Read metadata
            metadata_file = self.sync_dir / "metadata" / f"{filepath.name}.json"
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            return data, metadata
        except Exception as e:
            logger.error(f"Error downloading data: {e}")
            return None, {}
    
    def list_data(self, data_type: str = None) -> List[Dict]:
        """List available data files"""
        try:
            files = []
            pattern = f"{data_type}_*.dat" if data_type else "*.dat"
            
            for filepath in (self.sync_dir / "data").glob(pattern):
                metadata_file = self.sync_dir / "metadata" / f"{filepath.name}.json"
                metadata = {}
                
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                
                files.append({
                    'filename': filepath.name,
                    'size': filepath.stat().st_size,
                    'modified': datetime.fromtimestamp(filepath.stat().st_mtime),
                    'metadata': metadata
                })
            
            return sorted(files, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            logger.error(f"Error listing data: {e}")
            return []
    
    def create_backup(self, backup_name: str) -> bool:
        """Create a backup of all data"""
        try:
            backup_dir = self.sync_dir / "backups" / backup_name
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all data
            shutil.copytree(self.sync_dir / "data", backup_dir / "data", dirs_exist_ok=True)
            shutil.copytree(self.sync_dir / "metadata", backup_dir / "metadata", dirs_exist_ok=True)
            
            # Create backup metadata
            backup_metadata = {
                'backup_name': backup_name,
                'created_at': datetime.now().isoformat(),
                'data_files': len(list((self.sync_dir / "data").glob("*.dat"))),
                'total_size': sum(f.stat().st_size for f in (self.sync_dir / "data").glob("*.dat"))
            }
            
            with open(backup_dir / "backup_info.json", 'w') as f:
                json.dump(backup_metadata, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore data from backup"""
        try:
            backup_dir = self.sync_dir / "backups" / backup_name
            
            if not backup_dir.exists():
                logger.error(f"Backup {backup_name} not found")
                return False
            
            # Restore data
            shutil.rmtree(self.sync_dir / "data", ignore_errors=True)
            shutil.rmtree(self.sync_dir / "metadata", ignore_errors=True)
            
            shutil.copytree(backup_dir / "data", self.sync_dir / "data")
            shutil.copytree(backup_dir / "metadata", self.sync_dir / "metadata")
            
            return True
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False

class DropboxCloudProvider:
    """Dropbox cloud provider"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.dropboxapi.com/2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def upload_data(self, data_type: str, data: bytes, metadata: Dict) -> bool:
        """Upload data to Dropbox"""
        try:
            # Upload file
            filename = f"/scroll_stopping_tool/{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dat"
            
            upload_url = "https://content.dropboxapi.com/2/files/upload"
            upload_headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Dropbox-API-Arg": json.dumps({
                    "path": filename,
                    "mode": "add",
                    "autorename": True,
                    "mute": False
                }),
                "Content-Type": "application/octet-stream"
            }
            
            response = requests.post(upload_url, headers=upload_headers, data=data)
            response.raise_for_status()
            
            # Upload metadata
            metadata_filename = f"/scroll_stopping_tool/metadata/{os.path.basename(filename)}.json"
            metadata_headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Dropbox-API-Arg": json.dumps({
                    "path": metadata_filename,
                    "mode": "add",
                    "autorename": True,
                    "mute": False
                }),
                "Content-Type": "application/octet-stream"
            }
            
            metadata_data = json.dumps(metadata, default=str).encode()
            response = requests.post(upload_url, headers=metadata_headers, data=metadata_data)
            response.raise_for_status()
            
            return True
        except Exception as e:
            logger.error(f"Error uploading to Dropbox: {e}")
            return False
    
    def download_data(self, data_type: str, timestamp: str = None) -> Tuple[bytes, Dict]:
        """Download data from Dropbox"""
        try:
            # List files to find the latest
            list_url = f"{self.base_url}/files/list_folder"
            list_data = {
                "path": "/scroll_stopping_tool",
                "recursive": False
            }
            
            response = requests.post(list_url, headers=self.headers, json=list_data)
            response.raise_for_status()
            
            files = response.json().get("entries", [])
            target_files = [f for f in files if f["name"].startswith(f"{data_type}_")]
            
            if not target_files:
                return None, {}
            
            # Get the latest file
            latest_file = max(target_files, key=lambda x: x["server_modified"])
            
            # Download file
            download_url = "https://content.dropboxapi.com/2/files/download"
            download_headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Dropbox-API-Arg": json.dumps({"path": latest_file["path_lower"]})
            }
            
            response = requests.post(download_url, headers=download_headers)
            response.raise_for_status()
            
            return response.content, {}
        except Exception as e:
            logger.error(f"Error downloading from Dropbox: {e}")
            return None, {}

class CloudSyncManager:
    """Main cloud synchronization manager"""
    
    def __init__(self, config: SyncConfig, device_id: str = None):
        self.config = config
        self.device_id = device_id or self._generate_device_id()
        self.status = SyncStatus()
        
        # Initialize components
        self.encryption = DataEncryption()
        self.compression = DataCompression()
        
        # Initialize cloud provider
        if config.cloud_provider == "local":
            self.cloud_provider = LocalCloudProvider()
        elif config.cloud_provider == "dropbox":
            # This would be initialized with actual Dropbox credentials
            self.cloud_provider = None
        else:
            self.cloud_provider = LocalCloudProvider()
        
        # Sync queue
        self.sync_queue = queue.Queue()
        self.sync_thread = None
        self.running = False
    
    def _generate_device_id(self) -> str:
        """Generate a unique device ID"""
        import platform
        import uuid
        
        system_info = f"{platform.system()}_{platform.machine()}_{platform.node()}"
        device_hash = hashlib.md5(system_info.encode()).hexdigest()[:8]
        return f"device_{device_hash}"
    
    def start_sync_service(self):
        """Start the synchronization service"""
        if self.running:
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
        
        logger.info("Cloud sync service started")
    
    def stop_sync_service(self):
        """Stop the synchronization service"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        
        logger.info("Cloud sync service stopped")
    
    def _sync_worker(self):
        """Background sync worker"""
        while self.running:
            try:
                # Process sync queue
                while not self.sync_queue.empty():
                    sync_item = self.sync_queue.get_nowait()
                    self._process_sync_item(sync_item)
                
                # Auto sync if enabled
                if (self.config.enabled and 
                    (self.status.last_sync is None or 
                     (datetime.now() - self.status.last_sync).seconds >= self.config.sync_interval)):
                    self.sync_all_data()
                
                # Auto backup if enabled
                if (self.config.auto_backup and 
                    (self.status.last_backup is None or 
                     (datetime.now() - self.status.last_backup).seconds >= self.config.backup_interval)):
                    self.create_backup()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in sync worker: {e}")
                self.status.error_count += 1
                self.status.last_error = str(e)
                time.sleep(30)  # Wait longer on error
    
    def _process_sync_item(self, sync_item: Dict):
        """Process a sync queue item"""
        try:
            data_type = sync_item.get('type')
            data = sync_item.get('data')
            
            if data_type and data is not None:
                self._upload_data(data_type, data)
                
        except Exception as e:
            logger.error(f"Error processing sync item: {e}")
    
    def queue_sync(self, data_type: str, data: Any):
        """Queue data for synchronization"""
        if not self.config.enabled:
            return
        
        sync_item = {
            'type': data_type,
            'data': data,
            'timestamp': datetime.now()
        }
        
        self.sync_queue.put(sync_item)
        self.status.pending_changes += 1
    
    def sync_all_data(self):
        """Synchronize all local data"""
        if self.status.sync_in_progress:
            return
        
        self.status.sync_in_progress = True
        
        try:
            # Sync usage data
            self._sync_usage_data()
            
            # Sync settings
            self._sync_settings()
            
            # Sync analytics
            self._sync_analytics()
            
            # Sync ML models
            self._sync_ml_models()
            
            self.status.last_sync = datetime.now()
            self.status.pending_changes = 0
            
            logger.info("Full sync completed successfully")
            
        except Exception as e:
            logger.error(f"Error during full sync: {e}")
            self.status.error_count += 1
            self.status.last_error = str(e)
        
        finally:
            self.status.sync_in_progress = False
    
    def _sync_usage_data(self):
        """Synchronize usage data"""
        try:
            # Export usage data from database
            usage_data = self._export_usage_data()
            
            if usage_data:
                self._upload_data('usage', usage_data)
                
        except Exception as e:
            logger.error(f"Error syncing usage data: {e}")
    
    def _sync_settings(self):
        """Synchronize settings"""
        try:
            settings_file = Path('settings.json')
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings_data = json.load(f)
                
                self._upload_data('settings', settings_data)
                
        except Exception as e:
            logger.error(f"Error syncing settings: {e}")
    
    def _sync_analytics(self):
        """Synchronize analytics data"""
        try:
            analytics_data = self._export_analytics_data()
            
            if analytics_data:
                self._upload_data('analytics', analytics_data)
                
        except Exception as e:
            logger.error(f"Error syncing analytics: {e}")
    
    def _sync_ml_models(self):
        """Synchronize ML models"""
        try:
            models_dir = Path('ml_models')
            if models_dir.exists():
                models_data = {}
                
                for model_file in models_dir.glob("*.pkl"):
                    with open(model_file, 'rb') as f:
                        models_data[model_file.name] = pickle.load(f)
                
                if models_data:
                    self._upload_data('models', models_data)
                    
        except Exception as e:
            logger.error(f"Error syncing ML models: {e}")
    
    def _upload_data(self, data_type: str, data: Any):
        """Upload data to cloud storage"""
        try:
            # Serialize data
            if isinstance(data, (dict, list)):
                serialized_data = json.dumps(data, default=str).encode()
            else:
                serialized_data = pickle.dumps(data)
            
            # Compress if enabled
            if self.config.compression_enabled:
                serialized_data = self.compression.compress_data(serialized_data)
            
            # Encrypt if enabled
            if self.config.encryption_enabled:
                serialized_data = self.encryption.encrypt_data(serialized_data)
            
            # Create metadata
            metadata = {
                'data_type': data_type,
                'device_id': self.device_id,
                'timestamp': datetime.now().isoformat(),
                'compressed': self.config.compression_enabled,
                'encrypted': self.config.encryption_enabled,
                'data_hash': hashlib.md5(serialized_data).hexdigest(),
                'size': len(serialized_data)
            }
            
            # Upload to cloud provider
            if self.cloud_provider:
                success = self.cloud_provider.upload_data(data_type, serialized_data, metadata)
                if success:
                    logger.info(f"Successfully uploaded {data_type} data")
                else:
                    raise Exception(f"Failed to upload {data_type} data")
            
        except Exception as e:
            logger.error(f"Error uploading {data_type} data: {e}")
            raise
    
    def download_data(self, data_type: str) -> Any:
        """Download data from cloud storage"""
        try:
            if not self.cloud_provider:
                return None
            
            # Download from cloud provider
            data, metadata = self.cloud_provider.download_data(data_type)
            
            if data is None:
                return None
            
            # Decrypt if enabled
            if metadata.get('encrypted', False):
                data = self.encryption.decrypt_data(data)
            
            # Decompress if enabled
            if metadata.get('compressed', False):
                data = self.compression.decompress_data(data)
            
            # Deserialize data
            if metadata.get('data_type') in ['settings', 'analytics']:
                return json.loads(data.decode())
            else:
                return pickle.loads(data)
                
        except Exception as e:
            logger.error(f"Error downloading {data_type} data: {e}")
            return None
    
    def _export_usage_data(self) -> Dict:
        """Export usage data from database"""
        try:
            with sqlite3.connect('productivity.db') as conn:
                # Get usage data
                usage_query = "SELECT * FROM usage_data ORDER BY date"
                usage_df = pd.read_sql_query(usage_query, conn)
                
                # Get focus sessions
                sessions_query = "SELECT * FROM focus_sessions ORDER BY start_time"
                sessions_df = pd.read_sql_query(sessions_query, conn)
                
                return {
                    'usage_data': usage_df.to_dict('records'),
                    'focus_sessions': sessions_df.to_dict('records'),
                    'export_timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error exporting usage data: {e}")
            return {}
    
    def _export_analytics_data(self) -> Dict:
        """Export analytics data"""
        try:
            analytics_data = {}
            
            # Export usage statistics
            usage_file = Path('usage_data.json')
            if usage_file.exists():
                with open(usage_file, 'r') as f:
                    analytics_data['usage_stats'] = json.load(f)
            
            # Export productivity data
            productivity_file = Path('productivity.db')
            if productivity_file.exists():
                with sqlite3.connect('productivity.db') as conn:
                    # Get summary statistics
                    summary_query = """
                    SELECT 
                        COUNT(*) as total_sessions,
                        AVG(duration) as avg_duration,
                        AVG(productivity_score) as avg_productivity,
                        SUM(duration) as total_focus_time
                    FROM focus_sessions
                    """
                    summary = conn.execute(summary_query).fetchone()
                    
                    analytics_data['productivity_summary'] = {
                        'total_sessions': summary[0],
                        'avg_duration': summary[1],
                        'avg_productivity': summary[2],
                        'total_focus_time': summary[3]
                    }
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error exporting analytics data: {e}")
            return {}
    
    def create_backup(self, backup_name: str = None):
        """Create a backup of all data"""
        if self.status.backup_in_progress:
            return
        
        self.status.backup_in_progress = True
        
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if isinstance(self.cloud_provider, LocalCloudProvider):
                success = self.cloud_provider.create_backup(backup_name)
                if success:
                    self.status.last_backup = datetime.now()
                    logger.info(f"Backup created: {backup_name}")
                else:
                    raise Exception("Failed to create backup")
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            self.status.error_count += 1
            self.status.last_error = str(e)
        
        finally:
            self.status.backup_in_progress = False
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore data from backup"""
        try:
            if isinstance(self.cloud_provider, LocalCloudProvider):
                success = self.cloud_provider.restore_backup(backup_name)
                if success:
                    logger.info(f"Backup restored: {backup_name}")
                    return True
                else:
                    logger.error(f"Failed to restore backup: {backup_name}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def get_sync_status(self) -> SyncStatus:
        """Get current sync status"""
        return self.status
    
    def get_available_backups(self) -> List[Dict]:
        """Get list of available backups"""
        try:
            if isinstance(self.cloud_provider, LocalCloudProvider):
                backup_dir = self.cloud_provider.sync_dir / "backups"
                backups = []
                
                for backup_path in backup_dir.iterdir():
                    if backup_path.is_dir():
                        backup_info_file = backup_path / "backup_info.json"
                        if backup_info_file.exists():
                            with open(backup_info_file, 'r') as f:
                                backup_info = json.load(f)
                                backups.append(backup_info)
                
                return sorted(backups, key=lambda x: x['created_at'], reverse=True)
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting available backups: {e}")
            return []

class CloudSyncUI:
    """User interface for cloud synchronization"""
    
    def __init__(self, parent, sync_manager: CloudSyncManager):
        self.parent = parent
        self.sync_manager = sync_manager
        
        self.create_widgets()
        self.update_status()
    
    def create_widgets(self):
        """Create cloud sync UI widgets"""
        # Main sync frame
        self.sync_frame = ttk.LabelFrame(self.parent, text="Cloud Synchronization", padding="10")
        self.sync_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configuration section
        self.create_config_section()
        
        # Status section
        self.create_status_section()
        
        # Controls section
        self.create_controls_section()
        
        # Backup section
        self.create_backup_section()
    
    def create_config_section(self):
        """Create configuration section"""
        config_frame = ttk.LabelFrame(self.sync_frame, text="Configuration", padding="5")
        config_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Enable sync checkbox
        self.sync_enabled_var = tk.BooleanVar(value=self.sync_manager.config.enabled)
        sync_check = ttk.Checkbutton(config_frame, text="Enable Cloud Sync", 
                                   variable=self.sync_enabled_var, 
                                   command=self.toggle_sync)
        sync_check.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        # Auto backup checkbox
        self.auto_backup_var = tk.BooleanVar(value=self.sync_manager.config.auto_backup)
        backup_check = ttk.Checkbutton(config_frame, text="Auto Backup", 
                                     variable=self.auto_backup_var,
                                     command=self.toggle_auto_backup)
        backup_check.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Encryption checkbox
        self.encryption_var = tk.BooleanVar(value=self.sync_manager.config.encryption_enabled)
        encryption_check = ttk.Checkbutton(config_frame, text="Encrypt Data", 
                                         variable=self.encryption_var,
                                         command=self.toggle_encryption)
        encryption_check.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        # Compression checkbox
        self.compression_var = tk.BooleanVar(value=self.sync_manager.config.compression_enabled)
        compression_check = ttk.Checkbutton(config_frame, text="Compress Data", 
                                          variable=self.compression_var,
                                          command=self.toggle_compression)
        compression_check.grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    def create_status_section(self):
        """Create status section"""
        status_frame = ttk.LabelFrame(self.sync_frame, text="Sync Status", padding="5")
        status_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Status labels
        self.status_labels = {}
        status_items = [
            ("Last Sync", "Never"),
            ("Last Backup", "Never"),
            ("Pending Changes", "0"),
            ("Sync Status", "Idle"),
            ("Error Count", "0")
        ]
        
        for i, (label, value) in enumerate(status_items):
            ttk.Label(status_frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            self.status_labels[label] = ttk.Label(status_frame, text=value)
            self.status_labels[label].grid(row=i, column=1, sticky="w", padx=5, pady=2)
    
    def create_controls_section(self):
        """Create controls section"""
        controls_frame = ttk.LabelFrame(self.sync_frame, text="Controls", padding="5")
        controls_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Sync button
        self.sync_btn = ttk.Button(controls_frame, text="Sync Now", command=self.sync_now)
        self.sync_btn.pack(fill="x", padx=5, pady=2)
        
        # Download button
        download_btn = ttk.Button(controls_frame, text="Download Data", command=self.download_data)
        download_btn.pack(fill="x", padx=5, pady=2)
        
        # Refresh status button
        refresh_btn = ttk.Button(controls_frame, text="Refresh Status", command=self.update_status)
        refresh_btn.pack(fill="x", padx=5, pady=2)
    
    def create_backup_section(self):
        """Create backup section"""
        backup_frame = ttk.LabelFrame(self.sync_frame, text="Backups", padding="5")
        backup_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Backup listbox
        self.backup_listbox = tk.Listbox(backup_frame, height=4, width=50)
        self.backup_listbox.pack(fill="x", padx=5, pady=5)
        
        # Backup buttons
        backup_btn_frame = ttk.Frame(backup_frame)
        backup_btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(backup_btn_frame, text="Create Backup", command=self.create_backup).pack(side="left", padx=2)
        ttk.Button(backup_btn_frame, text="Restore Backup", command=self.restore_backup).pack(side="left", padx=2)
        ttk.Button(backup_btn_frame, text="Refresh Backups", command=self.refresh_backups).pack(side="left", padx=2)
    
    def toggle_sync(self):
        """Toggle sync enabled"""
        self.sync_manager.config.enabled = self.sync_enabled_var.get()
        if self.sync_manager.config.enabled:
            self.sync_manager.start_sync_service()
        else:
            self.sync_manager.stop_sync_service()
    
    def toggle_auto_backup(self):
        """Toggle auto backup"""
        self.sync_manager.config.auto_backup = self.auto_backup_var.get()
    
    def toggle_encryption(self):
        """Toggle encryption"""
        self.sync_manager.config.encryption_enabled = self.encryption_var.get()
    
    def toggle_compression(self):
        """Toggle compression"""
        self.sync_manager.config.compression_enabled = self.compression_var.get()
    
    def sync_now(self):
        """Trigger manual sync"""
        self.sync_btn.config(state="disabled")
        self.sync_btn.config(text="Syncing...")
        
        # Run sync in background
        threading.Thread(target=self._sync_background, daemon=True).start()
    
    def _sync_background(self):
        """Background sync operation"""
        try:
            self.sync_manager.sync_all_data()
        finally:
            # Re-enable button
            self.parent.after(0, self._sync_complete)
    
    def _sync_complete(self):
        """Sync completed"""
        self.sync_btn.config(state="normal")
        self.sync_btn.config(text="Sync Now")
        self.update_status()
    
    def download_data(self):
        """Download data from cloud"""
        # This would show a dialog to select what data to download
        pass
    
    def update_status(self):
        """Update status display"""
        status = self.sync_manager.get_sync_status()
        
        # Update status labels
        self.status_labels["Last Sync"].config(
            text=status.last_sync.strftime("%Y-%m-%d %H:%M") if status.last_sync else "Never"
        )
        self.status_labels["Last Backup"].config(
            text=status.last_backup.strftime("%Y-%m-%d %H:%M") if status.last_backup else "Never"
        )
        self.status_labels["Pending Changes"].config(text=str(status.pending_changes))
        self.status_labels["Error Count"].config(text=str(status.error_count))
        
        # Update sync status
        if status.sync_in_progress:
            self.status_labels["Sync Status"].config(text="Syncing...", foreground="blue")
        elif status.last_error:
            self.status_labels["Sync Status"].config(text="Error", foreground="red")
        else:
            self.status_labels["Sync Status"].config(text="Idle", foreground="green")
    
    def create_backup(self):
        """Create a new backup"""
        backup_name = f"manual_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.sync_manager.create_backup(backup_name)
        self.refresh_backups()
        self.update_status()
    
    def restore_backup(self):
        """Restore selected backup"""
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a backup to restore")
            return
        
        backup_name = self.backup_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm Restore", f"Restore backup: {backup_name}?"):
            success = self.sync_manager.restore_backup(backup_name)
            if success:
                messagebox.showinfo("Success", "Backup restored successfully")
            else:
                messagebox.showerror("Error", "Failed to restore backup")
    
    def refresh_backups(self):
        """Refresh backup list"""
        self.backup_listbox.delete(0, tk.END)
        
        backups = self.sync_manager.get_available_backups()
        for backup in backups:
            self.backup_listbox.insert(tk.END, backup['backup_name'])

def main():
    """Main function for testing cloud sync"""
    # Create sync configuration
    config = SyncConfig(
        enabled=True,
        sync_interval=300,
        auto_backup=True,
        backup_interval=86400,
        cloud_provider="local",
        encryption_enabled=True,
        compression_enabled=True
    )
    
    # Initialize sync manager
    sync_manager = CloudSyncManager(config)
    
    # Create UI
    root = tk.Tk()
    root.title("Cloud Sync - Scroll Stopping Tool")
    root.geometry("600x500")
    
    sync_ui = CloudSyncUI(root, sync_manager)
    
    # Start sync service
    sync_manager.start_sync_service()
    
    root.mainloop()
    
    # Cleanup
    sync_manager.stop_sync_service()

if __name__ == "__main__":
    main() 