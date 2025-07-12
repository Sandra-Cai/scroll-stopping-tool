# Scroll Stopping Tool - Advanced

A comprehensive Python application designed to help users break the habit of excessive social media scrolling and improve digital wellbeing. This advanced version includes focus mode, productivity tracking, website blocking, and detailed analytics.

## 🚀 Features

### Core Features
- **Real-time Usage Tracking**: Monitors social media usage across multiple platforms
- **Daily Limits**: Set and enforce daily time limits for social media
- **Break Reminders**: Automatic reminders to take breaks from screen time
- **Screen Locking**: Cross-platform screen locking when limits are reached
- **Alternative Activities**: Suggestions for offline activities

### Advanced Features
- **Focus Mode**: Enhanced blocking with productivity tracking
- **Website Blocking**: Block specific social media sites during work hours
- **Scheduled Breaks**: Set up automatic break reminders at specific times
- **Productivity Analytics**: Track focus sessions and productivity scores
- **Data Export**: Export usage data to CSV for analysis
- **Goal Setting**: Set daily, weekly, and monthly goals
- **Custom Notifications**: Personalized notification messages
- **SQLite Database**: Persistent storage for productivity sessions

### Focus Mode
- **Enhanced Blocking**: More aggressive site blocking during focus sessions
- **Interruption Tracking**: Monitor and score focus sessions based on interruptions
- **Productivity Scoring**: Calculate focus scores based on session quality
- **Session Analytics**: Detailed tracking of focus session performance

### Analytics & Reporting
- **Weekly Usage Charts**: Visual representation of social media usage
- **Productivity Metrics**: Track focus sessions and productivity scores
- **Goal Progress**: Monitor progress toward daily, weekly, and monthly goals
- **Data Export**: Export comprehensive usage data to CSV format
- **Historical Data**: Persistent storage of all usage and productivity data

## 📋 Requirements

- Python 3.7+
- macOS, Windows, or Linux
- Required packages (see requirements.txt):
  - tkinter (usually included with Python)
  - psutil
  - plyer
  - matplotlib
  - schedule

## 🛠️ Installation

### Option 1: Automated Installation
```bash
python install.py
```

### Option 2: Manual Installation
1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python run.py
   ```

### macOS Users
For matplotlib installation issues on macOS, use conda:
```bash
conda install matplotlib
```

## 🎯 Usage

### Getting Started
1. Launch the application using `python run.py`
2. Click "Start Tracking" to begin monitoring social media usage
3. Configure your settings in the Settings dialog
4. Set up your daily limits and goals

### Core Controls
- **Start/Stop Tracking**: Begin or end usage monitoring
- **Focus Mode**: Enable enhanced blocking and productivity tracking
- **Take Break**: Manually trigger a break reminder
- **Lock Screen**: Immediately lock your screen
- **Block Sites**: Configure website blocking settings
- **Export Data**: Export usage data to CSV

### Settings Configuration
Access advanced settings through the Settings button:

#### General Tab
- **Daily Limit**: Set maximum daily social media usage (minutes)
- **Break Reminder**: Set interval for break reminders (minutes)
- **Notifications**: Enable/disable system notifications
- **Auto Break**: Enable automatic break reminders
- **Auto Lock**: Automatically lock screen when limit reached
- **Focus Mode**: Enable focus mode features

#### Scheduled Breaks Tab
- Add/remove scheduled break times (HH:MM format)
- Automatic notifications at scheduled times
- Customizable break schedule

#### Goals Tab
- **Daily Limit**: Set daily usage goal
- **Weekly Goal**: Set weekly goal for days under limit
- **Monthly Goal**: Set monthly goal for days under limit

### Focus Mode
1. Click "Focus Mode" to enable enhanced blocking
2. Focus sessions are automatically tracked
3. Interruptions are monitored and scored
4. Productivity scores are calculated and stored
5. Click "Exit Focus Mode" to end the session

### Website Blocking
1. Click "Block Sites" to open blocking configuration
2. Enable website blocking
3. Add/remove sites from the blocked list
4. Blocking works in conjunction with focus mode

### Data Export
1. Click "Export Data" to save usage data
2. Choose location and filename
3. Data is exported in CSV format with:
   - Daily usage statistics
   - Break counts
   - Focus session data
   - Productivity scores

## 📊 Analytics

### Usage Tracking
- Real-time monitoring of social media processes
- Daily usage statistics
- Weekly usage charts
- Progress toward daily limits

### Productivity Metrics
- Focus session duration
- Interruption tracking
- Productivity scores
- Session quality analysis

### Goal Progress
- Daily limit adherence
- Weekly goal tracking
- Monthly goal progress
- Historical performance

## 🔧 Configuration

### Settings File (`settings.json`)
```json
{
  "daily_limit": 120,
  "break_reminder": 30,
  "block_hours": {
    "start": "22:00",
    "end": "07:00"
  },
  "notifications_enabled": true,
  "auto_break": true,
  "auto_lock": false,
  "blocking_enabled": false,
  "blocked_sites": ["facebook.com", "instagram.com"],
  "scheduled_breaks": ["12:00", "15:00", "18:00"],
  "focus_mode_enabled": true,
  "goals": {
    "daily_limit": 120,
    "weekly_goal": 5,
    "monthly_goal": 20
  }
}
```

### Data Files
- `usage_data.json`: Usage statistics and tracking data
- `productivity.db`: SQLite database for focus sessions
- `settings.json`: Application configuration

## 🎨 Features in Detail

### Focus Mode
- **Enhanced Blocking**: More aggressive site blocking during focus sessions
- **Interruption Tracking**: Count and score interruptions during focus
- **Session Analytics**: Detailed tracking of focus session performance
- **Productivity Scoring**: Calculate focus scores (0-100) based on interruptions

### Website Blocking
- **Process Monitoring**: Monitor browser processes for social media sites
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Configurable**: Add/remove sites from blocked list
- **Integration**: Works with focus mode for enhanced blocking

### Scheduled Breaks
- **Time-Based**: Set specific times for break reminders
- **Automatic**: No manual intervention required
- **Customizable**: Add/remove break times as needed
- **Notifications**: System notifications at scheduled times

### Data Export
- **CSV Format**: Standard format for data analysis
- **Comprehensive**: Includes all usage and productivity data
- **Historical**: Export historical data for trend analysis
- **Customizable**: Choose export location and filename

## 🚀 Advanced Usage

### Productivity Tracking
1. Enable focus mode for enhanced tracking
2. Monitor focus sessions and interruptions
3. Review productivity scores in analytics
4. Export data for detailed analysis

### Goal Setting
1. Set realistic daily, weekly, and monthly goals
2. Monitor progress in the main interface
3. Review goal achievement in analytics
4. Adjust goals based on performance

### Custom Notifications
1. Configure notification preferences in settings
2. Set up scheduled break notifications
3. Customize focus mode notifications
4. Enable/disable different notification types

## 🔒 Privacy & Security

- All data is stored locally on your device
- No data is transmitted to external servers
- Usage data is stored in JSON and SQLite formats
- Settings are stored in local configuration files

## 🛠️ Troubleshooting

### Common Issues
1. **Matplotlib Installation**: Use conda for macOS users
2. **Permission Errors**: Run with appropriate permissions for screen locking
3. **Process Detection**: Some browsers may not be detected in all configurations
4. **Notification Issues**: Check system notification permissions

### Platform-Specific Notes
- **macOS**: Screen locking uses CGSession
- **Windows**: Screen locking uses LockWorkStation
- **Linux**: Screen locking supports multiple methods (gnome-screensaver, loginctl)

## 📈 Future Enhancements

- Machine learning for usage pattern analysis
- Integration with calendar applications
- Mobile app companion
- Cloud sync for multi-device usage
- Advanced analytics dashboard
- Custom themes and UI customization

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Python and tkinter
- Uses psutil for process monitoring
- Matplotlib for data visualization
- Plyer for cross-platform notifications
- Schedule for task scheduling

---

**Start your journey to better digital wellbeing today!** 🎯
