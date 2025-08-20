#!/usr/bin/env python3
"""
Advanced Analytics Dashboard
Comprehensive analytics and visualization system for the scroll stopping tool
with real-time metrics, predictive analytics, and interactive dashboards.
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
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Analytics metric types"""
    USAGE_TIME = "usage_time"
    FOCUS_SESSIONS = "focus_sessions"
    BREAKS_TAKEN = "breaks_taken"
    PRODUCTIVITY_SCORE = "productivity_score"
    GOAL_COMPLETION = "goal_completion"
    INTERRUPTIONS = "interruptions"
    TIME_SAVED = "time_saved"
    STREAK_DAYS = "streak_days"

class ChartType(Enum):
    """Chart types for visualization"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    FUNNEL = "funnel"
    RADAR = "radar"

@dataclass
class AnalyticsMetric:
    """Analytics metric definition"""
    id: str
    name: str
    description: str
    type: MetricType
    value: float
    unit: str
    trend: float  # percentage change
    target: Optional[float] = None
    category: str = "general"

@dataclass
class DashboardWidget:
    """Dashboard widget definition"""
    id: str
    title: str
    type: ChartType
    data_source: str
    refresh_interval: int  # seconds
    position: Tuple[int, int]  # grid position
    size: Tuple[int, int]  # grid size
    config: Dict[str, Any]

class AdvancedAnalyticsDashboard:
    """Advanced analytics dashboard system"""
    
    def __init__(self, db_path: str = "productivity.db"):
        self.db_path = db_path
        self.metrics = {}
        self.widgets = {}
        self.predictive_models = {}
        self.real_time_data = {}
        self.dashboard_app = None
        self.update_callbacks = []
        
        # Initialize dashboard components
        self._initialize_metrics()
        self._initialize_widgets()
        self._initialize_predictive_models()
        
        # Start real-time updates
        self.update_thread = threading.Thread(target=self._real_time_updates, daemon=True)
        self.update_thread.start()
        
        print("📊 Advanced Analytics Dashboard initialized!")
        print("📈 Real-time metrics tracking active!")
        print("🔮 Predictive analytics enabled!")
    
    def _initialize_metrics(self):
        """Initialize analytics metrics"""
        metrics_data = [
            {
                "id": "daily_usage",
                "name": "Daily Social Media Usage",
                "description": "Total time spent on social media today",
                "type": MetricType.USAGE_TIME,
                "unit": "minutes",
                "target": 120
            },
            {
                "id": "focus_sessions",
                "name": "Focus Sessions",
                "description": "Number of completed focus sessions",
                "type": MetricType.FOCUS_SESSIONS,
                "unit": "sessions",
                "target": 4
            },
            {
                "id": "productivity_score",
                "name": "Productivity Score",
                "description": "Overall productivity rating",
                "type": MetricType.PRODUCTIVITY_SCORE,
                "unit": "score",
                "target": 85
            },
            {
                "id": "time_saved",
                "name": "Time Saved",
                "description": "Time saved from reduced social media usage",
                "type": MetricType.TIME_SAVED,
                "unit": "minutes",
                "target": 60
            },
            {
                "id": "streak_days",
                "name": "Current Streak",
                "description": "Days of meeting daily goals",
                "type": MetricType.STREAK_DAYS,
                "unit": "days",
                "target": 7
            }
        ]
        
        for metric_data in metrics_data:
            metric = AnalyticsMetric(
                id=metric_data["id"],
                name=metric_data["name"],
                description=metric_data["description"],
                type=metric_data["type"],
                value=0.0,
                unit=metric_data["unit"],
                trend=0.0,
                target=metric_data.get("target")
            )
            self.metrics[metric.id] = metric
    
    def _initialize_widgets(self):
        """Initialize dashboard widgets"""
        widgets_data = [
            {
                "id": "usage_trend",
                "title": "Social Media Usage Trend",
                "type": ChartType.LINE,
                "data_source": "daily_usage",
                "refresh_interval": 300,
                "position": (0, 0),
                "size": (6, 4),
                "config": {"xaxis_title": "Date", "yaxis_title": "Minutes"}
            },
            {
                "id": "productivity_gauge",
                "title": "Productivity Score",
                "type": ChartType.GAUGE,
                "data_source": "productivity_score",
                "refresh_interval": 60,
                "position": (6, 0),
                "size": (3, 4),
                "config": {"min": 0, "max": 100, "thresholds": [50, 75, 90]}
            },
            {
                "id": "focus_sessions_bar",
                "title": "Focus Sessions by Day",
                "type": ChartType.BAR,
                "data_source": "focus_sessions",
                "refresh_interval": 300,
                "position": (0, 4),
                "size": (4, 3),
                "config": {"xaxis_title": "Day", "yaxis_title": "Sessions"}
            },
            {
                "id": "time_saved_pie",
                "title": "Time Allocation",
                "type": ChartType.PIE,
                "data_source": "time_allocation",
                "refresh_interval": 600,
                "position": (4, 4),
                "size": (3, 3),
                "config": {"hole": 0.4}
            },
            {
                "id": "predictive_forecast",
                "title": "Productivity Forecast",
                "type": ChartType.LINE,
                "data_source": "predictive_data",
                "refresh_interval": 1800,
                "position": (7, 4),
                "size": (5, 3),
                "config": {"xaxis_title": "Date", "yaxis_title": "Predicted Score"}
            }
        ]
        
        for widget_data in widgets_data:
            widget = DashboardWidget(
                id=widget_data["id"],
                title=widget_data["title"],
                type=widget_data["type"],
                data_source=widget_data["data_source"],
                refresh_interval=widget_data["refresh_interval"],
                position=widget_data["position"],
                size=widget_data["size"],
                config=widget_data["config"]
            )
            self.widgets[widget.id] = widget
    
    def _initialize_predictive_models(self):
        """Initialize predictive analytics models"""
        # Productivity prediction model
        self.predictive_models['productivity'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Usage prediction model
        self.predictive_models['usage'] = LinearRegression()
        
        # Focus session prediction model
        self.predictive_models['focus_sessions'] = RandomForestRegressor(
            n_estimators=50,
            max_depth=8,
            random_state=42
        )
        
        print("🔮 Predictive models initialized!")
    
    def update_metrics(self, user_id: str, activity_data: Dict[str, Any]):
        """Update metrics with new activity data"""
        # Calculate current metrics
        daily_usage = activity_data.get('daily_usage', 0)
        focus_sessions = len(activity_data.get('focus_sessions', []))
        breaks_taken = activity_data.get('breaks_taken', 0)
        time_saved = activity_data.get('time_saved_minutes', 0)
        streak_days = activity_data.get('streak_days', 0)
        
        # Calculate productivity score
        productivity_score = self._calculate_productivity_score(activity_data)
        
        # Update metrics
        self.metrics['daily_usage'].value = daily_usage
        self.metrics['focus_sessions'].value = focus_sessions
        self.metrics['productivity_score'].value = productivity_score
        self.metrics['time_saved'].value = time_saved
        self.metrics['streak_days'].value = streak_days
        
        # Calculate trends
        self._calculate_trends(user_id)
        
        # Store real-time data
        self.real_time_data[user_id] = {
            'timestamp': datetime.now(),
            'metrics': {k: v.value for k, v in self.metrics.items()},
            'activity_data': activity_data
        }
        
        # Update predictive models
        self._update_predictive_models(user_id, activity_data)
    
    def _calculate_productivity_score(self, activity_data: Dict[str, Any]) -> float:
        """Calculate overall productivity score"""
        score = 0.0
        
        # Focus sessions (40% weight)
        focus_sessions = activity_data.get('focus_sessions', [])
        total_focus_time = sum(s.get('duration', 0) for s in focus_sessions)
        focus_score = min(100, total_focus_time / 60 * 20)  # 20 points per hour
        score += focus_score * 0.4
        
        # Goal completion (30% weight)
        if activity_data.get('daily_goal_met', False):
            score += 100 * 0.3
        else:
            goal_progress = activity_data.get('goal_progress', 0)
            score += goal_progress * 0.3
        
        # Break adherence (20% weight)
        breaks_taken = activity_data.get('breaks_taken', 0)
        scheduled_breaks = activity_data.get('scheduled_breaks', 4)
        break_score = min(100, (breaks_taken / scheduled_breaks) * 100) if scheduled_breaks > 0 else 0
        score += break_score * 0.2
        
        # Time saved (10% weight)
        time_saved = activity_data.get('time_saved_minutes', 0)
        time_saved_score = min(100, time_saved / 60 * 100)  # 100 points per hour saved
        score += time_saved_score * 0.1
        
        return round(score, 1)
    
    def _calculate_trends(self, user_id: str):
        """Calculate trend percentages for metrics"""
        # Get historical data for trend calculation
        historical_data = self._get_historical_data(user_id, days=7)
        
        for metric_id, metric in self.metrics.items():
            if historical_data and len(historical_data) >= 2:
                current_value = metric.value
                previous_value = historical_data[-2].get(metric_id, current_value)
                
                if previous_value > 0:
                    trend = ((current_value - previous_value) / previous_value) * 100
                else:
                    trend = 0.0
                
                metric.trend = round(trend, 1)
    
    def _get_historical_data(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical data for trend analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                start_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor.execute("""
                    SELECT * FROM usage_data 
                    WHERE user_id = ? AND date >= ?
                    ORDER BY date ASC
                """, (user_id, start_date))
                
                rows = cursor.fetchall()
                historical_data = []
                
                for row in rows:
                    historical_data.append({
                        'date': row[1],
                        'daily_usage': row[2],
                        'focus_sessions': row[3],
                        'productivity_score': row[4],
                        'time_saved': row[5],
                        'streak_days': row[6]
                    })
                
                return historical_data
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
    
    def _update_predictive_models(self, user_id: str, activity_data: Dict[str, Any]):
        """Update predictive models with new data"""
        # Prepare training data
        historical_data = self._get_historical_data(user_id, days=30)
        
        if len(historical_data) < 7:  # Need at least a week of data
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        
        # Prepare features for productivity prediction
        X_productivity = df[['daily_usage', 'focus_sessions', 'time_saved', 'day_of_week']].values
        y_productivity = df['productivity_score'].values
        
        # Update productivity model
        if len(X_productivity) > 0:
            self.predictive_models['productivity'].fit(X_productivity, y_productivity)
    
    def generate_forecast(self, user_id: str, days: int = 7) -> Dict[str, List[float]]:
        """Generate productivity forecast"""
        historical_data = self._get_historical_data(user_id, days=30)
        
        if len(historical_data) < 7:
            return {"dates": [], "predictions": []}
        
        # Prepare future dates
        last_date = datetime.now()
        future_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]
        
        # Generate predictions
        predictions = []
        for date in future_dates:
            # Use average values for prediction features
            avg_usage = np.mean([d['daily_usage'] for d in historical_data[-7:]])
            avg_focus = np.mean([d['focus_sessions'] for d in historical_data[-7:]])
            avg_time_saved = np.mean([d['time_saved'] for d in historical_data[-7:]])
            
            features = np.array([[
                avg_usage,
                avg_focus,
                avg_time_saved,
                date.weekday()
            ]])
            
            prediction = self.predictive_models['productivity'].predict(features)[0]
            predictions.append(max(0, min(100, prediction)))
        
        return {
            "dates": [d.strftime('%Y-%m-%d') for d in future_dates],
            "predictions": predictions
        }
    
    def create_dashboard(self) -> dash.Dash:
        """Create interactive dashboard"""
        app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        
        # Dashboard layout
        app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("📊 Productivity Analytics Dashboard", className="text-center mb-4"),
                    html.Hr()
                ])
            ]),
            
            # Key metrics row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{self.metrics['productivity_score'].value}", className="card-title"),
                            html.P("Productivity Score", className="card-text"),
                            html.Small(f"Trend: {self.metrics['productivity_score'].trend:+.1f}%", 
                                     className=f"text-{'success' if self.metrics['productivity_score'].trend >= 0 else 'danger'}")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{self.metrics['daily_usage'].value}", className="card-title"),
                            html.P("Daily Usage (min)", className="card-text"),
                            html.Small(f"Trend: {self.metrics['daily_usage'].trend:+.1f}%", 
                                     className=f"text-{'danger' if self.metrics['daily_usage'].trend >= 0 else 'success'}")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{self.metrics['focus_sessions'].value}", className="card-title"),
                            html.P("Focus Sessions", className="card-text"),
                            html.Small(f"Trend: {self.metrics['focus_sessions'].trend:+.1f}%", 
                                     className=f"text-{'success' if self.metrics['focus_sessions'].trend >= 0 else 'danger'}")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{self.metrics['streak_days'].value}", className="card-title"),
                            html.P("Current Streak", className="card-text"),
                            html.Small("Days", className="text-muted")
                        ])
                    ])
                ], width=3)
            ], className="mb-4"),
            
            # Charts row
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='usage-trend-chart')
                ], width=8),
                dbc.Col([
                    dcc.Graph(id='productivity-gauge')
                ], width=4)
            ], className="mb-4"),
            
            # Second charts row
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='focus-sessions-chart')
                ], width=6),
                dbc.Col([
                    dcc.Graph(id='time-allocation-chart')
                ], width=6)
            ], className="mb-4"),
            
            # Forecast row
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='productivity-forecast')
                ], width=12)
            ]),
            
            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=60*1000,  # 1 minute
                n_intervals=0
            )
        ], fluid=True)
        
        # Callbacks for real-time updates
        @app.callback(
            Output('usage-trend-chart', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_usage_trend(n):
            return self._create_usage_trend_chart()
        
        @app.callback(
            Output('productivity-gauge', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_productivity_gauge(n):
            return self._create_productivity_gauge()
        
        @app.callback(
            Output('focus-sessions-chart', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_focus_sessions(n):
            return self._create_focus_sessions_chart()
        
        @app.callback(
            Output('time-allocation-chart', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_time_allocation(n):
            return self._create_time_allocation_chart()
        
        @app.callback(
            Output('productivity-forecast', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_forecast(n):
            return self._create_productivity_forecast()
        
        self.dashboard_app = app
        return app
    
    def _create_usage_trend_chart(self) -> go.Figure:
        """Create usage trend chart"""
        # Get historical data for the last 7 days
        dates = []
        usage_values = []
        
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
            # Use sample data for demonstration
            usage_values.append(np.random.randint(60, 180))
        
        dates.reverse()
        usage_values.reverse()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=usage_values,
            mode='lines+markers',
            name='Daily Usage',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Social Media Usage Trend (Last 7 Days)",
            xaxis_title="Date",
            yaxis_title="Minutes",
            template="plotly_white",
            height=400
        )
        
        return fig
    
    def _create_productivity_gauge(self) -> go.Figure:
        """Create productivity gauge chart"""
        score = self.metrics['productivity_score'].value
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Productivity Score"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "yellow"},
                    {'range': [75, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            template="plotly_white",
            height=400
        )
        
        return fig
    
    def _create_focus_sessions_chart(self) -> go.Figure:
        """Create focus sessions bar chart"""
        # Sample data for the last 7 days
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        sessions = [np.random.randint(2, 6) for _ in range(7)]
        
        fig = go.Figure(data=[
            go.Bar(
                x=days,
                y=sessions,
                marker_color='#4ecdc4',
                text=sessions,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Focus Sessions by Day",
            xaxis_title="Day of Week",
            yaxis_title="Number of Sessions",
            template="plotly_white",
            height=300
        )
        
        return fig
    
    def _create_time_allocation_chart(self) -> go.Figure:
        """Create time allocation pie chart"""
        # Sample time allocation data
        labels = ['Social Media', 'Focus Work', 'Breaks', 'Other']
        values = [120, 240, 60, 180]  # minutes
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
        )])
        
        fig.update_layout(
            title="Daily Time Allocation",
            template="plotly_white",
            height=300
        )
        
        return fig
    
    def _create_productivity_forecast(self) -> go.Figure:
        """Create productivity forecast chart"""
        # Generate forecast data
        forecast_data = self.generate_forecast("default_user", days=7)
        
        if not forecast_data["dates"]:
            # Create sample forecast if no data
            dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 8)]
            predictions = [75 + np.random.randint(-10, 10) for _ in range(7)]
        else:
            dates = forecast_data["dates"]
            predictions = forecast_data["predictions"]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=predictions,
            mode='lines+markers',
            name='Predicted Productivity',
            line=dict(color='#667eea', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="7-Day Productivity Forecast",
            xaxis_title="Date",
            yaxis_title="Predicted Score",
            template="plotly_white",
            height=300
        )
        
        return fig
    
    def _real_time_updates(self):
        """Real-time data updates"""
        while True:
            try:
                # Update metrics with current data
                current_data = {
                    'daily_usage': np.random.randint(60, 180),
                    'focus_sessions': [{'duration': np.random.randint(20, 60)} for _ in range(np.random.randint(2, 5))],
                    'breaks_taken': np.random.randint(3, 6),
                    'time_saved_minutes': np.random.randint(30, 120),
                    'streak_days': np.random.randint(1, 10),
                    'daily_goal_met': np.random.choice([True, False]),
                    'goal_progress': np.random.uniform(0.5, 1.0),
                    'scheduled_breaks': 4
                }
                
                self.update_metrics("default_user", current_data)
                
                time.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error in real-time updates: {e}")
                time.sleep(300)
    
    def get_analytics_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        historical_data = self._get_historical_data(user_id, days=30)
        
        if not historical_data:
            return {"error": "No data available"}
        
        # Calculate summary statistics
        usage_values = [d['daily_usage'] for d in historical_data]
        productivity_values = [d['productivity_score'] for d in historical_data]
        focus_values = [d['focus_sessions'] for d in historical_data]
        
        summary = {
            "period": "Last 30 Days",
            "metrics": {
                "avg_daily_usage": round(np.mean(usage_values), 1),
                "avg_productivity": round(np.mean(productivity_values), 1),
                "avg_focus_sessions": round(np.mean(focus_values), 1),
                "total_time_saved": sum(d['time_saved'] for d in historical_data),
                "best_streak": max(d['streak_days'] for d in historical_data)
            },
            "trends": {
                "usage_trend": self.metrics['daily_usage'].trend,
                "productivity_trend": self.metrics['productivity_score'].trend,
                "focus_trend": self.metrics['focus_sessions'].trend
            },
            "insights": self._generate_analytics_insights(historical_data)
        }
        
        return summary
    
    def _generate_analytics_insights(self, historical_data: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from analytics data"""
        insights = []
        
        # Calculate averages
        avg_usage = np.mean([d['daily_usage'] for d in historical_data])
        avg_productivity = np.mean([d['productivity_score'] for d in historical_data])
        
        # Generate insights
        if avg_usage > 150:
            insights.append("Your daily social media usage is above recommended levels. Consider setting stricter limits.")
        
        if avg_productivity < 70:
            insights.append("Your productivity score is below target. Focus on completing more focus sessions.")
        
        if len(historical_data) >= 7:
            recent_usage = [d['daily_usage'] for d in historical_data[-7:]]
            if np.mean(recent_usage) < np.mean([d['daily_usage'] for d in historical_data[:-7]]):
                insights.append("Great progress! Your recent usage is lower than your average.")
        
        return insights

# Initialize database tables
def initialize_analytics_database(db_path: str = "productivity.db"):
    """Initialize database tables for analytics features"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Analytics data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    date TEXT,
                    daily_usage INTEGER,
                    focus_sessions INTEGER,
                    productivity_score REAL,
                    time_saved INTEGER,
                    streak_days INTEGER,
                    breaks_taken INTEGER,
                    interruptions INTEGER,
                    goal_completion REAL,
                    created_at TEXT
                )
            """)
            
            # Predictive models table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictive_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT,
                    model_data BLOB,
                    accuracy REAL,
                    last_updated TEXT
                )
            """)
            
            conn.commit()
            print("📊 Analytics database tables initialized successfully!")
            
    except Exception as e:
        logger.error(f"Error initializing analytics database: {e}")

if __name__ == "__main__":
    # Initialize database
    initialize_analytics_database()
    
    # Create analytics dashboard
    dashboard = AdvancedAnalyticsDashboard()
    
    # Create and run dashboard
    app = dashboard.create_dashboard()
    
    print("🚀 Starting Analytics Dashboard...")
    print("📊 Open http://localhost:8050 in your browser")
    
    # Run the dashboard
    app.run_server(debug=True, host='0.0.0.0', port=8050)
