#!/usr/bin/env python3
"""
Collaboration Suite for Scroll Stopping Tool
Advanced team productivity and collaboration features
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import threading
import time
import uuid
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging
import queue
import socket
import select
import pickle
import base64
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class TeamMember:
    """Data class for team member information"""
    id: str
    name: str
    email: str
    role: str
    join_date: datetime
    last_active: datetime
    productivity_score: float
    focus_sessions: int
    goals_met: int

@dataclass
class TeamGoal:
    """Data class for team goals"""
    id: str
    name: str
    description: str
    target_value: float
    current_value: float
    deadline: datetime
    created_by: str
    team_members: List[str]
    progress: float
    status: str  # 'active', 'completed', 'overdue'

@dataclass
class FocusSession:
    """Data class for collaborative focus sessions"""
    id: str
    name: str
    host_id: str
    participants: List[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration: int
    topic: str
    status: str  # 'scheduled', 'active', 'completed', 'cancelled'
    notes: str = ""

@dataclass
class TeamAnalytics:
    """Data class for team analytics"""
    team_id: str
    total_focus_time: int
    average_productivity: float
    goals_completed: int
    active_members: int
    weekly_progress: Dict[str, float]
    monthly_trends: Dict[str, float]

class CollaborationServer:
    """Real-time collaboration server"""
    
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.clients = {}
        self.teams = {}
        self.focus_sessions = {}
        self.running = False
        self.server_socket = None
        
    def start_server(self):
        """Start the collaboration server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"Collaboration server started on {self.host}:{self.port}")
            
            # Start client handling thread
            threading.Thread(target=self._handle_clients, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Failed to start collaboration server: {e}")
            raise
    
    def stop_server(self):
        """Stop the collaboration server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("Collaboration server stopped")
    
    def _handle_clients(self):
        """Handle client connections"""
        while self.running:
            try:
                readable, _, _ = select.select([self.server_socket] + list(self.clients.keys()), [], [], 1)
                
                for sock in readable:
                    if sock is self.server_socket:
                        # New client connection
                        client_socket, address = self.server_socket.accept()
                        self.clients[client_socket] = {'address': address, 'data': b''}
                        logger.info(f"New client connected: {address}")
                    else:
                        # Handle existing client
                        self._handle_client_message(sock)
                        
            except Exception as e:
                logger.error(f"Error handling clients: {e}")
    
    def _handle_client_message(self, client_socket):
        """Handle messages from clients"""
        try:
            data = client_socket.recv(4096)
            if not data:
                # Client disconnected
                del self.clients[client_socket]
                client_socket.close()
                return
            
            # Accumulate data
            self.clients[client_socket]['data'] += data
            
            # Try to process complete messages
            while b'\n' in self.clients[client_socket]['data']:
                message_data, remaining = self.clients[client_socket]['data'].split(b'\n', 1)
                self.clients[client_socket]['data'] = remaining
                
                # Process message
                self._process_message(client_socket, message_data)
                
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            if client_socket in self.clients:
                del self.clients[client_socket]
            client_socket.close()
    
    def _process_message(self, client_socket, message_data):
        """Process incoming messages"""
        try:
            message = pickle.loads(message_data)
            message_type = message.get('type')
            
            if message_type == 'join_team':
                self._handle_join_team(client_socket, message)
            elif message_type == 'focus_session':
                self._handle_focus_session(client_socket, message)
            elif message_type == 'goal_update':
                self._handle_goal_update(client_socket, message)
            elif message_type == 'productivity_update':
                self._handle_productivity_update(client_socket, message)
            elif message_type == 'chat_message':
                self._handle_chat_message(client_socket, message)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _handle_join_team(self, client_socket, message):
        """Handle team join requests"""
        team_id = message.get('team_id')
        member_data = message.get('member_data')
        
        if team_id not in self.teams:
            self.teams[team_id] = {'members': {}, 'goals': [], 'sessions': []}
        
        self.teams[team_id]['members'][member_data['id']] = member_data
        self.clients[client_socket]['team_id'] = team_id
        self.clients[client_socket]['member_id'] = member_data['id']
        
        # Notify other team members
        self._broadcast_to_team(team_id, {
            'type': 'member_joined',
            'member_data': member_data
        })
    
    def _handle_focus_session(self, client_socket, message):
        """Handle focus session updates"""
        session_data = message.get('session_data')
        session_id = session_data['id']
        
        if session_id not in self.focus_sessions:
            self.focus_sessions[session_id] = session_data
        else:
            self.focus_sessions[session_id].update(session_data)
        
        # Broadcast to session participants
        for participant_id in session_data.get('participants', []):
            self._broadcast_to_member(participant_id, {
                'type': 'focus_session_update',
                'session_data': session_data
            })
    
    def _handle_goal_update(self, client_socket, message):
        """Handle goal updates"""
        goal_data = message.get('goal_data')
        team_id = self.clients[client_socket].get('team_id')
        
        if team_id and team_id in self.teams:
            # Update goal in team
            goal_id = goal_data['id']
            team_goals = self.teams[team_id]['goals']
            
            for i, goal in enumerate(team_goals):
                if goal['id'] == goal_id:
                    team_goals[i] = goal_data
                    break
            else:
                team_goals.append(goal_data)
            
            # Broadcast to team
            self._broadcast_to_team(team_id, {
                'type': 'goal_updated',
                'goal_data': goal_data
            })
    
    def _handle_productivity_update(self, client_socket, message):
        """Handle productivity updates"""
        productivity_data = message.get('productivity_data')
        team_id = self.clients[client_socket].get('team_id')
        member_id = self.clients[client_socket].get('member_id')
        
        if team_id and member_id:
            # Update member productivity
            if team_id in self.teams and member_id in self.teams[team_id]['members']:
                self.teams[team_id]['members'][member_id].update(productivity_data)
            
            # Broadcast to team
            self._broadcast_to_team(team_id, {
                'type': 'productivity_updated',
                'member_id': member_id,
                'productivity_data': productivity_data
            })
    
    def _handle_chat_message(self, client_socket, message):
        """Handle chat messages"""
        chat_data = message.get('chat_data')
        team_id = self.clients[client_socket].get('team_id')
        
        if team_id:
            # Broadcast to team
            self._broadcast_to_team(team_id, {
                'type': 'chat_message',
                'chat_data': chat_data
            })
    
    def _broadcast_to_team(self, team_id, message):
        """Broadcast message to all team members"""
        if team_id in self.teams:
            for client_socket, client_data in self.clients.items():
                if client_data.get('team_id') == team_id:
                    try:
                        message_bytes = pickle.dumps(message) + b'\n'
                        client_socket.send(message_bytes)
                    except Exception as e:
                        logger.error(f"Error broadcasting to client: {e}")
    
    def _broadcast_to_member(self, member_id, message):
        """Broadcast message to specific member"""
        for client_socket, client_data in self.clients.items():
            if client_data.get('member_id') == member_id:
                try:
                    message_bytes = pickle.dumps(message) + b'\n'
                    client_socket.send(message_bytes)
                except Exception as e:
                    logger.error(f"Error broadcasting to member: {e}")

class CollaborationClient:
    """Real-time collaboration client"""
    
    def __init__(self, server_host='localhost', server_port=5000):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.team_id = None
        self.member_id = None
        self.message_queue = queue.Queue()
        self.callbacks = {}
        
    def connect(self, team_id: str, member_data: dict):
        """Connect to collaboration server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            self.team_id = team_id
            self.member_id = member_data['id']
            
            # Send join team message
            self.send_message({
                'type': 'join_team',
                'team_id': team_id,
                'member_data': member_data
            })
            
            # Start message handling thread
            threading.Thread(target=self._handle_messages, daemon=True).start()
            
            logger.info(f"Connected to collaboration server as {member_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to collaboration server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from collaboration server"""
        self.connected = False
        if self.socket:
            self.socket.close()
        logger.info("Disconnected from collaboration server")
    
    def send_message(self, message: dict):
        """Send message to server"""
        if self.connected and self.socket:
            try:
                message_bytes = pickle.dumps(message) + b'\n'
                self.socket.send(message_bytes)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                self.connected = False
    
    def _handle_messages(self):
        """Handle incoming messages from server"""
        data = b''
        while self.connected:
            try:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                
                data += chunk
                
                while b'\n' in data:
                    message_data, data = data.split(b'\n', 1)
                    message = pickle.loads(message_data)
                    self._process_message(message)
                    
            except Exception as e:
                logger.error(f"Error handling messages: {e}")
                break
        
        self.connected = False
    
    def _process_message(self, message: dict):
        """Process incoming message"""
        message_type = message.get('type')
        
        if message_type in self.callbacks:
            try:
                self.callbacks[message_type](message)
            except Exception as e:
                logger.error(f"Error in message callback: {e}")
    
    def register_callback(self, message_type: str, callback):
        """Register callback for message type"""
        self.callbacks[message_type] = callback
    
    def update_productivity(self, productivity_data: dict):
        """Update productivity data"""
        self.send_message({
            'type': 'productivity_update',
            'productivity_data': productivity_data
        })
    
    def update_goal(self, goal_data: dict):
        """Update goal data"""
        self.send_message({
            'type': 'goal_update',
            'goal_data': goal_data
        })
    
    def send_chat_message(self, message: str, message_type: str = 'text'):
        """Send chat message"""
        chat_data = {
            'id': str(uuid.uuid4()),
            'sender_id': self.member_id,
            'message': message,
            'type': message_type,
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_message({
            'type': 'chat_message',
            'chat_data': chat_data
        })

class TeamManager:
    """Team management and analytics"""
    
    def __init__(self, db_path: str = 'collaboration.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_date TEXT NOT NULL,
                    owner_id TEXT NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS team_members (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    role TEXT NOT NULL,
                    join_date TEXT NOT NULL,
                    last_active TEXT NOT NULL,
                    productivity_score REAL DEFAULT 0,
                    focus_sessions INTEGER DEFAULT 0,
                    goals_met INTEGER DEFAULT 0,
                    FOREIGN KEY (team_id) REFERENCES teams (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS team_goals (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    target_value REAL NOT NULL,
                    current_value REAL DEFAULT 0,
                    deadline TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    progress REAL DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (team_id) REFERENCES teams (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS focus_sessions (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    host_id TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration INTEGER DEFAULT 0,
                    topic TEXT,
                    status TEXT DEFAULT 'scheduled',
                    notes TEXT,
                    FOREIGN KEY (team_id) REFERENCES teams (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS session_participants (
                    session_id TEXT NOT NULL,
                    member_id TEXT NOT NULL,
                    join_time TEXT NOT NULL,
                    leave_time TEXT,
                    duration INTEGER DEFAULT 0,
                    PRIMARY KEY (session_id, member_id),
                    FOREIGN KEY (session_id) REFERENCES focus_sessions (id),
                    FOREIGN KEY (member_id) REFERENCES team_members (id)
                )
            ''')
            
            conn.commit()
    
    def create_team(self, name: str, description: str, owner_id: str) -> str:
        """Create a new team"""
        team_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO teams (id, name, description, created_date, owner_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (team_id, name, description, datetime.now().isoformat(), owner_id))
            conn.commit()
        
        return team_id
    
    def add_member(self, team_id: str, member_data: dict) -> bool:
        """Add member to team"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO team_members 
                    (id, team_id, name, email, role, join_date, last_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    member_data['id'],
                    team_id,
                    member_data['name'],
                    member_data['email'],
                    member_data['role'],
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding member: {e}")
            return False
    
    def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all team members"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM team_members WHERE team_id = ?
            ''', (team_id,))
            
            members = []
            for row in cursor.fetchall():
                members.append(TeamMember(
                    id=row[0],
                    name=row[2],
                    email=row[3],
                    role=row[4],
                    join_date=datetime.fromisoformat(row[5]),
                    last_active=datetime.fromisoformat(row[6]),
                    productivity_score=row[7],
                    focus_sessions=row[8],
                    goals_met=row[9]
                ))
            
            return members
    
    def update_member_productivity(self, member_id: str, productivity_data: dict):
        """Update member productivity data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE team_members 
                SET productivity_score = ?, focus_sessions = ?, goals_met = ?, last_active = ?
                WHERE id = ?
            ''', (
                productivity_data.get('productivity_score', 0),
                productivity_data.get('focus_sessions', 0),
                productivity_data.get('goals_met', 0),
                datetime.now().isoformat(),
                member_id
            ))
            conn.commit()
    
    def create_team_goal(self, team_id: str, goal_data: dict) -> str:
        """Create a new team goal"""
        goal_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO team_goals 
                (id, team_id, name, description, target_value, deadline, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                goal_id,
                team_id,
                goal_data['name'],
                goal_data.get('description', ''),
                goal_data['target_value'],
                goal_data['deadline'],
                goal_data['created_by']
            ))
            conn.commit()
        
        return goal_id
    
    def update_goal_progress(self, goal_id: str, current_value: float):
        """Update goal progress"""
        with sqlite3.connect(self.db_path) as conn:
            # Get goal details
            cursor = conn.execute('''
                SELECT target_value FROM team_goals WHERE id = ?
            ''', (goal_id,))
            row = cursor.fetchone()
            
            if row:
                target_value = row[0]
                progress = min(current_value / target_value * 100, 100)
                status = 'completed' if progress >= 100 else 'active'
                
                conn.execute('''
                    UPDATE team_goals 
                    SET current_value = ?, progress = ?, status = ?
                    WHERE id = ?
                ''', (current_value, progress, status, goal_id))
                conn.commit()
    
    def get_team_analytics(self, team_id: str) -> TeamAnalytics:
        """Get team analytics"""
        with sqlite3.connect(self.db_path) as conn:
            # Get basic stats
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as member_count,
                    AVG(productivity_score) as avg_productivity,
                    SUM(focus_sessions) as total_sessions,
                    SUM(goals_met) as total_goals
                FROM team_members 
                WHERE team_id = ?
            ''', (team_id,))
            
            row = cursor.fetchone()
            if row:
                return TeamAnalytics(
                    team_id=team_id,
                    total_focus_time=row[2] * 25,  # Assume 25 minutes per session
                    average_productivity=row[1] or 0,
                    goals_completed=row[3] or 0,
                    active_members=row[0] or 0,
                    weekly_progress={},
                    monthly_trends={}
                )
            
            return TeamAnalytics(
                team_id=team_id,
                total_focus_time=0,
                average_productivity=0,
                goals_completed=0,
                active_members=0,
                weekly_progress={},
                monthly_trends={}
            )

class CollaborationUI:
    """Collaboration user interface"""
    
    def __init__(self, parent, team_manager: TeamManager, client: CollaborationClient):
        self.parent = parent
        self.team_manager = team_manager
        self.client = client
        self.current_team_id = None
        self.current_member_id = None
        
        # Register callbacks
        self.client.register_callback('member_joined', self._on_member_joined)
        self.client.register_callback('focus_session_update', self._on_focus_session_update)
        self.client.register_callback('goal_updated', self._on_goal_updated)
        self.client.register_callback('productivity_updated', self._on_productivity_updated)
        self.client.register_callback('chat_message', self._on_chat_message)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create collaboration UI widgets"""
        # Main collaboration frame
        self.collab_frame = ttk.LabelFrame(self.parent, text="Team Collaboration", padding="10")
        self.collab_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Team connection section
        self.create_connection_section()
        
        # Team members section
        self.create_members_section()
        
        # Goals section
        self.create_goals_section()
        
        # Focus sessions section
        self.create_sessions_section()
        
        # Chat section
        self.create_chat_section()
        
        # Analytics section
        self.create_analytics_section()
    
    def create_connection_section(self):
        """Create team connection section"""
        conn_frame = ttk.LabelFrame(self.collab_frame, text="Team Connection", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Team ID entry
        ttk.Label(conn_frame, text="Team ID:").grid(row=0, column=0, sticky="w", padx=5)
        self.team_id_var = tk.StringVar()
        self.team_id_entry = ttk.Entry(conn_frame, textvariable=self.team_id_var, width=30)
        self.team_id_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Member info
        ttk.Label(conn_frame, text="Your Name:").grid(row=1, column=0, sticky="w", padx=5)
        self.member_name_var = tk.StringVar()
        self.member_name_entry = ttk.Entry(conn_frame, textvariable=self.member_name_var, width=30)
        self.member_name_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Connect button
        self.connect_btn = ttk.Button(conn_frame, text="Connect to Team", command=self.connect_to_team)
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Not connected")
        self.status_label = ttk.Label(conn_frame, textvariable=self.status_var, foreground="red")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=2)
    
    def create_members_section(self):
        """Create team members section"""
        members_frame = ttk.LabelFrame(self.collab_frame, text="Team Members", padding="5")
        members_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Members listbox
        self.members_listbox = tk.Listbox(members_frame, height=6, width=30)
        self.members_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Refresh button
        refresh_btn = ttk.Button(members_frame, text="Refresh Members", command=self.refresh_members)
        refresh_btn.pack(pady=5)
    
    def create_goals_section(self):
        """Create team goals section"""
        goals_frame = ttk.LabelFrame(self.collab_frame, text="Team Goals", padding="5")
        goals_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Goals treeview
        columns = ('Name', 'Progress', 'Status')
        self.goals_tree = ttk.Treeview(goals_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.goals_tree.heading(col, text=col)
            self.goals_tree.column(col, width=80)
        
        self.goals_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Goal buttons
        goal_btn_frame = ttk.Frame(goals_frame)
        goal_btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(goal_btn_frame, text="Add Goal", command=self.add_goal).pack(side="left", padx=2)
        ttk.Button(goal_btn_frame, text="Update Progress", command=self.update_goal_progress).pack(side="left", padx=2)
    
    def create_sessions_section(self):
        """Create focus sessions section"""
        sessions_frame = ttk.LabelFrame(self.collab_frame, text="Focus Sessions", padding="5")
        sessions_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # Sessions listbox
        self.sessions_listbox = tk.Listbox(sessions_frame, height=4, width=30)
        self.sessions_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Session buttons
        session_btn_frame = ttk.Frame(sessions_frame)
        session_btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(session_btn_frame, text="Host Session", command=self.host_session).pack(side="left", padx=2)
        ttk.Button(session_btn_frame, text="Join Session", command=self.join_session).pack(side="left", padx=2)
    
    def create_chat_section(self):
        """Create chat section"""
        chat_frame = ttk.LabelFrame(self.collab_frame, text="Team Chat", padding="5")
        chat_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        
        # Chat display
        self.chat_display = tk.Text(chat_frame, height=4, width=30, state="disabled")
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Message entry
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(chat_frame, textvariable=self.message_var, width=25)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        # Send button
        send_btn = ttk.Button(chat_frame, text="Send", command=self.send_chat_message)
        send_btn.pack(side="right", padx=5, pady=5)
    
    def create_analytics_section(self):
        """Create analytics section"""
        analytics_frame = ttk.LabelFrame(self.collab_frame, text="Team Analytics", padding="5")
        analytics_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Analytics labels
        self.analytics_labels = {}
        analytics_data = [
            ("Total Focus Time", "0 hours"),
            ("Average Productivity", "0%"),
            ("Goals Completed", "0"),
            ("Active Members", "0")
        ]
        
        for i, (label, value) in enumerate(analytics_data):
            ttk.Label(analytics_frame, text=f"{label}:").grid(row=i//2, column=(i%2)*2, sticky="w", padx=5)
            self.analytics_labels[label] = ttk.Label(analytics_frame, text=value, font=("Arial", 10, "bold"))
            self.analytics_labels[label].grid(row=i//2, column=(i%2)*2+1, sticky="w", padx=5)
        
        # Refresh analytics button
        refresh_analytics_btn = ttk.Button(analytics_frame, text="Refresh Analytics", command=self.refresh_analytics)
        refresh_analytics_btn.grid(row=2, column=0, columnspan=4, pady=5)
    
    def connect_to_team(self):
        """Connect to team"""
        team_id = self.team_id_var.get().strip()
        member_name = self.member_name_var.get().strip()
        
        if not team_id or not member_name:
            messagebox.showerror("Error", "Please enter both Team ID and your name")
            return
        
        # Create member data
        member_data = {
            'id': str(uuid.uuid4()),
            'name': member_name,
            'email': f"{member_name.lower().replace(' ', '.')}@team.com",
            'role': 'Member',
            'productivity_score': 0,
            'focus_sessions': 0,
            'goals_met': 0
        }
        
        # Connect to server
        if self.client.connect(team_id, member_data):
            self.current_team_id = team_id
            self.current_member_id = member_data['id']
            self.status_var.set("Connected")
            self.status_label.config(foreground="green")
            self.connect_btn.config(state="disabled")
            
            # Add member to team in database
            self.team_manager.add_member(team_id, member_data)
            
            # Refresh UI
            self.refresh_members()
            self.refresh_analytics()
        else:
            messagebox.showerror("Error", "Failed to connect to team")
    
    def refresh_members(self):
        """Refresh team members list"""
        if not self.current_team_id:
            return
        
        self.members_listbox.delete(0, tk.END)
        members = self.team_manager.get_team_members(self.current_team_id)
        
        for member in members:
            status = "🟢" if (datetime.now() - member.last_active).seconds < 300 else "🔴"
            self.members_listbox.insert(tk.END, f"{status} {member.name} ({member.role})")
    
    def add_goal(self):
        """Add new team goal"""
        if not self.current_team_id:
            messagebox.showerror("Error", "Not connected to team")
            return
        
        # Simple goal creation dialog
        goal_name = simpledialog.askstring("New Goal", "Goal name:")
        if not goal_name:
            return
        
        goal_description = simpledialog.askstring("New Goal", "Goal description:")
        target_value = simpledialog.askfloat("New Goal", "Target value:")
        
        if target_value is None:
            return
        
        goal_data = {
            'name': goal_name,
            'description': goal_description or '',
            'target_value': target_value,
            'deadline': (datetime.now() + timedelta(days=7)).isoformat(),
            'created_by': self.current_member_id
        }
        
        goal_id = self.team_manager.create_team_goal(self.current_team_id, goal_data)
        goal_data['id'] = goal_id
        
        # Send to server
        self.client.update_goal(goal_data)
        
        # Refresh goals
        self.refresh_goals()
    
    def refresh_goals(self):
        """Refresh goals display"""
        # This would load goals from database and update treeview
        pass
    
    def update_goal_progress(self):
        """Update goal progress"""
        # This would allow updating progress on selected goal
        pass
    
    def host_session(self):
        """Host a focus session"""
        if not self.current_team_id:
            messagebox.showerror("Error", "Not connected to team")
            return
        
        session_name = simpledialog.askstring("Host Session", "Session name:")
        if not session_name:
            return
        
        session_data = {
            'id': str(uuid.uuid4()),
            'name': session_name,
            'host_id': self.current_member_id,
            'participants': [self.current_member_id],
            'start_time': datetime.now().isoformat(),
            'topic': session_name,
            'status': 'active'
        }
        
        # Send to server
        self.client.send_message({
            'type': 'focus_session',
            'session_data': session_data
        })
        
        # Update local display
        self.sessions_listbox.insert(tk.END, f"🎯 {session_name} (Hosting)")
    
    def join_session(self):
        """Join a focus session"""
        # This would allow joining existing sessions
        pass
    
    def send_chat_message(self):
        """Send chat message"""
        message = self.message_var.get().strip()
        if not message:
            return
        
        self.client.send_chat_message(message)
        self.message_var.set("")
    
    def refresh_analytics(self):
        """Refresh team analytics"""
        if not self.current_team_id:
            return
        
        analytics = self.team_manager.get_team_analytics(self.current_team_id)
        
        self.analytics_labels["Total Focus Time"].config(text=f"{analytics.total_focus_time//60} hours")
        self.analytics_labels["Average Productivity"].config(text=f"{analytics.average_productivity:.1f}%")
        self.analytics_labels["Goals Completed"].config(text=str(analytics.goals_completed))
        self.analytics_labels["Active Members"].config(text=str(analytics.active_members))
    
    # Callback methods
    def _on_member_joined(self, message):
        """Handle member joined event"""
        self.refresh_members()
    
    def _on_focus_session_update(self, message):
        """Handle focus session update"""
        session_data = message['session_data']
        # Update sessions display
        pass
    
    def _on_goal_updated(self, message):
        """Handle goal update"""
        self.refresh_goals()
    
    def _on_productivity_updated(self, message):
        """Handle productivity update"""
        self.refresh_members()
        self.refresh_analytics()
    
    def _on_chat_message(self, message):
        """Handle chat message"""
        chat_data = message['chat_data']
        
        self.chat_display.config(state="normal")
        timestamp = datetime.fromisoformat(chat_data['timestamp']).strftime("%H:%M")
        self.chat_display.insert(tk.END, f"[{timestamp}] {chat_data['message']}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

def main():
    """Main function for testing collaboration features"""
    root = tk.Tk()
    root.title("Collaboration Suite - Scroll Stopping Tool")
    root.geometry("800x600")
    
    # Initialize components
    team_manager = TeamManager()
    client = CollaborationClient()
    
    # Create UI
    collaboration_ui = CollaborationUI(root, team_manager, client)
    
    # Start server in background (for testing)
    server = CollaborationServer()
    server_thread = threading.Thread(target=server.start_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(1)
    
    root.mainloop()
    
    # Cleanup
    client.disconnect()
    server.stop_server()

if __name__ == "__main__":
    main() 