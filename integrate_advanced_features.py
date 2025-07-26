#!/usr/bin/env python3
"""
Advanced Features Integration Script
Integrates all advanced features into the enhanced scroll stopping tool.
"""

import sys
import os
from pathlib import Path

def integrate_advanced_features():
    """Integrate all advanced features into the main application"""
    
    print("🚀 Integrating Advanced Features into Enhanced Scroll Stopping Tool")
    print("=" * 60)
    
    # Check if all required files exist
    required_files = [
        'scroll_stopping_tool_enhanced.py',
        'advanced_features.py',
        'ml_analytics.py',
        'gamification.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please ensure all advanced feature modules are present.")
        return False
    
    print("✅ All required files found")
    
    # Read the main enhanced file
    try:
        with open('scroll_stopping_tool_enhanced.py', 'r') as f:
            main_content = f.read()
        
        print("📖 Reading main application file...")
        
        # Check if advanced features are already integrated
        if 'from advanced_features import' in main_content:
            print("⚠️  Advanced features already integrated")
            return True
        
        # Find the integration point (after imports, before main class)
        integration_point = main_content.find('class EnhancedScrollStoppingTool:')
        
        if integration_point == -1:
            print("❌ Could not find integration point")
            return False
        
        # Create the integration code
        integration_code = '''

# Advanced Features Integration
try:
    from advanced_features import AdvancedFeatures
    from ml_analytics import PredictiveAnalytics
    from gamification import GamificationEngine
    ADVANCED_FEATURES_AVAILABLE = True
    logger.info("Advanced features loaded successfully")
except ImportError as e:
    ADVANCED_FEATURES_AVAILABLE = False
    logger.warning(f"Advanced features not available: {e}")

'''
        
        # Insert the integration code
        new_content = (
            main_content[:integration_point] + 
            integration_code + 
            main_content[integration_point:]
        )
        
        # Add advanced features to the main class
        class_integration = '''
        # Advanced features integration
        self.advanced_features = None
        self.ml_analytics = None
        self.gamification = None
        
        if ADVANCED_FEATURES_AVAILABLE:
            self.setup_advanced_features()
'''
        
        # Find the setup_managers method
        setup_managers_pos = new_content.find('def setup_managers(self):')
        if setup_managers_pos != -1:
            # Find the end of the method
            method_end = new_content.find('\n    def ', setup_managers_pos + 1)
            if method_end == -1:
                method_end = len(new_content)
            
            # Insert advanced features setup
            new_content = (
                new_content[:method_end] + 
                class_integration + 
                new_content[method_end:]
            )
        
        # Add the advanced features setup method
        advanced_methods = '''
    def setup_advanced_features(self):
        """Setup advanced features if available"""
        try:
            if ADVANCED_FEATURES_AVAILABLE:
                self.advanced_features = AdvancedFeatures()
                self.ml_analytics = PredictiveAnalytics()
                self.gamification = GamificationEngine()
                
                # Initialize with existing data
                user_data = {
                    'goals': [],
                    'usage_history': []
                }
                self.advanced_features.initialize_advanced_features(user_data)
                
                logger.info("Advanced features initialized successfully")
        except Exception as e:
            logger.error(f"Failed to setup advanced features: {e}")
    
    def get_advanced_insights(self) -> Dict[str, Any]:
        """Get advanced insights and recommendations"""
        if not self.advanced_features:
            return {'error': 'Advanced features not available'}
        
        try:
            # Get current data
            current_data = {
                'daily_usage': self.today_usage,
                'productivity_score': self.productivity_score,
                'focus_sessions': self.focus_sessions,
                'breaks_taken': self.breaks_taken,
                'daily_limit_met': self.today_usage <= self.settings.get('daily_limit', 120)
            }
            
            # Get ML predictions
            predictions = {}
            if self.ml_analytics:
                predictions = self.ml_analytics.get_predictions(current_data)
            
            # Get gamification updates
            gamification_results = {}
            if self.gamification:
                gamification_results = self.gamification.process_daily_update(current_data)
            
            # Get advanced insights
            insights = []
            if self.advanced_features:
                insights = self.advanced_features.get_daily_insights(current_data)
            
            return {
                'predictions': predictions,
                'gamification': gamification_results,
                'insights': [vars(insight) for insight in insights],
                'advanced_summary': self.advanced_features.get_gamification_summary() if self.gamification else {}
            }
        except Exception as e:
            logger.error(f"Failed to get advanced insights: {e}")
            return {'error': str(e)}
    
    def show_advanced_dashboard(self):
        """Show advanced analytics dashboard"""
        if not self.advanced_features:
            messagebox.showinfo("Advanced Features", "Advanced features are not available. Please install additional dependencies.")
            return
        
        try:
            insights = self.get_advanced_insights()
            
            # Create advanced dashboard window
            dashboard_window = tk.Toplevel(self.root)
            dashboard_window.title("Advanced Analytics Dashboard")
            dashboard_window.geometry("800x600")
            
            # Create notebook for tabs
            notebook = ttk.Notebook(dashboard_window)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # ML Predictions tab
            predictions_frame = ttk.Frame(notebook)
            notebook.add(predictions_frame, text="🤖 ML Predictions")
            self.create_predictions_tab(predictions_frame, insights.get('predictions', {}))
            
            # Gamification tab
            gamification_frame = ttk.Frame(notebook)
            notebook.add(gamification_frame, text="🏆 Gamification")
            self.create_gamification_tab(gamification_frame, insights.get('gamification', {}))
            
            # Insights tab
            insights_frame = ttk.Frame(notebook)
            notebook.add(insights_frame, text="💡 Insights")
            self.create_insights_tab(insights_frame, insights.get('insights', []))
            
        except Exception as e:
            logger.error(f"Failed to show advanced dashboard: {e}")
            messagebox.showerror("Error", f"Failed to show advanced dashboard: {e}")
    
    def create_predictions_tab(self, parent, predictions):
        """Create ML predictions tab"""
        # Title
        title_label = ttk.Label(parent, text="Machine Learning Predictions", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Predictions display
        if predictions:
            for pred_type, prediction in predictions.items():
                if hasattr(prediction, 'value'):
                    frame = ttk.LabelFrame(parent, text=pred_type.replace('_', ' ').title())
                    frame.pack(fill='x', padx=10, pady=5)
                    
                    ttk.Label(frame, text=f"Predicted Value: {prediction.value:.1f}").pack(anchor='w', padx=5)
                    ttk.Label(frame, text=f"Confidence: {prediction.confidence:.1%}").pack(anchor='w', padx=5)
                    ttk.Label(frame, text=f"Factors: {', '.join(prediction.factors)}").pack(anchor='w', padx=5)
        else:
            ttk.Label(parent, text="No predictions available yet. More data needed.").pack(pady=20)
    
    def create_gamification_tab(self, parent, gamification_data):
        """Create gamification tab"""
        # Title
        title_label = ttk.Label(parent, text="Gamification & Achievements", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        if gamification_data:
            # Level and points
            level_frame = ttk.LabelFrame(parent, text="Progress")
            level_frame.pack(fill='x', padx=10, pady=5)
            
            if self.gamification:
                summary = self.gamification.get_gamification_summary()
                ttk.Label(level_frame, text=f"Level: {summary.get('level', 1)}").pack(anchor='w', padx=5)
                ttk.Label(level_frame, text=f"Experience: {summary.get('experience', 0)}").pack(anchor='w', padx=5)
                ttk.Label(level_frame, text=f"Points: {summary.get('points', 0)}").pack(anchor='w', padx=5)
            
            # Recent achievements
            achievements_frame = ttk.LabelFrame(parent, text="Recent Achievements")
            achievements_frame.pack(fill='x', padx=10, pady=5)
            
            new_achievements = gamification_data.get('achievements_unlocked', [])
            if new_achievements:
                for achievement in new_achievements:
                    ttk.Label(achievements_frame, text=f"🏆 {achievement.name}").pack(anchor='w', padx=5)
            else:
                ttk.Label(achievements_frame, text="No new achievements yet").pack(padx=5)
        else:
            ttk.Label(parent, text="Gamification data not available").pack(pady=20)
    
    def create_insights_tab(self, parent, insights):
        """Create insights tab"""
        # Title
        title_label = ttk.Label(parent, text="Smart Insights", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        if insights:
            for insight in insights:
                frame = ttk.LabelFrame(parent, text=insight.get('type', 'Insight').title())
                frame.pack(fill='x', padx=10, pady=5)
                
                ttk.Label(frame, text=insight.get('message', 'No message')).pack(anchor='w', padx=5)
                ttk.Label(frame, text=f"Confidence: {insight.get('confidence', 0):.1%}").pack(anchor='w', padx=5)
                
                action_items = insight.get('action_items', [])
                if action_items:
                    ttk.Label(frame, text="Action Items:").pack(anchor='w', padx=5)
                    for item in action_items:
                        ttk.Label(frame, text=f"• {item}").pack(anchor='w', padx=15)
        else:
            ttk.Label(parent, text="No insights available yet").pack(pady=20)

'''
        
        # Add the advanced methods to the class
        class_end = new_content.rfind('    def ')
        if class_end != -1:
            # Find the end of the last method
            last_method_end = new_content.rfind('\n\n', class_end)
            if last_method_end == -1:
                last_method_end = len(new_content)
            
            new_content = (
                new_content[:last_method_end] + 
                advanced_methods + 
                new_content[last_method_end:]
            )
        
        # Add advanced dashboard button to the UI
        ui_integration = '''
        # Advanced Analytics button
        self.advanced_button = ttk.Button(
            secondary_frame,
            text="🤖 Advanced Analytics",
            command=self.show_advanced_dashboard,
            width=15
        )
        self.advanced_button.grid(row=0, column=4, padx=(0, 10))
'''
        
        # Find the secondary controls section
        secondary_controls = new_content.find('secondary_frame = ttk.Frame(control_frame)')
        if secondary_controls != -1:
            # Find where to insert the button
            insert_pos = new_content.find('ttk.Button(', secondary_controls)
            if insert_pos != -1:
                # Find the end of the button section
                button_section_end = new_content.find('\n        ', insert_pos)
                if button_section_end != -1:
                    new_content = (
                        new_content[:button_section_end] + 
                        ui_integration + 
                        new_content[button_section_end:]
                    )
        
        # Write the updated content back
        with open('scroll_stopping_tool_enhanced.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Advanced features integrated successfully!")
        print("\n🎯 New features added:")
        print("  • Machine Learning Predictions")
        print("  • Advanced Analytics Dashboard")
        print("  • Gamification System")
        print("  • Smart Insights")
        print("  • Achievement Tracking")
        print("  • Predictive Analytics")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        return False

def create_advanced_requirements():
    """Create comprehensive requirements file with all advanced features"""
    
    advanced_requirements = '''# Enhanced Scroll Stopping Tool - Complete Requirements
# Core dependencies
psutil==5.9.6
plyer==2.1.0
schedule==1.2.0
matplotlib==3.7.2
ttkbootstrap==1.10.1

# Enhanced UI and visualization
Pillow==10.2.0
qrcode==7.4.2

# Web and API features
Flask==2.3.2
requests==2.31.0

# Audio and voice features
pygame==2.5.2
SpeechRecognition==3.10.0
pyttsx3==2.90

# Cloud and external services
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
twilio==8.10.0

# Data processing and analysis
pandas==2.1.4
numpy==1.25.2
seaborn==0.13.0

# Machine Learning (for advanced features)
scikit-learn==1.3.2

# Security and encryption
cryptography==42.0.5

# Development and testing
pytest==7.4.3
black==23.11.0
flake8==6.1.0

# Optional: Database enhancements
sqlalchemy==2.0.23

# Optional: Async support
aiohttp==3.9.1
asyncio-mqtt==0.16.1
'''
    
    try:
        with open('requirements_complete.txt', 'w') as f:
            f.write(advanced_requirements)
        print("✅ Complete requirements file created: requirements_complete.txt")
        return True
    except Exception as e:
        print(f"❌ Failed to create requirements file: {e}")
        return False

def create_advanced_installer():
    """Create advanced installer script"""
    
    installer_content = '''#!/usr/bin/env python3
"""
Complete Installation Script for Enhanced Scroll Stopping Tool with Advanced Features
"""

import subprocess
import sys
import os
from pathlib import Path

def install_complete():
    """Install all dependencies including advanced features"""
    
    print("🚀 Installing Enhanced Scroll Stopping Tool with Advanced Features")
    print("=" * 70)
    
    # Install core requirements
    print("📦 Installing core dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_complete.txt"], check=True)
        print("✅ Core dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install core dependencies: {e}")
        return False
    
    # Install optional ML dependencies
    print("🤖 Installing machine learning dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "scikit-learn", "pandas", "numpy"], check=True)
        print("✅ ML dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  ML dependencies failed (optional): {e}")
    
    # Test the installation
    print("🧪 Testing installation...")
    try:
        result = subprocess.run([sys.executable, "test_enhanced.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Installation test passed")
        else:
            print("⚠️  Installation test had issues")
    except Exception as e:
        print(f"⚠️  Could not run installation test: {e}")
    
    print("\\n🎉 Installation completed!")
    print("\\n🎯 To run the enhanced version with advanced features:")
    print("   python scroll_stopping_tool_enhanced.py")
    print("\\n📊 Advanced features include:")
    print("   • Machine Learning Predictions")
    print("   • Advanced Analytics Dashboard")
    print("   • Gamification System")
    print("   • Smart Insights")
    print("   • Achievement Tracking")
    
    return True

if __name__ == "__main__":
    install_complete()
'''
    
    try:
        with open('install_complete.py', 'w') as f:
            f.write(installer_content)
        print("✅ Complete installer created: install_complete.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create installer: {e}")
        return False

def main():
    """Main integration function"""
    print("🔧 Advanced Features Integration Tool")
    print("=" * 50)
    
    # Step 1: Integrate advanced features
    if not integrate_advanced_features():
        print("❌ Integration failed. Exiting.")
        return False
    
    # Step 2: Create complete requirements
    if not create_advanced_requirements():
        print("❌ Failed to create requirements. Continuing...")
    
    # Step 3: Create complete installer
    if not create_advanced_installer():
        print("❌ Failed to create installer. Continuing...")
    
    print("\n🎉 Integration completed successfully!")
    print("\n📋 Next steps:")
    print("1. Install complete dependencies:")
    print("   pip install -r requirements_complete.txt")
    print("2. Or use the complete installer:")
    print("   python install_complete.py")
    print("3. Run the enhanced application:")
    print("   python scroll_stopping_tool_enhanced.py")
    print("\n🚀 Enjoy your enhanced productivity tool!")
    
    return True

if __name__ == "__main__":
    main() 