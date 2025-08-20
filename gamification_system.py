#!/usr/bin/env python3
"""
Advanced Gamification System
Comprehensive gamification engine for the scroll stopping tool with achievements,
levels, challenges, rewards, and social features.
"""

import json
import time
import threading
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from enum import Enum
import sqlite3
import hashlib
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Achievement types"""
    DAILY_STREAK = "daily_streak"
    FOCUS_SESSION = "focus_session"
    TIME_SAVED = "time_saved"
    GOAL_COMPLETION = "goal_completion"
    SOCIAL_MEDIA_FREE = "social_media_free"
    PRODUCTIVITY_MILESTONE = "productivity_milestone"
    CONSISTENCY = "consistency"
    BREAK_MASTER = "break_master"
    FOCUS_MASTER = "focus_master"
    WELLNESS_CHAMPION = "wellness_champion"

class ChallengeType(Enum):
    """Challenge types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIAL = "special"
    SOCIAL = "social"
    COMPETITIVE = "competitive"

class RewardType(Enum):
    """Reward types"""
    XP = "xp"
    BADGE = "badge"
    TITLE = "title"
    FEATURE_UNLOCK = "feature_unlock"
    CUSTOMIZATION = "customization"
    SOCIAL_RECOGNITION = "social_recognition"

@dataclass
class Achievement:
    """Achievement definition"""
    id: str
    name: str
    description: str
    type: AchievementType
    icon: str
    xp_reward: int
    rarity: str  # common, rare, epic, legendary
    requirements: Dict[str, Any]
    unlocked: bool = False
    unlocked_date: Optional[datetime] = None
    progress: float = 0.0

@dataclass
class Challenge:
    """Challenge definition"""
    id: str
    name: str
    description: str
    type: ChallengeType
    duration_days: int
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    active: bool = True
    completed: bool = False
    progress: float = 0.0
    participants: List[str] = None

@dataclass
class UserProfile:
    """User gamification profile"""
    user_id: str
    level: int
    xp: int
    total_xp: int
    streak_days: int
    best_streak: int
    achievements_unlocked: int
    challenges_completed: int
    rank: str
    title: str
    badges: List[str]
    last_activity: datetime
    created_date: datetime

@dataclass
class Reward:
    """Reward definition"""
    id: str
    name: str
    description: str
    type: RewardType
    value: Any
    icon: str
    rarity: str
    unlocked_date: Optional[datetime] = None

class GamificationSystem:
    """Advanced gamification system"""
    
    def __init__(self, db_path: str = "productivity.db"):
        self.db_path = db_path
        self.achievements = {}
        self.challenges = {}
        self.user_profiles = {}
        self.rewards = {}
        self.leaderboard_cache = {}
        self.notification_queue = []
        
        # Initialize achievements and challenges
        self._initialize_achievements()
        self._initialize_challenges()
        self._initialize_rewards()
        
        # Start background processing
        self.processing_thread = threading.Thread(target=self._background_processing, daemon=True)
        self.processing_thread.start()
        
        print("🎮 Gamification System initialized!")
        print("🏆 Achievements and challenges loaded!")
        print("⭐ Reward system active!")
    
    def _initialize_achievements(self):
        """Initialize all achievements"""
        achievements_data = [
            {
                "id": "first_focus",
                "name": "First Focus",
                "description": "Complete your first focus session",
                "type": AchievementType.FOCUS_SESSION,
                "icon": "🎯",
                "xp_reward": 50,
                "rarity": "common",
                "requirements": {"focus_sessions": 1}
            },
            {
                "id": "focus_streak_3",
                "name": "Focus Streak",
                "description": "Complete 3 focus sessions in a row",
                "type": AchievementType.FOCUS_SESSION,
                "icon": "🔥",
                "xp_reward": 100,
                "rarity": "common",
                "requirements": {"focus_streak": 3}
            },
            {
                "id": "focus_streak_7",
                "name": "Week Warrior",
                "description": "Complete 7 focus sessions in a row",
                "type": AchievementType.FOCUS_SESSION,
                "icon": "⚔️",
                "xp_reward": 250,
                "rarity": "rare",
                "requirements": {"focus_streak": 7}
            },
            {
                "id": "focus_streak_30",
                "name": "Focus Master",
                "description": "Complete 30 focus sessions in a row",
                "type": AchievementType.FOCUS_SESSION,
                "icon": "👑",
                "xp_reward": 1000,
                "rarity": "epic",
                "requirements": {"focus_streak": 30}
            },
            {
                "id": "daily_streak_7",
                "name": "Week Warrior",
                "description": "Maintain daily usage limits for 7 days",
                "type": AchievementType.DAILY_STREAK,
                "icon": "📅",
                "xp_reward": 200,
                "rarity": "rare",
                "requirements": {"daily_streak": 7}
            },
            {
                "id": "daily_streak_30",
                "name": "Month Master",
                "description": "Maintain daily usage limits for 30 days",
                "type": AchievementType.DAILY_STREAK,
                "icon": "📆",
                "xp_reward": 500,
                "rarity": "epic",
                "requirements": {"daily_streak": 30}
            },
            {
                "id": "time_saved_1h",
                "name": "Time Saver",
                "description": "Save 1 hour of social media time",
                "type": AchievementType.TIME_SAVED,
                "icon": "⏰",
                "xp_reward": 75,
                "rarity": "common",
                "requirements": {"time_saved_hours": 1}
            },
            {
                "id": "time_saved_10h",
                "name": "Time Master",
                "description": "Save 10 hours of social media time",
                "type": AchievementType.TIME_SAVED,
                "icon": "⌛",
                "xp_reward": 300,
                "rarity": "rare",
                "requirements": {"time_saved_hours": 10}
            },
            {
                "id": "social_media_free_day",
                "name": "Digital Detox",
                "description": "Go one full day without social media",
                "type": AchievementType.SOCIAL_MEDIA_FREE,
                "icon": "🚫",
                "xp_reward": 150,
                "rarity": "rare",
                "requirements": {"social_media_free_days": 1}
            },
            {
                "id": "social_media_free_week",
                "name": "Digital Freedom",
                "description": "Go one full week without social media",
                "type": AchievementType.SOCIAL_MEDIA_FREE,
                "icon": "🕊️",
                "xp_reward": 750,
                "rarity": "epic",
                "requirements": {"social_media_free_days": 7}
            },
            {
                "id": "break_master",
                "name": "Break Master",
                "description": "Take 50 scheduled breaks",
                "type": AchievementType.BREAK_MASTER,
                "icon": "☕",
                "xp_reward": 200,
                "rarity": "rare",
                "requirements": {"breaks_taken": 50}
            },
            {
                "id": "wellness_champion",
                "name": "Wellness Champion",
                "description": "Maintain healthy digital habits for 60 days",
                "type": AchievementType.WELLNESS_CHAMPION,
                "icon": "💪",
                "xp_reward": 1000,
                "rarity": "legendary",
                "requirements": {"wellness_days": 60}
            }
        ]
        
        for ach_data in achievements_data:
            achievement = Achievement(
                id=ach_data["id"],
                name=ach_data["name"],
                description=ach_data["description"],
                type=ach_data["type"],
                icon=ach_data["icon"],
                xp_reward=ach_data["xp_reward"],
                rarity=ach_data["rarity"],
                requirements=ach_data["requirements"]
            )
            self.achievements[achievement.id] = achievement
    
    def _initialize_challenges(self):
        """Initialize challenges"""
        # Daily challenges
        daily_challenges = [
            {
                "id": "daily_focus_2h",
                "name": "2-Hour Focus Challenge",
                "description": "Complete 2 hours of focused work today",
                "type": ChallengeType.DAILY,
                "duration_days": 1,
                "requirements": {"focus_time_minutes": 120},
                "rewards": {"xp": 100, "badge": "daily_focus"}
            },
            {
                "id": "daily_breaks_5",
                "name": "Break Champion",
                "description": "Take 5 scheduled breaks today",
                "type": ChallengeType.DAILY,
                "duration_days": 1,
                "requirements": {"breaks_taken": 5},
                "rewards": {"xp": 75, "badge": "break_champion"}
            }
        ]
        
        # Weekly challenges
        weekly_challenges = [
            {
                "id": "weekly_focus_10h",
                "name": "10-Hour Focus Week",
                "description": "Complete 10 hours of focused work this week",
                "type": ChallengeType.WEEKLY,
                "duration_days": 7,
                "requirements": {"focus_time_minutes": 600},
                "rewards": {"xp": 500, "badge": "weekly_focus"}
            },
            {
                "id": "weekly_social_free",
                "name": "Social Media Free Week",
                "description": "Limit social media to 30 minutes per day this week",
                "type": ChallengeType.WEEKLY,
                "duration_days": 7,
                "requirements": {"daily_social_limit": 30},
                "rewards": {"xp": 300, "badge": "social_free"}
            }
        ]
        
        # Add challenges to system
        all_challenges = daily_challenges + weekly_challenges
        
        for ch_data in all_challenges:
            challenge = Challenge(
                id=ch_data["id"],
                name=ch_data["name"],
                description=ch_data["description"],
                type=ch_data["type"],
                duration_days=ch_data["duration_days"],
                requirements=ch_data["requirements"],
                rewards=ch_data["rewards"],
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=ch_data["duration_days"]),
                participants=[]
            )
            self.challenges[challenge.id] = challenge
    
    def _initialize_rewards(self):
        """Initialize rewards"""
        rewards_data = [
            {
                "id": "level_5_title",
                "name": "Focus Novice",
                "description": "Unlocked at level 5",
                "type": RewardType.TITLE,
                "value": "Focus Novice",
                "icon": "🎯",
                "rarity": "common"
            },
            {
                "id": "level_10_title",
                "name": "Focus Apprentice",
                "description": "Unlocked at level 10",
                "type": RewardType.TITLE,
                "value": "Focus Apprentice",
                "icon": "⚔️",
                "rarity": "rare"
            },
            {
                "id": "level_20_title",
                "name": "Focus Master",
                "description": "Unlocked at level 20",
                "type": RewardType.TITLE,
                "value": "Focus Master",
                "icon": "👑",
                "rarity": "epic"
            },
            {
                "id": "level_50_title",
                "name": "Focus Legend",
                "description": "Unlocked at level 50",
                "type": RewardType.TITLE,
                "value": "Focus Legend",
                "icon": "🌟",
                "rarity": "legendary"
            }
        ]
        
        for reward_data in rewards_data:
            reward = Reward(
                id=reward_data["id"],
                name=reward_data["name"],
                description=reward_data["description"],
                type=reward_data["type"],
                value=reward_data["value"],
                icon=reward_data["icon"],
                rarity=reward_data["rarity"]
            )
            self.rewards[reward.id] = reward
    
    def get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # Check database
        profile = self._load_user_profile(user_id)
        if profile:
            self.user_profiles[user_id] = profile
            return profile
        
        # Create new profile
        profile = UserProfile(
            user_id=user_id,
            level=1,
            xp=0,
            total_xp=0,
            streak_days=0,
            best_streak=0,
            achievements_unlocked=0,
            challenges_completed=0,
            rank="Novice",
            title="Newcomer",
            badges=[],
            last_activity=datetime.now(),
            created_date=datetime.now()
        )
        
        self.user_profiles[user_id] = profile
        self._save_user_profile(profile)
        
        return profile
    
    def process_user_activity(self, user_id: str, activity_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process user activity and check for achievements/challenges"""
        profile = self.get_or_create_user_profile(user_id)
        notifications = []
        
        # Update profile with activity data
        self._update_profile_with_activity(profile, activity_data)
        
        # Check achievements
        new_achievements = self._check_achievements(profile, activity_data)
        for achievement in new_achievements:
            self._unlock_achievement(profile, achievement)
            notifications.append({
                "type": "achievement_unlocked",
                "title": f"🏆 Achievement Unlocked: {achievement.name}",
                "message": achievement.description,
                "icon": achievement.icon,
                "xp_gained": achievement.xp_reward
            })
        
        # Check challenges
        challenge_updates = self._check_challenges(profile, activity_data)
        for challenge, progress in challenge_updates:
            if progress >= 1.0 and not challenge.completed:
                self._complete_challenge(profile, challenge)
                notifications.append({
                    "type": "challenge_completed",
                    "title": f"🎯 Challenge Completed: {challenge.name}",
                    "message": f"Rewards: {challenge.rewards.get('xp', 0)} XP",
                    "icon": "🎯",
                    "xp_gained": challenge.rewards.get('xp', 0)
                })
        
        # Check level up
        old_level = profile.level
        new_level = self._calculate_level(profile.xp)
        if new_level > old_level:
            level_rewards = self._process_level_up(profile, new_level)
            notifications.append({
                "type": "level_up",
                "title": f"⭐ Level Up! You're now level {new_level}",
                "message": f"New rewards unlocked!",
                "icon": "⭐",
                "level": new_level,
                "rewards": level_rewards
            })
        
        # Save updated profile
        self._save_user_profile(profile)
        
        return notifications
    
    def _update_profile_with_activity(self, profile: UserProfile, activity_data: Dict[str, Any]):
        """Update user profile with activity data"""
        # Update last activity
        profile.last_activity = datetime.now()
        
        # Update streak if daily goal was met
        if activity_data.get('daily_goal_met', False):
            profile.streak_days += 1
            if profile.streak_days > profile.best_streak:
                profile.best_streak = profile.streak_days
        else:
            profile.streak_days = 0
        
        # Add XP for various activities
        xp_gained = 0
        
        # Focus session XP
        focus_sessions = activity_data.get('focus_sessions', [])
        for session in focus_sessions:
            duration = session.get('duration', 0)
            xp_gained += duration // 5  # 1 XP per 5 minutes of focus
        
        # Break XP
        breaks_taken = activity_data.get('breaks_taken', 0)
        xp_gained += breaks_taken * 5  # 5 XP per break
        
        # Goal completion XP
        if activity_data.get('daily_goal_met', False):
            xp_gained += 50  # 50 XP for meeting daily goal
        
        # Time saved XP
        time_saved = activity_data.get('time_saved_minutes', 0)
        xp_gained += time_saved // 10  # 1 XP per 10 minutes saved
        
        profile.xp += xp_gained
        profile.total_xp += xp_gained
    
    def _check_achievements(self, profile: UserProfile, activity_data: Dict[str, Any]) -> List[Achievement]:
        """Check for newly unlocked achievements"""
        new_achievements = []
        
        for achievement in self.achievements.values():
            if achievement.unlocked:
                continue
            
            # Check if achievement requirements are met
            if self._check_achievement_requirements(achievement, profile, activity_data):
                new_achievements.append(achievement)
        
        return new_achievements
    
    def _check_achievement_requirements(self, achievement: Achievement, profile: UserProfile, activity_data: Dict[str, Any]) -> bool:
        """Check if achievement requirements are met"""
        requirements = achievement.requirements
        
        for req_type, req_value in requirements.items():
            if req_type == "focus_sessions":
                if len(activity_data.get('focus_sessions', [])) < req_value:
                    return False
            elif req_type == "focus_streak":
                if profile.streak_days < req_value:
                    return False
            elif req_type == "daily_streak":
                if profile.streak_days < req_value:
                    return False
            elif req_type == "time_saved_hours":
                time_saved_hours = activity_data.get('time_saved_minutes', 0) / 60
                if time_saved_hours < req_value:
                    return False
            elif req_type == "social_media_free_days":
                # This would need to be tracked over time
                return False
            elif req_type == "breaks_taken":
                if activity_data.get('breaks_taken', 0) < req_value:
                    return False
            elif req_type == "wellness_days":
                # This would need to be tracked over time
                return False
        
        return True
    
    def _unlock_achievement(self, profile: UserProfile, achievement: Achievement):
        """Unlock an achievement for a user"""
        achievement.unlocked = True
        achievement.unlocked_date = datetime.now()
        
        # Add XP reward
        profile.xp += achievement.xp_reward
        profile.total_xp += achievement.xp_reward
        profile.achievements_unlocked += 1
        
        # Save achievement unlock
        self._save_achievement_unlock(profile.user_id, achievement)
    
    def _check_challenges(self, profile: UserProfile, activity_data: Dict[str, Any]) -> List[Tuple[Challenge, float]]:
        """Check challenge progress"""
        updates = []
        
        for challenge in self.challenges.values():
            if not challenge.active or challenge.completed:
                continue
            
            # Calculate progress
            progress = self._calculate_challenge_progress(challenge, profile, activity_data)
            challenge.progress = progress
            updates.append((challenge, progress))
        
        return updates
    
    def _calculate_challenge_progress(self, challenge: Challenge, profile: UserProfile, activity_data: Dict[str, Any]) -> float:
        """Calculate progress for a challenge"""
        requirements = challenge.requirements
        
        for req_type, req_value in requirements.items():
            if req_type == "focus_time_minutes":
                total_focus_time = sum(s.get('duration', 0) for s in activity_data.get('focus_sessions', []))
                return min(1.0, total_focus_time / req_value)
            elif req_type == "breaks_taken":
                breaks_taken = activity_data.get('breaks_taken', 0)
                return min(1.0, breaks_taken / req_value)
            elif req_type == "daily_social_limit":
                # This would need to be tracked over time
                return 0.0
        
        return 0.0
    
    def _complete_challenge(self, profile: UserProfile, challenge: Challenge):
        """Complete a challenge"""
        challenge.completed = True
        
        # Add rewards
        rewards = challenge.rewards
        if 'xp' in rewards:
            profile.xp += rewards['xp']
            profile.total_xp += rewards['xp']
        
        if 'badge' in rewards:
            if rewards['badge'] not in profile.badges:
                profile.badges.append(rewards['badge'])
        
        profile.challenges_completed += 1
        
        # Save challenge completion
        self._save_challenge_completion(profile.user_id, challenge)
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate level based on XP"""
        # Simple level calculation: each level requires level * 100 XP
        level = 1
        xp_required = 0
        
        while xp >= xp_required:
            level += 1
            xp_required += level * 100
        
        return level - 1
    
    def _process_level_up(self, profile: UserProfile, new_level: int) -> List[Dict[str, Any]]:
        """Process level up and return rewards"""
        rewards = []
        
        # Check for level-based rewards
        for reward in self.rewards.values():
            if reward.type == RewardType.TITLE:
                level_requirement = int(reward.id.split('_')[1])
                if new_level >= level_requirement and reward.id not in profile.badges:
                    profile.badges.append(reward.id)
                    rewards.append({
                        "type": "title_unlocked",
                        "name": reward.name,
                        "value": reward.value,
                        "icon": reward.icon
                    })
        
        # Update rank based on level
        if new_level >= 50:
            profile.rank = "Legend"
        elif new_level >= 30:
            profile.rank = "Master"
        elif new_level >= 20:
            profile.rank = "Expert"
        elif new_level >= 10:
            profile.rank = "Advanced"
        elif new_level >= 5:
            profile.rank = "Intermediate"
        else:
            profile.rank = "Novice"
        
        return rewards
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, level, xp, total_xp, achievements_unlocked, challenges_completed
                    FROM user_profiles
                    ORDER BY level DESC, xp DESC
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                
                leaderboard = []
                for i, row in enumerate(rows):
                    leaderboard.append({
                        "rank": i + 1,
                        "user_id": row[0],
                        "level": row[1],
                        "xp": row[2],
                        "total_xp": row[3],
                        "achievements": row[4],
                        "challenges": row[5]
                    })
                
                return leaderboard
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        profile = self.get_or_create_user_profile(user_id)
        
        # Calculate additional stats
        xp_to_next_level = (profile.level + 1) * 100 - profile.xp
        level_progress = (profile.xp % (profile.level * 100)) / (profile.level * 100)
        
        # Get achievement stats
        unlocked_achievements = [ach for ach in self.achievements.values() if ach.unlocked]
        achievement_progress = len(unlocked_achievements) / len(self.achievements)
        
        # Get challenge stats
        active_challenges = [ch for ch in self.challenges.values() if ch.active and not ch.completed]
        completed_challenges = [ch for ch in self.challenges.values() if ch.completed]
        
        return {
            "profile": {
                "user_id": profile.user_id,
                "level": profile.level,
                "xp": profile.xp,
                "total_xp": profile.total_xp,
                "rank": profile.rank,
                "title": profile.title,
                "streak_days": profile.streak_days,
                "best_streak": profile.best_streak
            },
            "progress": {
                "xp_to_next_level": xp_to_next_level,
                "level_progress": level_progress,
                "achievement_progress": achievement_progress
            },
            "achievements": {
                "unlocked": len(unlocked_achievements),
                "total": len(self.achievements),
                "recent": unlocked_achievements[-5:] if unlocked_achievements else []
            },
            "challenges": {
                "active": len(active_challenges),
                "completed": len(completed_challenges),
                "current": active_challenges
            },
            "badges": profile.badges
        }
    
    def _background_processing(self):
        """Background processing for gamification system"""
        while True:
            try:
                # Process notifications
                while self.notification_queue:
                    notification = self.notification_queue.pop(0)
                    # Here you would send the notification to the user
                    print(f"🎮 Gamification notification: {notification}")
                
                # Update daily challenges
                if datetime.now().hour == 0 and datetime.now().minute == 0:
                    self._update_daily_challenges()
                
                # Update weekly challenges
                if datetime.now().weekday() == 0 and datetime.now().hour == 0:
                    self._update_weekly_challenges()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in gamification background processing: {e}")
                time.sleep(300)
    
    def _update_daily_challenges(self):
        """Update daily challenges"""
        for challenge in self.challenges.values():
            if challenge.type == ChallengeType.DAILY:
                challenge.start_date = datetime.now()
                challenge.end_date = datetime.now() + timedelta(days=1)
                challenge.completed = False
                challenge.progress = 0.0
                challenge.participants = []
    
    def _update_weekly_challenges(self):
        """Update weekly challenges"""
        for challenge in self.challenges.values():
            if challenge.type == ChallengeType.WEEKLY:
                challenge.start_date = datetime.now()
                challenge.end_date = datetime.now() + timedelta(days=7)
                challenge.completed = False
                challenge.progress = 0.0
                challenge.participants = []
    
    def _save_user_profile(self, profile: UserProfile):
        """Save user profile to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, level, xp, total_xp, streak_days, best_streak, 
                     achievements_unlocked, challenges_completed, rank, title, 
                     badges, last_activity, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    profile.level,
                    profile.xp,
                    profile.total_xp,
                    profile.streak_days,
                    profile.best_streak,
                    profile.achievements_unlocked,
                    profile.challenges_completed,
                    profile.rank,
                    profile.title,
                    json.dumps(profile.badges),
                    profile.last_activity.isoformat(),
                    profile.created_date.isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
    
    def _load_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load user profile from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return UserProfile(
                        user_id=row[0],
                        level=row[1],
                        xp=row[2],
                        total_xp=row[3],
                        streak_days=row[4],
                        best_streak=row[5],
                        achievements_unlocked=row[6],
                        challenges_completed=row[7],
                        rank=row[8],
                        title=row[9],
                        badges=json.loads(row[10]),
                        last_activity=datetime.fromisoformat(row[11]),
                        created_date=datetime.fromisoformat(row[12])
                    )
                
                return None
        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            return None
    
    def _save_achievement_unlock(self, user_id: str, achievement: Achievement):
        """Save achievement unlock to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO achievement_unlocks 
                    (user_id, achievement_id, unlocked_date)
                    VALUES (?, ?, ?)
                """, (
                    user_id,
                    achievement.id,
                    achievement.unlocked_date.isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving achievement unlock: {e}")
    
    def _save_challenge_completion(self, user_id: str, challenge: Challenge):
        """Save challenge completion to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO challenge_completions 
                    (user_id, challenge_id, completed_date)
                    VALUES (?, ?, ?)
                """, (
                    user_id,
                    challenge.id,
                    datetime.now().isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving challenge completion: {e}")

# Initialize database tables
def initialize_gamification_database(db_path: str = "productivity.db"):
    """Initialize database tables for gamification features"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # User profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    level INTEGER,
                    xp INTEGER,
                    total_xp INTEGER,
                    streak_days INTEGER,
                    best_streak INTEGER,
                    achievements_unlocked INTEGER,
                    challenges_completed INTEGER,
                    rank TEXT,
                    title TEXT,
                    badges TEXT,
                    last_activity TEXT,
                    created_date TEXT
                )
            """)
            
            # Achievement unlocks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievement_unlocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    achievement_id TEXT,
                    unlocked_date TEXT,
                    UNIQUE(user_id, achievement_id)
                )
            """)
            
            # Challenge completions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS challenge_completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    challenge_id TEXT,
                    completed_date TEXT,
                    UNIQUE(user_id, challenge_id)
                )
            """)
            
            conn.commit()
            print("🎮 Gamification database tables initialized successfully!")
            
    except Exception as e:
        logger.error(f"Error initializing gamification database: {e}")

if __name__ == "__main__":
    # Initialize database
    initialize_gamification_database()
    
    # Create gamification system
    gamification = GamificationSystem()
    
    # Example usage
    user_id = "test_user"
    activity_data = {
        "focus_sessions": [
            {"duration": 45, "interruptions": 2},
            {"duration": 30, "interruptions": 1}
        ],
        "breaks_taken": 3,
        "daily_goal_met": True,
        "time_saved_minutes": 120
    }
    
    # Process activity
    notifications = gamification.process_user_activity(user_id, activity_data)
    
    # Get user stats
    stats = gamification.get_user_stats(user_id)
    
    print(f"Generated {len(notifications)} notifications!")
    print(f"User level: {stats['profile']['level']}")
    print(f"User XP: {stats['profile']['xp']}")
