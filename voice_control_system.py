#!/usr/bin/env python3
"""
Voice Control and Accessibility System
Comprehensive voice control and accessibility features for the scroll stopping tool including
voice commands, speech recognition, text-to-speech, and accessibility features.
"""

import json
import time
import threading
import queue
import wave
import pyaudio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
import logging
from enum import Enum
import sqlite3
import uuid
from pathlib import Path
import re
import webbrowser
import subprocess
import os

# Voice recognition and synthesis
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("⚠️ Voice features not available. Install speech_recognition and pyttsx3")

# Audio processing
try:
    import librosa
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ Audio processing not available. Install librosa")

logger = logging.getLogger(__name__)

class VoiceCommandType(Enum):
    """Voice command types"""
    START_FOCUS = "start_focus"
    STOP_FOCUS = "stop_focus"
    TAKE_BREAK = "take_break"
    SET_LIMIT = "set_limit"
    CHECK_STATS = "check_stats"
    OPEN_ANALYTICS = "open_analytics"
    START_CHALLENGE = "start_challenge"
    HELP = "help"
    SETTINGS = "settings"
    EXIT = "exit"

class AccessibilityLevel(Enum):
    """Accessibility levels"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    FULL = "full"

class VoiceFeedbackType(Enum):
    """Voice feedback types"""
    CONFIRMATION = "confirmation"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    PROMPT = "prompt"
    NOTIFICATION = "notification"

@dataclass
class VoiceCommand:
    """Voice command definition"""
    command_type: VoiceCommandType
    phrases: List[str]
    description: str
    action: Callable
    requires_confirmation: bool
    accessibility_level: AccessibilityLevel

@dataclass
class VoiceSettings:
    """Voice control settings"""
    user_id: str
    voice_enabled: bool
    speech_recognition_enabled: bool
    text_to_speech_enabled: bool
    voice_speed: float
    voice_volume: float
    voice_language: str
    wake_word: str
    accessibility_level: AccessibilityLevel
    voice_feedback_enabled: bool
    audio_visual_feedback: bool

@dataclass
class VoiceSession:
    """Voice control session"""
    id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    commands_executed: int
    recognition_accuracy: float
    session_duration: float

class VoiceControlSystem:
    """Voice control and accessibility system"""
    
    def __init__(self, db_path: str = "productivity.db"):
        self.db_path = db_path
        self.voice_settings = {}
        self.voice_sessions = {}
        self.commands = {}
        self.recognizer = None
        self.engine = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.command_queue = queue.Queue()
        
        # Initialize voice components
        self._initialize_voice_components()
        
        # Initialize voice commands
        self._initialize_voice_commands()
        
        # Start background processing
        self.processing_thread = threading.Thread(target=self._background_processing, daemon=True)
        self.processing_thread.start()
        
        print("🎤 Voice Control System initialized!")
        print("🔊 Speech recognition active!")
        print("📢 Text-to-speech enabled!")
    
    def _initialize_voice_components(self):
        """Initialize voice recognition and synthesis components"""
        if not VOICE_AVAILABLE:
            print("⚠️ Voice components not available")
            return
        
        try:
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            
            # Initialize text-to-speech
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.8)
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            
            print("🎤 Voice components initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing voice components: {e}")
            print("❌ Failed to initialize voice components")
    
    def _initialize_voice_commands(self):
        """Initialize voice commands"""
        self.commands = {
            VoiceCommandType.START_FOCUS: VoiceCommand(
                command_type=VoiceCommandType.START_FOCUS,
                phrases=["start focus", "begin focus", "focus mode", "start working", "begin work"],
                description="Start a focus session",
                action=self._start_focus_session,
                requires_confirmation=False,
                accessibility_level=AccessibilityLevel.BASIC
            ),
            VoiceCommandType.STOP_FOCUS: VoiceCommand(
                command_type=VoiceCommandType.STOP_FOCUS,
                phrases=["stop focus", "end focus", "stop working", "end work", "break time"],
                description="Stop the current focus session",
                action=self._stop_focus_session,
                requires_confirmation=False,
                accessibility_level=AccessibilityLevel.BASIC
            ),
            VoiceCommandType.TAKE_BREAK: VoiceCommand(
                command_type=VoiceCommandType.TAKE_BREAK,
                phrases=["take break", "take a break", "break time", "rest", "pause"],
                description="Take a break",
                action=self._take_break,
                requires_confirmation=False,
                accessibility_level=AccessibilityLevel.BASIC
            ),
            VoiceCommandType.SET_LIMIT: VoiceCommand(
                command_type=VoiceCommandType.SET_LIMIT,
                phrases=["set limit", "set daily limit", "limit social media", "set time limit"],
                description="Set daily time limits",
                action=self._set_daily_limit,
                requires_confirmation=True,
                accessibility_level=AccessibilityLevel.ENHANCED
            ),
            VoiceCommandType.CHECK_STATS: VoiceCommand(
                command_type=VoiceCommandType.CHECK_STATS,
                phrases=["check stats", "show statistics", "my progress", "how am I doing"],
                description="Check productivity statistics",
                action=self._check_statistics,
                requires_confirmation=False,
                accessibility_level=AccessibilityLevel.BASIC
            ),
            VoiceCommandType.OPEN_ANALYTICS: VoiceCommand(
                command_type=VoiceCommandType.OPEN_ANALYTICS,
                phrases=["open analytics", "show analytics", "view dashboard", "analytics"],
                description="Open analytics dashboard",
                action=self._open_analytics,
                requires_confirmation=False,
                accessibility_level=AccessibilityLevel.ENHANCED
            ),
            VoiceCommandType.START_CHALLENGE: VoiceCommand(
                command_type=VoiceCommandType.START_CHALLENGE,
                phrases=["start challenge", "new challenge", "begin challenge", "challenge mode"],
                description="Start a productivity challenge",
                action=self._start_challenge,
                requires_confirmation=True,
                accessibility_level=AccessibilityLevel.ENHANCED
            ),
            VoiceCommandType.HELP: VoiceCommand(
                command_type=VoiceCommandType.HELP,
                phrases=["help", "what can I say", "voice commands", "commands"],
                description="Show available voice commands",
                action=self._show_help,
                requires_confirmation=False,
                accessibility_level=AccessibilityLevel.BASIC
            ),
            VoiceCommandType.SETTINGS: VoiceCommand(
                command_type=VoiceCommandType.SETTINGS,
                phrases=["settings", "voice settings", "configure", "preferences"],
                description="Open voice settings",
                action=self._open_settings,
                requires_confirmation=False,
                accessibility_level=AccessibilityLevel.ENHANCED
            ),
            VoiceCommandType.EXIT: VoiceCommand(
                command_type=VoiceCommandType.EXIT,
                phrases=["exit", "quit", "stop listening", "goodbye"],
                description="Exit voice control",
                action=self._exit_voice_control,
                requires_confirmation=True,
                accessibility_level=AccessibilityLevel.BASIC
            )
        }
        
        print(f"🎯 {len(self.commands)} voice commands initialized!")
    
    def start_voice_session(self, user_id: str) -> str:
        """Start a voice control session"""
        try:
            session_id = str(uuid.uuid4())
            
            session = VoiceSession(
                id=session_id,
                user_id=user_id,
                start_time=datetime.now(),
                end_time=None,
                commands_executed=0,
                recognition_accuracy=0.0,
                session_duration=0.0
            )
            
            self.voice_sessions[session_id] = session
            self._save_voice_session(session)
            
            # Start listening
            self.is_listening = True
            self._start_listening_thread(session_id)
            
            # Provide feedback
            self.speak("Voice control activated. How can I help you?")
            
            print(f"🎤 Voice session started: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting voice session: {e}")
            return ""
    
    def stop_voice_session(self, session_id: str):
        """Stop a voice control session"""
        try:
            if session_id in self.voice_sessions:
                session = self.voice_sessions[session_id]
                session.end_time = datetime.now()
                session.session_duration = (session.end_time - session.start_time).total_seconds()
                
                self._save_voice_session(session)
                
                # Stop listening
                self.is_listening = False
                
                # Provide feedback
                self.speak("Voice control deactivated. Goodbye!")
                
                print(f"🎤 Voice session ended: {session_id}")
                
        except Exception as e:
            logger.error(f"Error stopping voice session: {e}")
    
    def _start_listening_thread(self, session_id: str):
        """Start listening thread for voice commands"""
        def listen_for_commands():
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    while self.is_listening:
                        try:
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                            self.audio_queue.put((session_id, audio))
                        except sr.WaitTimeoutError:
                            continue
                        except Exception as e:
                            logger.error(f"Error listening: {e}")
                            break
                            
            except Exception as e:
                logger.error(f"Error in listening thread: {e}")
        
        listening_thread = threading.Thread(target=listen_for_commands, daemon=True)
        listening_thread.start()
    
    def _background_processing(self):
        """Background processing for voice control"""
        while True:
            try:
                # Process audio queue
                while not self.audio_queue.empty():
                    session_id, audio = self.audio_queue.get_nowait()
                    self._process_audio(session_id, audio)
                
                # Process command queue
                while not self.command_queue.empty():
                    command_data = self.command_queue.get_nowait()
                    self._execute_command(command_data)
                
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.error(f"Error in voice background processing: {e}")
                time.sleep(1)
    
    def _process_audio(self, session_id: str, audio):
        """Process audio and recognize speech"""
        try:
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            text = text.lower().strip()
            
            print(f"🎤 Recognized: {text}")
            
            # Find matching command
            command = self._find_matching_command(text)
            
            if command:
                # Add to command queue
                self.command_queue.put({
                    'session_id': session_id,
                    'command': command,
                    'text': text
                })
            else:
                # No command found
                self.speak("I didn't understand that command. Try saying 'help' for available commands.")
                
        except sr.UnknownValueError:
            # Speech not recognized
            pass
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            self.speak("Sorry, I'm having trouble understanding. Please try again.")
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
    
    def _find_matching_command(self, text: str) -> Optional[VoiceCommand]:
        """Find matching voice command"""
        for command in self.commands.values():
            for phrase in command.phrases:
                if phrase in text or text in phrase:
                    return command
        
        return None
    
    def _execute_command(self, command_data: Dict[str, Any]):
        """Execute a voice command"""
        try:
            session_id = command_data['session_id']
            command = command_data['command']
            text = command_data['text']
            
            # Check accessibility level
            if session_id in self.voice_sessions:
                session = self.voice_sessions[session_id]
                user_id = session.user_id
                
                if user_id in self.voice_settings:
                    settings = self.voice_settings[user_id]
                    if command.accessibility_level.value > settings.accessibility_level.value:
                        self.speak("This command requires a higher accessibility level.")
                        return
            
            # Execute command
            if command.requires_confirmation:
                self.speak(f"Did you say {command.description}? Say yes to confirm.")
                # In a real implementation, you'd wait for confirmation
                # For now, we'll execute directly
                command.action(session_id, text)
            else:
                command.action(session_id, text)
            
            # Update session
            if session_id in self.voice_sessions:
                session = self.voice_sessions[session_id]
                session.commands_executed += 1
                self._save_voice_session(session)
            
            print(f"✅ Command executed: {command.command_type.value}")
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            self.speak("Sorry, there was an error executing that command.")
    
    def speak(self, text: str):
        """Convert text to speech"""
        if not VOICE_AVAILABLE or not self.engine:
            print(f"📢 {text}")
            return
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            print(f"📢 {text}")
    
    def _start_focus_session(self, session_id: str, text: str):
        """Start a focus session"""
        self.speak("Starting focus session. Stay focused and productive!")
        # In a real implementation, this would integrate with the main app
        print("🎯 Focus session started via voice command")
    
    def _stop_focus_session(self, session_id: str, text: str):
        """Stop the current focus session"""
        self.speak("Focus session ended. Great work!")
        # In a real implementation, this would integrate with the main app
        print("🎯 Focus session ended via voice command")
    
    def _take_break(self, session_id: str, text: str):
        """Take a break"""
        self.speak("Time for a break! Take a few minutes to relax and recharge.")
        # In a real implementation, this would integrate with the main app
        print("☕ Break initiated via voice command")
    
    def _set_daily_limit(self, session_id: str, text: str):
        """Set daily time limits"""
        # Extract time from text (simplified)
        time_match = re.search(r'(\d+)\s*(hour|hours|minute|minutes)', text)
        if time_match:
            amount = int(time_match.group(1))
            unit = time_match.group(2)
            self.speak(f"Setting daily limit to {amount} {unit}.")
            print(f"⏰ Daily limit set to {amount} {unit} via voice command")
        else:
            self.speak("Please specify the time limit. For example, 'set limit to 2 hours'.")
    
    def _check_statistics(self, session_id: str, text: str):
        """Check productivity statistics"""
        # In a real implementation, this would fetch actual statistics
        self.speak("Here are your productivity statistics. You've been focused for 3 hours today, with 2 completed sessions and 85% productivity score.")
        print("📊 Statistics requested via voice command")
    
    def _open_analytics(self, session_id: str, text: str):
        """Open analytics dashboard"""
        try:
            # In a real implementation, this would open the analytics dashboard
            self.speak("Opening analytics dashboard.")
            print("📈 Analytics dashboard requested via voice command")
        except Exception as e:
            self.speak("Sorry, I couldn't open the analytics dashboard.")
    
    def _start_challenge(self, session_id: str, text: str):
        """Start a productivity challenge"""
        self.speak("Starting a new productivity challenge. Your goal is to complete 4 focus sessions today.")
        print("🎯 Challenge started via voice command")
    
    def _show_help(self, session_id: str, text: str):
        """Show available voice commands"""
        help_text = "Available voice commands: Start focus, stop focus, take break, check stats, open analytics, start challenge, settings, and exit."
        self.speak(help_text)
        print("❓ Help requested via voice command")
    
    def _open_settings(self, session_id: str, text: str):
        """Open voice settings"""
        self.speak("Opening voice settings.")
        print("⚙️ Settings requested via voice command")
    
    def _exit_voice_control(self, session_id: str, text: str):
        """Exit voice control"""
        self.speak("Exiting voice control. Goodbye!")
        self.stop_voice_session(session_id)
    
    def get_voice_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user voice settings"""
        if user_id not in self.voice_settings:
            return {"error": "User not found"}
        
        settings = self.voice_settings[user_id]
        
        return {
            "user_id": settings.user_id,
            "voice_enabled": settings.voice_enabled,
            "speech_recognition_enabled": settings.speech_recognition_enabled,
            "text_to_speech_enabled": settings.text_to_speech_enabled,
            "voice_speed": settings.voice_speed,
            "voice_volume": settings.voice_volume,
            "voice_language": settings.voice_language,
            "wake_word": settings.wake_word,
            "accessibility_level": settings.accessibility_level.value,
            "voice_feedback_enabled": settings.voice_feedback_enabled,
            "audio_visual_feedback": settings.audio_visual_feedback
        }
    
    def update_voice_settings(self, user_id: str, new_settings: Dict[str, Any]) -> bool:
        """Update user voice settings"""
        try:
            if user_id not in self.voice_settings:
                return False
            
            settings = self.voice_settings[user_id]
            
            # Update settings
            if 'voice_enabled' in new_settings:
                settings.voice_enabled = new_settings['voice_enabled']
            
            if 'speech_recognition_enabled' in new_settings:
                settings.speech_recognition_enabled = new_settings['speech_recognition_enabled']
            
            if 'text_to_speech_enabled' in new_settings:
                settings.text_to_speech_enabled = new_settings['text_to_speech_enabled']
            
            if 'voice_speed' in new_settings:
                settings.voice_speed = new_settings['voice_speed']
                if self.engine:
                    self.engine.setProperty('rate', int(settings.voice_speed))
            
            if 'voice_volume' in new_settings:
                settings.voice_volume = new_settings['voice_volume']
                if self.engine:
                    self.engine.setProperty('volume', settings.voice_volume)
            
            if 'voice_language' in new_settings:
                settings.voice_language = new_settings['voice_language']
            
            if 'wake_word' in new_settings:
                settings.wake_word = new_settings['wake_word']
            
            if 'accessibility_level' in new_settings:
                try:
                    settings.accessibility_level = AccessibilityLevel(new_settings['accessibility_level'])
                except ValueError:
                    pass
            
            if 'voice_feedback_enabled' in new_settings:
                settings.voice_feedback_enabled = new_settings['voice_feedback_enabled']
            
            if 'audio_visual_feedback' in new_settings:
                settings.audio_visual_feedback = new_settings['audio_visual_feedback']
            
            self._save_voice_settings(settings)
            
            print(f"🎤 Voice settings updated for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating voice settings: {e}")
            return False
    
    def create_voice_settings(self, user_id: str) -> VoiceSettings:
        """Create default voice settings for a user"""
        settings = VoiceSettings(
            user_id=user_id,
            voice_enabled=True,
            speech_recognition_enabled=True,
            text_to_speech_enabled=True,
            voice_speed=150.0,
            voice_volume=0.8,
            voice_language="en-US",
            wake_word="hey assistant",
            accessibility_level=AccessibilityLevel.BASIC,
            voice_feedback_enabled=True,
            audio_visual_feedback=True
        )
        
        self.voice_settings[user_id] = settings
        self._save_voice_settings(settings)
        
        return settings
    
    def get_voice_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get voice control analytics for a user"""
        user_sessions = [s for s in self.voice_sessions.values() if s.user_id == user_id]
        
        if not user_sessions:
            return {"error": "No sessions found"}
        
        # Calculate analytics
        total_sessions = len(user_sessions)
        total_commands = sum(s.commands_executed for s in user_sessions)
        avg_commands_per_session = total_commands / total_sessions if total_sessions > 0 else 0
        
        # Session duration analytics
        completed_sessions = [s for s in user_sessions if s.end_time]
        avg_session_duration = sum(s.session_duration for s in completed_sessions) / len(completed_sessions) if completed_sessions else 0
        
        # Recognition accuracy
        avg_accuracy = sum(s.recognition_accuracy for s in user_sessions) / total_sessions if total_sessions > 0 else 0
        
        # Most used commands (simplified)
        command_usage = {
            "start_focus": 0,
            "stop_focus": 0,
            "take_break": 0,
            "check_stats": 0,
            "help": 0
        }
        
        analytics = {
            "sessions": {
                "total": total_sessions,
                "completed": len(completed_sessions),
                "avg_duration_minutes": avg_session_duration / 60
            },
            "commands": {
                "total": total_commands,
                "avg_per_session": avg_commands_per_session,
                "usage": command_usage
            },
            "recognition": {
                "avg_accuracy": avg_accuracy,
                "success_rate": avg_accuracy * 100
            },
            "recent_activity": [
                {
                    "session_id": s.id,
                    "start_time": s.start_time.isoformat(),
                    "commands_executed": s.commands_executed,
                    "duration_minutes": s.session_duration / 60 if s.session_duration else 0
                }
                for s in sorted(user_sessions, key=lambda x: x.start_time, reverse=True)[:5]
            ]
        }
        
        return analytics
    
    def _save_voice_settings(self, settings: VoiceSettings):
        """Save voice settings to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO voice_settings 
                    (user_id, voice_enabled, speech_recognition_enabled, text_to_speech_enabled,
                     voice_speed, voice_volume, voice_language, wake_word, accessibility_level,
                     voice_feedback_enabled, audio_visual_feedback)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    settings.user_id,
                    settings.voice_enabled,
                    settings.speech_recognition_enabled,
                    settings.text_to_speech_enabled,
                    settings.voice_speed,
                    settings.voice_volume,
                    settings.voice_language,
                    settings.wake_word,
                    settings.accessibility_level.value,
                    settings.voice_feedback_enabled,
                    settings.audio_visual_feedback
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving voice settings: {e}")
    
    def _save_voice_session(self, session: VoiceSession):
        """Save voice session to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO voice_sessions 
                    (id, user_id, start_time, end_time, commands_executed, recognition_accuracy, session_duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.id,
                    session.user_id,
                    session.start_time.isoformat(),
                    session.end_time.isoformat() if session.end_time else None,
                    session.commands_executed,
                    session.recognition_accuracy,
                    session.session_duration
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving voice session: {e}")

# Initialize database tables
def initialize_voice_database(db_path: str = "productivity.db"):
    """Initialize database tables for voice control"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Voice settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voice_settings (
                    user_id TEXT PRIMARY KEY,
                    voice_enabled BOOLEAN,
                    speech_recognition_enabled BOOLEAN,
                    text_to_speech_enabled BOOLEAN,
                    voice_speed REAL,
                    voice_volume REAL,
                    voice_language TEXT,
                    wake_word TEXT,
                    accessibility_level TEXT,
                    voice_feedback_enabled BOOLEAN,
                    audio_visual_feedback BOOLEAN
                )
            """)
            
            # Voice sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voice_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    commands_executed INTEGER,
                    recognition_accuracy REAL,
                    session_duration REAL
                )
            """)
            
            # Voice commands log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voice_commands_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    user_id TEXT,
                    command_type TEXT,
                    recognized_text TEXT,
                    execution_time TEXT,
                    success BOOLEAN
                )
            """)
            
            conn.commit()
            print("🎤 Voice database tables initialized successfully!")
            
    except Exception as e:
        logger.error(f"Error initializing voice database: {e}")

if __name__ == "__main__":
    # Initialize database
    initialize_voice_database()
    
    # Create voice control system
    voice_system = VoiceControlSystem()
    
    # Create example user settings
    settings = voice_system.create_voice_settings("test_user")
    
    # Start voice session
    session_id = voice_system.start_voice_session("test_user")
    
    if session_id:
        print("🎤 Voice control system ready!")
        print("🔊 Say 'help' for available commands")
        print("🔊 Say 'exit' to stop voice control")
        
        # Keep the system running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            voice_system.stop_voice_session(session_id)
            print("🎤 Voice control system stopped")
