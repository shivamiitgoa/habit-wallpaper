import sqlite3
from datetime import datetime, date
from config import DB_NAME

class HabitTracker:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()

    def add_habit(self):
        name = input("Enter habit name: ")
        
        print("\nChoose habit type:")
        print("1. Yes/No (boolean)")
        print("2. Numeric (with value)")
        
        while True:
            type_choice = input("Enter choice (1 or 2): ")
            if type_choice in ['1', '2']:
                habit_type = 'boolean' if type_choice == '1' else 'numeric'
                break
            print("Invalid choice. Please enter 1 or 2.")

        target_value = None
        if habit_type == 'numeric':
            while True:
                try:
                    target_value = float(input("Enter target value (or press enter to skip): ") or 0)
                    break
                except ValueError:
                    print("Please enter a valid number.")

        try:
            self.cursor.execute(
                "INSERT INTO habits (name, type, target_value) VALUES (?, ?, ?)",
                (name, habit_type, target_value)
            )
            self.conn.commit()
            print(f"Successfully added habit: {name}")
        except sqlite3.Error as e:
            print(f"Error adding habit: {e}")

    def log_habit(self):
        # Get all habits
        self.cursor.execute("SELECT id, name, type FROM habits")
        habits = self.cursor.fetchall()
        
        if not habits:
            print("No habits found. Please add a habit first.")
            return

        print("\nAvailable habits:")
        for id, name, type in habits:
            print(f"{id}. {name} ({type})")

        while True:
            try:
                habit_id = int(input("\nEnter habit ID: "))
                habit = next((h for h in habits if h[0] == habit_id), None)
                if habit:
                    break
                print("Invalid habit ID. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

        # Check if already logged today
        today = date.today()
        self.cursor.execute(
            "SELECT * FROM habit_logs WHERE habit_id = ? AND date = ?",
            (habit_id, today)
        )
        if self.cursor.fetchone():
            overwrite = input("Entry already exists for today. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                return

        # Get value based on habit type
        if habit[2] == 'boolean':
            while True:
                response = input("Did you complete this habit today? (y/n): ")
                if response.lower() in ['y', 'n']:
                    value = 1 if response.lower() == 'y' else 0
                    break
                print("Please enter 'y' or 'n'")
        else:
            while True:
                try:
                    value = float(input("Enter value for today: "))
                    break
                except ValueError:
                    print("Please enter a valid number.")

        # Insert or update log
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO habit_logs (habit_id, value, date)
                VALUES (?, ?, ?)
            """, (habit_id, value, today))
            self.conn.commit()
            print("Successfully logged habit!")
        except sqlite3.Error as e:
            print(f"Error logging habit: {e}")

    def view_progress(self):
        self.cursor.execute("""
            SELECT h.name, h.type, hl.date, hl.value 
            FROM habits h
            LEFT JOIN habit_logs hl ON h.id = hl.habit_id
            ORDER BY h.name, hl.date DESC
        """)
        
        results = self.cursor.fetchall()
        if not results:
            print("No habits or logs found.")
            return

        current_habit = None
        for name, type, log_date, value in results:
            if current_habit != name:
                print(f"\n{name} ({type}):")
                current_habit = name
            
            if log_date:
                value_display = "Yes" if value == 1 and type == 'boolean' else "No" if value == 0 and type == 'boolean' else value
                print(f"  {log_date}: {value_display}")

    def delete_habit(self):
        self.cursor.execute("SELECT id, name, type FROM habits")
        habits = self.cursor.fetchall()
        
        if not habits:
            print("No habits found.")
            return

        print("\nAvailable habits:")
        for id, name, type in habits:
            print(f"{id}. {name} ({type})")

        while True:
            try:
                habit_id = int(input("\nEnter habit ID to delete (or 0 to cancel): "))
                if habit_id == 0:
                    return
                habit = next((h for h in habits if h[0] == habit_id), None)
                if habit:
                    break
                print("Invalid habit ID. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

        confirm = input(f"Are you sure you want to delete '{habit[1]}'? (y/n): ")
        if confirm.lower() == 'y':
            try:
                self.cursor.execute("DELETE FROM habit_logs WHERE habit_id = ?", (habit_id,))
                self.cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
                self.conn.commit()
                print("Habit deleted successfully!")
            except sqlite3.Error as e:
                print(f"Error deleting habit: {e}")

    def __del__(self):
        self.conn.close() 