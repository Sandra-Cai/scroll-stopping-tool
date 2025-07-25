#!/usr/bin/env python3
"""
Scroll Stopping Tool - Advanced
A Python application to help users break the habit of excessive social media scrolling.
Enhanced version with improved UI, performance, and features.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import time
import threading
import psutil
import schedule
from datetime import datetime, timedelta
import logging
import sys
import os
import platform
import subprocess
import webbrowser
import urllib.parse
import csv
import sqlite3
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scroll_stopping_tool.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Optional imports with better error handling
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    logger.warning("Plyer not available - notifications will be disabled")

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib not available - charts will be disabled")

try:
    from matplotlib.backends.backend_pdf import PdfPages
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as pdf_canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not available - PDF export will be disabled")

try:
    import smtplib
    from email.mime.text import MIMEText
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False
    logger.warning("SMTP not available - email notifications will be disabled")

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not available - SMS notifications will be disabled")

try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    logger.warning("Google API not available - calendar integration will be disabled")

try:
    import qrcode
    from PIL import Image, ImageTk
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    logger.warning("QRCode/PIL not available - QR code features will be disabled")

try:
    from flask import Flask, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask not available - web API will be disabled")

try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logger.warning("Speech recognition not available - voice features will be disabled")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("Pygame not available - audio features will be disabled")

try:
    import ttkbootstrap as tb
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    logger.warning("ttkbootstrap not available - using default tkinter theme")

# Platform-specific imports
if platform.system() == "Windows":
    try:
        import winsound
        WINSOUND_AVAILABLE = True
    except ImportError:
        WINSOUND_AVAILABLE = False
else:
    WINSOUND_AVAILABLE = False

# Data classes for better type safety
@dataclass
class UsageData:
    """Data class for usage statistics"""
    date: str
    total_time: int
    breaks_taken: int
    focus_sessions: int
    productivity_score: float
    goals_met: bool

@dataclass
class FocusSession:
    """Data class for focus session data"""
    start_time: datetime
    end_time: Optional[datetime]
    duration: int
    interruptions: int
    productivity_score: float
    notes: str = ""

@dataclass
class Settings:
    """Data class for application settings"""
    daily_limit: int = 120
    break_reminder: int = 30
    notifications_enabled: bool = True
    auto_break: bool = True
    auto_lock: bool = False
    blocking_enabled: bool = False
    focus_mode_enabled: bool = True
    theme: str = "flatly"
    language: str = "en"

class Theme(Enum):
    """Available themes"""
    FLATLY = "flatly"
    DARKLY = "darkly"
    LITERA = "litera"
    COSMOS = "cosmos"
    SIMPLEX = "simplex"

class NotificationType(Enum):
    """Notification types"""
    BREAK_REMINDER = "break_reminder"
    LIMIT_REACHED = "limit_reached"
    FOCUS_START = "focus_start"
    FOCUS_END = "focus_end"
    ACHIEVEMENT = "achievement"

# Configuration constants
CONFIG_DIR = Path.home() / ".scroll_stopping_tool"
DATA_DIR = CONFIG_DIR / "data"
BACKUP_DIR = CONFIG_DIR / "backups"
LOG_DIR = CONFIG_DIR / "logs"

# Ensure directories exist
for directory in [CONFIG_DIR, DATA_DIR, BACKUP_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "daily_limit": 120,
    "break_reminder": 30,
    "notifications_enabled": True,
    "auto_break": True,
    "auto_lock": False,
    "blocking_enabled": False,
    "focus_mode_enabled": True,
    "theme": "flatly",
    "language": "en",
    "blocked_sites": [
        "facebook.com", "instagram.com", "twitter.com", "tiktok.com",
        "youtube.com", "reddit.com", "snapchat.com", "linkedin.com"
    ],
    "scheduled_breaks": ["12:00", "15:00", "18:00"],
    "goals": {
        "daily_limit": 120,
        "weekly_goal": 5,
        "monthly_goal": 20
    }
}

# Social media detection patterns
SOCIAL_MEDIA_PATTERNS = {
    "processes": [
        'chrome.exe', 'firefox.exe', 'safari.exe', 'msedge.exe',
        'instagram.exe', 'facebook.exe', 'twitter.exe', 'tiktok.exe'
    ],
    "sites": [
        'facebook.com', 'instagram.com', 'twitter.com', 'tiktok.com',
        'youtube.com', 'reddit.com', 'snapchat.com', 'linkedin.com',
        'pinterest.com', 'whatsapp.com', 'telegram.org', 'discord.com'
    ],
    "keywords": [
        'social', 'media', 'feed', 'scroll', 'post', 'share', 'like'
    ]
}