#!/usr/bin/env python3
import os
import sys

# Add project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from habit_tracker import HabitTracker
from wallpaper_generator import WallpaperGenerator

def main():
    habit_tracker = HabitTracker()
    wallpaper_generator = WallpaperGenerator(habit_tracker)
    wallpaper_generator.update_wallpaper()

if __name__ == "__main__":
    main() 