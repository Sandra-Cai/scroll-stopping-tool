#!/usr/bin/env python3
"""
Voice Control Module for Enhanced Scroll Stopping Tool
Voice commands and speech recognition for hands-free operation.
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
import queue
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class VoiceCommand(Enum):
    """Voice command types"""
    START_FOCUS = "start_focus"
    STOP_FOCUS = "stop_focus"
    TAKE_BREAK = "take_break"
    SHOW_STATS = "show_stats"
    START_TRACKING = "start_tracking"
    STOP_TRACKING = "stop_tracking"
    SHOW_ACHIEVEMENTS = "show_achievements"
    HELP = "help"
    EXIT = "exit"

@dataclass
class VoiceCommandData:
    """Voice command data structure"""
    command: VoiceCommand
    confidence: float
    raw_text: str
    timestamp: float

class VoiceController:
    """Voice control system for the scroll stopping tool"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.callback_functions = {}
        self.voice_thread = None
        
        # Configure speech recognition
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Configure text-to-speech
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.8)
        
        # Voice command mappings
        self.command_mappings = {
            "start focus": VoiceCommand.START_FOCUS,
            "begin focus": VoiceCommand.START_FOCUS,
            "focus mode": VoiceCommand.START_FOCUS,
            "stop focus": VoiceCommand.STOP_FOCUS,
            "end focus": VoiceCommand.STOP_FOCUS,
            "take break": VoiceCommand.TAKE_BREAK,
            "break time": VoiceCommand.TAKE_BREAK,
            "show stats": VoiceCommand.SHOW_STATS,
            "show statistics": VoiceCommand.SHOW_STATS,
            "start tracking": VoiceCommand.START_TRACKING,
            "begin tracking": VoiceCommand.START_TRACKING,
            "stop tracking": VoiceCommand.STOP_TRACKING,
            "end tracking": VoiceCommand.STOP_TRACKING,
            "show achievements": VoiceCommand.SHOW_ACHIEVEMENTS,
            "achievements": VoiceCommand.SHOW_ACHIEVEMENTS,
            "help": VoiceCommand.HELP,
            "voice help": VoiceCommand.HELP,
            "exit": VoiceCommand.EXIT,
            "quit": VoiceCommand.EXIT,
            "close": VoiceCommand.EXIT
        }
        
        logger.info("Voice controller initialized")
    
    def start_listening(self):
        """Start listening for voice commands"""
        if self.is_listening:
            logger.warning("Voice controller is already listening")
            return
        
        self.is_listening = True
        self.voice_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.voice_thread.start()
        logger.info("Voice controller started listening")
    
    def stop_listening(self):
        """Stop listening for voice commands"""
        self.is_listening = False
        if self.voice_thread:
            self.voice_thread.join(timeout=1)
        logger.info("Voice controller stopped listening")
    
    def _listen_loop(self):
        """Main listening loop"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    self._process_audio(audio)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    logger.error(f"Error in voice listening: {e}")
                    time.sleep(1)
    
    def _process_audio(self, audio):
        """Process captured audio"""
        try:
            # Recognize speech
            text = self.recognizer.recognize_google(audio).lower()
            logger.info(f"Recognized: {text}")
            
            # Find matching command
            command = self._find_command(text)
            if command:
                confidence = 0.8  # Default confidence for matched commands
                command_data = VoiceCommandData(
                    command=command,
                    confidence=confidence,
                    raw_text=text,
                    timestamp=time.time()
                )
                
                # Add to queue
                self.command_queue.put(command_data)
                
                # Provide audio feedback
                self.speak(f"Executing {command.value.replace('_', ' ')}")
                
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
    
    def _find_command(self, text: str) -> Optional[VoiceCommand]:
        """Find matching voice command"""
        for phrase, command in self.command_mappings.items():
            if phrase in text:
                return command
        return None
    
    def register_callback(self, command: VoiceCommand, callback: Callable):
        """Register callback function for a command"""
        self.callback_functions[command] = callback
        logger.info(f"Registered callback for {command.value}")
    
    def process_commands(self):
        """Process queued voice commands"""
        while not self.command_queue.empty():
            try:
                command_data = self.command_queue.get_nowait()
                callback = self.callback_functions.get(command_data.command)
                
                if callback:
                    callback(command_data)
                else:
                    logger.warning(f"No callback registered for {command_data.command.value}")
                    
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error processing command: {e}")
    
    def speak(self, text: str):
        """Convert text to speech"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
    
    def speak_help(self):
        """Speak available voice commands"""
        help_text = """
        Available voice commands:
        - Start focus or begin focus to start focus mode
        - Stop focus or end focus to stop focus mode
        - Take break or break time for a break
        - Show stats or show statistics for current statistics
        - Start tracking or begin tracking to start usage tracking
        - Stop tracking or end tracking to stop usage tracking
        - Show achievements or achievements to view achievements
        - Help or voice help for this message
        - Exit, quit, or close to exit the application
        """
        self.speak(help_text)
    
    def speak_status(self, status_data: Dict):
        """Speak current status"""
        usage_time = status_data.get('usage_time', 0)
        productivity = status_data.get('productivity_score', 0)
        focus_sessions = status_data.get('focus_sessions', 0)
        
        status_text = f"""
        Current status:
        Usage time: {usage_time} minutes
        Productivity score: {productivity} percent
        Focus sessions today: {focus_sessions}
        """
        self.speak(status_text)
    
    def speak_achievements(self, achievements: List[Dict]):
        """Speak achievements"""
        if not achievements:
            self.speak("No achievements unlocked yet. Keep working towards your goals!")
            return
        
        achievement_text = f"You have unlocked {len(achievements)} achievements: "
        for achievement in achievements[:3]:  # Limit to first 3
            achievement_text += f"{achievement.get('name', 'Unknown')}, "
        
        self.speak(achievement_text)

class VoiceCommandHandler:
    """Handle voice commands and execute actions"""
    
    def __init__(self, voice_controller: VoiceController, app_instance):
        self.voice_controller = voice_controller
        self.app = app_instance
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """Setup callback functions for voice commands"""
        self.voice_controller.register_callback(VoiceCommand.START_FOCUS, self.start_focus)
        self.voice_controller.register_callback(VoiceCommand.STOP_FOCUS, self.stop_focus)
        self.voice_controller.register_callback(VoiceCommand.TAKE_BREAK, self.take_break)
        self.voice_controller.register_callback(VoiceCommand.SHOW_STATS, self.show_stats)
        self.voice_controller.register_callback(VoiceCommand.START_TRACKING, self.start_tracking)
        self.voice_controller.register_callback(VoiceCommand.STOP_TRACKING, self.stop_tracking)
        self.voice_controller.register_callback(VoiceCommand.SHOW_ACHIEVEMENTS, self.show_achievements)
        self.voice_controller.register_callback(VoiceCommand.HELP, self.show_help)
        self.voice_controller.register_callback(VoiceCommand.EXIT, self.exit_app)
    
    def start_focus(self, command_data: VoiceCommandData):
        """Start focus mode via voice command"""
        try:
            if hasattr(self.app, 'start_focus_mode'):
                self.app.start_focus_mode()
                self.voice_controller.speak("Focus mode started. Stay productive!")
            else:
                self.voice_controller.speak("Focus mode not available")
        except Exception as e:
            logger.error(f"Error starting focus mode: {e}")
            self.voice_controller.speak("Error starting focus mode")
    
    def stop_focus(self, command_data: VoiceCommandData):
        """Stop focus mode via voice command"""
        try:
            if hasattr(self.app, 'stop_focus_mode'):
                self.app.stop_focus_mode()
                self.voice_controller.speak("Focus mode stopped. Great work!")
            else:
                self.voice_controller.speak("Focus mode not available")
        except Exception as e:
            logger.error(f"Error stopping focus mode: {e}")
            self.voice_controller.speak("Error stopping focus mode")
    
    def take_break(self, command_data: VoiceCommandData):
        """Take a break via voice command"""
        try:
            if hasattr(self.app, 'take_break'):
                self.app.take_break()
                self.voice_controller.speak("Break time! Take a moment to relax.")
            else:
                self.voice_controller.speak("Break feature not available")
        except Exception as e:
            logger.error(f"Error taking break: {e}")
            self.voice_controller.speak("Error taking break")
    
    def show_stats(self, command_data: VoiceCommandData):
        """Show statistics via voice command"""
        try:
            # Get current status data
            status_data = {
                'usage_time': getattr(self.app, 'today_usage', 0),
                'productivity_score': getattr(self.app, 'productivity_score', 0),
                'focus_sessions': getattr(self.app, 'focus_sessions', 0)
            }
            self.voice_controller.speak_status(status_data)
        except Exception as e:
            logger.error(f"Error showing stats: {e}")
            self.voice_controller.speak("Error retrieving statistics")
    
    def start_tracking(self, command_data: VoiceCommandData):
        """Start tracking via voice command"""
        try:
            if hasattr(self.app, 'start_tracking'):
                self.app.start_tracking()
                self.voice_controller.speak("Usage tracking started")
            else:
                self.voice_controller.speak("Tracking feature not available")
        except Exception as e:
            logger.error(f"Error starting tracking: {e}")
            self.voice_controller.speak("Error starting tracking")
    
    def stop_tracking(self, command_data: VoiceCommandData):
        """Stop tracking via voice command"""
        try:
            if hasattr(self.app, 'stop_tracking'):
                self.app.stop_tracking()
                self.voice_controller.speak("Usage tracking stopped")
            else:
                self.voice_controller.speak("Tracking feature not available")
        except Exception as e:
            logger.error(f"Error stopping tracking: {e}")
            self.voice_controller.speak("Error stopping tracking")
    
    def show_achievements(self, command_data: VoiceCommandData):
        """Show achievements via voice command"""
        try:
            # Get achievements data
            achievements = getattr(self.app, 'achievements', [])
            self.voice_controller.speak_achievements(achievements)
        except Exception as e:
            logger.error(f"Error showing achievements: {e}")
            self.voice_controller.speak("Error retrieving achievements")
    
    def show_help(self, command_data: VoiceCommandData):
        """Show voice command help"""
        self.voice_controller.speak_help()
    
    def exit_app(self, command_data: VoiceCommandData):
        """Exit application via voice command"""
        try:
            self.voice_controller.speak("Exiting application. Goodbye!")
            if hasattr(self.app, 'root'):
                self.app.root.after(2000, self.app.root.quit)
        except Exception as e:
            logger.error(f"Error exiting app: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize voice controller
    voice_controller = VoiceController()
    
    # Start listening
    voice_controller.start_listening()
    
    print("🎤 Voice control system started!")
    print("Say 'help' for available commands")
    
    try:
        while True:
            # Process commands
            voice_controller.process_commands()
            time.sleep(0.1)
    except KeyboardInterrupt:
        voice_controller.stop_listening()
        print("Voice control system stopped") 