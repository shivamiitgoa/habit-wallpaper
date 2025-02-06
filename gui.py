from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QLineEdit, QTableWidget, QTableWidgetItem, 
                            QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime, date
import sys
from habit_tracker import HabitTracker
from wallpaper_generator import WallpaperGenerator

class HabitTrackerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.habit_tracker = HabitTracker()
        self.wallpaper_generator = WallpaperGenerator()
        self.init_ui()
        
        # Set up timer for daily wallpaper update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_wallpaper)
        self.timer.start(3600000)  # Check every hour
        
    def init_ui(self):
        self.setWindowTitle('Habit Tracker')
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton('Add Habit')
        add_button.clicked.connect(self.add_habit)
        
        log_button = QPushButton('Log Habit')
        log_button.clicked.connect(self.log_habit)
        
        update_button = QPushButton('Update Wallpaper')
        update_button.clicked.connect(self.update_wallpaper)
        
        delete_button = QPushButton('Delete Habit')
        delete_button.clicked.connect(self.delete_habit)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(log_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
        # Create table for habits
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Name', 'Type', 'Today\'s Value', 'Target'])
        layout.addWidget(self.table)
        
        self.refresh_table()
        
    def refresh_table(self):
        self.table.setRowCount(0)
        today = date.today()
        
        # Get all habits
        self.habit_tracker.cursor.execute("""
            SELECT h.id, h.name, h.type, h.target_value, hl.value
            FROM habits h
            LEFT JOIN habit_logs hl ON h.id = hl.habit_id 
            AND hl.date = ?
            ORDER BY h.name
        """, (today,))
        
        habits = self.habit_tracker.cursor.fetchall()
        
        self.table.setRowCount(len(habits))
        for row, (id, name, type, target, value) in enumerate(habits):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(type))
            
            value_display = ''
            if value is not None:
                if type == 'boolean':
                    value_display = 'Yes' if value == 1 else 'No'
                else:
                    value_display = str(value)
            self.table.setItem(row, 2, QTableWidgetItem(value_display))
            
            target_display = str(target) if target else ''
            self.table.setItem(row, 3, QTableWidgetItem(target_display))
        
        self.table.resizeColumnsToContents()
        
    def add_habit(self):
        name, ok = QInputDialog.getText(self, 'Add Habit', 'Enter habit name:')
        if ok and name:
            type_dialog = QMessageBox()
            type_dialog.setWindowTitle('Habit Type')
            type_dialog.setText('Choose habit type:')
            type_dialog.addButton('Yes/No', QMessageBox.ButtonRole.AcceptRole)
            type_dialog.addButton('Numeric', QMessageBox.ButtonRole.RejectRole)
            
            if type_dialog.exec() == 0:  # Yes/No selected
                habit_type = 'boolean'
                target_value = None
            else:  # Numeric selected
                habit_type = 'numeric'
                target_value, ok = QInputDialog.getDouble(
                    self, 'Target Value', 
                    'Enter target value (0 for no target):', 
                    0, 0, 10000, 2
                )
                if not ok:
                    return
                
            try:
                self.habit_tracker.cursor.execute(
                    "INSERT INTO habits (name, type, target_value) VALUES (?, ?, ?)",
                    (name, habit_type, target_value)
                )
                self.habit_tracker.conn.commit()
                self.refresh_table()
                QMessageBox.information(self, 'Success', f'Added habit: {name}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error adding habit: {str(e)}')
    
    def log_habit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Warning', 'Please select a habit to log')
            return
            
        habit_name = self.table.item(row, 0).text()
        habit_type = self.table.item(row, 1).text()
        
        self.habit_tracker.cursor.execute(
            "SELECT id FROM habits WHERE name = ?", (habit_name,)
        )
        habit_id = self.habit_tracker.cursor.fetchone()[0]
        
        if habit_type == 'boolean':
            reply = QMessageBox.question(
                self, 'Log Habit', 
                f'Did you complete {habit_name} today?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            value = 1 if reply == QMessageBox.StandardButton.Yes else 0
        else:
            value, ok = QInputDialog.getDouble(
                self, 'Log Habit', 
                f'Enter value for {habit_name}:', 
                0, 0, 10000, 2
            )
            if not ok:
                return
        
        try:
            self.habit_tracker.cursor.execute("""
                INSERT OR REPLACE INTO habit_logs (habit_id, value, date)
                VALUES (?, ?, ?)
            """, (habit_id, value, date.today()))
            self.habit_tracker.conn.commit()
            self.refresh_table()
            QMessageBox.information(self, 'Success', 'Habit logged successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error logging habit: {str(e)}')
    
    def delete_habit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Warning', 'Please select a habit to delete')
            return
            
        habit_name = self.table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, 'Delete Habit', 
            f'Are you sure you want to delete {habit_name}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.habit_tracker.cursor.execute(
                    "DELETE FROM habits WHERE name = ?", (habit_name,)
                )
                self.habit_tracker.conn.commit()
                self.refresh_table()
                QMessageBox.information(self, 'Success', f'Deleted habit: {habit_name}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error deleting habit: {str(e)}')
    
    def update_wallpaper(self):
        try:
            self.wallpaper_generator.update_wallpaper()
            QMessageBox.information(self, 'Success', 'Wallpaper updated successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error updating wallpaper: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = HabitTrackerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 