#!/usr/bin/env python3
"""
Real-Time Collaboration System
Advanced collaboration features for the scroll stopping tool including
team challenges, shared goals, real-time messaging, and group analytics.
"""

import json
import time
import threading
import asyncio
import websockets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
import logging
from enum import Enum
import sqlite3
import uuid
import hashlib
from pathlib import Path
import queue
import socketio
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Collaboration types"""
    TEAM_CHALLENGE = "team_challenge"
    SHARED_GOAL = "shared_goal"
    ACCOUNTABILITY_PARTNER = "accountability_partner"
    GROUP_STUDY = "group_study"
    WORKSPACE = "workspace"
    COMPETITION = "competition"

class MessageType(Enum):
    """Message types"""
    TEXT = "text"
    ACHIEVEMENT = "achievement"
    CHALLENGE_UPDATE = "challenge_update"
    GOAL_PROGRESS = "goal_progress"
    MOTIVATION = "motivation"
    SYSTEM = "system"

class TeamRole(Enum):
    """Team member roles"""
    LEADER = "leader"
    MEMBER = "member"
    MODERATOR = "moderator"
    OBSERVER = "observer"

@dataclass
class Team:
    """Team definition"""
    id: str
    name: str
    description: str
    type: CollaborationType
    created_by: str
    created_date: datetime
    members: List[str]
    challenges: List[str]
    goals: List[str]
    settings: Dict[str, Any]
    is_active: bool = True

@dataclass
class SharedGoal:
    """Shared goal definition"""
    id: str
    team_id: str
    name: str
    description: str
    target: int
    current: int
    deadline: datetime
    participants: List[str]
    progress_updates: List[Dict[str, Any]]
    is_completed: bool = False

@dataclass
class TeamChallenge:
    """Team challenge definition"""
    id: str
    team_id: str
    name: str
    description: str
    type: str
    duration_days: int
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    participants: List[str]
    progress: Dict[str, float]
    is_active: bool = True
    is_completed: bool = False

@dataclass
class CollaborationMessage:
    """Collaboration message"""
    id: str
    team_id: str
    sender_id: str
    type: MessageType
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    is_system: bool = False

@dataclass
class UserCollaborationProfile:
    """User collaboration profile"""
    user_id: str
    teams: List[str]
    shared_goals: List[str]
    challenges_participated: List[str]
    achievements_shared: List[str]
    messages_sent: int
    last_activity: datetime
    collaboration_score: float

class RealTimeCollaborationSystem:
    """Real-time collaboration system"""
    
    def __init__(self, db_path: str = "productivity.db"):
        self.db_path = db_path
        self.teams = {}
        self.shared_goals = {}
        self.team_challenges = {}
        self.messages = {}
        self.user_profiles = {}
        self.active_connections = {}
        self.message_queue = queue.Queue()
        
        # Initialize Flask app for WebSocket support
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'collaboration_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize WebSocket events
        self._initialize_socket_events()
        
        # Start background processing
        self.processing_thread = threading.Thread(target=self._background_processing, daemon=True)
        self.processing_thread.start()
        
        print("🤝 Real-Time Collaboration System initialized!")
        print("💬 WebSocket messaging active!")
        print("👥 Team features enabled!")
    
    def _initialize_socket_events(self):
        """Initialize WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print(f"Client connected: {request.sid}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"Client disconnected: {request.sid}")
            self._remove_connection(request.sid)
        
        @self.socketio.on('join_team')
        def handle_join_team(data):
            team_id = data.get('team_id')
            user_id = data.get('user_id')
            if team_id and user_id:
                join_room(team_id)
                self.active_connections[request.sid] = {'user_id': user_id, 'team_id': team_id}
                print(f"User {user_id} joined team {team_id}")
        
        @self.socketio.on('leave_team')
        def handle_leave_team(data):
            team_id = data.get('team_id')
            if team_id:
                leave_room(team_id)
                if request.sid in self.active_connections:
                    del self.active_connections[request.sid]
                print(f"User left team {team_id}")
        
        @self.socketio.on('send_message')
        def handle_send_message(data):
            team_id = data.get('team_id')
            user_id = data.get('user_id')
            message_content = data.get('content')
            message_type = data.get('type', 'text')
            
            if team_id and user_id and message_content:
                message = self._create_message(team_id, user_id, message_content, MessageType(message_type))
                self._broadcast_message(message)
                print(f"Message sent in team {team_id}: {message_content[:50]}...")
    
    def create_team(self, name: str, description: str, created_by: str, 
                   collaboration_type: CollaborationType, settings: Dict[str, Any] = None) -> Team:
        """Create a new team"""
        team_id = str(uuid.uuid4())
        
        team = Team(
            id=team_id,
            name=name,
            description=description,
            type=collaboration_type,
            created_by=created_by,
            created_date=datetime.now(),
            members=[created_by],
            challenges=[],
            goals=[],
            settings=settings or {},
            is_active=True
        )
        
        self.teams[team_id] = team
        self._save_team(team)
        
        # Add team to user's profile
        self._add_team_to_user_profile(created_by, team_id)
        
        print(f"🏆 Team '{name}' created by {created_by}")
        return team
    
    def join_team(self, user_id: str, team_id: str) -> bool:
        """Join a team"""
        if team_id not in self.teams:
            return False
        
        team = self.teams[team_id]
        if user_id not in team.members:
            team.members.append(user_id)
            self._save_team(team)
            self._add_team_to_user_profile(user_id, team_id)
            
            # Send system message
            system_message = self._create_system_message(
                team_id, f"{user_id} joined the team!"
            )
            self._broadcast_message(system_message)
            
            print(f"👋 {user_id} joined team '{team.name}'")
            return True
        
        return False
    
    def leave_team(self, user_id: str, team_id: str) -> bool:
        """Leave a team"""
        if team_id not in self.teams:
            return False
        
        team = self.teams[team_id]
        if user_id in team.members:
            team.members.remove(user_id)
            self._save_team(team)
            self._remove_team_from_user_profile(user_id, team_id)
            
            # Send system message
            system_message = self._create_system_message(
                team_id, f"{user_id} left the team."
            )
            self._broadcast_message(system_message)
            
            print(f"👋 {user_id} left team '{team.name}'")
            return True
        
        return False
    
    def create_shared_goal(self, team_id: str, name: str, description: str, 
                          target: int, deadline: datetime, created_by: str) -> SharedGoal:
        """Create a shared goal for a team"""
        goal_id = str(uuid.uuid4())
        
        goal = SharedGoal(
            id=goal_id,
            team_id=team_id,
            name=name,
            description=description,
            target=target,
            current=0,
            deadline=deadline,
            participants=[],
            progress_updates=[]
        )
        
        self.shared_goals[goal_id] = goal
        
        # Add goal to team
        if team_id in self.teams:
            self.teams[team_id].goals.append(goal_id)
            self._save_team(self.teams[team_id])
        
        self._save_shared_goal(goal)
        
        # Send system message
        system_message = self._create_system_message(
            team_id, f"New shared goal created: {name}"
        )
        self._broadcast_message(system_message)
        
        print(f"🎯 Shared goal '{name}' created in team {team_id}")
        return goal
    
    def update_goal_progress(self, goal_id: str, user_id: str, progress: int, 
                           message: str = "") -> bool:
        """Update progress on a shared goal"""
        if goal_id not in self.shared_goals:
            return False
        
        goal = self.shared_goals[goal_id]
        goal.current += progress
        
        # Add progress update
        update = {
            'user_id': user_id,
            'progress': progress,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'new_total': goal.current
        }
        goal.progress_updates.append(update)
        
        # Check if goal is completed
        if goal.current >= goal.target and not goal.is_completed:
            goal.is_completed = True
            self._handle_goal_completion(goal)
        
        self._save_shared_goal(goal)
        
        # Send progress message
        progress_message = self._create_message(
            goal.team_id, user_id, 
            f"Updated goal '{goal.name}': +{progress} progress. {message}",
            MessageType.GOAL_PROGRESS
        )
        self._broadcast_message(progress_message)
        
        print(f"📈 Goal progress updated: {user_id} added {progress} to '{goal.name}'")
        return True
    
    def create_team_challenge(self, team_id: str, name: str, description: str,
                             challenge_type: str, duration_days: int,
                             requirements: Dict[str, Any], rewards: Dict[str, Any],
                             created_by: str) -> TeamChallenge:
        """Create a team challenge"""
        challenge_id = str(uuid.uuid4())
        
        challenge = TeamChallenge(
            id=challenge_id,
            team_id=team_id,
            name=name,
            description=description,
            type=challenge_type,
            duration_days=duration_days,
            requirements=requirements,
            rewards=rewards,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            participants=[],
            progress={}
        )
        
        self.team_challenges[challenge_id] = challenge
        
        # Add challenge to team
        if team_id in self.teams:
            self.teams[team_id].challenges.append(challenge_id)
            self._save_team(self.teams[team_id])
        
        self._save_team_challenge(challenge)
        
        # Send system message
        system_message = self._create_system_message(
            team_id, f"New team challenge started: {name}"
        )
        self._broadcast_message(system_message)
        
        print(f"🏁 Team challenge '{name}' created in team {team_id}")
        return challenge
    
    def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Join a team challenge"""
        if challenge_id not in self.team_challenges:
            return False
        
        challenge = self.team_challenges[challenge_id]
        if user_id not in challenge.participants:
            challenge.participants.append(user_id)
            challenge.progress[user_id] = 0.0
            self._save_team_challenge(challenge)
            
            # Send system message
            system_message = self._create_system_message(
                challenge.team_id, f"{user_id} joined challenge '{challenge.name}'"
            )
            self._broadcast_message(system_message)
            
            print(f"🏁 {user_id} joined challenge '{challenge.name}'")
            return True
        
        return False
    
    def update_challenge_progress(self, challenge_id: str, user_id: str, 
                                progress: float, activity_data: Dict[str, Any]) -> bool:
        """Update progress on a team challenge"""
        if challenge_id not in self.team_challenges:
            return False
        
        challenge = self.team_challenges[challenge_id]
        if user_id not in challenge.participants:
            return False
        
        challenge.progress[user_id] = progress
        self._save_team_challenge(challenge)
        
        # Check if challenge is completed
        if self._check_challenge_completion(challenge):
            self._handle_challenge_completion(challenge)
        
        # Send progress message
        progress_message = self._create_message(
            challenge.team_id, user_id,
            f"Challenge progress: {progress:.1f}% complete in '{challenge.name}'",
            MessageType.CHALLENGE_UPDATE
        )
        self._broadcast_message(progress_message)
        
        print(f"🏁 Challenge progress: {user_id} is {progress:.1f}% complete")
        return True
    
    def share_achievement(self, user_id: str, team_id: str, achievement_name: str,
                         achievement_description: str) -> bool:
        """Share an achievement with the team"""
        if team_id not in self.teams:
            return False
        
        # Create achievement message
        achievement_message = self._create_message(
            team_id, user_id,
            f"🏆 Achievement Unlocked: {achievement_name}",
            MessageType.ACHIEVEMENT
        )
        achievement_message.metadata = {
            'achievement_name': achievement_name,
            'achievement_description': achievement_description
        }
        
        self._broadcast_message(achievement_message)
        
        # Update user profile
        self._add_achievement_to_user_profile(user_id, achievement_name)
        
        print(f"🏆 {user_id} shared achievement: {achievement_name}")
        return True
    
    def send_motivation(self, user_id: str, team_id: str, message: str) -> bool:
        """Send a motivational message to the team"""
        if team_id not in self.teams:
            return False
        
        motivation_message = self._create_message(
            team_id, user_id, message, MessageType.MOTIVATION
        )
        self._broadcast_message(motivation_message)
        
        print(f"💪 {user_id} sent motivation: {message[:50]}...")
        return True
    
    def get_team_analytics(self, team_id: str) -> Dict[str, Any]:
        """Get analytics for a team"""
        if team_id not in self.teams:
            return {"error": "Team not found"}
        
        team = self.teams[team_id]
        
        # Get team goals
        team_goals = [self.shared_goals[goal_id] for goal_id in team.goals 
                     if goal_id in self.shared_goals]
        
        # Get team challenges
        team_challenges = [self.team_challenges[challenge_id] for challenge_id in team.challenges
                          if challenge_id in self.team_challenges]
        
        # Calculate team statistics
        total_members = len(team.members)
        active_goals = len([g for g in team_goals if not g.is_completed])
        completed_goals = len([g for g in team_goals if g.is_completed])
        active_challenges = len([c for c in team_challenges if c.is_active])
        
        # Get recent messages
        recent_messages = self._get_recent_messages(team_id, limit=10)
        
        analytics = {
            "team_info": {
                "name": team.name,
                "description": team.description,
                "type": team.type.value,
                "created_date": team.created_date.isoformat(),
                "total_members": total_members
            },
            "goals": {
                "total": len(team_goals),
                "active": active_goals,
                "completed": completed_goals,
                "completion_rate": completed_goals / len(team_goals) if team_goals else 0
            },
            "challenges": {
                "total": len(team_challenges),
                "active": active_challenges,
                "completed": len(team_challenges) - active_challenges
            },
            "activity": {
                "recent_messages": len(recent_messages),
                "most_active_member": self._get_most_active_member(team_id),
                "message_count": self._get_message_count(team_id)
            },
            "recent_messages": recent_messages
        }
        
        return analytics
    
    def _create_message(self, team_id: str, sender_id: str, content: str, 
                       message_type: MessageType) -> CollaborationMessage:
        """Create a new collaboration message"""
        message_id = str(uuid.uuid4())
        
        message = CollaborationMessage(
            id=message_id,
            team_id=team_id,
            sender_id=sender_id,
            type=message_type,
            content=content,
            timestamp=datetime.now(),
            metadata={}
        )
        
        self.messages[message_id] = message
        self._save_message(message)
        
        return message
    
    def _create_system_message(self, team_id: str, content: str) -> CollaborationMessage:
        """Create a system message"""
        message = self._create_message(team_id, "system", content, MessageType.SYSTEM)
        message.is_system = True
        return message
    
    def _broadcast_message(self, message: CollaborationMessage):
        """Broadcast message to team members"""
        # Add to message queue for processing
        self.message_queue.put(message)
        
        # Emit via WebSocket
        self.socketio.emit('new_message', {
            'id': message.id,
            'team_id': message.team_id,
            'sender_id': message.sender_id,
            'type': message.type.value,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'metadata': message.metadata,
            'is_system': message.is_system
        }, room=message.team_id)
    
    def _check_challenge_completion(self, challenge: TeamChallenge) -> bool:
        """Check if a challenge is completed by all participants"""
        if not challenge.participants:
            return False
        
        # Check if all participants have 100% progress
        for participant in challenge.participants:
            if challenge.progress.get(participant, 0) < 100.0:
                return False
        
        return True
    
    def _handle_challenge_completion(self, challenge: TeamChallenge):
        """Handle challenge completion"""
        challenge.is_completed = True
        challenge.is_active = False
        self._save_team_challenge(challenge)
        
        # Send completion message
        completion_message = self._create_system_message(
            challenge.team_id, f"🎉 Team challenge '{challenge.name}' completed!"
        )
        self._broadcast_message(completion_message)
        
        print(f"🎉 Team challenge '{challenge.name}' completed!")
    
    def _handle_goal_completion(self, goal: SharedGoal):
        """Handle goal completion"""
        # Send completion message
        completion_message = self._create_system_message(
            goal.team_id, f"🎯 Shared goal '{goal.name}' completed!"
        )
        self._broadcast_message(completion_message)
        
        print(f"🎯 Shared goal '{goal.name}' completed!")
    
    def _add_team_to_user_profile(self, user_id: str, team_id: str):
        """Add team to user's collaboration profile"""
        profile = self._get_or_create_user_profile(user_id)
        if team_id not in profile.teams:
            profile.teams.append(team_id)
            self._save_user_profile(profile)
    
    def _remove_team_from_user_profile(self, user_id: str, team_id: str):
        """Remove team from user's collaboration profile"""
        profile = self._get_or_create_user_profile(user_id)
        if team_id in profile.teams:
            profile.teams.remove(team_id)
            self._save_user_profile(profile)
    
    def _add_achievement_to_user_profile(self, user_id: str, achievement_name: str):
        """Add achievement to user's collaboration profile"""
        profile = self._get_or_create_user_profile(user_id)
        if achievement_name not in profile.achievements_shared:
            profile.achievements_shared.append(achievement_name)
            self._save_user_profile(profile)
    
    def _get_or_create_user_profile(self, user_id: str) -> UserCollaborationProfile:
        """Get or create user collaboration profile"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # Check database
        profile = self._load_user_profile(user_id)
        if profile:
            self.user_profiles[user_id] = profile
            return profile
        
        # Create new profile
        profile = UserCollaborationProfile(
            user_id=user_id,
            teams=[],
            shared_goals=[],
            challenges_participated=[],
            achievements_shared=[],
            messages_sent=0,
            last_activity=datetime.now(),
            collaboration_score=0.0
        )
        
        self.user_profiles[user_id] = profile
        self._save_user_profile(profile)
        
        return profile
    
    def _get_recent_messages(self, team_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages for a team"""
        team_messages = [msg for msg in self.messages.values() if msg.team_id == team_id]
        team_messages.sort(key=lambda x: x.timestamp, reverse=True)
        
        recent_messages = []
        for message in team_messages[:limit]:
            recent_messages.append({
                'id': message.id,
                'sender_id': message.sender_id,
                'type': message.type.value,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'is_system': message.is_system
            })
        
        return recent_messages
    
    def _get_most_active_member(self, team_id: str) -> str:
        """Get the most active member in a team"""
        team_messages = [msg for msg in self.messages.values() if msg.team_id == team_id]
        
        if not team_messages:
            return "No activity"
        
        message_counts = {}
        for message in team_messages:
            if not message.is_system:
                message_counts[message.sender_id] = message_counts.get(message.sender_id, 0) + 1
        
        if not message_counts:
            return "No activity"
        
        return max(message_counts, key=message_counts.get)
    
    def _get_message_count(self, team_id: str) -> int:
        """Get total message count for a team"""
        return len([msg for msg in self.messages.values() if msg.team_id == team_id])
    
    def _remove_connection(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
    
    def _background_processing(self):
        """Background processing for collaboration system"""
        while True:
            try:
                # Process message queue
                while not self.message_queue.empty():
                    message = self.message_queue.get_nowait()
                    # Additional processing can be added here
                
                # Update collaboration scores
                self._update_collaboration_scores()
                
                # Clean up old messages
                self._cleanup_old_messages()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in collaboration background processing: {e}")
                time.sleep(60)
    
    def _update_collaboration_scores(self):
        """Update collaboration scores for all users"""
        for user_id, profile in self.user_profiles.items():
            # Calculate collaboration score based on activity
            score = 0.0
            
            # Team participation
            score += len(profile.teams) * 10
            
            # Shared goals
            score += len(profile.shared_goals) * 15
            
            # Challenge participation
            score += len(profile.challenges_participated) * 20
            
            # Achievements shared
            score += len(profile.achievements_shared) * 25
            
            # Messages sent
            score += profile.messages_sent * 2
            
            profile.collaboration_score = min(100.0, score)
            self._save_user_profile(profile)
    
    def _cleanup_old_messages(self):
        """Clean up old messages (keep last 1000 per team)"""
        for team_id in self.teams:
            team_messages = [msg for msg in self.messages.values() if msg.team_id == team_id]
            if len(team_messages) > 1000:
                # Sort by timestamp and keep only the most recent 1000
                team_messages.sort(key=lambda x: x.timestamp)
                messages_to_remove = team_messages[:-1000]
                
                for message in messages_to_remove:
                    del self.messages[message.id]
    
    def _save_team(self, team: Team):
        """Save team to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO teams 
                    (id, name, description, type, created_by, created_date, 
                     members, challenges, goals, settings, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    team.id,
                    team.name,
                    team.description,
                    team.type.value,
                    team.created_by,
                    team.created_date.isoformat(),
                    json.dumps(team.members),
                    json.dumps(team.challenges),
                    json.dumps(team.goals),
                    json.dumps(team.settings),
                    team.is_active
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving team: {e}")
    
    def _save_shared_goal(self, goal: SharedGoal):
        """Save shared goal to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO shared_goals 
                    (id, team_id, name, description, target, current, deadline,
                     participants, progress_updates, is_completed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    goal.id,
                    goal.team_id,
                    goal.name,
                    goal.description,
                    goal.target,
                    goal.current,
                    goal.deadline.isoformat(),
                    json.dumps(goal.participants),
                    json.dumps(goal.progress_updates),
                    goal.is_completed
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving shared goal: {e}")
    
    def _save_team_challenge(self, challenge: TeamChallenge):
        """Save team challenge to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO team_challenges 
                    (id, team_id, name, description, type, duration_days,
                     requirements, rewards, start_date, end_date, participants,
                     progress, is_active, is_completed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    challenge.id,
                    challenge.team_id,
                    challenge.name,
                    challenge.description,
                    challenge.type,
                    challenge.duration_days,
                    json.dumps(challenge.requirements),
                    json.dumps(challenge.rewards),
                    challenge.start_date.isoformat(),
                    challenge.end_date.isoformat(),
                    json.dumps(challenge.participants),
                    json.dumps(challenge.progress),
                    challenge.is_active,
                    challenge.is_completed
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving team challenge: {e}")
    
    def _save_message(self, message: CollaborationMessage):
        """Save message to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO collaboration_messages 
                    (id, team_id, sender_id, type, content, timestamp, metadata, is_system)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.id,
                    message.team_id,
                    message.sender_id,
                    message.type.value,
                    message.content,
                    message.timestamp.isoformat(),
                    json.dumps(message.metadata),
                    message.is_system
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving message: {e}")
    
    def _save_user_profile(self, profile: UserCollaborationProfile):
        """Save user profile to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_collaboration_profiles 
                    (user_id, teams, shared_goals, challenges_participated,
                     achievements_shared, messages_sent, last_activity, collaboration_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    json.dumps(profile.teams),
                    json.dumps(profile.shared_goals),
                    json.dumps(profile.challenges_participated),
                    json.dumps(profile.achievements_shared),
                    profile.messages_sent,
                    profile.last_activity.isoformat(),
                    profile.collaboration_score
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
    
    def _load_user_profile(self, user_id: str) -> Optional[UserCollaborationProfile]:
        """Load user profile from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_collaboration_profiles WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return UserCollaborationProfile(
                        user_id=row[0],
                        teams=json.loads(row[1]),
                        shared_goals=json.loads(row[2]),
                        challenges_participated=json.loads(row[3]),
                        achievements_shared=json.loads(row[4]),
                        messages_sent=row[5],
                        last_activity=datetime.fromisoformat(row[6]),
                        collaboration_score=row[7]
                    )
                
                return None
        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            return None
    
    def run_server(self, host: str = '0.0.0.0', port: int = 5001):
        """Run the collaboration server"""
        print(f"🚀 Starting Collaboration Server on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=False)

# Initialize database tables
def initialize_collaboration_database(db_path: str = "productivity.db"):
    """Initialize database tables for collaboration features"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Teams table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    type TEXT,
                    created_by TEXT,
                    created_date TEXT,
                    members TEXT,
                    challenges TEXT,
                    goals TEXT,
                    settings TEXT,
                    is_active BOOLEAN
                )
            """)
            
            # Shared goals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shared_goals (
                    id TEXT PRIMARY KEY,
                    team_id TEXT,
                    name TEXT,
                    description TEXT,
                    target INTEGER,
                    current INTEGER,
                    deadline TEXT,
                    participants TEXT,
                    progress_updates TEXT,
                    is_completed BOOLEAN
                )
            """)
            
            # Team challenges table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_challenges (
                    id TEXT PRIMARY KEY,
                    team_id TEXT,
                    name TEXT,
                    description TEXT,
                    type TEXT,
                    duration_days INTEGER,
                    requirements TEXT,
                    rewards TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    participants TEXT,
                    progress TEXT,
                    is_active BOOLEAN,
                    is_completed BOOLEAN
                )
            """)
            
            # Collaboration messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collaboration_messages (
                    id TEXT PRIMARY KEY,
                    team_id TEXT,
                    sender_id TEXT,
                    type TEXT,
                    content TEXT,
                    timestamp TEXT,
                    metadata TEXT,
                    is_system BOOLEAN
                )
            """)
            
            # User collaboration profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_collaboration_profiles (
                    user_id TEXT PRIMARY KEY,
                    teams TEXT,
                    shared_goals TEXT,
                    challenges_participated TEXT,
                    achievements_shared TEXT,
                    messages_sent INTEGER,
                    last_activity TEXT,
                    collaboration_score REAL
                )
            """)
            
            conn.commit()
            print("🤝 Collaboration database tables initialized successfully!")
            
    except Exception as e:
        logger.error(f"Error initializing collaboration database: {e}")

if __name__ == "__main__":
    # Initialize database
    initialize_collaboration_database()
    
    # Create collaboration system
    collaboration = RealTimeCollaborationSystem()
    
    # Example usage
    team = collaboration.create_team(
        name="Productivity Warriors",
        description="A team focused on improving productivity and reducing social media usage",
        created_by="user1",
        collaboration_type=CollaborationType.TEAM_CHALLENGE
    )
    
    # Create a shared goal
    goal = collaboration.create_shared_goal(
        team_id=team.id,
        name="Reduce Social Media Usage",
        description="Collectively reduce social media usage by 50%",
        target=1000,  # minutes saved
        deadline=datetime.now() + timedelta(days=30),
        created_by="user1"
    )
    
    # Create a team challenge
    challenge = collaboration.create_team_challenge(
        team_id=team.id,
        name="Focus Week Challenge",
        description="Complete 5 focus sessions each day for a week",
        challenge_type="focus_sessions",
        duration_days=7,
        requirements={"daily_focus_sessions": 5},
        rewards={"xp": 500, "badge": "focus_warrior"},
        created_by="user1"
    )
    
    print("🤝 Collaboration system ready!")
    print("💬 Starting WebSocket server...")
    
    # Run the server
    collaboration.run_server()
