#!/usr/bin/env python3
"""
AI Assistant Module for Enhanced Scroll Stopping Tool
Intelligent coaching, personalized recommendations, and conversational interface.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import random

logger = logging.getLogger(__name__)

class ConversationType(Enum):
    """Types of AI conversations"""
    COACHING = "coaching"
    MOTIVATION = "motivation"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    CELEBRATION = "celebration"

class AIPersonality(Enum):
    """AI personality types"""
    SUPPORTIVE = "supportive"
    CHALLENGING = "challenging"
    ANALYTICAL = "analytical"
    MOTIVATIONAL = "motivational"
    FRIENDLY = "friendly"

@dataclass
class AIConversation:
    """AI conversation data"""
    type: ConversationType
    message: str
    timestamp: datetime
    user_response: Optional[str] = None
    follow_up: Optional[str] = None
    sentiment: str = "neutral"

@dataclass
class UserProfile:
    """User profile for AI personalization"""
    personality_type: str
    learning_style: str
    motivation_factors: List[str]
    preferred_communication: str
    goals: List[str]
    challenges: List[str]
    achievements: List[str]

class AIAssistant:
    """AI-powered assistant for productivity coaching"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_profile = None
        self.personality = AIPersonality.SUPPORTIVE
        self.coaching_sessions = []
        self.recommendations = []
        self.motivation_quotes = self._load_motivation_quotes()
        self.productivity_tips = self._load_productivity_tips()
    
    def _load_motivation_quotes(self) -> List[str]:
        """Load motivational quotes"""
        return [
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Productivity is never an accident. It is always the result of a commitment to excellence. - Paul J. Meyer",
            "Focus is not about saying yes to the things you've got to focus on, but about saying no to the hundred other good ideas. - Steve Jobs",
            "The future depends on what you do today. - Mahatma Gandhi",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
            "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt",
            "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
            "The way to get started is to quit talking and begin doing. - Walt Disney",
            "It always seems impossible until it's done. - Nelson Mandela",
            "The only person you are destined to become is the person you decide to be. - Ralph Waldo Emerson"
        ]
    
    def _load_productivity_tips(self) -> List[str]:
        """Load productivity tips"""
        return [
            "Use the Pomodoro Technique: 25 minutes of focused work followed by 5-minute breaks",
            "Eliminate distractions by putting your phone in another room",
            "Start your day with the most important task (Eat the Frog method)",
            "Use the 2-minute rule: if it takes less than 2 minutes, do it now",
            "Batch similar tasks together to maintain focus",
            "Take regular breaks to maintain mental clarity",
            "Use time blocking to schedule your day in advance",
            "Practice the 80/20 rule: focus on tasks that give the most results",
            "Set specific, measurable goals for each day",
            "Review and reflect on your progress regularly"
        ]
    
    def create_user_profile(self, user_data: Dict) -> UserProfile:
        """Create personalized user profile"""
        # Analyze user behavior to determine personality type
        personality_type = self._analyze_personality(user_data)
        learning_style = self._determine_learning_style(user_data)
        motivation_factors = self._identify_motivation_factors(user_data)
        
        profile = UserProfile(
            personality_type=personality_type,
            learning_style=learning_style,
            motivation_factors=motivation_factors,
            preferred_communication="conversational",
            goals=self._extract_goals(user_data),
            challenges=self._identify_challenges(user_data),
            achievements=self._extract_achievements(user_data)
        )
        
        self.user_profile = profile
        logger.info(f"Created user profile: {personality_type} personality, {learning_style} learner")
        return profile
    
    def _analyze_personality(self, user_data: Dict) -> str:
        """Analyze user personality based on behavior"""
        # Simple personality analysis based on usage patterns
        avg_usage = user_data.get('average_usage', 120)
        productivity = user_data.get('average_productivity', 70)
        focus_sessions = user_data.get('focus_sessions_count', 0)
        
        if productivity > 85 and focus_sessions > 5:
            return "achiever"
        elif avg_usage < 90:
            return "disciplined"
        elif productivity < 60:
            return "struggling"
        else:
            return "balanced"
    
    def _determine_learning_style(self, user_data: Dict) -> str:
        """Determine user's learning style"""
        # Analyze how user responds to different types of feedback
        achievements = user_data.get('achievements_unlocked', 0)
        streak_days = user_data.get('streak_days', 0)
        
        if achievements > 10:
            return "achievement-driven"
        elif streak_days > 7:
            return "consistency-focused"
        else:
            return "guidance-seeking"
    
    def _identify_motivation_factors(self, user_data: Dict) -> List[str]:
        """Identify what motivates the user"""
        factors = []
        
        if user_data.get('achievements_unlocked', 0) > 5:
            factors.append("achievements")
        if user_data.get('streak_days', 0) > 3:
            factors.append("streaks")
        if user_data.get('productivity_score', 0) > 80:
            factors.append("performance")
        if user_data.get('focus_sessions', 0) > 2:
            factors.append("focus")
        
        return factors if factors else ["general_improvement"]
    
    def _extract_goals(self, user_data: Dict) -> List[str]:
        """Extract user goals from data"""
        goals = []
        
        if user_data.get('daily_limit', 120) < 120:
            goals.append("reduce_social_media_usage")
        if user_data.get('focus_sessions', 0) < 3:
            goals.append("increase_focus_sessions")
        if user_data.get('productivity_score', 0) < 80:
            goals.append("improve_productivity")
        
        return goals if goals else ["general_improvement"]
    
    def _identify_challenges(self, user_data: Dict) -> List[str]:
        """Identify user challenges"""
        challenges = []
        
        if user_data.get('interruptions', 0) > 5:
            challenges.append("frequent_interruptions")
        if user_data.get('usage_time', 0) > 150:
            challenges.append("high_usage")
        if user_data.get('productivity_score', 0) < 70:
            challenges.append("low_productivity")
        
        return challenges
    
    def _extract_achievements(self, user_data: Dict) -> List[str]:
        """Extract user achievements"""
        achievements = []
        
        if user_data.get('streak_days', 0) >= 7:
            achievements.append("week_streak")
        if user_data.get('achievements_unlocked', 0) >= 5:
            achievements.append("multiple_achievements")
        if user_data.get('productivity_score', 0) >= 90:
            achievements.append("high_productivity")
        
        return achievements
    
    def generate_personalized_message(self, context: str, user_data: Dict) -> str:
        """Generate personalized message based on user profile and context"""
        if not self.user_profile:
            self.create_user_profile(user_data)
        
        personality = self.user_profile.personality_type
        learning_style = self.user_profile.learning_style
        
        # Generate context-specific messages
        if context == "daily_start":
            return self._generate_daily_start_message(personality, learning_style)
        elif context == "low_productivity":
            return self._generate_low_productivity_message(personality, learning_style)
        elif context == "achievement_unlocked":
            return self._generate_achievement_message(personality, learning_style)
        elif context == "streak_broken":
            return self._generate_streak_broken_message(personality, learning_style)
        elif context == "high_usage":
            return self._generate_high_usage_message(personality, learning_style)
        else:
            return self._generate_general_message(personality, learning_style)
    
    def _generate_daily_start_message(self, personality: str, learning_style: str) -> str:
        """Generate daily start message"""
        messages = {
            "achiever": "Ready to crush another productive day! 🚀 What's your main focus today?",
            "disciplined": "Great to see you back! Let's maintain that excellent momentum. 💪",
            "struggling": "Every day is a fresh start! Let's make today better than yesterday. 🌟",
            "balanced": "Welcome back! Ready to find that perfect balance today? ⚖️"
        }
        
        base_message = messages.get(personality, "Good morning! Ready to be productive? ☀️")
        
        if learning_style == "achievement-driven":
            base_message += " Set a specific goal to unlock today's achievement!"
        elif learning_style == "consistency-focused":
            base_message += " Focus on building that consistent routine."
        
        return base_message
    
    def _generate_low_productivity_message(self, personality: str, learning_style: str) -> str:
        """Generate low productivity message"""
        messages = {
            "achiever": "I know you can do better! Let's identify what's holding you back. 🔍",
            "disciplined": "Even the most disciplined people have off days. Tomorrow is a new opportunity!",
            "struggling": "It's okay to have challenging days. Let's work together to improve. 🤝",
            "balanced": "Productivity ebbs and flows. Let's find your rhythm again. 🎵"
        }
        
        base_message = messages.get(personality, "Having a tough day? Let's turn it around! 💪")
        
        # Add specific tip
        tip = random.choice(self.productivity_tips)
        return f"{base_message} Here's a tip: {tip}"
    
    def _generate_achievement_message(self, personality: str, learning_style: str) -> str:
        """Generate achievement celebration message"""
        messages = {
            "achiever": "Another achievement unlocked! You're on fire! 🔥",
            "disciplined": "Your consistency is paying off! Well done! 🎯",
            "struggling": "Look at you go! Every achievement is a step forward! 🌟",
            "balanced": "Perfect balance of effort and reward! Congratulations! 🎉"
        }
        
        base_message = messages.get(personality, "Congratulations on your achievement! 🏆")
        
        if learning_style == "achievement-driven":
            base_message += " Ready for the next challenge?"
        
        return base_message
    
    def _generate_streak_broken_message(self, personality: str, learning_style: str) -> str:
        """Generate streak broken message"""
        messages = {
            "achiever": "Streaks end, but your determination doesn't have to! Let's start a new one! 💪",
            "disciplined": "Even the most disciplined people have setbacks. Tomorrow is a fresh start!",
            "struggling": "Don't let one setback define you. Every day is a new opportunity! 🌅",
            "balanced": "Life happens! Let's get back on track and find that balance again. ⚖️"
        }
        
        base_message = messages.get(personality, "Streak broken, but you're not! Let's bounce back! 🔄")
        
        if learning_style == "consistency-focused":
            base_message += " Focus on building a new, stronger streak."
        
        return base_message
    
    def _generate_high_usage_message(self, personality: str, learning_style: str) -> str:
        """Generate high usage warning message"""
        messages = {
            "achiever": "High usage detected! Time to refocus on your goals! 🎯",
            "disciplined": "Your usage is higher than usual. Let's get back to your routine!",
            "struggling": "I notice you're spending more time online. Let's find a better balance! 🤝",
            "balanced": "Your usage is out of balance. Let's restore that equilibrium! ⚖️"
        }
        
        base_message = messages.get(personality, "High usage alert! Time to take a break! ⏰")
        
        # Add specific recommendation
        recommendations = [
            "Try a 10-minute focus session",
            "Take a walk outside",
            "Read a book for 15 minutes",
            "Practice deep breathing exercises"
        ]
        
        recommendation = random.choice(recommendations)
        return f"{base_message} Suggestion: {recommendation}"
    
    def _generate_general_message(self, personality: str, learning_style: str) -> str:
        """Generate general motivational message"""
        quote = random.choice(self.motivation_quotes)
        return f"💭 {quote}"
    
    def provide_coaching_session(self, user_data: Dict) -> Dict[str, Any]:
        """Provide a personalized coaching session"""
        if not self.user_profile:
            self.create_user_profile(user_data)
        
        # Analyze current situation
        analysis = self._analyze_current_situation(user_data)
        
        # Generate coaching plan
        coaching_plan = self._generate_coaching_plan(analysis)
        
        # Create session
        session = {
            'timestamp': datetime.now(),
            'analysis': analysis,
            'plan': coaching_plan,
            'recommendations': self._generate_recommendations(analysis),
            'motivational_message': self._generate_motivational_message(analysis)
        }
        
        self.coaching_sessions.append(session)
        return session
    
    def _analyze_current_situation(self, user_data: Dict) -> Dict[str, Any]:
        """Analyze current user situation"""
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': [],
            'overall_score': 0
        }
        
        # Analyze strengths
        if user_data.get('streak_days', 0) > 3:
            analysis['strengths'].append("consistent_daily_routine")
        if user_data.get('productivity_score', 0) > 80:
            analysis['strengths'].append("high_productivity")
        if user_data.get('focus_sessions', 0) > 2:
            analysis['strengths'].append("good_focus_ability")
        
        # Analyze weaknesses
        if user_data.get('usage_time', 0) > 150:
            analysis['weaknesses'].append("high_social_media_usage")
        if user_data.get('interruptions', 0) > 5:
            analysis['weaknesses'].append("frequent_interruptions")
        if user_data.get('productivity_score', 0) < 70:
            analysis['weaknesses'].append("low_productivity")
        
        # Calculate overall score
        score = 50  # Base score
        
        # Adjust based on various factors
        score += min(20, user_data.get('streak_days', 0) * 2)
        score += min(15, user_data.get('productivity_score', 70) - 70)
        score -= min(20, max(0, user_data.get('usage_time', 120) - 120) // 10)
        score += min(10, user_data.get('focus_sessions', 0) * 2)
        
        analysis['overall_score'] = max(0, min(100, score))
        
        return analysis
    
    def _generate_coaching_plan(self, analysis: Dict) -> Dict[str, Any]:
        """Generate personalized coaching plan"""
        plan = {
            'short_term_goals': [],
            'long_term_goals': [],
            'action_items': [],
            'timeline': '2_weeks'
        }
        
        # Generate goals based on analysis
        if 'high_social_media_usage' in analysis['weaknesses']:
            plan['short_term_goals'].append("Reduce daily usage by 20%")
            plan['action_items'].append("Set specific time limits for social media")
        
        if 'frequent_interruptions' in analysis['weaknesses']:
            plan['short_term_goals'].append("Minimize interruptions during focus sessions")
            plan['action_items'].append("Use focus mode more frequently")
        
        if 'low_productivity' in analysis['weaknesses']:
            plan['short_term_goals'].append("Improve productivity score by 10%")
            plan['action_items'].append("Implement Pomodoro technique")
        
        # Long-term goals
        plan['long_term_goals'].extend([
            "Maintain 7-day streak consistently",
            "Achieve 90% productivity score",
            "Complete 50 focus sessions"
        ])
        
        return plan
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if analysis['overall_score'] < 50:
            recommendations.extend([
                "Start with small, achievable goals",
                "Focus on building consistent habits",
                "Use the app's focus mode regularly"
            ])
        elif analysis['overall_score'] < 75:
            recommendations.extend([
                "Optimize your daily routine",
                "Set more challenging goals",
                "Track your progress more closely"
            ])
        else:
            recommendations.extend([
                "Maintain your excellent progress",
                "Help others with their productivity journey",
                "Set even more ambitious goals"
            ])
        
        return recommendations
    
    def _generate_motivational_message(self, analysis: Dict) -> str:
        """Generate motivational message based on analysis"""
        if analysis['overall_score'] < 50:
            return "Every expert was once a beginner. Your journey to productivity starts now! 🌟"
        elif analysis['overall_score'] < 75:
            return "You're making great progress! Keep pushing forward! 💪"
        else:
            return "You're absolutely crushing it! Keep up the amazing work! 🚀"
    
    def get_conversation_history(self) -> List[AIConversation]:
        """Get conversation history"""
        return self.conversation_history
    
    def add_conversation(self, conversation: AIConversation):
        """Add conversation to history"""
        self.conversation_history.append(conversation)
        
        # Keep only last 50 conversations
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def get_ai_insights(self, user_data: Dict) -> List[Dict[str, Any]]:
        """Get AI-powered insights"""
        insights = []
        
        # Usage pattern insights
        if user_data.get('usage_time', 0) > 120:
            insights.append({
                'type': 'warning',
                'title': 'High Usage Detected',
                'message': 'Your social media usage is above your daily limit.',
                'suggestion': 'Consider taking a break and focusing on other activities.',
                'confidence': 0.85
            })
        
        # Productivity insights
        if user_data.get('productivity_score', 0) < 70:
            insights.append({
                'type': 'suggestion',
                'title': 'Productivity Opportunity',
                'message': 'Your productivity score could be improved.',
                'suggestion': 'Try using focus mode for 25-minute sessions.',
                'confidence': 0.78
            })
        
        # Streak insights
        if user_data.get('streak_days', 0) >= 5:
            insights.append({
                'type': 'celebration',
                'title': 'Streak Achievement',
                'message': f'Great job maintaining a {user_data.get("streak_days", 0)}-day streak!',
                'suggestion': 'Keep up the consistency!',
                'confidence': 0.92
            })
        
        return insights

class ConversationalAI:
    """Conversational AI interface"""
    
    def __init__(self, ai_assistant: AIAssistant):
        self.ai_assistant = ai_assistant
        self.conversation_context = {}
        self.response_templates = self._load_response_templates()
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates"""
        return {
            'greeting': [
                "Hello! How can I help you with your productivity today?",
                "Hi there! Ready to boost your productivity?",
                "Welcome back! What would you like to work on?"
            ],
            'motivation': [
                "You've got this! Every small step counts towards your goals.",
                "Remember why you started. You're capable of amazing things!",
                "Progress is progress, no matter how small. Keep going!"
            ],
            'advice': [
                "Based on your patterns, I'd recommend trying this approach.",
                "Here's what I think might help you improve.",
                "Let me suggest a strategy that could work for you."
            ],
            'celebration': [
                "Fantastic work! You should be proud of yourself!",
                "Congratulations! This is a significant achievement!",
                "Amazing progress! You're really making it happen!"
            ]
        }
    
    def process_user_message(self, message: str, user_data: Dict) -> str:
        """Process user message and generate response"""
        # Analyze message intent
        intent = self._analyze_intent(message)
        
        # Generate appropriate response
        if intent == 'greeting':
            return self._generate_greeting_response()
        elif intent == 'help':
            return self._generate_help_response()
        elif intent == 'motivation':
            return self._generate_motivation_response()
        elif intent == 'advice':
            return self._generate_advice_response(user_data)
        elif intent == 'celebration':
            return self._generate_celebration_response()
        else:
            return self._generate_general_response()
    
    def _analyze_intent(self, message: str) -> str:
        """Analyze message intent"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return 'greeting'
        elif any(word in message_lower for word in ['help', 'support', 'assist']):
            return 'help'
        elif any(word in message_lower for word in ['motivate', 'encourage', 'inspire']):
            return 'motivation'
        elif any(word in message_lower for word in ['advice', 'suggest', 'recommend']):
            return 'advice'
        elif any(word in message_lower for word in ['celebrate', 'achievement', 'success']):
            return 'celebration'
        else:
            return 'general'
    
    def _generate_greeting_response(self) -> str:
        """Generate greeting response"""
        return random.choice(self.response_templates['greeting'])
    
    def _generate_help_response(self) -> str:
        """Generate help response"""
        return "I'm here to help you with your productivity journey! I can provide coaching, motivation, advice, and insights. What would you like to know?"
    
    def _generate_motivation_response(self) -> str:
        """Generate motivation response"""
        return random.choice(self.response_templates['motivation'])
    
    def _generate_advice_response(self, user_data: Dict) -> str:
        """Generate personalized advice response"""
        tip = random.choice(self.ai_assistant.productivity_tips)
        return f"Here's a tip that might help: {tip}"
    
    def _generate_celebration_response(self) -> str:
        """Generate celebration response"""
        return random.choice(self.response_templates['celebration'])
    
    def _generate_general_response(self) -> str:
        """Generate general response"""
        return "I'm here to support your productivity journey. Feel free to ask me anything about improving your focus, managing your time, or staying motivated!"

# Example usage
if __name__ == "__main__":
    # Initialize AI Assistant
    ai_assistant = AIAssistant()
    
    # Sample user data
    user_data = {
        'average_usage': 110,
        'average_productivity': 75,
        'focus_sessions_count': 3,
        'achievements_unlocked': 6,
        'streak_days': 5,
        'usage_time': 95,
        'productivity_score': 78,
        'focus_sessions': 2,
        'interruptions': 3
    }
    
    # Create user profile
    profile = ai_assistant.create_user_profile(user_data)
    print(f"User Profile: {profile.personality_type} personality")
    
    # Generate personalized message
    message = ai_assistant.generate_personalized_message("daily_start", user_data)
    print(f"AI Message: {message}")
    
    # Provide coaching session
    coaching = ai_assistant.provide_coaching_session(user_data)
    print(f"Coaching Score: {coaching['analysis']['overall_score']}")
    
    # Get AI insights
    insights = ai_assistant.get_ai_insights(user_data)
    print(f"AI Insights: {len(insights)} insights generated")
    
    print("AI Assistant module loaded successfully!") 