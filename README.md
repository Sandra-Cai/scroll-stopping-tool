# Scroll Stopping Tool

## Overview

This program is designed to help users break the habit of excessive social media scrolling. It aims to promote healthier digital habits by providing tools and features that encourage mindful technology use.

## Purpose

Social media platforms are designed to capture and maintain user attention through infinite scrolling, notifications, and engaging content. This can lead to:

- **Time waste**: Hours spent mindlessly scrolling
- **Reduced productivity**: Distraction from important tasks
- **Mental health impacts**: Comparison, FOMO, and anxiety
- **Sleep disruption**: Blue light exposure and late-night usage

This tool helps combat these issues by providing features that:

- Track social media usage time
- Set daily limits and reminders
- Block or restrict access during certain hours
- Provide mindfulness prompts and breaks
- Offer alternative activities and suggestions

## Features

- **Usage Tracking**: Monitor time spent on social media platforms
- **Time Limits**: Set daily or session-based limits
- **Scheduled Blocks**: Restrict access during work hours or bedtime
- **Mindfulness Prompts**: Gentle reminders to take breaks
- **Alternative Suggestions**: Recommend offline activities
- **Progress Reports**: Track your digital wellness journey
- **Weekly Charts**: Visualize your usage patterns
- **Notifications**: Get gentle reminders and alerts

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

#### Option 1: Quick Install (Recommended)
1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd scroll-stopping-tool
   ```

2. **Run the installation script**
   ```bash
   python install.py
   ```
   
   This will automatically:
   - Check Python version compatibility
   - Install all required dependencies
   - Optionally create a desktop shortcut

#### Option 2: Manual Install
1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd scroll-stopping-tool
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the installation**
   ```bash
   python test_installation.py
   ```

4. **Run the application**
   ```bash
   python run.py
   ```
   
   Or alternatively:
   ```bash
   python scroll_stopping_tool.py
   ```

### Usage

1. **Start Tracking**: Click "Start Tracking" to begin monitoring your social media usage
2. **Set Limits**: Use the Settings button to configure daily limits and break reminders
3. **Take Breaks**: Click "Take Break" when you want to pause and do something else
4. **View Progress**: Check the statistics and weekly chart to see your usage patterns
5. **Try Alternatives**: Use the alternative activities buttons for suggestions

### Configuration

The application automatically saves your settings and usage data in:
- `settings.json` - Your preferences and limits
- `usage_data.json` - Your usage history and statistics

## How It Works

The tool monitors your system for:
- **Browser processes** (Chrome, Firefox, Safari, Edge)
- **Social media apps** (Instagram, Facebook, Twitter, TikTok)
- **Social media websites** in browser tabs

When social media is detected, it:
- Tracks usage time
- Sends break reminders
- Enforces daily limits
- Provides gentle notifications

## Contributing

We welcome contributions to help improve this tool and make it more effective for users worldwide.

### Development Setup

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application in development mode:
   ```bash
   python scroll_stopping_tool.py
   ```

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Make sure you've installed all dependencies with `pip install -r requirements.txt`

2. **Permission errors**: On some systems, you may need to run with administrator privileges to monitor processes

3. **Notifications not working**: Check your system's notification settings and ensure the application has permission

4. **Tracking not accurate**: The tool monitors common social media processes and websites. Some apps or sites might not be detected

### Platform Support

- **Windows**: Full support
- **macOS**: Full support (may require accessibility permissions)
- **Linux**: Full support

## License

[License information will be added here]

---

**Remember**: The goal isn't to eliminate social media entirely, but to develop a healthier, more intentional relationship with technology.
