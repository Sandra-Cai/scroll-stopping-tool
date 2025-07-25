#!/usr/bin/env python3
"""
Machine Learning Analytics Module for Enhanced Scroll Stopping Tool
Predictive analytics and smart insights using ML techniques.
"""

import numpy as np
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Prediction:
    """ML prediction result"""
    type: str  # usage, productivity, behavior
    value: float
    confidence: float
    factors: List[str]
    timestamp: datetime

@dataclass
class BehaviorPattern:
    """Identified behavior pattern"""
    pattern_type: str
    description: str
    confidence: float
    frequency: float
    impact: str  # positive, negative, neutral

class SimpleMLPredictor:
    """Simple machine learning predictor using basic algorithms"""
    
    def __init__(self):
        self.usage_history = []
        self.productivity_history = []
        self.patterns = {}
        self.models = {}
    
    def add_data_point(self, usage_time: int, productivity_score: float, 
                      focus_sessions: int, breaks: int, timestamp: datetime = None):
        """Add a new data point for training"""
        if timestamp is None:
            timestamp = datetime.now()
        
        data_point = {
            'usage_time': usage_time,
            'productivity_score': productivity_score,
            'focus_sessions': focus_sessions,
            'breaks': breaks,
            'timestamp': timestamp,
            'hour': timestamp.hour,
            'weekday': timestamp.strftime('%A'),
            'is_weekend': timestamp.weekday() >= 5
        }
        
        self.usage_history.append(data_point)
        
        # Keep only last 30 days of data
        if len(self.usage_history) > 30:
            self.usage_history = self.usage_history[-30:]
        
        logger.info(f"Added data point: {usage_time}min usage, {productivity_score}% productivity")
    
    def predict_usage_tomorrow(self) -> Prediction:
        """Predict tomorrow's usage based on historical patterns"""
        if len(self.usage_history) < 7:
            return Prediction(
                type='usage',
                value=120.0,  # Default prediction
                confidence=0.3,
                factors=['insufficient_data'],
                timestamp=datetime.now()
            )
        
        # Simple moving average with trend
        recent_usage = [d['usage_time'] for d in self.usage_history[-7:]]
        avg_usage = np.mean(recent_usage)
        
        # Calculate trend
        if len(recent_usage) >= 2:
            trend = np.polyfit(range(len(recent_usage)), recent_usage, 1)[0]
            predicted_usage = avg_usage + trend
        else:
            predicted_usage = avg_usage
        
        # Adjust for day of week patterns
        tomorrow = datetime.now() + timedelta(days=1)
        weekday_patterns = self._get_weekday_patterns()
        weekday_adjustment = weekday_patterns.get(tomorrow.strftime('%A'), 1.0)
        
        final_prediction = predicted_usage * weekday_adjustment
        
        # Calculate confidence based on data consistency
        confidence = min(0.9, 0.3 + len(self.usage_history) * 0.02)
        
        factors = ['historical_average', 'trend_analysis', 'weekday_patterns']
        
        return Prediction(
            type='usage',
            value=max(0, final_prediction),
            confidence=confidence,
            factors=factors,
            timestamp=datetime.now()
        )
    
    def predict_productivity_score(self, planned_usage: int) -> Prediction:
        """Predict productivity score based on planned usage"""
        if len(self.usage_history) < 5:
            return Prediction(
                type='productivity',
                value=70.0,  # Default prediction
                confidence=0.3,
                factors=['insufficient_data'],
                timestamp=datetime.now()
            )
        
        # Find similar usage patterns
        similar_data = [d for d in self.usage_history 
                       if abs(d['usage_time'] - planned_usage) <= 30]
        
        if similar_data:
            avg_productivity = np.mean([d['productivity_score'] for d in similar_data])
            confidence = min(0.9, len(similar_data) * 0.1)
        else:
            # Use overall average
            avg_productivity = np.mean([d['productivity_score'] for d in self.usage_history])
            confidence = 0.5
        
        # Adjust based on usage amount
        if planned_usage > 180:  # High usage
            avg_productivity *= 0.8
        elif planned_usage < 60:  # Low usage
            avg_productivity *= 1.1
        
        factors = ['usage_correlation', 'historical_patterns']
        
        return Prediction(
            type='productivity',
            value=max(0, min(100, avg_productivity)),
            confidence=confidence,
            factors=factors,
            timestamp=datetime.now()
        )
    
    def detect_behavior_patterns(self) -> List[BehaviorPattern]:
        """Detect behavioral patterns in user data"""
        patterns = []
        
        if len(self.usage_history) < 7:
            return patterns
        
        # Pattern 1: Weekend vs Weekday usage
        weekday_usage = [d['usage_time'] for d in self.usage_history if not d['is_weekend']]
        weekend_usage = [d['usage_time'] for d in self.usage_history if d['is_weekend']]
        
        if weekday_usage and weekend_usage:
            weekday_avg = np.mean(weekday_usage)
            weekend_avg = np.mean(weekend_usage)
            
            if weekend_avg > weekday_avg * 1.5:
                patterns.append(BehaviorPattern(
                    pattern_type='weekend_spike',
                    description=f'Weekend usage is {weekend_avg/weekday_avg:.1f}x higher than weekdays',
                    confidence=0.8,
                    frequency=len(weekend_usage) / len(self.usage_history),
                    impact='negative'
                ))
        
        # Pattern 2: Productivity decline
        recent_productivity = [d['productivity_score'] for d in self.usage_history[-5:]]
        if len(recent_productivity) >= 3:
            trend = np.polyfit(range(len(recent_productivity)), recent_productivity, 1)[0]
            if trend < -5:  # Declining by more than 5% per day
                patterns.append(BehaviorPattern(
                    pattern_type='productivity_decline',
                    description='Productivity score is declining',
                    confidence=0.7,
                    frequency=1.0,
                    impact='negative'
                ))
        
        # Pattern 3: Consistent improvement
        if len(self.usage_history) >= 10:
            first_half = self.usage_history[:len(self.usage_history)//2]
            second_half = self.usage_history[len(self.usage_history)//2:]
            
            first_avg = np.mean([d['usage_time'] for d in first_half])
            second_avg = np.mean([d['usage_time'] for d in second_half])
            
            if second_avg < first_avg * 0.8:  # 20% improvement
                patterns.append(BehaviorPattern(
                    pattern_type='improvement',
                    description=f'Usage reduced by {((first_avg-second_avg)/first_avg)*100:.1f}%',
                    confidence=0.9,
                    frequency=1.0,
                    impact='positive'
                ))
        
        return patterns
    
    def _get_weekday_patterns(self) -> Dict[str, float]:
        """Get usage patterns by day of week"""
        patterns = {}
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_data = [d['usage_time'] for d in self.usage_history 
                       if d['weekday'] == day]
            
            if day_data:
                patterns[day] = np.mean(day_data)
            else:
                patterns[day] = 120.0  # Default
        
        # Normalize to average
        overall_avg = np.mean(list(patterns.values()))
        for day in patterns:
            patterns[day] = patterns[day] / overall_avg
        
        return patterns
    
    def get_optimal_schedule(self) -> Dict[str, Any]:
        """Get optimal schedule recommendations"""
        if len(self.usage_history) < 7:
            return {'recommendations': ['Need more data for personalized recommendations']}
        
        # Analyze peak productivity hours
        hour_productivity = {}
        for data in self.usage_history:
            hour = data['hour']
            if hour not in hour_productivity:
                hour_productivity[hour] = []
            hour_productivity[hour].append(data['productivity_score'])
        
        # Find best hours
        best_hours = []
        for hour, scores in hour_productivity.items():
            if len(scores) >= 3:  # Need at least 3 data points
                avg_score = np.mean(scores)
                best_hours.append((hour, avg_score))
        
        best_hours.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        if best_hours:
            top_hour = best_hours[0][0]
            recommendations.append(f"Schedule focus sessions around {top_hour}:00 for best productivity")
        
        # Analyze break patterns
        break_data = [d['breaks'] for d in self.usage_history if d['breaks'] > 0]
        if break_data:
            avg_breaks = np.mean(break_data)
            recommendations.append(f"Take approximately {avg_breaks:.1f} breaks per day")
        
        return {
            'recommendations': recommendations,
            'best_hours': [hour for hour, _ in best_hours[:3]],
            'optimal_break_frequency': avg_breaks if break_data else 3
        }

class SmartRecommendations:
    """Smart recommendation system based on ML insights"""
    
    def __init__(self):
        self.predictor = SimpleMLPredictor()
        self.recommendations_history = []
        self.user_preferences = {}
    
    def generate_recommendations(self, current_data: Dict) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Add current data to predictor
        self.predictor.add_data_point(
            current_data.get('usage_time', 0),
            current_data.get('productivity_score', 0),
            current_data.get('focus_sessions', 0),
            current_data.get('breaks', 0)
        )
        
        # Get predictions
        usage_prediction = self.predictor.predict_usage_tomorrow()
        productivity_prediction = self.predictor.predict_productivity_score(
            current_data.get('usage_time', 120)
        )
        
        # Generate recommendations based on predictions
        if usage_prediction.value > 180:
            recommendations.append({
                'type': 'warning',
                'title': 'High Usage Predicted',
                'message': f'Tomorrow\'s usage is predicted to be {usage_prediction.value:.0f} minutes',
                'action': 'Set a lower daily limit',
                'confidence': usage_prediction.confidence
            })
        
        if productivity_prediction.value < 60:
            recommendations.append({
                'type': 'suggestion',
                'title': 'Low Productivity Expected',
                'message': f'Productivity score predicted to be {productivity_prediction.value:.0f}%',
                'action': 'Plan more focus sessions',
                'confidence': productivity_prediction.confidence
            })
        
        # Get behavior patterns
        patterns = self.predictor.detect_behavior_patterns()
        for pattern in patterns:
            if pattern.impact == 'negative':
                recommendations.append({
                    'type': 'pattern',
                    'title': 'Behavior Pattern Detected',
                    'message': pattern.description,
                    'action': 'Consider adjusting your routine',
                    'confidence': pattern.confidence
                })
        
        # Get optimal schedule
        schedule = self.predictor.get_optimal_schedule()
        for rec in schedule['recommendations']:
            recommendations.append({
                'type': 'schedule',
                'title': 'Schedule Optimization',
                'message': rec,
                'action': 'Follow the recommended schedule',
                'confidence': 0.8
            })
        
        return recommendations
    
    def get_adaptive_goals(self, current_performance: Dict) -> Dict[str, Any]:
        """Get adaptive goal suggestions"""
        if len(self.predictor.usage_history) < 5:
            return {'suggestions': ['Need more data for adaptive goals']}
        
        # Analyze current performance
        avg_usage = np.mean([d['usage_time'] for d in self.predictor.usage_history])
        avg_productivity = np.mean([d['productivity_score'] for d in self.predictor.usage_history])
        
        suggestions = []
        
        # Usage-based suggestions
        if avg_usage > 150:
            suggestions.append({
                'type': 'usage_reduction',
                'current': avg_usage,
                'suggested': max(60, avg_usage * 0.8),
                'reason': 'High average usage detected'
            })
        
        # Productivity-based suggestions
        if avg_productivity < 70:
            suggestions.append({
                'type': 'productivity_improvement',
                'current': avg_productivity,
                'suggested': min(100, avg_productivity * 1.2),
                'reason': 'Low productivity score detected'
            })
        
        return {'suggestions': suggestions}

class PredictiveAnalytics:
    """Main class for predictive analytics"""
    
    def __init__(self):
        self.predictor = SimpleMLPredictor()
        self.recommendations = SmartRecommendations()
        self.models_trained = False
    
    def train_models(self, historical_data: List[Dict]) -> bool:
        """Train ML models with historical data"""
        try:
            # Add historical data to predictor
            for data_point in historical_data:
                self.predictor.add_data_point(
                    data_point.get('usage_time', 0),
                    data_point.get('productivity_score', 0),
                    data_point.get('focus_sessions', 0),
                    data_point.get('breaks', 0),
                    datetime.fromisoformat(data_point.get('timestamp', datetime.now().isoformat()))
                )
            
            self.models_trained = True
            logger.info(f"Trained models with {len(historical_data)} data points")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train models: {e}")
            return False
    
    def get_predictions(self, current_data: Dict) -> Dict[str, Prediction]:
        """Get all predictions for current data"""
        # Add current data
        self.predictor.add_data_point(
            current_data.get('usage_time', 0),
            current_data.get('productivity_score', 0),
            current_data.get('focus_sessions', 0),
            current_data.get('breaks', 0)
        )
        
        # Get predictions
        predictions = {
            'usage_tomorrow': self.predictor.predict_usage_tomorrow(),
            'productivity_score': self.predictor.predict_productivity_score(
                current_data.get('usage_time', 120)
            )
        }
        
        return predictions
    
    def get_insights(self) -> Dict[str, Any]:
        """Get comprehensive insights"""
        patterns = self.predictor.detect_behavior_patterns()
        schedule = self.predictor.get_optimal_schedule()
        recommendations = self.recommendations.generate_recommendations({})
        
        return {
            'patterns': [vars(pattern) for pattern in patterns],
            'optimal_schedule': schedule,
            'recommendations': recommendations,
            'data_points': len(self.predictor.usage_history)
        }
    
    def export_ml_report(self) -> str:
        """Export ML analysis report"""
        insights = self.get_insights()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'models_trained': self.models_trained,
            'data_points': len(self.predictor.usage_history),
            'insights': insights,
            'predictions': {
                'usage_tomorrow': vars(self.predictor.predict_usage_tomorrow()),
                'productivity_trend': 'stable'  # Simplified for now
            }
        }
        
        # Save to file
        filename = f"ml_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return filename

# Example usage
if __name__ == "__main__":
    # Initialize predictive analytics
    analytics = PredictiveAnalytics()
    
    # Sample historical data
    historical_data = [
        {'usage_time': 120, 'productivity_score': 75, 'focus_sessions': 2, 'breaks': 3, 'timestamp': '2024-01-01T10:00:00'},
        {'usage_time': 90, 'productivity_score': 85, 'focus_sessions': 3, 'breaks': 4, 'timestamp': '2024-01-02T10:00:00'},
        {'usage_time': 150, 'productivity_score': 60, 'focus_sessions': 1, 'breaks': 2, 'timestamp': '2024-01-03T10:00:00'},
    ]
    
    # Train models
    analytics.train_models(historical_data)
    
    # Get predictions
    current_data = {'usage_time': 100, 'productivity_score': 80, 'focus_sessions': 2, 'breaks': 3}
    predictions = analytics.get_predictions(current_data)
    
    print("ML Analytics Module Loaded Successfully!")
    print(f"Usage prediction: {predictions['usage_tomorrow'].value:.0f} minutes")
    print(f"Productivity prediction: {predictions['productivity_score'].value:.0f}%") 