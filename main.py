import sqlite3
from datetime import datetime
from habit_tracker import HabitTracker
from wallpaper_generator import WallpaperGenerator
from database import init_db

def main():
    # Initialize database
    init_db()
    
    # Initialize components
    habit_tracker = HabitTracker()
    wallpaper_generator = WallpaperGenerator()
    
    while True:
        print("\n1. Add new habit")
        print("2. Log habit")
        print("3. View progress")
        print("4. Update wallpaper")
        print("5. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == "1":
            habit_tracker.add_habit()
        elif choice == "2":
            habit_tracker.log_habit()
        elif choice == "3":
            habit_tracker.view_progress()
        elif choice == "4":
            wallpaper_generator.update_wallpaper()
        elif choice == "5":
            break

if __name__ == "__main__":
    main() 