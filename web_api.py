#!/usr/bin/env python3
"""
Web API Module for Enhanced Scroll Stopping Tool
RESTful API for remote access, mobile integration, and web dashboard.
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Standard API response structure"""
    success: bool
    data: Any
    message: str
    timestamp: str

class WebAPI:
    """Web API server for the scroll stopping tool"""
    
    def __init__(self, app_instance=None, host='localhost', port=5000):
        self.app = Flask(__name__)
        self.app_instance = app_instance
        self.host = host
        self.port = port
        self.server_thread = None
        self.is_running = False
        
        # Enable CORS for cross-origin requests
        CORS(self.app)
        
        # Setup routes
        self.setup_routes()
        
        # API documentation
        self.api_docs = self._generate_api_docs()
        
        logger.info(f"Web API initialized on {host}:{port}")
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/')
        def index():
            """API documentation page"""
            return self._render_docs_page()
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get current application status"""
            try:
                status_data = self._get_status_data()
                return jsonify(APIResponse(
                    success=True,
                    data=status_data,
                    message="Status retrieved successfully",
                    timestamp=datetime.now().isoformat()
                ).__dict__)
            except Exception as e:
                logger.error(f"Error getting status: {e}")
                return jsonify(APIResponse(
                    success=False,
                    data=None,
                    message=f"Error retrieving status: {str(e)}",
                    timestamp=datetime.now().isoformat()
                ).__dict__), 500
        
        @self.app.route('/api/usage', methods=['GET'])
        def get_usage():
            """Get usage statistics"""
            try:
                usage_data = self._get_usage_data()
                return jsonify(APIResponse(
                    success=True,
                    data=usage_data,
                    message="Usage data retrieved successfully",
                    timestamp=datetime.now().isoformat()
                ).__dict__)
            except Exception as e:
                logger.error(f"Error getting usage: {e}")
                return jsonify(APIResponse(
                    success=False,
                    data=None,
                    message=f"Error retrieving usage: {str(e)}",
                    timestamp=datetime.now().isoformat()
                ).__dict__), 500
        
        @self.app.route('/api/focus/start', methods=['POST'])
        def start_focus():
            """Start focus mode"""
            try:
                if self.app_instance and hasattr(self.app_instance, 'start_focus_mode'):
                    self.app_instance.start_focus_mode()
                    return jsonify(APIResponse(
                        success=True,
                        data={"focus_mode": "started"},
                        message="Focus mode started successfully",
                        timestamp=datetime.now().isoformat()
                    ).__dict__)
                else:
                    return jsonify(APIResponse(
                        success=False,
                        data=None,
                        message="Focus mode not available",
                        timestamp=datetime.now().isoformat()
                    ).__dict__), 400
            except Exception as e:
                logger.error(f"Error starting focus mode: {e}")
                return jsonify(APIResponse(
                    success=False,
                    data=None,
                    message=f"Error starting focus mode: {str(e)}",
                    timestamp=datetime.now().isoformat()
                ).__dict__), 500
        
        @self.app.route('/api/focus/stop', methods=['POST'])
        def stop_focus():
            """Stop focus mode"""
            try:
                if self.app_instance and hasattr(self.app_instance, 'stop_focus_mode'):
                    self.app_instance.stop_focus_mode()
                    return jsonify(APIResponse(
                        success=True,
                        data={"focus_mode": "stopped"},
                        message="Focus mode stopped successfully",
                        timestamp=datetime.now().isoformat()
                    ).__dict__)
                else:
                    return jsonify(APIResponse(
                        success=False,
                        data=None,
                        message="Focus mode not available",
                        timestamp=datetime.now().isoformat()
                    ).__dict__), 400
            except Exception as e:
                logger.error(f"Error stopping focus mode: {e}")
                return jsonify(APIResponse(
                    success=False,
                    data=None,
                    message=f"Error stopping focus mode: {str(e)}",
                    timestamp=datetime.now().isoformat()
                ).__dict__), 500
        
        @self.app.route('/api/break', methods=['POST'])
        def take_break():
            """Take a break"""
            try:
                if self.app_instance and hasattr(self.app_instance, 'take_break'):
                    self.app_instance.take_break()
                    return jsonify(APIResponse(
                        success=True,
                        data={"break": "started"},
                        message="Break started successfully",
                        timestamp=datetime.now().isoformat()
                    ).__dict__)
                else:
                    return jsonify(APIResponse(
                        success=False,
                        data=None,
                        message="Break feature not available",
                        timestamp=datetime.now().isoformat()
                    ).__dict__), 400
            except Exception as e:
                logger.error(f"Error taking break: {e}")
                return jsonify(APIResponse(
                    success=False,
                    data=None,
                    message=f"Error taking break: {str(e)}",
                    timestamp=datetime.now().isoformat()
                ).__dict__), 500
        
        @self.app.route('/api/achievements', methods=['GET'])
        def get_achievements():
            """Get achievements"""
            try:
                achievements = self._get_achievements_data()
                return jsonify(APIResponse(
                    success=True,
                    data=achievements,
                    message="Achievements retrieved successfully",
                    timestamp=datetime.now().isoformat()
                ).__dict__)
            except Exception as e:
                logger.error(f"Error getting achievements: {e}")
                return jsonify(APIResponse(
                    success=False,
                    data=None,
                    message=f"Error retrieving achievements: {str(e)}",
                    timestamp=datetime.now().isoformat()
                ).__dict__), 500
        
        @self.app.route('/api/analytics', methods=['GET'])
        def get_analytics():
            """Get analytics data"""
            try:
                analytics_data = self._get_analytics_data()
                return jsonify(APIResponse(
                    success=True,
                    data=analytics_data,
                    message="Analytics data retrieved successfully",
                    timestamp=datetime.now().isoformat()
                ).__dict__)
            except Exception as e:
                logger.error(f"Error getting analytics: {e}")
                return jsonify(APIResponse(
                    success=False,
                    data=None,
                    message=f"Error retrieving analytics: {str(e)}",
                    timestamp=datetime.now().isoformat()
                ).__dict__), 500
        
        @self.app.route('/api/settings', methods=['GET', 'PUT'])
        def manage_settings():
            """Get or update settings"""
            if request.method == 'GET':
                try:
                    settings = self._get_settings_data()
                    return jsonify(APIResponse(
                        success=True,
                        data=settings,
                        message="Settings retrieved successfully",
                        timestamp=datetime.now().isoformat()
                    ).__dict__)
                except Exception as e:
                    logger.error(f"Error getting settings: {e}")
                    return jsonify(APIResponse(
                        success=False,
                        data=None,
                        message=f"Error retrieving settings: {str(e)}",
                        timestamp=datetime.now().isoformat()
                    ).__dict__), 500
            
            elif request.method == 'PUT':
                try:
                    new_settings = request.get_json()
                    if self.app_instance and hasattr(self.app_instance, 'update_settings'):
                        self.app_instance.update_settings(new_settings)
                        return jsonify(APIResponse(
                            success=True,
                            data=new_settings,
                            message="Settings updated successfully",
                            timestamp=datetime.now().isoformat()
                        ).__dict__)
                    else:
                        return jsonify(APIResponse(
                            success=False,
                            data=None,
                            message="Settings update not available",
                            timestamp=datetime.now().isoformat()
                        ).__dict__), 400
                except Exception as e:
                    logger.error(f"Error updating settings: {e}")
                    return jsonify(APIResponse(
                        success=False,
                        data=None,
                        message=f"Error updating settings: {str(e)}",
                        timestamp=datetime.now().isoformat()
                    ).__dict__), 500
        
        @self.app.route('/api/export', methods=['GET'])
        def export_data():
            """Export data in various formats"""
            try:
                format_type = request.args.get('format', 'json')
                data = self._get_export_data()
                
                if format_type == 'json':
                    return jsonify(data)
                elif format_type == 'csv':
                    # Convert to CSV format
                    csv_data = self._convert_to_csv(data)
                    return csv_data, 200, {'Content-Type': 'text/csv'}
                else:
                    return jsonify(APIResponse(
                        success=False,
                        data=None,
                        message=f"Unsupported format: {format_type}",
                        timestamp=datetime.now().isoformat()
                    ).__dict__), 400
            except Exception as e:
                logger.error(f"Error exporting data: {e}")
                return jsonify(APIResponse(
                    success=False,
                    data=None,
                    message=f"Error exporting data: {str(e)}",
                    timestamp=datetime.now().isoformat()
                ).__dict__), 500
    
    def _get_status_data(self) -> Dict:
        """Get current status data"""
        if self.app_instance:
            return {
                'usage_time': getattr(self.app_instance, 'today_usage', 0),
                'productivity_score': getattr(self.app_instance, 'productivity_score', 0),
                'focus_sessions': getattr(self.app_instance, 'focus_sessions', 0),
                'breaks_taken': getattr(self.app_instance, 'breaks_taken', 0),
                'streak_days': getattr(self.app_instance, 'streak_days', 0),
                'is_tracking': getattr(self.app_instance, 'is_tracking', False),
                'is_focus_mode': getattr(self.app_instance, 'is_focus_mode', False),
                'last_updated': datetime.now().isoformat()
            }
        else:
            return {
                'usage_time': 0,
                'productivity_score': 0,
                'focus_sessions': 0,
                'breaks_taken': 0,
                'streak_days': 0,
                'is_tracking': False,
                'is_focus_mode': False,
                'last_updated': datetime.now().isoformat()
            }
    
    def _get_usage_data(self) -> Dict:
        """Get usage statistics"""
        if self.app_instance:
            return {
                'today_usage': getattr(self.app_instance, 'today_usage', 0),
                'weekly_usage': self._get_weekly_usage(),
                'monthly_usage': self._get_monthly_usage(),
                'daily_limit': getattr(self.app_instance, 'settings', {}).get('daily_limit', 120),
                'usage_trend': self._get_usage_trend()
            }
        else:
            return {
                'today_usage': 0,
                'weekly_usage': [],
                'monthly_usage': [],
                'daily_limit': 120,
                'usage_trend': []
            }
    
    def _get_achievements_data(self) -> List[Dict]:
        """Get achievements data"""
        if self.app_instance and hasattr(self.app_instance, 'achievements'):
            return self.app_instance.achievements
        else:
            return [
                {'name': 'Getting Started', 'description': 'Complete your first day', 'unlocked': True},
                {'name': 'Week Warrior', 'description': 'Maintain a 7-day streak', 'unlocked': False},
                {'name': 'Productivity Pro', 'description': 'Achieve 90% productivity', 'unlocked': False}
            ]
    
    def _get_analytics_data(self) -> Dict:
        """Get analytics data"""
        return {
            'productivity_trend': self._get_productivity_trend(),
            'focus_session_analytics': self._get_focus_analytics(),
            'usage_patterns': self._get_usage_patterns(),
            'achievement_progress': self._get_achievement_progress()
        }
    
    def _get_settings_data(self) -> Dict:
        """Get settings data"""
        if self.app_instance and hasattr(self.app_instance, 'settings'):
            return self.app_instance.settings
        else:
            return {
                'daily_limit': 120,
                'break_reminder': 30,
                'notifications_enabled': True,
                'auto_break': True,
                'theme': 'flatly'
            }
    
    def _get_export_data(self) -> Dict:
        """Get data for export"""
        return {
            'status': self._get_status_data(),
            'usage': self._get_usage_data(),
            'achievements': self._get_achievements_data(),
            'analytics': self._get_analytics_data(),
            'settings': self._get_settings_data(),
            'export_timestamp': datetime.now().isoformat()
        }
    
    def _get_weekly_usage(self) -> List[int]:
        """Get weekly usage data"""
        # Simulate weekly usage data
        return [random.randint(60, 150) for _ in range(7)]
    
    def _get_monthly_usage(self) -> List[int]:
        """Get monthly usage data"""
        # Simulate monthly usage data
        return [random.randint(800, 2000) for _ in range(12)]
    
    def _get_usage_trend(self) -> List[Dict]:
        """Get usage trend data"""
        # Simulate usage trend
        return [
            {'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 
             'usage': random.randint(60, 150)} 
            for i in range(7, 0, -1)
        ]
    
    def _get_productivity_trend(self) -> List[Dict]:
        """Get productivity trend data"""
        # Simulate productivity trend
        return [
            {'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 
             'productivity': random.randint(60, 95)} 
            for i in range(7, 0, -1)
        ]
    
    def _get_focus_analytics(self) -> Dict:
        """Get focus session analytics"""
        return {
            'total_sessions': random.randint(10, 50),
            'average_duration': random.randint(25, 60),
            'best_session': random.randint(80, 95),
            'sessions_today': random.randint(0, 5)
        }
    
    def _get_usage_patterns(self) -> Dict:
        """Get usage patterns"""
        return {
            'peak_hours': [9, 10, 14, 15],
            'low_usage_hours': [0, 1, 2, 3, 4, 5, 6],
            'most_productive_day': 'Tuesday',
            'least_productive_day': 'Sunday'
        }
    
    def _get_achievement_progress(self) -> Dict:
        """Get achievement progress"""
        return {
            'total_achievements': 20,
            'unlocked': random.randint(3, 8),
            'completion_rate': random.randint(15, 40),
            'next_achievement': 'Focus Marathon'
        }
    
    def _convert_to_csv(self, data: Dict) -> str:
        """Convert data to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Metric', 'Value'])
        
        # Flatten data and write rows
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                writer.writerow([key, json.dumps(value)])
            else:
                writer.writerow([key, value])
        
        return output.getvalue()
    
    def _generate_api_docs(self) -> Dict:
        """Generate API documentation"""
        return {
            'title': 'Enhanced Scroll Stopping Tool API',
            'version': '1.0.0',
            'description': 'RESTful API for remote access and mobile integration',
            'endpoints': {
                'GET /api/status': 'Get current application status',
                'GET /api/usage': 'Get usage statistics',
                'POST /api/focus/start': 'Start focus mode',
                'POST /api/focus/stop': 'Stop focus mode',
                'POST /api/break': 'Take a break',
                'GET /api/achievements': 'Get achievements',
                'GET /api/analytics': 'Get analytics data',
                'GET /api/settings': 'Get current settings',
                'PUT /api/settings': 'Update settings',
                'GET /api/export': 'Export data (format=json|csv)'
            }
        }
    
    def _render_docs_page(self) -> str:
        """Render API documentation page"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ docs.title }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { background: #f8f9fa; padding: 20px; border-radius: 5px; }
                .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .method { font-weight: bold; color: #007bff; }
                .description { color: #666; margin-top: 5px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ docs.title }}</h1>
                <p><strong>Version:</strong> {{ docs.version }}</p>
                <p>{{ docs.description }}</p>
            </div>
            
            <h2>API Endpoints</h2>
            {% for endpoint, description in docs.endpoints.items() %}
            <div class="endpoint">
                <div class="method">{{ endpoint }}</div>
                <div class="description">{{ description }}</div>
            </div>
            {% endfor %}
            
            <h2>Example Usage</h2>
            <pre>
# Get status
curl http://localhost:5000/api/status

# Start focus mode
curl -X POST http://localhost:5000/api/focus/start

# Get usage data
curl http://localhost:5000/api/usage

# Export data as CSV
curl http://localhost:5000/api/export?format=csv
            </pre>
        </body>
        </html>
        """
        
        from jinja2 import Template
        template = Template(html_template)
        return template.render(docs=self.api_docs)
    
    def start_server(self):
        """Start the web API server"""
        if self.is_running:
            logger.warning("Web API server is already running")
            return
        
        self.is_running = True
        self.server_thread = threading.Thread(
            target=self._run_server, 
            daemon=True
        )
        self.server_thread.start()
        logger.info(f"Web API server started on http://{self.host}:{self.port}")
    
    def stop_server(self):
        """Stop the web API server"""
        self.is_running = False
        if self.server_thread:
            self.server_thread.join(timeout=5)
        logger.info("Web API server stopped")
    
    def _run_server(self):
        """Run the Flask server"""
        try:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"Error running web API server: {e}")
            self.is_running = False

# Example usage
if __name__ == "__main__":
    import random
    
    # Initialize web API
    web_api = WebAPI()
    
    # Start server
    web_api.start_server()
    
    print("🌐 Web API server started!")
    print("📖 Documentation: http://localhost:5000")
    print("🔗 API Base URL: http://localhost:5000/api")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        web_api.stop_server()
        print("Web API server stopped") 