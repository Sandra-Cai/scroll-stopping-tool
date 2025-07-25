#!/usr/bin/env python3
"""
Gamification Module for Enhanced Scroll Stopping Tool
Achievements, streaks, rewards, and engagement features.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Types of achievements"""
    STREAK = "streak"
    USAGE_REDUCTION = "usage_reduction"
    PRODUCTIVITY = "productivity"
    FOCUS = "focus"
    CONSISTENCY = "consistency"
    MILESTONE = "milestone"

class RewardType(Enum):
    """Types of rewards"""
    BADGE = "badge"
    TITLE = "title"
    UNLOCK = "unlock"
    BONUS = "bonus"

@dataclass
class Achievement:
    """Achievement definition"""
    id: str
    name: str
    description: str
    type: AchievementType
    requirement: Dict[str, Any]
    reward: Dict[str, Any]
    icon: str
    rarity: str  # common, rare, epic, legendary
    unlocked: bool = False
    unlocked_date: Optional[datetime] = None

@dataclass
class Streak:
    """Streak tracking"""
    type: str  # daily_limit, focus_sessions, productivity
    current: int
    best: int
    start_date: datetime
    last_update: datetime

@dataclass
class Reward:
    """Reward definition"""
    id: str
    name: str
    description: str
    type: RewardType
    value: Any
    unlocked: bool = False
    unlocked_date: Optional[datetime] = None

class AchievementSystem:
    """Achievement system with various types of achievements"""
    
    def __init__(self):
        self.achievements = self._initialize_achievements()
        self.unlocked_achievements = []
        self.streaks = {}
        self.points = 0
        self.level = 1
        self.experience = 0
    
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize all available achievements"""
        achievements = {}
        
        # Streak achievements
        achievements['streak_3_days'] = Achievement(
            id='streak_3_days',
            name='Getting Started',
            description='Maintain daily limit for 3 consecutive days',
            type=AchievementType.STREAK,
            requirement={'type': 'daily_limit', 'days': 3},
            reward={'type': 'badge', 'name': 'Beginner Badge', 'points': 50},
            icon='🔥',
            rarity='common'
        )
        
        achievements['streak_7_days'] = Achievement(
            id='streak_7_days',
            name='Week Warrior',
            description='Maintain daily limit for 7 consecutive days',
            type=AchievementType.STREAK,
            requirement={'type': 'daily_limit', 'days': 7},
            reward={'type': 'badge', 'name': 'Week Warrior Badge', 'points': 100},
            icon='⚡',
            rarity='common'
        )
        
        achievements['streak_30_days'] = Achievement(
            id='streak_30_days',
            name='Month Master',
            description='Maintain daily limit for 30 consecutive days',
            type=AchievementType.STREAK,
            requirement={'type': 'daily_limit', 'days': 30},
            reward={'type': 'title', 'name': 'Month Master', 'points': 500},
            icon='👑',
            rarity='epic'
        )
        
        # Usage reduction achievements
        achievements['reduce_50_percent'] = Achievement(
            id='reduce_50_percent',
            name='Half Time Hero',
            description='Reduce daily usage by 50% compared to baseline',
            type=AchievementType.USAGE_REDUCTION,
            requirement={'reduction_percent': 50},
            reward={'type': 'badge', 'name': 'Half Time Hero', 'points': 200},
            icon='📉',
            rarity='rare'
        )
        
        # Productivity achievements
        achievements['productivity_90'] = Achievement(
            id='productivity_90',
            name='Productivity Pro',
            description='Achieve 90% productivity score',
            type=AchievementType.PRODUCTIVITY,
            requirement={'productivity_score': 90},
            reward={'type': 'badge', 'name': 'Productivity Pro', 'points': 150},
            icon='📊',
            rarity='rare'
        )
        
        # Focus achievements
        achievements['focus_marathon'] = Achievement(
            id='focus_marathon',
            name='Focus Marathon',
            description='Complete a 90-minute focus session',
            type=AchievementType.FOCUS,
            requirement={'focus_duration': 90},
            reward={'type': 'badge', 'name': 'Focus Marathon', 'points': 300},
            icon='🎯',
            rarity='epic'
        )
        
        # Consistency achievements
        achievements['perfect_week'] = Achievement(
            id='perfect_week',
            name='Perfect Week',
            description='Meet all daily goals for 7 consecutive days',
            type=AchievementType.CONSISTENCY,
            requirement={'perfect_days': 7},
            reward={'type': 'title', 'name': 'Perfect Week', 'points': 400},
            icon='⭐',
            rarity='epic'
        )
        
        # Milestone achievements
        achievements['first_focus'] = Achievement(
            id='first_focus',
            name='First Focus',
            description='Complete your first focus session',
            type=AchievementType.MILESTONE,
            requirement={'focus_sessions': 1},
            reward={'type': 'badge', 'name': 'First Focus', 'points': 25},
            icon='🎯',
            rarity='common'
        )
        
        return achievements
    
    def check_achievements(self, user_data: Dict) -> List[Achievement]:
        """Check and unlock achievements based on user data"""
        newly_unlocked = []
        
        for achievement in self.achievements.values():
            if not achievement.unlocked and self._check_achievement_requirement(achievement, user_data):
                achievement.unlocked = True
                achievement.unlocked_date = datetime.now()
                self.unlocked_achievements.append(achievement)
                newly_unlocked.append(achievement)
                
                # Award points
                self._award_points(achievement.reward.get('points', 0))
                
                logger.info(f"Achievement unlocked: {achievement.name}")
        
        return newly_unlocked
    
    def _check_achievement_requirement(self, achievement: Achievement, user_data: Dict) -> bool:
        """Check if achievement requirement is met"""
        req = achievement.requirement
        
        if achievement.type == AchievementType.STREAK:
            if req['type'] == 'daily_limit':
                streak = self.streaks.get('daily_limit', Streak('daily_limit', 0, 0, datetime.now(), datetime.now()))
                return streak.current >= req['days']
        
        elif achievement.type == AchievementType.USAGE_REDUCTION:
            baseline = user_data.get('baseline_usage', 120)
            current_usage = user_data.get('daily_usage', 0)
            reduction = ((baseline - current_usage) / baseline) * 100
            return reduction >= req['reduction_percent']
        
        elif achievement.type == AchievementType.PRODUCTIVITY:
            productivity = user_data.get('productivity_score', 0)
            return productivity >= req['productivity_score']
        
        elif achievement.type == AchievementType.FOCUS:
            if 'focus_duration' in req:
                focus_sessions = user_data.get('focus_sessions', [])
                for session in focus_sessions:
                    if session.get('duration', 0) >= req['focus_duration']:
                        return True
            elif 'focus_sessions' in req:
                total_sessions = user_data.get('total_focus_sessions', 0)
                return total_sessions >= req['focus_sessions']
        
        elif achievement.type == AchievementType.CONSISTENCY:
            if 'perfect_days' in req:
                perfect_streak = self.streaks.get('perfect_days', Streak('perfect_days', 0, 0, datetime.now(), datetime.now()))
                return perfect_streak.current >= req['perfect_days']
        
        return False
    
    def _award_points(self, points: int):
        """Award points and check for level up"""
        self.points += points
        self.experience += points
        
        # Check for level up (every 1000 points)
        new_level = (self.experience // 1000) + 1
        if new_level > self.level:
            self.level = new_level
            logger.info(f"Level up! You are now level {self.level}")

class StreakTracker:
    """Track various types of streaks"""
    
    def __init__(self):
        self.streaks = {}
    
    def update_streak(self, streak_type: str, success: bool, user_data: Dict = None):
        """Update a specific streak"""
        if streak_type not in self.streaks:
            self.streaks[streak_type] = Streak(
                type=streak_type,
                current=0,
                best=0,
                start_date=datetime.now(),
                last_update=datetime.now()
            )
        
        streak = self.streaks[streak_type]
        
        if success:
            # Check if streak should continue
            days_since_update = (datetime.now() - streak.last_update).days
            
            if days_since_update == 1:  # Consecutive day
                streak.current += 1
                if streak.current > streak.best:
                    streak.best = streak.current
            elif days_since_update == 0:  # Same day, no change
                pass
            else:  # Gap in streak, reset
                streak.current = 1
                streak.start_date = datetime.now()
            
            streak.last_update = datetime.now()
        else:
            # Reset streak
            streak.current = 0
            streak.start_date = datetime.now()
            streak.last_update = datetime.now()
    
    def get_streak_info(self, streak_type: str) -> Optional[Streak]:
        """Get information about a specific streak"""
        return self.streaks.get(streak_type)
    
    def get_all_streaks(self) -> Dict[str, Streak]:
        """Get all streak information"""
        return self.streaks.copy()

class RewardSystem:
    """Reward system with various types of rewards"""
    
    def __init__(self):
        self.rewards = self._initialize_rewards()
        self.unlocked_rewards = []
    
    def _initialize_rewards(self) -> Dict[str, Reward]:
        """Initialize all available rewards"""
        rewards = {}
        
        # Badge rewards
        rewards['beginner_badge'] = Reward(
            id='beginner_badge',
            name='Beginner Badge',
            description='Complete your first achievement',
            type=RewardType.BADGE,
            value={'icon': '🥉', 'color': '#CD7F32'}
        )
        
        rewards['intermediate_badge'] = Reward(
            id='intermediate_badge',
            name='Intermediate Badge',
            description='Unlock 5 achievements',
            type=RewardType.BADGE,
            value={'icon': '🥈', 'color': '#C0C0C0'}
        )
        
        rewards['expert_badge'] = Reward(
            id='expert_badge',
            name='Expert Badge',
            description='Unlock 10 achievements',
            type=RewardType.BADGE,
            value={'icon': '🥇', 'color': '#FFD700'}
        )
        
        # Title rewards
        rewards['productivity_master'] = Reward(
            id='productivity_master',
            name='Productivity Master',
            description='Achieve 95% productivity score',
            type=RewardType.TITLE,
            value={'title': 'Productivity Master', 'color': '#FF6B6B'}
        )
        
        rewards['focus_champion'] = Reward(
            id='focus_champion',
            name='Focus Champion',
            description='Complete 50 focus sessions',
            type=RewardType.TITLE,
            value={'title': 'Focus Champion', 'color': '#4ECDC4'}
        )
        
        # Unlock rewards
        rewards['advanced_analytics'] = Reward(
            id='advanced_analytics',
            name='Advanced Analytics',
            description='Unlock advanced analytics features',
            type=RewardType.UNLOCK,
            value={'feature': 'advanced_analytics', 'description': 'Access to detailed productivity insights'}
        )
        
        rewards['custom_themes'] = Reward(
            id='custom_themes',
            name='Custom Themes',
            description='Unlock custom UI themes',
            type=RewardType.UNLOCK,
            value={'feature': 'custom_themes', 'description': 'Personalize your interface'}
        )
        
        return rewards
    
    def unlock_reward(self, reward_id: str) -> Optional[Reward]:
        """Unlock a specific reward"""
        if reward_id in self.rewards and not self.rewards[reward_id].unlocked:
            reward = self.rewards[reward_id]
            reward.unlocked = True
            reward.unlocked_date = datetime.now()
            self.unlocked_rewards.append(reward)
            
            logger.info(f"Reward unlocked: {reward.name}")
            return reward
        
        return None
    
    def check_reward_conditions(self, achievement_count: int, productivity_score: float, focus_sessions: int):
        """Check if any rewards should be unlocked"""
        unlocked = []
        
        # Check badge conditions
        if achievement_count >= 1 and not self.rewards['beginner_badge'].unlocked:
            unlocked.append(self.unlock_reward('beginner_badge'))
        
        if achievement_count >= 5 and not self.rewards['intermediate_badge'].unlocked:
            unlocked.append(self.unlock_reward('intermediate_badge'))
        
        if achievement_count >= 10 and not self.rewards['expert_badge'].unlocked:
            unlocked.append(self.unlock_reward('expert_badge'))
        
        # Check title conditions
        if productivity_score >= 95 and not self.rewards['productivity_master'].unlocked:
            unlocked.append(self.unlock_reward('productivity_master'))
        
        if focus_sessions >= 50 and not self.rewards['focus_champion'].unlocked:
            unlocked.append(self.unlock_reward('focus_champion'))
        
        return [r for r in unlocked if r is not None]

class GamificationEngine:
    """Main gamification engine that coordinates all systems"""
    
    def __init__(self):
        self.achievements = AchievementSystem()
        self.streaks = StreakTracker()
        self.rewards = RewardSystem()
        self.daily_challenges = []
        self.weekly_goals = []
    
    def process_daily_update(self, user_data: Dict) -> Dict[str, Any]:
        """Process daily user data and update gamification systems"""
        results = {
            'achievements_unlocked': [],
            'rewards_unlocked': [],
            'streaks_updated': [],
            'points_earned': 0,
            'level_up': False
        }
        
        # Update streaks
        self._update_streaks(user_data)
        
        # Check achievements
        new_achievements = self.achievements.check_achievements(user_data)
        results['achievements_unlocked'] = new_achievements
        
        # Check rewards
        achievement_count = len(self.achievements.unlocked_achievements)
        productivity_score = user_data.get('productivity_score', 0)
        focus_sessions = user_data.get('total_focus_sessions', 0)
        
        new_rewards = self.rewards.check_reward_conditions(
            achievement_count, productivity_score, focus_sessions
        )
        results['rewards_unlocked'] = new_rewards
        
        # Calculate points earned
        points_earned = sum(ach.reward.get('points', 0) for ach in new_achievements)
        results['points_earned'] = points_earned
        
        # Check for level up
        old_level = self.achievements.level
        if self.achievements.level > old_level:
            results['level_up'] = True
        
        return results
    
    def _update_streaks(self, user_data: Dict):
        """Update all relevant streaks"""
        # Daily limit streak
        daily_limit_met = user_data.get('daily_limit_met', False)
        self.streaks.update_streak('daily_limit', daily_limit_met)
        
        # Focus sessions streak
        focus_sessions_today = user_data.get('focus_sessions_today', 0)
        focus_streak_success = focus_sessions_today > 0
        self.streaks.update_streak('focus_sessions', focus_streak_success)
        
        # Productivity streak
        productivity_score = user_data.get('productivity_score', 0)
        productivity_streak_success = productivity_score >= 70
        self.streaks.update_streak('productivity', productivity_streak_success)
        
        # Perfect day streak
        perfect_day = (daily_limit_met and focus_sessions_today > 0 and productivity_score >= 70)
        self.streaks.update_streak('perfect_days', perfect_day)
    
    def get_gamification_summary(self) -> Dict[str, Any]:
        """Get comprehensive gamification summary"""
        return {
            'level': self.achievements.level,
            'experience': self.achievements.experience,
            'points': self.achievements.points,
            'achievements': {
                'total': len(self.achievements.achievements),
                'unlocked': len(self.achievements.unlocked_achievements),
                'recent': [vars(ach) for ach in self.achievements.unlocked_achievements[-5:]]
            },
            'streaks': {
                streak_type: {
                    'current': streak.current,
                    'best': streak.best,
                    'start_date': streak.start_date.isoformat()
                }
                for streak_type, streak in self.streaks.streaks.items()
            },
            'rewards': {
                'total': len(self.rewards.rewards),
                'unlocked': len(self.rewards.unlocked_rewards),
                'recent': [vars(reward) for reward in self.rewards.unlocked_rewards[-5:]]
            }
        }
    
    def create_daily_challenge(self) -> Dict[str, Any]:
        """Create a daily challenge for the user"""
        challenges = [
            {
                'id': 'reduce_usage_20',
                'name': 'Usage Reduction',
                'description': 'Reduce today\'s usage by 20% compared to yesterday',
                'reward': {'points': 50, 'type': 'daily_challenge'},
                'icon': '📉'
            },
            {
                'id': 'focus_45_min',
                'name': 'Focus Session',
                'description': 'Complete a 45-minute focus session',
                'reward': {'points': 75, 'type': 'daily_challenge'},
                'icon': '🎯'
            },
            {
                'id': 'productivity_80',
                'name': 'High Productivity',
                'description': 'Achieve 80% productivity score',
                'reward': {'points': 60, 'type': 'daily_challenge'},
                'icon': '📊'
            },
            {
                'id': 'take_breaks',
                'name': 'Break Time',
                'description': 'Take at least 4 breaks today',
                'reward': {'points': 40, 'type': 'daily_challenge'},
                'icon': '☕'
            }
        ]
        
        # Select a random challenge
        import random
        challenge = random.choice(challenges)
        challenge['date'] = datetime.now().date().isoformat()
        
        return challenge
    
    def check_challenge_completion(self, challenge: Dict, user_data: Dict) -> bool:
        """Check if daily challenge is completed"""
        challenge_id = challenge['id']
        
        if challenge_id == 'reduce_usage_20':
            yesterday_usage = user_data.get('yesterday_usage', 120)
            today_usage = user_data.get('daily_usage', 0)
            reduction = ((yesterday_usage - today_usage) / yesterday_usage) * 100
            return reduction >= 20
        
        elif challenge_id == 'focus_45_min':
            focus_sessions = user_data.get('focus_sessions', [])
            for session in focus_sessions:
                if session.get('duration', 0) >= 45:
                    return True
            return False
        
        elif challenge_id == 'productivity_80':
            productivity = user_data.get('productivity_score', 0)
            return productivity >= 80
        
        elif challenge_id == 'take_breaks':
            breaks_taken = user_data.get('breaks_taken', 0)
            return breaks_taken >= 4
        
        return False

# Example usage
if __name__ == "__main__":
    # Initialize gamification engine
    gamification = GamificationEngine()
    
    # Sample user data
    user_data = {
        'daily_usage': 90,
        'yesterday_usage': 120,
        'productivity_score': 85,
        'focus_sessions': [{'duration': 45}],
        'breaks_taken': 4,
        'daily_limit_met': True,
        'focus_sessions_today': 1,
        'total_focus_sessions': 5,
        'baseline_usage': 120
    }
    
    # Process daily update
    results = gamification.process_daily_update(user_data)
    
    print("Gamification Module Loaded Successfully!")
    print(f"Level: {gamification.achievements.level}")
    print(f"Points: {gamification.achievements.points}")
    print(f"Achievements unlocked: {len(results['achievements_unlocked'])}")
    print(f"Rewards unlocked: {len(results['rewards_unlocked'])}") 