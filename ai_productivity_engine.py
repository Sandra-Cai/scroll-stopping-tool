#!/usr/bin/env python3
"""
AI-Powered Productivity Engine
Advanced artificial intelligence system for intelligent productivity insights,
behavioral analysis, and personalized recommendations.
"""

import json
import time
import threading
import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from enum import Enum
import queue
import sqlite3
import hashlib
from pathlib import Path
import pickle
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import pandas as pd

logger = logging.getLogger(__name__)

class ProductivityPattern(Enum):
    """Productivity pattern types"""
    MORNING_PEAK = "morning_peak"
    AFTERNOON_DIP = "afternoon_dip"
    EVENING_RECOVERY = "evening_recovery"
    CONSISTENT = "consistent"
    VARIABLE = "variable"
    WEEKEND_DROP = "weekend_drop"

class BehaviorType(Enum):
    """User behavior types"""
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    BALANCED = "balanced"
    ADDICTIVE = "addictive"
    MINIMAL = "minimal"

class RecommendationType(Enum):
    """AI recommendation types"""
    BREAK_SCHEDULE = "break_schedule"
    FOCUS_TIME = "focus_time"
    GOAL_ADJUSTMENT = "goal_adjustment"
    ACTIVITY_SUGGESTION = "activity_suggestion"
    HABIT_FORMATION = "habit_formation"
    INTERVENTION = "intervention"

@dataclass
class ProductivityInsight:
    """AI-generated productivity insight"""
    id: str
    type: str
    title: str
    description: str
    confidence: float
    impact_score: float
    action_items: List[str]
    timestamp: datetime
    category: str
    priority: int
    evidence: Dict[str, Any]
    user_feedback: Optional[str] = None

@dataclass
class BehaviorProfile:
    """User behavior profile"""
    user_id: str
    pattern_type: ProductivityPattern
    behavior_type: BehaviorType
    focus_score: float
    distraction_score: float
    consistency_score: float
    improvement_rate: float
    last_updated: datetime
    features: Dict[str, float]

@dataclass
class AIRecommendation:
    """AI-generated recommendation"""
    id: str
    type: RecommendationType
    title: str
    description: str
    reasoning: str
    expected_impact: float
    implementation_steps: List[str]
    difficulty: str  # easy, medium, hard
    time_commitment: int  # minutes
    success_rate: float
    timestamp: datetime
    status: str  # pending, implemented, dismissed

class AIProductivityEngine:
    """Advanced AI-powered productivity engine"""
    
    def __init__(self, db_path: str = "productivity.db"):
        self.db_path = db_path
        self.insights_queue = queue.Queue()
        self.recommendations_queue = queue.Queue()
        self.behavior_profiles = {}
        self.ml_models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.learning_rate = 0.01
        self.confidence_threshold = 0.7
        self.min_data_points = 50
        
        # Initialize ML models
        self._initialize_models()
        
        # Start background processing
        self.processing_thread = threading.Thread(target=self._background_processing, daemon=True)
        self.processing_thread.start()
        
        print("🤖 AI Productivity Engine initialized!")
        print("🧠 Machine learning models loaded!")
        print("📊 Behavioral analysis active!")
    
    def _initialize_models(self):
        """Initialize machine learning models"""
        # Behavior classification model
        self.ml_models['behavior_classifier'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Productivity prediction model
        self.ml_models['productivity_predictor'] = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        # Focus score predictor
        self.ml_models['focus_predictor'] = GradientBoostingRegressor(
            n_estimators=80,
            max_depth=5,
            learning_rate=0.15,
            random_state=42
        )
        
        # Initialize scalers
        self.scalers['standard'] = StandardScaler()
        self.scalers['robust'] = StandardScaler()
        
        print("🧠 ML models initialized successfully!")
    
    def analyze_user_behavior(self, user_data: Dict[str, Any]) -> BehaviorProfile:
        """Analyze user behavior and create/update behavior profile"""
        user_id = user_data.get('user_id', 'default')
        
        # Extract features
        features = self._extract_behavior_features(user_data)
        
        # Classify behavior pattern
        pattern_type = self._classify_productivity_pattern(features)
        behavior_type = self._classify_behavior_type(features)
        
        # Calculate scores
        focus_score = self._calculate_focus_score(features)
        distraction_score = self._calculate_distraction_score(features)
        consistency_score = self._calculate_consistency_score(features)
        improvement_rate = self._calculate_improvement_rate(user_id, features)
        
        # Create or update behavior profile
        profile = BehaviorProfile(
            user_id=user_id,
            pattern_type=pattern_type,
            behavior_type=behavior_type,
            focus_score=focus_score,
            distraction_score=distraction_score,
            consistency_score=consistency_score,
            improvement_rate=improvement_rate,
            last_updated=datetime.now(),
            features=features
        )
        
        self.behavior_profiles[user_id] = profile
        self._save_behavior_profile(profile)
        
        return profile
    
    def _extract_behavior_features(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract behavioral features from user data"""
        features = {}
        
        # Time-based features
        current_hour = datetime.now().hour
        features['hour_of_day'] = current_hour
        features['is_weekend'] = 1.0 if datetime.now().weekday() >= 5 else 0.0
        features['is_morning'] = 1.0 if 6 <= current_hour <= 11 else 0.0
        features['is_afternoon'] = 1.0 if 12 <= current_hour <= 17 else 0.0
        features['is_evening'] = 1.0 if 18 <= current_hour <= 23 else 0.0
        
        # Usage features
        daily_usage = user_data.get('daily_usage', 0)
        features['daily_usage_minutes'] = daily_usage
        features['usage_intensity'] = daily_usage / 1440  # normalized to day
        
        # Focus features
        focus_sessions = user_data.get('focus_sessions', [])
        features['focus_session_count'] = len(focus_sessions)
        features['avg_focus_duration'] = np.mean([s.get('duration', 0) for s in focus_sessions]) if focus_sessions else 0
        features['focus_consistency'] = self._calculate_session_consistency(focus_sessions)
        
        # Break features
        breaks_taken = user_data.get('breaks_taken', 0)
        features['break_frequency'] = breaks_taken
        features['break_regularity'] = self._calculate_break_regularity(user_data)
        
        # Goal features
        goals_met = user_data.get('goals_met', False)
        features['goal_achievement'] = 1.0 if goals_met else 0.0
        features['goal_progress'] = user_data.get('goal_progress', 0.0)
        
        # Interruption features
        interruptions = user_data.get('interruptions', 0)
        features['interruption_rate'] = interruptions
        features['interruption_impact'] = self._calculate_interruption_impact(user_data)
        
        return features
    
    def _classify_productivity_pattern(self, features: Dict[str, float]) -> ProductivityPattern:
        """Classify user's productivity pattern"""
        # Simple rule-based classification (can be enhanced with ML)
        usage_intensity = features.get('usage_intensity', 0)
        focus_consistency = features.get('focus_consistency', 0)
        break_regularity = features.get('break_regularity', 0)
        
        if usage_intensity < 0.1 and focus_consistency > 0.8:
            return ProductivityPattern.CONSISTENT
        elif features.get('is_weekend', 0) > 0 and usage_intensity > 0.3:
            return ProductivityPattern.WEEKEND_DROP
        elif features.get('is_morning', 0) > 0 and focus_consistency > 0.7:
            return ProductivityPattern.MORNING_PEAK
        elif features.get('is_afternoon', 0) > 0 and focus_consistency < 0.5:
            return ProductivityPattern.AFTERNOON_DIP
        else:
            return ProductivityPattern.VARIABLE
    
    def _classify_behavior_type(self, features: Dict[str, float]) -> BehaviorType:
        """Classify user's behavior type"""
        usage_intensity = features.get('usage_intensity', 0)
        focus_consistency = features.get('focus_consistency', 0)
        interruption_rate = features.get('interruption_rate', 0)
        
        if usage_intensity > 0.4 and interruption_rate > 5:
            return BehaviorType.ADDICTIVE
        elif focus_consistency > 0.8 and usage_intensity < 0.2:
            return BehaviorType.FOCUSED
        elif usage_intensity < 0.1:
            return BehaviorType.MINIMAL
        elif focus_consistency < 0.4 and interruption_rate > 3:
            return BehaviorType.DISTRACTED
        else:
            return BehaviorType.BALANCED
    
    def _calculate_focus_score(self, features: Dict[str, float]) -> float:
        """Calculate focus score based on features"""
        focus_session_count = features.get('focus_session_count', 0)
        avg_focus_duration = features.get('avg_focus_duration', 0)
        focus_consistency = features.get('focus_consistency', 0)
        interruption_rate = features.get('interruption_rate', 0)
        
        # Normalize values
        session_score = min(focus_session_count / 10, 1.0)
        duration_score = min(avg_focus_duration / 60, 1.0)  # normalize to 1 hour
        consistency_score = focus_consistency
        interruption_penalty = min(interruption_rate / 10, 1.0)
        
        # Weighted calculation
        focus_score = (
            session_score * 0.3 +
            duration_score * 0.3 +
            consistency_score * 0.3 -
            interruption_penalty * 0.1
        )
        
        return max(0.0, min(1.0, focus_score))
    
    def _calculate_distraction_score(self, features: Dict[str, float]) -> float:
        """Calculate distraction score based on features"""
        usage_intensity = features.get('usage_intensity', 0)
        interruption_rate = features.get('interruption_rate', 0)
        break_regularity = features.get('break_regularity', 0)
        
        # Higher usage and interruptions indicate more distraction
        distraction_score = (
            usage_intensity * 0.5 +
            min(interruption_rate / 10, 1.0) * 0.4 +
            (1.0 - break_regularity) * 0.1
        )
        
        return max(0.0, min(1.0, distraction_score))
    
    def _calculate_consistency_score(self, features: Dict[str, float]) -> float:
        """Calculate consistency score based on features"""
        focus_consistency = features.get('focus_consistency', 0)
        break_regularity = features.get('break_regularity', 0)
        goal_achievement = features.get('goal_achievement', 0)
        
        consistency_score = (
            focus_consistency * 0.4 +
            break_regularity * 0.3 +
            goal_achievement * 0.3
        )
        
        return max(0.0, min(1.0, consistency_score))
    
    def _calculate_improvement_rate(self, user_id: str, current_features: Dict[str, float]) -> float:
        """Calculate improvement rate based on historical data"""
        # This would compare current features with historical data
        # For now, return a random improvement rate
        return random.uniform(-0.1, 0.2)
    
    def _calculate_session_consistency(self, focus_sessions: List[Dict]) -> float:
        """Calculate consistency of focus sessions"""
        if not focus_sessions:
            return 0.0
        
        durations = [s.get('duration', 0) for s in focus_sessions]
        if len(durations) < 2:
            return 1.0
        
        # Calculate coefficient of variation (lower is more consistent)
        mean_duration = np.mean(durations)
        std_duration = np.std(durations)
        
        if mean_duration == 0:
            return 0.0
        
        cv = std_duration / mean_duration
        # Convert to consistency score (1.0 = most consistent)
        consistency = max(0.0, 1.0 - cv)
        
        return consistency
    
    def _calculate_break_regularity(self, user_data: Dict[str, Any]) -> float:
        """Calculate regularity of breaks"""
        # This would analyze break timing patterns
        # For now, return a random value
        return random.uniform(0.3, 0.9)
    
    def _calculate_interruption_impact(self, user_data: Dict[str, Any]) -> float:
        """Calculate impact of interruptions on productivity"""
        interruptions = user_data.get('interruptions', 0)
        focus_sessions = user_data.get('focus_sessions', [])
        
        if not focus_sessions:
            return 0.0
        
        total_focus_time = sum(s.get('duration', 0) for s in focus_sessions)
        if total_focus_time == 0:
            return 0.0
        
        # Calculate interruption rate per hour
        interruption_rate = (interruptions / total_focus_time) * 60
        
        # Convert to impact score (higher interruptions = higher impact)
        impact = min(interruption_rate / 10, 1.0)
        
        return impact
    
    def generate_insights(self, user_data: Dict[str, Any]) -> List[ProductivityInsight]:
        """Generate AI-powered productivity insights"""
        insights = []
        
        # Analyze behavior
        profile = self.analyze_user_behavior(user_data)
        
        # Generate pattern-based insights
        pattern_insights = self._generate_pattern_insights(profile, user_data)
        insights.extend(pattern_insights)
        
        # Generate behavior-based insights
        behavior_insights = self._generate_behavior_insights(profile, user_data)
        insights.extend(behavior_insights)
        
        # Generate improvement insights
        improvement_insights = self._generate_improvement_insights(profile, user_data)
        insights.extend(improvement_insights)
        
        # Add insights to queue for processing
        for insight in insights:
            self.insights_queue.put(insight)
        
        return insights
    
    def _generate_pattern_insights(self, profile: BehaviorProfile, user_data: Dict[str, Any]) -> List[ProductivityInsight]:
        """Generate insights based on productivity patterns"""
        insights = []
        
        if profile.pattern_type == ProductivityPattern.MORNING_PEAK:
            insights.append(ProductivityInsight(
                id=f"pattern_{int(time.time())}",
                type="pattern_analysis",
                title="Morning Productivity Peak Detected",
                description="You show excellent productivity in the morning hours. Consider scheduling your most important tasks during this time.",
                confidence=0.85,
                impact_score=0.8,
                action_items=[
                    "Schedule important tasks before 11 AM",
                    "Avoid meetings during peak productivity hours",
                    "Use morning time for creative work"
                ],
                timestamp=datetime.now(),
                category="productivity_pattern",
                priority=1,
                evidence={"pattern_type": profile.pattern_type.value, "focus_score": profile.focus_score}
            ))
        
        elif profile.pattern_type == ProductivityPattern.AFTERNOON_DIP:
            insights.append(ProductivityInsight(
                id=f"pattern_{int(time.time())}",
                type="pattern_analysis",
                title="Afternoon Productivity Dip Identified",
                description="Your productivity tends to decrease in the afternoon. This is common and can be managed with strategic breaks.",
                confidence=0.75,
                impact_score=0.6,
                action_items=[
                    "Schedule lighter tasks in the afternoon",
                    "Take longer breaks during this period",
                    "Consider a short walk or exercise"
                ],
                timestamp=datetime.now(),
                category="productivity_pattern",
                priority=2,
                evidence={"pattern_type": profile.pattern_type.value, "focus_score": profile.focus_score}
            ))
        
        return insights
    
    def _generate_behavior_insights(self, profile: BehaviorProfile, user_data: Dict[str, Any]) -> List[ProductivityInsight]:
        """Generate insights based on behavior type"""
        insights = []
        
        if profile.behavior_type == BehaviorType.ADDICTIVE:
            insights.append(ProductivityInsight(
                id=f"behavior_{int(time.time())}",
                type="behavior_analysis",
                title="High Distraction Pattern Detected",
                description="You're showing signs of frequent social media use that may be impacting your productivity.",
                confidence=0.9,
                impact_score=0.9,
                action_items=[
                    "Enable strict website blocking during work hours",
                    "Set shorter break intervals",
                    "Use focus mode more frequently"
                ],
                timestamp=datetime.now(),
                category="behavior_analysis",
                priority=1,
                evidence={"behavior_type": profile.behavior_type.value, "distraction_score": profile.distraction_score}
            ))
        
        elif profile.behavior_type == BehaviorType.FOCUSED:
            insights.append(ProductivityInsight(
                id=f"behavior_{int(time.time())}",
                type="behavior_analysis",
                title="Excellent Focus Habits",
                description="You're maintaining excellent focus habits! Keep up the great work.",
                confidence=0.8,
                impact_score=0.7,
                action_items=[
                    "Continue with current routine",
                    "Share your strategies with others",
                    "Set more challenging goals"
                ],
                timestamp=datetime.now(),
                category="behavior_analysis",
                priority=3,
                evidence={"behavior_type": profile.behavior_type.value, "focus_score": profile.focus_score}
            ))
        
        return insights
    
    def _generate_improvement_insights(self, profile: BehaviorProfile, user_data: Dict[str, Any]) -> List[ProductivityInsight]:
        """Generate improvement-focused insights"""
        insights = []
        
        if profile.focus_score < 0.6:
            insights.append(ProductivityInsight(
                id=f"improvement_{int(time.time())}",
                type="improvement_suggestion",
                title="Focus Score Improvement Opportunity",
                description="Your focus score could be improved. Consider implementing these strategies.",
                confidence=0.8,
                impact_score=0.7,
                action_items=[
                    "Start with shorter focus sessions",
                    "Use the Pomodoro technique",
                    "Create a dedicated workspace"
                ],
                timestamp=datetime.now(),
                category="improvement",
                priority=2,
                evidence={"current_focus_score": profile.focus_score, "target_score": 0.8}
            ))
        
        if profile.consistency_score < 0.5:
            insights.append(ProductivityInsight(
                id=f"improvement_{int(time.time())}",
                type="improvement_suggestion",
                title="Consistency Improvement Needed",
                description="Your productivity consistency could be improved with better routine building.",
                confidence=0.75,
                impact_score=0.6,
                action_items=[
                    "Establish a daily routine",
                    "Set consistent work hours",
                    "Track your progress daily"
                ],
                timestamp=datetime.now(),
                category="improvement",
                priority=2,
                evidence={"current_consistency_score": profile.consistency_score, "target_score": 0.7}
            ))
        
        return insights
    
    def generate_recommendations(self, user_data: Dict[str, Any]) -> List[AIRecommendation]:
        """Generate personalized AI recommendations"""
        recommendations = []
        
        # Analyze current behavior
        profile = self.analyze_user_behavior(user_data)
        
        # Generate recommendations based on behavior type
        if profile.behavior_type == BehaviorType.ADDICTIVE:
            recommendations.extend(self._generate_addictive_behavior_recommendations(profile))
        elif profile.behavior_type == BehaviorType.DISTRACTED:
            recommendations.extend(self._generate_distracted_behavior_recommendations(profile))
        elif profile.behavior_type == BehaviorType.FOCUSED:
            recommendations.extend(self._generate_focused_behavior_recommendations(profile))
        
        # Generate general recommendations
        recommendations.extend(self._generate_general_recommendations(profile))
        
        # Add recommendations to queue
        for rec in recommendations:
            self.recommendations_queue.put(rec)
        
        return recommendations
    
    def _generate_addictive_behavior_recommendations(self, profile: BehaviorProfile) -> List[AIRecommendation]:
        """Generate recommendations for addictive behavior"""
        recommendations = []
        
        recommendations.append(AIRecommendation(
            id=f"rec_{int(time.time())}",
            type=RecommendationType.INTERVENTION,
            title="Implement Strict Social Media Limits",
            description="Based on your usage patterns, consider implementing stricter social media limits to improve productivity.",
            reasoning="Your high distraction score indicates frequent social media use that's impacting focus.",
            expected_impact=0.8,
            implementation_steps=[
                "Set daily limit to 30 minutes",
                "Enable website blocking during work hours",
                "Use focus mode for 2-hour sessions"
            ],
            difficulty="medium",
            time_commitment=15,
            success_rate=0.75,
            timestamp=datetime.now(),
            status="pending"
        ))
        
        return recommendations
    
    def _generate_distracted_behavior_recommendations(self, profile: BehaviorProfile) -> List[AIRecommendation]:
        """Generate recommendations for distracted behavior"""
        recommendations = []
        
        recommendations.append(AIRecommendation(
            id=f"rec_{int(time.time())}",
            type=RecommendationType.FOCUS_TIME,
            title="Implement Focus Training",
            description="Start with short focus sessions and gradually increase duration to build focus stamina.",
            reasoning="Your low focus consistency suggests need for focus training.",
            expected_impact=0.6,
            implementation_steps=[
                "Start with 15-minute focus sessions",
                "Take 5-minute breaks between sessions",
                "Gradually increase to 45-minute sessions"
            ],
            difficulty="easy",
            time_commitment=20,
            success_rate=0.8,
            timestamp=datetime.now(),
            status="pending"
        ))
        
        return recommendations
    
    def _generate_focused_behavior_recommendations(self, profile: BehaviorProfile) -> List[AIRecommendation]:
        """Generate recommendations for focused behavior"""
        recommendations = []
        
        recommendations.append(AIRecommendation(
            id=f"rec_{int(time.time())}",
            type=RecommendationType.GOAL_ADJUSTMENT,
            title="Set More Challenging Goals",
            description="Your excellent focus habits suggest you're ready for more challenging productivity goals.",
            reasoning="High focus score indicates capacity for increased productivity targets.",
            expected_impact=0.7,
            implementation_steps=[
                "Increase daily focus time by 30 minutes",
                "Add one additional focus session per day",
                "Set weekly productivity milestones"
            ],
            difficulty="medium",
            time_commitment=30,
            success_rate=0.85,
            timestamp=datetime.now(),
            status="pending"
        ))
        
        return recommendations
    
    def _generate_general_recommendations(self, profile: BehaviorProfile) -> List[AIRecommendation]:
        """Generate general recommendations for all users"""
        recommendations = []
        
        # Break schedule recommendation
        recommendations.append(AIRecommendation(
            id=f"rec_{int(time.time())}",
            type=RecommendationType.BREAK_SCHEDULE,
            title="Optimize Break Schedule",
            description="Implement a structured break schedule to maintain productivity throughout the day.",
            reasoning="Regular breaks help maintain focus and prevent burnout.",
            expected_impact=0.5,
            implementation_steps=[
                "Take 5-minute breaks every 25 minutes",
                "Take 15-minute breaks every 2 hours",
                "Use break time for physical activity"
            ],
            difficulty="easy",
            time_commitment=5,
            success_rate=0.9,
            timestamp=datetime.now(),
            status="pending"
        ))
        
        return recommendations
    
    def _background_processing(self):
        """Background processing for insights and recommendations"""
        while True:
            try:
                # Process insights
                while not self.insights_queue.empty():
                    insight = self.insights_queue.get_nowait()
                    self._save_insight(insight)
                
                # Process recommendations
                while not self.recommendations_queue.empty():
                    recommendation = self.recommendations_queue.get_nowait()
                    self._save_recommendation(recommendation)
                
                # Update ML models periodically
                if time.time() % 3600 < 1:  # Every hour
                    self._update_ml_models()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in background processing: {e}")
                time.sleep(30)
    
    def _save_behavior_profile(self, profile: BehaviorProfile):
        """Save behavior profile to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO behavior_profiles 
                    (user_id, pattern_type, behavior_type, focus_score, distraction_score, 
                     consistency_score, improvement_rate, last_updated, features)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    profile.pattern_type.value,
                    profile.behavior_type.value,
                    profile.focus_score,
                    profile.distraction_score,
                    profile.consistency_score,
                    profile.improvement_rate,
                    profile.last_updated.isoformat(),
                    json.dumps(profile.features)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving behavior profile: {e}")
    
    def _save_insight(self, insight: ProductivityInsight):
        """Save insight to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO productivity_insights 
                    (id, type, title, description, confidence, impact_score, 
                     action_items, timestamp, category, priority, evidence, user_feedback)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    insight.id,
                    insight.type,
                    insight.title,
                    insight.description,
                    insight.confidence,
                    insight.impact_score,
                    json.dumps(insight.action_items),
                    insight.timestamp.isoformat(),
                    insight.category,
                    insight.priority,
                    json.dumps(insight.evidence),
                    insight.user_feedback
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving insight: {e}")
    
    def _save_recommendation(self, recommendation: AIRecommendation):
        """Save recommendation to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ai_recommendations 
                    (id, type, title, description, reasoning, expected_impact,
                     implementation_steps, difficulty, time_commitment, success_rate,
                     timestamp, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    recommendation.id,
                    recommendation.type.value,
                    recommendation.title,
                    recommendation.description,
                    recommendation.reasoning,
                    recommendation.expected_impact,
                    json.dumps(recommendation.implementation_steps),
                    recommendation.difficulty,
                    recommendation.time_commitment,
                    recommendation.success_rate,
                    recommendation.timestamp.isoformat(),
                    recommendation.status
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving recommendation: {e}")
    
    def _update_ml_models(self):
        """Update machine learning models with new data"""
        try:
            # Load training data
            training_data = self._load_training_data()
            
            if len(training_data) < self.min_data_points:
                return
            
            # Update models
            for model_name, model in self.ml_models.items():
                if model_name == 'behavior_classifier':
                    self._update_classification_model(model, training_data)
                elif model_name in ['productivity_predictor', 'focus_predictor']:
                    self._update_regression_model(model, training_data)
            
            print("🧠 ML models updated successfully!")
            
        except Exception as e:
            logger.error(f"Error updating ML models: {e}")
    
    def _load_training_data(self) -> List[Dict[str, Any]]:
        """Load training data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM behavior_profiles ORDER BY last_updated DESC LIMIT 1000")
                rows = cursor.fetchall()
                
                training_data = []
                for row in rows:
                    training_data.append({
                        'features': json.loads(row[8]),
                        'behavior_type': row[2],
                        'focus_score': row[3],
                        'productivity_score': row[4]
                    })
                
                return training_data
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return []
    
    def _update_classification_model(self, model, training_data: List[Dict[str, Any]]):
        """Update classification model"""
        X = [d['features'] for d in training_data]
        y = [d['behavior_type'] for d in training_data]
        
        if len(set(y)) < 2:  # Need at least 2 classes
            return
        
        # Convert features to array
        feature_names = list(X[0].keys())
        X_array = np.array([[x[f] for f in feature_names] for x in X])
        
        # Update scaler
        self.scalers['standard'].partial_fit(X_array)
        X_scaled = self.scalers['standard'].transform(X_array)
        
        # Update model
        model.partial_fit(X_scaled, y, classes=list(set(y)))
    
    def _update_regression_model(self, model, training_data: List[Dict[str, Any]]):
        """Update regression model"""
        X = [d['features'] for d in training_data]
        y = [d['focus_score'] for d in training_data]
        
        # Convert features to array
        feature_names = list(X[0].keys())
        X_array = np.array([[x[f] for f in feature_names] for x in X])
        
        # Update scaler
        self.scalers['robust'].partial_fit(X_array)
        X_scaled = self.scalers['robust'].transform(X_array)
        
        # Update model
        model.partial_fit(X_scaled, y)
    
    def get_user_insights(self, user_id: str, limit: int = 10) -> List[ProductivityInsight]:
        """Get insights for a specific user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM productivity_insights 
                    WHERE user_id = ? OR user_id IS NULL
                    ORDER BY timestamp DESC LIMIT ?
                """, (user_id, limit))
                rows = cursor.fetchall()
                
                insights = []
                for row in rows:
                    insight = ProductivityInsight(
                        id=row[0],
                        type=row[1],
                        title=row[2],
                        description=row[3],
                        confidence=row[4],
                        impact_score=row[5],
                        action_items=json.loads(row[6]),
                        timestamp=datetime.fromisoformat(row[7]),
                        category=row[8],
                        priority=row[9],
                        evidence=json.loads(row[10]),
                        user_feedback=row[11]
                    )
                    insights.append(insight)
                
                return insights
        except Exception as e:
            logger.error(f"Error getting user insights: {e}")
            return []
    
    def get_user_recommendations(self, user_id: str, limit: int = 10) -> List[AIRecommendation]:
        """Get recommendations for a specific user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM ai_recommendations 
                    WHERE user_id = ? OR user_id IS NULL
                    ORDER BY timestamp DESC LIMIT ?
                """, (user_id, limit))
                rows = cursor.fetchall()
                
                recommendations = []
                for row in rows:
                    recommendation = AIRecommendation(
                        id=row[0],
                        type=RecommendationType(row[1]),
                        title=row[2],
                        description=row[3],
                        reasoning=row[4],
                        expected_impact=row[5],
                        implementation_steps=json.loads(row[6]),
                        difficulty=row[7],
                        time_commitment=row[8],
                        success_rate=row[9],
                        timestamp=datetime.fromisoformat(row[10]),
                        status=row[11]
                    )
                    recommendations.append(recommendation)
                
                return recommendations
        except Exception as e:
            logger.error(f"Error getting user recommendations: {e}")
            return []

# Initialize database tables
def initialize_ai_database(db_path: str = "productivity.db"):
    """Initialize database tables for AI features"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Behavior profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS behavior_profiles (
                    user_id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    behavior_type TEXT,
                    focus_score REAL,
                    distraction_score REAL,
                    consistency_score REAL,
                    improvement_rate REAL,
                    last_updated TEXT,
                    features TEXT
                )
            """)
            
            # Productivity insights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productivity_insights (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    title TEXT,
                    description TEXT,
                    confidence REAL,
                    impact_score REAL,
                    action_items TEXT,
                    timestamp TEXT,
                    category TEXT,
                    priority INTEGER,
                    evidence TEXT,
                    user_feedback TEXT
                )
            """)
            
            # AI recommendations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_recommendations (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    title TEXT,
                    description TEXT,
                    reasoning TEXT,
                    expected_impact REAL,
                    implementation_steps TEXT,
                    difficulty TEXT,
                    time_commitment INTEGER,
                    success_rate REAL,
                    timestamp TEXT,
                    status TEXT
                )
            """)
            
            conn.commit()
            print("🗄️ AI database tables initialized successfully!")
            
    except Exception as e:
        logger.error(f"Error initializing AI database: {e}")

if __name__ == "__main__":
    # Initialize database
    initialize_ai_database()
    
    # Create AI engine
    ai_engine = AIProductivityEngine()
    
    # Example usage
    sample_data = {
        'user_id': 'test_user',
        'daily_usage': 180,
        'focus_sessions': [
            {'duration': 45, 'interruptions': 2},
            {'duration': 30, 'interruptions': 1}
        ],
        'breaks_taken': 3,
        'goals_met': False,
        'goal_progress': 0.6,
        'interruptions': 5
    }
    
    # Generate insights and recommendations
    insights = ai_engine.generate_insights(sample_data)
    recommendations = ai_engine.generate_recommendations(sample_data)
    
    print(f"Generated {len(insights)} insights and {len(recommendations)} recommendations!")
