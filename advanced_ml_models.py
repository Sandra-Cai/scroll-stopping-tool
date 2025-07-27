#!/usr/bin/env python3
"""
Advanced Machine Learning Models for Scroll Stopping Tool
Sophisticated ML models for usage prediction, behavioral analysis, and recommendations
"""

import numpy as np
import pandas as pd
import json
import pickle
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import logging
import threading
import time
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
    from sklearn.decomposition import PCA
    from sklearn.feature_selection import SelectKBest, f_regression
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available - ML features will be disabled")

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import Dense, LSTM, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not available - deep learning features will be disabled")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available - advanced ML features will be disabled")

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet not available - time series forecasting will be disabled")

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class UsagePattern:
    """Data class for usage patterns"""
    user_id: str
    date: str
    hour: int
    day_of_week: int
    total_time: float
    session_count: int
    avg_session_length: float
    max_session_length: float
    break_count: int
    productivity_score: float
    focus_sessions: int
    goals_met: bool
    weather: Optional[str] = None
    mood: Optional[str] = None
    stress_level: Optional[int] = None

@dataclass
class PredictionResult:
    """Data class for prediction results"""
    prediction_type: str
    predicted_value: float
    confidence: float
    features_used: List[str]
    model_used: str
    timestamp: datetime
    explanation: str

@dataclass
class BehavioralInsight:
    """Data class for behavioral insights"""
    insight_type: str
    description: str
    confidence: float
    actionable: bool
    recommendation: str
    impact_score: float

@dataclass
class ModelPerformance:
    """Data class for model performance metrics"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    r2_score: float
    last_updated: datetime

class FeatureEngineer:
    """Advanced feature engineering for ML models"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        df = df.copy()
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Time features
        df['hour'] = df['date'].dt.hour
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_morning'] = (df['hour'] >= 6) & (df['hour'] < 12).astype(int)
        df['is_afternoon'] = (df['hour'] >= 12) & (df['hour'] < 18).astype(int)
        df['is_evening'] = (df['hour'] >= 18) & (df['hour'] < 22).astype(int)
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] < 6)).astype(int)
        
        # Cyclical features
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        return df
    
    def create_lag_features(self, df: pd.DataFrame, target_col: str, lags: List[int] = [1, 2, 3, 7]) -> pd.DataFrame:
        """Create lag features for time series"""
        df = df.copy()
        df = df.sort_values('date')
        
        for lag in lags:
            df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
            df[f'{target_col}_lag_{lag}_diff'] = df[target_col].diff(lag)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, target_col: str, windows: List[int] = [3, 7, 14]) -> pd.DataFrame:
        """Create rolling window features"""
        df = df.copy()
        df = df.sort_values('date')
        
        for window in windows:
            df[f'{target_col}_rolling_mean_{window}'] = df[target_col].rolling(window=window, min_periods=1).mean()
            df[f'{target_col}_rolling_std_{window}'] = df[target_col].rolling(window=window, min_periods=1).std()
            df[f'{target_col}_rolling_min_{window}'] = df[target_col].rolling(window=window, min_periods=1).min()
            df[f'{target_col}_rolling_max_{window}'] = df[target_col].rolling(window=window, min_periods=1).max()
        
        return df
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features"""
        df = df.copy()
        
        # Productivity interactions
        df['productivity_efficiency'] = df['productivity_score'] * df['focus_sessions']
        df['time_productivity_ratio'] = df['total_time'] / (df['productivity_score'] + 1)
        df['session_efficiency'] = df['avg_session_length'] * df['productivity_score']
        
        # Time-based interactions
        df['weekend_productivity'] = df['is_weekend'] * df['productivity_score']
        df['morning_productivity'] = df['is_morning'] * df['productivity_score']
        df['evening_productivity'] = df['is_evening'] * df['productivity_score']
        
        return df
    
    def create_behavioral_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create behavioral pattern features"""
        df = df.copy()
        
        # Consistency features
        df['usage_consistency'] = 1 / (df['total_time'].rolling(window=7, min_periods=1).std() + 1)
        df['productivity_consistency'] = 1 / (df['productivity_score'].rolling(window=7, min_periods=1).std() + 1)
        
        # Trend features
        df['usage_trend'] = df['total_time'].rolling(window=7, min_periods=1).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
        )
        df['productivity_trend'] = df['productivity_score'].rolling(window=7, min_periods=1).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
        )
        
        # Pattern features
        df['high_usage_days'] = (df['total_time'] > df['total_time'].rolling(window=30, min_periods=1).quantile(0.8)).astype(int)
        df['low_productivity_days'] = (df['productivity_score'] < df['productivity_score'].rolling(window=30, min_periods=1).quantile(0.2)).astype(int)
        
        return df
    
    def engineer_features(self, df: pd.DataFrame, target_col: str = 'total_time') -> pd.DataFrame:
        """Complete feature engineering pipeline"""
        df = self.create_time_features(df)
        df = self.create_lag_features(df, target_col)
        df = self.create_rolling_features(df, target_col)
        df = self.create_interaction_features(df)
        df = self.create_behavioral_features(df)
        
        # Store feature names
        self.feature_names = [col for col in df.columns if col not in ['date', 'user_id', target_col]]
        
        return df

class UsagePredictor:
    """Advanced usage prediction models"""
    
    def __init__(self, db_path: str = 'productivity.db'):
        self.db_path = db_path
        self.feature_engineer = FeatureEngineer()
        self.models = {}
        self.scalers = {}
        self.performance_metrics = {}
        
    def load_usage_data(self, user_id: str = None, days: int = 90) -> pd.DataFrame:
        """Load usage data from database"""
        query = """
        SELECT 
            date,
            total_time,
            breaks_taken,
            focus_sessions,
            productivity_score,
            goals_met
        FROM usage_data
        WHERE date >= date('now', '-{} days')
        ORDER BY date
        """.format(days)
        
        if user_id:
            query = query.replace("WHERE", f"WHERE user_id = '{user_id}' AND")
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
        
        # Add synthetic features for demonstration
        df['session_count'] = np.random.randint(1, 10, len(df))
        df['avg_session_length'] = df['total_time'] / df['session_count']
        df['max_session_length'] = df['avg_session_length'] * np.random.uniform(1.2, 2.0, len(df))
        
        return df
    
    def prepare_data(self, df: pd.DataFrame, target_col: str = 'total_time') -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training"""
        # Engineer features
        df_engineered = self.feature_engineer.engineer_features(df, target_col)
        
        # Remove rows with NaN values
        df_engineered = df_engineered.dropna()
        
        # Prepare features and target
        X = df_engineered[self.feature_engineer.feature_names].values
        y = df_engineered[target_col].values
        
        return X, y
    
    def train_models(self, user_id: str = None):
        """Train multiple prediction models"""
        # Load data
        df = self.load_usage_data(user_id)
        X, y = self.prepare_data(df)
        
        if len(X) < 10:
            logger.warning("Insufficient data for training models")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Define models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        
        if XGBOOST_AVAILABLE:
            models['xgboost'] = xgb.XGBRegressor(n_estimators=100, random_state=42)
        
        # Train models
        for name, model in models.items():
            logger.info(f"Training {name} model...")
            
            # Scale features for some models
            if name in ['linear_regression']:
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                self.scalers[name] = scaler
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Calculate performance metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.performance_metrics[name] = ModelPerformance(
                model_name=name,
                accuracy=r2,
                precision=0,  # Not applicable for regression
                recall=0,     # Not applicable for regression
                f1_score=0,   # Not applicable for regression
                mse=mse,
                r2_score=r2,
                last_updated=datetime.now()
            )
            
            self.models[name] = model
            
            logger.info(f"{name} - R²: {r2:.3f}, MSE: {mse:.3f}")
    
    def predict_usage(self, days_ahead: int = 7, model_name: str = 'random_forest') -> List[PredictionResult]:
        """Predict usage for future days"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Available models: {list(self.models.keys())}")
        
        # Load recent data
        df = self.load_usage_data(days=30)
        X, _ = self.prepare_data(df)
        
        if len(X) == 0:
            return []
        
        # Use the most recent data point for prediction
        latest_features = X[-1:].copy()
        model = self.models[model_name]
        
        predictions = []
        for i in range(days_ahead):
            # Make prediction
            if model_name in self.scalers:
                latest_features_scaled = self.scalers[model_name].transform(latest_features)
                pred_value = model.predict(latest_features_scaled)[0]
            else:
                pred_value = model.predict(latest_features)[0]
            
            # Create prediction result
            prediction = PredictionResult(
                prediction_type="usage_forecast",
                predicted_value=max(0, pred_value),  # Ensure non-negative
                confidence=self.performance_metrics[model_name].accuracy,
                features_used=self.feature_engineer.feature_names,
                model_used=model_name,
                timestamp=datetime.now(),
                explanation=f"Predicted usage for day {i+1} using {model_name} model"
            )
            
            predictions.append(prediction)
            
            # Update features for next prediction (simplified)
            # In a real implementation, you'd update time features properly
            latest_features[0, 0] += 1  # Increment hour feature
        
        return predictions

class BehavioralAnalyzer:
    """Advanced behavioral analysis using ML"""
    
    def __init__(self, db_path: str = 'productivity.db'):
        self.db_path = db_path
        self.feature_engineer = FeatureEngineer()
        self.clustering_model = None
        self.anomaly_detector = None
        
    def analyze_usage_patterns(self, user_id: str = None) -> List[BehavioralInsight]:
        """Analyze usage patterns and generate insights"""
        df = self.load_usage_data(user_id)
        df_engineered = self.feature_engineer.engineer_features(df)
        
        insights = []
        
        # Pattern 1: Time-based usage analysis
        hourly_usage = df.groupby('hour')['total_time'].mean()
        peak_hour = hourly_usage.idxmax()
        insights.append(BehavioralInsight(
            insight_type="peak_usage_time",
            description=f"Peak usage occurs at {peak_hour}:00 hours",
            confidence=0.85,
            actionable=True,
            recommendation="Schedule important tasks during off-peak hours",
            impact_score=0.7
        ))
        
        # Pattern 2: Weekend vs weekday analysis
        weekend_usage = df[df['is_weekend'] == 1]['total_time'].mean()
        weekday_usage = df[df['is_weekend'] == 0]['total_time'].mean()
        
        if weekend_usage > weekday_usage * 1.2:
            insights.append(BehavioralInsight(
                insight_type="weekend_overuse",
                description="Usage is significantly higher on weekends",
                confidence=0.8,
                actionable=True,
                recommendation="Set stricter limits for weekend usage",
                impact_score=0.6
            ))
        
        # Pattern 3: Productivity consistency
        productivity_std = df['productivity_score'].std()
        if productivity_std > df['productivity_score'].mean() * 0.5:
            insights.append(BehavioralInsight(
                insight_type="inconsistent_productivity",
                description="Productivity varies significantly day-to-day",
                confidence=0.75,
                actionable=True,
                recommendation="Establish consistent daily routines",
                impact_score=0.8
            ))
        
        # Pattern 4: Session length analysis
        avg_session = df['avg_session_length'].mean()
        if avg_session > 60:  # More than 1 hour average
            insights.append(BehavioralInsight(
                insight_type="long_sessions",
                description=f"Average session length is {avg_session:.1f} minutes",
                confidence=0.9,
                actionable=True,
                recommendation="Break sessions into shorter intervals",
                impact_score=0.7
            ))
        
        return insights
    
    def detect_anomalies(self, user_id: str = None) -> List[Dict]:
        """Detect anomalous usage patterns"""
        df = self.load_usage_data(user_id)
        df_engineered = self.feature_engineer.engineer_features(df)
        
        # Prepare features for anomaly detection
        feature_cols = ['total_time', 'productivity_score', 'session_count', 'avg_session_length']
        X = df_engineered[feature_cols].dropna().values
        
        if len(X) < 10:
            return []
        
        # Train isolation forest
        if SKLEARN_AVAILABLE:
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            anomalies = self.anomaly_detector.fit_predict(X)
            
            # Get anomalous dates
            anomaly_dates = df_engineered[feature_cols].dropna().index[anomalies == -1]
            
            results = []
            for date_idx in anomaly_dates:
                date = df.iloc[date_idx]['date']
                usage_data = df.iloc[date_idx]
                
                results.append({
                    'date': date,
                    'total_time': usage_data['total_time'],
                    'productivity_score': usage_data['productivity_score'],
                    'anomaly_type': 'usage_pattern',
                    'severity': 'high' if usage_data['total_time'] > df['total_time'].quantile(0.9) else 'medium'
                })
            
            return results
        
        return []
    
    def cluster_behavior_patterns(self, user_id: str = None) -> Dict:
        """Cluster users into behavior patterns"""
        df = self.load_usage_data(user_id)
        df_engineered = self.feature_engineer.engineer_features(df)
        
        # Prepare features for clustering
        feature_cols = ['total_time', 'productivity_score', 'session_count', 'avg_session_length']
        X = df_engineered[feature_cols].dropna().values
        
        if len(X) < 5:
            return {}
        
        # Perform clustering
        if SKLEARN_AVAILABLE:
            self.clustering_model = KMeans(n_clusters=min(3, len(X)), random_state=42)
            clusters = self.clustering_model.fit_predict(X)
            
            # Analyze clusters
            cluster_analysis = {}
            for i in range(self.clustering_model.n_clusters):
                cluster_data = X[clusters == i]
                cluster_analysis[f'cluster_{i}'] = {
                    'size': len(cluster_data),
                    'avg_usage': cluster_data[:, 0].mean(),
                    'avg_productivity': cluster_data[:, 1].mean(),
                    'avg_sessions': cluster_data[:, 2].mean(),
                    'avg_session_length': cluster_data[:, 3].mean()
                }
            
            return cluster_analysis
        
        return {}
    
    def load_usage_data(self, user_id: str = None, days: int = 90) -> pd.DataFrame:
        """Load usage data for analysis"""
        query = """
        SELECT 
            date,
            total_time,
            breaks_taken,
            focus_sessions,
            productivity_score,
            goals_met
        FROM usage_data
        WHERE date >= date('now', '-{} days')
        ORDER BY date
        """.format(days)
        
        if user_id:
            query = query.replace("WHERE", f"WHERE user_id = '{user_id}' AND")
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
        
        # Add synthetic features for demonstration
        df['session_count'] = np.random.randint(1, 10, len(df))
        df['avg_session_length'] = df['total_time'] / df['session_count']
        df['max_session_length'] = df['avg_session_length'] * np.random.uniform(1.2, 2.0, len(df))
        
        return df

class DeepLearningPredictor:
    """Deep learning models for advanced predictions"""
    
    def __init__(self, db_path: str = 'productivity.db'):
        self.db_path = db_path
        self.feature_engineer = FeatureEngineer()
        self.models = {}
        
    def create_lstm_model(self, input_shape: Tuple[int, int]) -> tf.keras.Model:
        """Create LSTM model for time series prediction"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        return model
    
    def create_sequences(self, data: np.ndarray, seq_length: int = 7) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training"""
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:(i + seq_length)])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)
    
    def train_lstm_model(self, user_id: str = None, seq_length: int = 7):
        """Train LSTM model for usage prediction"""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available for LSTM training")
            return
        
        # Load and prepare data
        df = self.load_usage_data(user_id)
        df_engineered = self.feature_engineer.engineer_features(df)
        
        # Prepare target variable
        target_data = df_engineered['total_time'].values.reshape(-1, 1)
        
        # Create sequences
        X, y = self.create_sequences(target_data, seq_length)
        
        if len(X) < 10:
            logger.warning("Insufficient data for LSTM training")
            return
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Create and train model
        model = self.create_lstm_model((seq_length, 1))
        
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(patience=5, factor=0.5)
        ]
        
        history = model.fit(
            X_train, y_train,
            epochs=100,
            batch_size=32,
            validation_data=(X_test, y_test),
            callbacks=callbacks,
            verbose=0
        )
        
        self.models['lstm'] = model
        
        # Evaluate model
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"LSTM Model - R²: {r2:.3f}, MSE: {mse:.3f}")
    
    def predict_with_lstm(self, days_ahead: int = 7) -> List[float]:
        """Predict usage using LSTM model"""
        if 'lstm' not in self.models:
            raise ValueError("LSTM model not trained")
        
        # Load recent data
        df = self.load_usage_data(days=30)
        df_engineered = self.feature_engineer.engineer_features(df)
        
        # Get recent sequence
        target_data = df_engineered['total_time'].values[-7:].reshape(1, 7, 1)
        
        predictions = []
        current_sequence = target_data.copy()
        
        for _ in range(days_ahead):
            # Make prediction
            pred = self.models['lstm'].predict(current_sequence, verbose=0)[0, 0]
            predictions.append(max(0, pred))
            
            # Update sequence for next prediction
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1, 0] = pred
        
        return predictions
    
    def load_usage_data(self, user_id: str = None, days: int = 90) -> pd.DataFrame:
        """Load usage data for deep learning"""
        query = """
        SELECT 
            date,
            total_time,
            breaks_taken,
            focus_sessions,
            productivity_score,
            goals_met
        FROM usage_data
        WHERE date >= date('now', '-{} days')
        ORDER BY date
        """.format(days)
        
        if user_id:
            query = query.replace("WHERE", f"WHERE user_id = '{user_id}' AND")
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
        
        # Add synthetic features for demonstration
        df['session_count'] = np.random.randint(1, 10, len(df))
        df['avg_session_length'] = df['total_time'] / df['session_count']
        df['max_session_length'] = df['avg_session_length'] * np.random.uniform(1.2, 2.0, len(df))
        
        return df

class TimeSeriesForecaster:
    """Advanced time series forecasting using Prophet"""
    
    def __init__(self, db_path: str = 'productivity.db'):
        self.db_path = db_path
        self.models = {}
        
    def train_prophet_model(self, user_id: str = None):
        """Train Prophet model for time series forecasting"""
        if not PROPHET_AVAILABLE:
            logger.warning("Prophet not available for time series forecasting")
            return
        
        # Load data
        df = self.load_usage_data(user_id)
        
        if len(df) < 14:
            logger.warning("Insufficient data for Prophet training")
            return
        
        # Prepare data for Prophet
        prophet_df = df[['date', 'total_time']].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        
        # Create and train model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
        
        model.fit(prophet_df)
        self.models['prophet'] = model
        
        logger.info("Prophet model trained successfully")
    
    def forecast_usage(self, days_ahead: int = 30) -> pd.DataFrame:
        """Forecast usage using Prophet"""
        if 'prophet' not in self.models:
            raise ValueError("Prophet model not trained")
        
        # Create future dates
        future = self.models['prophet'].make_future_dataframe(periods=days_ahead)
        
        # Make forecast
        forecast = self.models['prophet'].predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    
    def load_usage_data(self, user_id: str = None, days: int = 90) -> pd.DataFrame:
        """Load usage data for forecasting"""
        query = """
        SELECT 
            date,
            total_time,
            breaks_taken,
            focus_sessions,
            productivity_score,
            goals_met
        FROM usage_data
        WHERE date >= date('now', '-{} days')
        ORDER BY date
        """.format(days)
        
        if user_id:
            query = query.replace("WHERE", f"WHERE user_id = '{user_id}' AND")
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
        
        return df

class MLModelManager:
    """Central manager for all ML models"""
    
    def __init__(self, db_path: str = 'productivity.db'):
        self.db_path = db_path
        self.usage_predictor = UsagePredictor(db_path)
        self.behavioral_analyzer = BehavioralAnalyzer(db_path)
        self.deep_learning_predictor = DeepLearningPredictor(db_path)
        self.time_series_forecaster = TimeSeriesForecaster(db_path)
        
        # Model storage
        self.model_path = Path('ml_models')
        self.model_path.mkdir(exist_ok=True)
    
    def train_all_models(self, user_id: str = None):
        """Train all available ML models"""
        logger.info("Starting comprehensive model training...")
        
        # Train usage prediction models
        if SKLEARN_AVAILABLE:
            self.usage_predictor.train_models(user_id)
        
        # Train LSTM model
        if TENSORFLOW_AVAILABLE:
            self.deep_learning_predictor.train_lstm_model(user_id)
        
        # Train Prophet model
        if PROPHET_AVAILABLE:
            self.time_series_forecaster.train_prophet_model(user_id)
        
        logger.info("All models trained successfully")
    
    def get_comprehensive_predictions(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Get predictions from all models"""
        predictions = {}
        
        # Usage predictions
        if self.usage_predictor.models:
            predictions['usage_forecast'] = self.usage_predictor.predict_usage(days_ahead)
        
        # LSTM predictions
        if 'lstm' in self.deep_learning_predictor.models:
            try:
                lstm_predictions = self.deep_learning_predictor.predict_with_lstm(days_ahead)
                predictions['lstm_forecast'] = lstm_predictions
            except Exception as e:
                logger.error(f"LSTM prediction error: {e}")
        
        # Prophet forecasts
        if 'prophet' in self.time_series_forecaster.models:
            try:
                prophet_forecast = self.time_series_forecaster.forecast_usage(days_ahead)
                predictions['prophet_forecast'] = prophet_forecast
            except Exception as e:
                logger.error(f"Prophet forecast error: {e}")
        
        return predictions
    
    def get_behavioral_insights(self, user_id: str = None) -> Dict[str, Any]:
        """Get comprehensive behavioral insights"""
        insights = {}
        
        # Pattern analysis
        insights['patterns'] = self.behavioral_analyzer.analyze_usage_patterns(user_id)
        
        # Anomaly detection
        insights['anomalies'] = self.behavioral_analyzer.detect_anomalies(user_id)
        
        # Behavior clustering
        insights['clusters'] = self.behavioral_analyzer.cluster_behavior_patterns(user_id)
        
        return insights
    
    def save_models(self):
        """Save trained models to disk"""
        for name, model in self.usage_predictor.models.items():
            model_path = self.model_path / f"{name}_model.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
        
        # Save LSTM model
        if 'lstm' in self.deep_learning_predictor.models:
            model_path = self.model_path / "lstm_model.h5"
            self.deep_learning_predictor.models['lstm'].save(model_path)
        
        # Save Prophet model
        if 'prophet' in self.time_series_forecaster.models:
            model_path = self.model_path / "prophet_model.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(self.time_series_forecaster.models['prophet'], f)
        
        logger.info("All models saved successfully")
    
    def load_models(self):
        """Load trained models from disk"""
        # Load scikit-learn models
        for model_file in self.model_path.glob("*_model.pkl"):
            if model_file.name != "prophet_model.pkl":
                with open(model_file, 'rb') as f:
                    model_name = model_file.stem.replace("_model", "")
                    self.usage_predictor.models[model_name] = pickle.load(f)
        
        # Load LSTM model
        lstm_path = self.model_path / "lstm_model.h5"
        if lstm_path.exists() and TENSORFLOW_AVAILABLE:
            self.deep_learning_predictor.models['lstm'] = load_model(lstm_path)
        
        # Load Prophet model
        prophet_path = self.model_path / "prophet_model.pkl"
        if prophet_path.exists() and PROPHET_AVAILABLE:
            with open(prophet_path, 'rb') as f:
                self.time_series_forecaster.models['prophet'] = pickle.load(f)
        
        logger.info("All models loaded successfully")

def main():
    """Main function for testing ML models"""
    # Initialize ML manager
    ml_manager = MLModelManager()
    
    # Train models
    print("Training ML models...")
    ml_manager.train_all_models()
    
    # Get predictions
    print("\nGetting predictions...")
    predictions = ml_manager.get_comprehensive_predictions()
    
    for model_type, pred_data in predictions.items():
        print(f"\n{model_type.upper()}:")
        if isinstance(pred_data, list):
            for i, pred in enumerate(pred_data[:3]):  # Show first 3 predictions
                print(f"  Day {i+1}: {pred.predicted_value:.1f} minutes")
        elif isinstance(pred_data, pd.DataFrame):
            print(pred_data.head())
    
    # Get behavioral insights
    print("\nGetting behavioral insights...")
    insights = ml_manager.get_behavioral_insights()
    
    print(f"\nPatterns found: {len(insights['patterns'])}")
    for insight in insights['patterns']:
        print(f"  - {insight.description}")
    
    print(f"\nAnomalies detected: {len(insights['anomalies'])}")
    for anomaly in insights['anomalies'][:3]:  # Show first 3 anomalies
        print(f"  - {anomaly['date']}: {anomaly['total_time']:.1f} minutes")

if __name__ == "__main__":
    main() 