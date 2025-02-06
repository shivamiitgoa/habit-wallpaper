# Habit Wallpaper Tracker

A Python application that tracks daily habits and displays progress by updating your MacBook wallpaper.

## Features
- Track habits with Yes/No responses or numerical values
- Automatically updates MacBook wallpaper daily to show habit progress
- Visual progress tracking through custom wallpaper generation

## Requirements
- macOS
- Python 3.8+
- Required packages (install via `pip install -r requirements.txt`):
  - pandas
  - pillow
  - apscheduler

## Setup
1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Run the application: `python main.py`

## Environment Setup

1. Create and activate virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

2. Set up environment configuration:
```bash
# For production
cp .env.prod .env

# For testing
cp .env.test .env
```

## Environments

The application supports two environments:

### Production Environment
- Uses `habits.db` as the database file
- Preserves data between runs
- Default if no environment is specified

### Test Environment
- Uses `habits_test.db` as the database file
- Resets database on each run
- Useful for testing and development

To switch environments:
1. Copy the appropriate .env file:
   - For production: `cp .env.prod .env`
   - For testing: `cp .env.test .env`
2. Restart the application

## Usage
1. Add habits through the command line interface
2. Track your habits daily
3. The wallpaper will automatically update to show your progress
