#!/usr/bin/env python3
"""
Advanced Machine Learning Analytics System
Advanced ML analytics including predictive modeling, behavior analysis, and intelligent insights.
"""

import json
import time
import threading
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from enum import Enum
import sqlite3
import uuid
from pathlib import Path
import pickle
import joblib

# Machine Learning imports
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
    from sklearn.decomposition import PCA
    from sklearn.feature_extraction.text import TfidfVectorizer
    import xgboost as xgb
    import lightgbm as lgb
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML libraries not available. Install scikit-learn, xgboost, lightgbm")

logger = logging.getLogger(__name__)

class MLModelType(Enum):
    """Machine learning model types"""
    PRODUCTIVITY_PREDICTOR = "productivity_predictor"
    BEHAVIOR_CLASSIFIER = "behavior_classifier"
    FOCUS_OPTIMIZER = "focus_optimizer"
    BREAK_RECOMMENDER = "break_recommender"
    GOAL_ACHIEVEMENT_PREDICTOR = "goal_achievement_predictor"
    ANOMALY_DETECTOR = "anomaly_detector"

class PredictionType(Enum):
    """Prediction types"""
    DAILY_PRODUCTIVITY = "daily_productivity"
    FOCUS_SESSION_DURATION = "focus_session_duration"
    BREAK_OPTIMAL_TIME = "break_optimal_time"
    GOAL_COMPLETION_PROBABILITY = "goal_completion_probability"
    BEHAVIOR_PATTERN = "behavior_pattern"
    ANOMALY_SCORE = "anomaly_score"

@dataclass
class MLModel:
    """Machine learning model definition"""
    model_id: str
    model_type: MLModelType
    model_object: Any
    features: List[str]
    target: str
    accuracy: float
    created_date: datetime
    last_updated: datetime
    version: str
    hyperparameters: Dict[str, Any]

@dataclass
class Prediction:
    """Prediction result"""
    id: str
    user_id: str
    model_id: str
    prediction_type: PredictionType
    predicted_value: float
    confidence: float
    features_used: Dict[str, float]
    timestamp: datetime
    actual_value: Optional[float]

@dataclass
class BehaviorPattern:
    """Behavior pattern analysis"""
    user_id: str
    pattern_type: str
    confidence: float
    features: Dict[str, float]
    recommendations: List[str]
    created_date: datetime

class AdvancedMLAnalytics:
    """Advanced machine learning analytics system"""
    
    def __init__(self, db_path: str = "productivity.db"):
        self.db_path = db_path
        self.models = {}
        self.predictions = {}
        self.behavior_patterns = {}
        self.scalers = {}
        self.feature_importance = {}
        
        # Initialize ML components
        self._initialize_ml_components()
        
        # Start background processing
        self.processing_thread = threading.Thread(target=self._background_processing, daemon=True)
        self.processing_thread.start()
        
        print("🤖 Advanced ML Analytics System initialized!")
        print("🧠 Predictive models active!")
        print("📊 Intelligent insights enabled!")
    
    def _initialize_ml_components(self):
        """Initialize machine learning components"""
        if not ML_AVAILABLE:
            print("⚠️ ML components not available")
            return
        
        try:
            # Initialize models
            self._create_productivity_predictor()
            self._create_behavior_classifier()
            self._create_focus_optimizer()
            self._create_break_recommender()
            self._create_goal_predictor()
            self._create_anomaly_detector()
            
            print("🤖 ML models initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing ML components: {e}")
    
    def _create_productivity_predictor(self):
        """Create productivity prediction model"""
        model_id = str(uuid.uuid4())
        
        model = MLModel(
            model_id=model_id,
            model_type=MLModelType.PRODUCTIVITY_PREDICTOR,
            model_object=RandomForestRegressor(n_estimators=100, random_state=42),
            features=['focus_time', 'breaks_taken', 'interruptions', 'time_of_day', 'day_of_week'],
            target='productivity_score',
            accuracy=0.0,
            created_date=datetime.now(),
            last_updated=datetime.now(),
            version="1.0",
            hyperparameters={'n_estimators': 100, 'max_depth': 10}
        )
        
        self.models[model_id] = model
        self.scalers[model_id] = StandardScaler()
        
        print("📈 Productivity predictor created")
    
    def _create_behavior_classifier(self):
        """Create behavior classification model"""
        model_id = str(uuid.uuid4())
        
        model = MLModel(
            model_id=model_id,
            model_type=MLModelType.BEHAVIOR_CLASSIFIER,
            model_object=GradientBoostingClassifier(n_estimators=100, random_state=42),
            features=['session_duration', 'break_frequency', 'interruption_rate', 'focus_score'],
            target='behavior_type',
            accuracy=0.0,
            created_date=datetime.now(),
            last_updated=datetime.now(),
            version="1.0",
            hyperparameters={'n_estimators': 100, 'learning_rate': 0.1}
        )
        
        self.models[model_id] = model
        self.scalers[model_id] = StandardScaler()
        
        print("🎯 Behavior classifier created")
    
    def _create_focus_optimizer(self):
        """Create focus optimization model"""
        model_id = str(uuid.uuid4())
        
        model = MLModel(
            model_id=model_id,
            model_type=MLModelType.FOCUS_OPTIMIZER,
            model_object=xgb.XGBRegressor(n_estimators=100, random_state=42),
            features=['time_of_day', 'energy_level', 'previous_focus_duration', 'environment_noise'],
            target='optimal_focus_duration',
            accuracy=0.0,
            created_date=datetime.now(),
            last_updated=datetime.now(),
            version="1.0",
            hyperparameters={'n_estimators': 100, 'max_depth': 6}
        )
        
        self.models[model_id] = model
        self.scalers[model_id] = StandardScaler()
        
        print("🎯 Focus optimizer created")
    
    def _create_break_recommender(self):
        """Create break recommendation model"""
        model_id = str(uuid.uuid4())
        
        model = MLModel(
            model_id=model_id,
            model_type=MLModelType.BREAK_RECOMMENDER,
            model_object=lgb.LGBMRegressor(n_estimators=100, random_state=42),
            features=['focus_duration', 'energy_level', 'stress_level', 'time_since_last_break'],
            target='break_duration',
            accuracy=0.0,
            created_date=datetime.now(),
            last_updated=datetime.now(),
            version="1.0",
            hyperparameters={'n_estimators': 100, 'learning_rate': 0.1}
        )
        
        self.models[model_id] = model
        self.scalers[model_id] = StandardScaler()
        
        print("☕ Break recommender created")
    
    def _create_goal_predictor(self):
        """Create goal achievement prediction model"""
        model_id = str(uuid.uuid4())
        
        model = MLModel(
            model_id=model_id,
            model_type=MLModelType.GOAL_ACHIEVEMENT_PREDICTOR,
            model_object=LogisticRegression(random_state=42),
            features=['goal_difficulty', 'time_remaining', 'progress_rate', 'motivation_level'],
            target='achievement_probability',
            accuracy=0.0,
            created_date=datetime.now(),
            last_updated=datetime.now(),
            version="1.0",
            hyperparameters={'C': 1.0, 'max_iter': 1000}
        )
        
        self.models[model_id] = model
        self.scalers[model_id] = StandardScaler()
        
        print("🎯 Goal predictor created")
    
    def _create_anomaly_detector(self):
        """Create anomaly detection model"""
        model_id = str(uuid.uuid4())
        
        model = MLModel(
            model_id=model_id,
            model_type=MLModelType.ANOMALY_DETECTOR,
            model_object=DBSCAN(eps=0.5, min_samples=5),
            features=['focus_time', 'break_time', 'interruptions', 'productivity_score'],
            target='anomaly_score',
            accuracy=0.0,
            created_date=datetime.now(),
            last_updated=datetime.now(),
            version="1.0",
            hyperparameters={'eps': 0.5, 'min_samples': 5}
        )
        
        self.models[model_id] = model
        self.scalers[model_id] = StandardScaler()
        
        print("🔍 Anomaly detector created")
    
    def train_models(self, user_id: str = None):
        """Train all ML models with user data"""
        try:
            # Get training data
            training_data = self._get_training_data(user_id)
            
            if training_data.empty:
                print("⚠️ No training data available")
                return
            
            for model_id, model in self.models.items():
                self._train_model(model_id, training_data)
            
            print("✅ All models trained successfully!")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    def _train_model(self, model_id: str, training_data: pd.DataFrame):
        """Train a specific model"""
        try:
            model = self.models[model_id]
            
            # Prepare features and target
            X = training_data[model.features].fillna(0)
            y = training_data[model.target] if model.target in training_data.columns else None
            
            if y is None:
                print(f"⚠️ No target data for model {model.model_type.value}")
                return
            
            # Scale features
            X_scaled = self.scalers[model_id].fit_transform(X)
            
            # Train model
            model.model_object.fit(X_scaled, y)
            
            # Calculate accuracy
            if hasattr(model.model_object, 'score'):
                accuracy = model.model_object.score(X_scaled, y)
                model.accuracy = accuracy
            
            # Update model
            model.last_updated = datetime.now()
            self._save_model(model)
            
            print(f"✅ {model.model_type.value} trained with accuracy: {accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"Error training model {model_id}: {e}")
    
    def predict_productivity(self, user_id: str, features: Dict[str, float]) -> Prediction:
        """Predict productivity score"""
        try:
            model_id = self._get_model_id(MLModelType.PRODUCTIVITY_PREDICTOR)
            if not model_id:
                return None
            
            prediction = self._make_prediction(
                user_id=user_id,
                model_id=model_id,
                prediction_type=PredictionType.DAILY_PRODUCTIVITY,
                features=features
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting productivity: {e}")
            return None
    
    def classify_behavior(self, user_id: str, features: Dict[str, float]) -> Prediction:
        """Classify user behavior"""
        try:
            model_id = self._get_model_id(MLModelType.BEHAVIOR_CLASSIFIER)
            if not model_id:
                return None
            
            prediction = self._make_prediction(
                user_id=user_id,
                model_id=model_id,
                prediction_type=PredictionType.BEHAVIOR_PATTERN,
                features=features
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error classifying behavior: {e}")
            return None
    
    def optimize_focus_duration(self, user_id: str, features: Dict[str, float]) -> Prediction:
        """Optimize focus session duration"""
        try:
            model_id = self._get_model_id(MLModelType.FOCUS_OPTIMIZER)
            if not model_id:
                return None
            
            prediction = self._make_prediction(
                user_id=user_id,
                model_id=model_id,
                prediction_type=PredictionType.FOCUS_SESSION_DURATION,
                features=features
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error optimizing focus duration: {e}")
            return None
    
    def recommend_break_duration(self, user_id: str, features: Dict[str, float]) -> Prediction:
        """Recommend break duration"""
        try:
            model_id = self._get_model_id(MLModelType.BREAK_RECOMMENDER)
            if not model_id:
                return None
            
            prediction = self._make_prediction(
                user_id=user_id,
                model_id=model_id,
                prediction_type=PredictionType.BREAK_OPTIMAL_TIME,
                features=features
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error recommending break duration: {e}")
            return None
    
    def predict_goal_achievement(self, user_id: str, features: Dict[str, float]) -> Prediction:
        """Predict goal achievement probability"""
        try:
            model_id = self._get_model_id(MLModelType.GOAL_ACHIEVEMENT_PREDICTOR)
            if not model_id:
                return None
            
            prediction = self._make_prediction(
                user_id=user_id,
                model_id=model_id,
                prediction_type=PredictionType.GOAL_COMPLETION_PROBABILITY,
                features=features
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting goal achievement: {e}")
            return None
    
    def detect_anomalies(self, user_id: str, features: Dict[str, float]) -> Prediction:
        """Detect behavioral anomalies"""
        try:
            model_id = self._get_model_id(MLModelType.ANOMALY_DETECTOR)
            if not model_id:
                return None
            
            prediction = self._make_prediction(
                user_id=user_id,
                model_id=model_id,
                prediction_type=PredictionType.ANOMALY_SCORE,
                features=features
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return None
    
    def _make_prediction(self, user_id: str, model_id: str, prediction_type: PredictionType, 
                        features: Dict[str, float]) -> Prediction:
        """Make a prediction using a trained model"""
        try:
            model = self.models[model_id]
            
            # Prepare features
            feature_vector = []
            for feature in model.features:
                feature_vector.append(features.get(feature, 0.0))
            
            # Scale features
            feature_vector_scaled = self.scalers[model_id].transform([feature_vector])
            
            # Make prediction
            if prediction_type == PredictionType.GOAL_COMPLETION_PROBABILITY:
                predicted_value = model.model_object.predict_proba(feature_vector_scaled)[0][1]
            else:
                predicted_value = model.model_object.predict(feature_vector_scaled)[0]
            
            # Calculate confidence (simplified)
            confidence = min(0.95, model.accuracy + 0.1)
            
            # Create prediction object
            prediction_id = str(uuid.uuid4())
            prediction = Prediction(
                id=prediction_id,
                user_id=user_id,
                model_id=model_id,
                prediction_type=prediction_type,
                predicted_value=float(predicted_value),
                confidence=confidence,
                features_used=features,
                timestamp=datetime.now(),
                actual_value=None
            )
            
            self.predictions[prediction_id] = prediction
            self._save_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return None
    
    def analyze_behavior_patterns(self, user_id: str) -> List[BehaviorPattern]:
        """Analyze user behavior patterns"""
        try:
            # Get user data
            user_data = self._get_user_data(user_id)
            
            if user_data.empty:
                return []
            
            patterns = []
            
            # Pattern 1: Time-based patterns
            time_pattern = self._analyze_time_patterns(user_data)
            if time_pattern:
                patterns.append(time_pattern)
            
            # Pattern 2: Focus patterns
            focus_pattern = self._analyze_focus_patterns(user_data)
            if focus_pattern:
                patterns.append(focus_pattern)
            
            # Pattern 3: Break patterns
            break_pattern = self._analyze_break_patterns(user_data)
            if break_pattern:
                patterns.append(break_pattern)
            
            # Save patterns
            for pattern in patterns:
                self.behavior_patterns[pattern.user_id] = pattern
                self._save_behavior_pattern(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing behavior patterns: {e}")
            return []
    
    def _analyze_time_patterns(self, user_data: pd.DataFrame) -> Optional[BehaviorPattern]:
        """Analyze time-based behavior patterns"""
        try:
            # Analyze peak productivity hours
            if 'time_of_day' in user_data.columns and 'productivity_score' in user_data.columns:
                peak_hours = user_data.groupby('time_of_day')['productivity_score'].mean().nlargest(3)
                
                pattern = BehaviorPattern(
                    user_id=user_data['user_id'].iloc[0] if 'user_id' in user_data.columns else "unknown",
                    pattern_type="peak_productivity_hours",
                    confidence=0.8,
                    features={'peak_hours': peak_hours.to_dict()},
                    recommendations=[
                        "Schedule important tasks during peak hours",
                        "Use peak hours for deep work sessions",
                        "Avoid meetings during peak productivity times"
                    ],
                    created_date=datetime.now()
                )
                
                return pattern
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing time patterns: {e}")
            return None
    
    def _analyze_focus_patterns(self, user_data: pd.DataFrame) -> Optional[BehaviorPattern]:
        """Analyze focus behavior patterns"""
        try:
            if 'focus_duration' in user_data.columns:
                avg_focus_duration = user_data['focus_duration'].mean()
                focus_std = user_data['focus_duration'].std()
                
                pattern = BehaviorPattern(
                    user_id=user_data['user_id'].iloc[0] if 'user_id' in user_data.columns else "unknown",
                    pattern_type="focus_duration_pattern",
                    confidence=0.7,
                    features={
                        'avg_focus_duration': avg_focus_duration,
                        'focus_std': focus_std,
                        'optimal_range': [avg_focus_duration - focus_std, avg_focus_duration + focus_std]
                    },
                    recommendations=[
                        f"Target focus sessions around {avg_focus_duration:.1f} minutes",
                        "Take breaks when focus duration exceeds optimal range",
                        "Gradually increase focus duration for improvement"
                    ],
                    created_date=datetime.now()
                )
                
                return pattern
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing focus patterns: {e}")
            return None
    
    def _analyze_break_patterns(self, user_data: pd.DataFrame) -> Optional[BehaviorPattern]:
        """Analyze break behavior patterns"""
        try:
            if 'break_duration' in user_data.columns:
                avg_break_duration = user_data['break_duration'].mean()
                break_frequency = len(user_data) / max(1, user_data['break_duration'].sum() / 60)
                
                pattern = BehaviorPattern(
                    user_id=user_data['user_id'].iloc[0] if 'user_id' in user_data.columns else "unknown",
                    pattern_type="break_pattern",
                    confidence=0.6,
                    features={
                        'avg_break_duration': avg_break_duration,
                        'break_frequency': break_frequency
                    },
                    recommendations=[
                        f"Take breaks of {avg_break_duration:.1f} minutes",
                        "Schedule breaks every 90-120 minutes",
                        "Use breaks for physical activity when possible"
                    ],
                    created_date=datetime.now()
                )
                
                return pattern
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing break patterns: {e}")
            return None
    
    def get_ml_insights(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive ML insights for a user"""
        try:
            insights = {
                "user_id": user_id,
                "predictions": {},
                "patterns": [],
                "recommendations": [],
                "model_performance": {}
            }
            
            # Get recent predictions
            user_predictions = [p for p in self.predictions.values() if p.user_id == user_id]
            for prediction in user_predictions[-5:]:  # Last 5 predictions
                insights["predictions"][prediction.prediction_type.value] = {
                    "value": prediction.predicted_value,
                    "confidence": prediction.confidence,
                    "timestamp": prediction.timestamp.isoformat()
                }
            
            # Get behavior patterns
            user_patterns = [p for p in self.behavior_patterns.values() if p.user_id == user_id]
            insights["patterns"] = [
                {
                    "type": pattern.pattern_type,
                    "confidence": pattern.confidence,
                    "features": pattern.features,
                    "recommendations": pattern.recommendations
                }
                for pattern in user_patterns
            ]
            
            # Generate recommendations
            insights["recommendations"] = self._generate_recommendations(user_id, insights)
            
            # Model performance
            for model_id, model in self.models.items():
                insights["model_performance"][model.model_type.value] = {
                    "accuracy": model.accuracy,
                    "last_updated": model.last_updated.isoformat(),
                    "version": model.version
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting ML insights: {e}")
            return {"error": "Failed to generate insights"}
    
    def _generate_recommendations(self, user_id: str, insights: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        try:
            # Productivity recommendations
            if "daily_productivity" in insights["predictions"]:
                productivity = insights["predictions"]["daily_productivity"]["value"]
                if productivity < 0.6:
                    recommendations.append("Consider reducing distractions during work hours")
                    recommendations.append("Try the Pomodoro technique for better focus")
                elif productivity > 0.8:
                    recommendations.append("Excellent productivity! Maintain this momentum")
            
            # Focus recommendations
            if "focus_session_duration" in insights["predictions"]:
                focus_duration = insights["predictions"]["focus_session_duration"]["value"]
                if focus_duration < 25:
                    recommendations.append("Try extending focus sessions gradually")
                elif focus_duration > 90:
                    recommendations.append("Consider shorter focus sessions with more breaks")
            
            # Break recommendations
            if "break_optimal_time" in insights["predictions"]:
                break_time = insights["predictions"]["break_optimal_time"]["value"]
                recommendations.append(f"Take breaks of {break_time:.0f} minutes for optimal recovery")
            
            # Pattern-based recommendations
            for pattern in insights["patterns"]:
                recommendations.extend(pattern["recommendations"][:2])  # Top 2 recommendations per pattern
            
            return list(set(recommendations))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Focus on maintaining consistent work habits", "Take regular breaks to stay productive"]
    
    def _get_model_id(self, model_type: MLModelType) -> Optional[str]:
        """Get model ID by type"""
        for model_id, model in self.models.items():
            if model.model_type == model_type:
                return model_id
        return None
    
    def _get_training_data(self, user_id: str = None) -> pd.DataFrame:
        """Get training data for ML models"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get usage data
                query = "SELECT * FROM usage_data"
                if user_id:
                    query += f" WHERE user_id = '{user_id}'"
                
                usage_data = pd.read_sql_query(query, conn)
                
                # Get focus sessions
                query = "SELECT * FROM focus_sessions"
                if user_id:
                    query += f" WHERE user_id = '{user_id}'"
                
                focus_data = pd.read_sql_query(query, conn)
                
                # Combine data (simplified)
                if not usage_data.empty and not focus_data.empty:
                    combined_data = pd.merge(usage_data, focus_data, on='user_id', how='outer')
                else:
                    combined_data = usage_data if not usage_data.empty else focus_data
                
                return combined_data
                
        except Exception as e:
            logger.error(f"Error getting training data: {e}")
            return pd.DataFrame()
    
    def _get_user_data(self, user_id: str) -> pd.DataFrame:
        """Get user data for analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = f"SELECT * FROM usage_data WHERE user_id = '{user_id}'"
                return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return pd.DataFrame()
    
    def _background_processing(self):
        """Background processing for ML analytics"""
        while True:
            try:
                # Retrain models periodically
                if datetime.now().hour % 6 == 0:  # Every 6 hours
                    self.train_models()
                
                # Update predictions with actual values
                self._update_predictions()
                
                time.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in ML background processing: {e}")
                time.sleep(3600)
    
    def _update_predictions(self):
        """Update predictions with actual values"""
        try:
            # This would compare predictions with actual outcomes
            # and update model accuracy
            pass
        except Exception as e:
            logger.error(f"Error updating predictions: {e}")
    
    def _save_model(self, model: MLModel):
        """Save model to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO ml_models 
                    (model_id, model_type, features, target, accuracy, created_date, 
                     last_updated, version, hyperparameters)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model.model_id,
                    model.model_type.value,
                    json.dumps(model.features),
                    model.target,
                    model.accuracy,
                    model.created_date.isoformat(),
                    model.last_updated.isoformat(),
                    model.version,
                    json.dumps(model.hyperparameters)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def _save_prediction(self, prediction: Prediction):
        """Save prediction to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ml_predictions 
                    (id, user_id, model_id, prediction_type, predicted_value, confidence,
                     features_used, timestamp, actual_value)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prediction.id,
                    prediction.user_id,
                    prediction.model_id,
                    prediction.prediction_type.value,
                    prediction.predicted_value,
                    prediction.confidence,
                    json.dumps(prediction.features_used),
                    prediction.timestamp.isoformat(),
                    prediction.actual_value
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
    
    def _save_behavior_pattern(self, pattern: BehaviorPattern):
        """Save behavior pattern to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO behavior_patterns 
                    (user_id, pattern_type, confidence, features, recommendations, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    pattern.user_id,
                    pattern.pattern_type,
                    pattern.confidence,
                    json.dumps(pattern.features),
                    json.dumps(pattern.recommendations),
                    pattern.created_date.isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving behavior pattern: {e}")

# Initialize database tables
def initialize_ml_database(db_path: str = "productivity.db"):
    """Initialize database tables for ML analytics"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # ML models table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_models (
                    model_id TEXT PRIMARY KEY,
                    model_type TEXT,
                    features TEXT,
                    target TEXT,
                    accuracy REAL,
                    created_date TEXT,
                    last_updated TEXT,
                    version TEXT,
                    hyperparameters TEXT
                )
            """)
            
            # ML predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    model_id TEXT,
                    prediction_type TEXT,
                    predicted_value REAL,
                    confidence REAL,
                    features_used TEXT,
                    timestamp TEXT,
                    actual_value REAL
                )
            """)
            
            # Behavior patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS behavior_patterns (
                    user_id TEXT,
                    pattern_type TEXT,
                    confidence REAL,
                    features TEXT,
                    recommendations TEXT,
                    created_date TEXT,
                    PRIMARY KEY (user_id, pattern_type)
                )
            """)
            
            conn.commit()
            print("🤖 ML database tables initialized successfully!")
            
    except Exception as e:
        logger.error(f"Error initializing ML database: {e}")

if __name__ == "__main__":
    # Initialize database
    initialize_ml_database()
    
    # Create ML analytics system
    ml_system = AdvancedMLAnalytics()
    
    # Train models
    ml_system.train_models()
    
    # Example predictions
    features = {
        'focus_time': 120,
        'breaks_taken': 3,
        'interruptions': 2,
        'time_of_day': 14,
        'day_of_week': 2
    }
    
    prediction = ml_system.predict_productivity("test_user", features)
    if prediction:
        print(f"📈 Productivity prediction: {prediction.predicted_value:.3f}")
    
    # Get insights
    insights = ml_system.get_ml_insights("test_user")
    print(f"🧠 ML insights generated for test_user")
    
    print("🤖 Advanced ML Analytics System ready!")
