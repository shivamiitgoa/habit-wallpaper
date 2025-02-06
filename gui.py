from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QLineEdit, QTableWidget, QTableWidgetItem, 
                            QMessageBox, QInputDialog, QTabWidget, QCheckBox,
                            QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
from datetime import datetime, date, timedelta
import sys
from habit_tracker import HabitTracker
from wallpaper_generator import WallpaperGenerator
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from plot_utils import create_habit_progress_plot

class HabitTrackerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.habit_tracker = HabitTracker()
        self.wallpaper_generator = WallpaperGenerator(self.habit_tracker)
        
        # Initialize checkbox_layout
        self.checkbox_layout = None
        self.progress_layout = None
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Habit Tracker')
        self.setGeometry(100, 100, 1000, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create and add tabs
        habits_tab = self.create_habits_tab()
        progress_tab = self.create_progress_tab()
        
        tab_widget.addTab(habits_tab, "Habits")
        tab_widget.addTab(progress_tab, "Progress View")
        
        layout.addWidget(tab_widget)
    
    def create_habits_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton('Add Habit')
        add_button.clicked.connect(self.add_habit)
        
        update_button = QPushButton('Update Wallpaper')
        update_button.clicked.connect(self.update_wallpaper)
        
        delete_button = QPushButton('Delete Selected Habit')
        delete_button.clicked.connect(self.delete_habit)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
        # Create table for habits
        self.table = QTableWidget()
        # Name, Type, Target, Default Value, and 7 days
        self.table.setColumnCount(11)  # Increased by 1 for Default Value
        
        # Set headers
        headers = ['Name', 'Type', 'Target', 'Default']  # Added Default
        today = date.today()
        for i in range(7):
            day = today - timedelta(days=6-i)
            headers.append(day.strftime('%Y-%m-%d'))
        
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)
        
        # Add label for instructions
        instructions = QLabel("Select a habit from the table to delete it. Use dropdowns to log boolean habits.")
        instructions.setStyleSheet("color: gray;")
        layout.addWidget(instructions)
        
        tab.setLayout(layout)
        self.refresh_table()
        return tab
    
    def create_progress_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Create habit selection area
        selection_widget = QWidget()
        selection_layout = QHBoxLayout()  # Changed to horizontal layout
        
        # Add "Select All" and "Deselect All" buttons
        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Deselect All")
        select_all_btn.clicked.connect(self.select_all_habits)
        deselect_all_btn.clicked.connect(self.deselect_all_habits)
        
        selection_layout.addWidget(select_all_btn)
        selection_layout.addWidget(deselect_all_btn)
        selection_widget.setLayout(selection_layout)
        layout.addWidget(selection_widget)
        
        # Create scrollable area for habit checkboxes
        checkbox_widget = QWidget()
        self.checkbox_layout = QHBoxLayout()  # Changed to horizontal layout
        checkbox_widget.setLayout(self.checkbox_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(checkbox_widget)
        scroll.setMaximumHeight(100)  # Limit height of checkbox area
        layout.addWidget(scroll)
        
        # Create progress view area
        self.progress_view = QWidget()
        self.progress_layout = QVBoxLayout()
        self.progress_view.setLayout(self.progress_layout)
        
        # Add progress view to a scroll area
        progress_scroll = QScrollArea()
        progress_scroll.setWidgetResizable(True)
        progress_scroll.setWidget(self.progress_view)
        layout.addWidget(progress_scroll)
        
        tab.setLayout(layout)
        self.refresh_habit_checkboxes()
        self.refresh_progress_view()
        return tab
    
    def select_all_habits(self):
        # Temporarily disconnect all checkbox signals
        for i in range(self.checkbox_layout.count()):
            checkbox = self.checkbox_layout.itemAt(i).widget()
            checkbox.stateChanged.disconnect()
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.refresh_progress_view)
        
        # Refresh progress view once after all changes
        self.refresh_progress_view()

    def deselect_all_habits(self):
        # Temporarily disconnect all checkbox signals
        for i in range(self.checkbox_layout.count()):
            checkbox = self.checkbox_layout.itemAt(i).widget()
            checkbox.stateChanged.disconnect()
            checkbox.setChecked(False)
            checkbox.stateChanged.connect(self.refresh_progress_view)
        
        # Refresh progress view once after all changes
        self.refresh_progress_view()

    def refresh_habit_checkboxes(self):
        # Clear existing checkboxes
        for i in reversed(range(self.checkbox_layout.count())):
            self.checkbox_layout.itemAt(i).widget().setParent(None)
        
        # Add checkboxes for each habit
        self.habit_tracker.cursor.execute("SELECT id, name FROM habits ORDER BY name")
        habits = self.habit_tracker.cursor.fetchall()
        
        for habit_id, name in habits:
            checkbox = QCheckBox(name)
            checkbox.setObjectName(str(habit_id))
            checkbox.stateChanged.connect(self.refresh_progress_view)
            checkbox.setChecked(True)  # Set checked by default
            self.checkbox_layout.addWidget(checkbox)
        
        # Force a refresh of the progress view after all checkboxes are created
        if habits:  # Only refresh if there are habits
            self.refresh_progress_view()

    def create_habit_plot(self, habit_id, habit_name, habit_type, target_value):
        # Create figure
        fig = Figure(figsize=(8, 3))
        ax = fig.add_subplot(111)
        
        # Get habit's default value
        self.habit_tracker.cursor.execute("""
            SELECT default_value FROM habits WHERE id = ?
        """, (habit_id,))
        default_value = self.habit_tracker.cursor.fetchone()[0]
        
        # Get all logs for this habit
        self.habit_tracker.cursor.execute("""
            SELECT DISTINCT date, value 
            FROM habit_logs 
            WHERE habit_id = ?
            GROUP BY date
            ORDER BY date
        """, (habit_id,))
        logs = dict(self.habit_tracker.cursor.fetchall())
        
        if not logs:
            # If no logs exist, start from today
            start_date = date.today()
        else:
            # Start from the earliest log
            start_date = datetime.strptime(min(logs.keys()), '%Y-%m-%d').date()
        
        end_date = date.today()
        dates = []
        values = []
        
        # Generate data points for each day from start to today
        current = start_date
        while current <= end_date:
            dates.append(current)
            current_str = current.strftime('%Y-%m-%d')
            values.append(logs.get(current_str, default_value))  # Use default value if no log exists
            current += timedelta(days=1)
        
        # Plot data
        if habit_type == 'boolean':
            ax.step(dates, values, where='mid', label='Actual', color='blue')
            if target_value:
                ax.axhline(y=target_value, color='green', linestyle='--', label='Target')
        else:
            ax.plot(dates, values, label='Actual', color='blue')
            if target_value:
                ax.axhline(y=target_value, color='green', linestyle='--', label='Target')
        
        # Customize plot
        ax.set_title(habit_name)
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.grid(True)
        ax.legend()
        
        # Format x-axis with no duplicate dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        fig.autofmt_xdate()
        
        # Create canvas
        canvas = FigureCanvas(fig)
        return canvas

    def create_combined_plot(self, selected_habits):
        fig, ax = create_habit_progress_plot(self.habit_tracker, selected_habits)
        
        # Add GUI-specific adjustments with reduced right margin
        ax.legend(bbox_to_anchor=(1.02, 1),
                 loc='upper left',
                 borderaxespad=0,
                 frameon=True,
                 fancybox=True,
                 shadow=True)
        
        # Reduce right margin from 0.85 to 0.92
        fig.tight_layout(rect=[0, 0, 0.92, 1])
        
        return FigureCanvas(fig)

    def refresh_progress_view(self):
        # Clear existing progress views
        for i in reversed(range(self.progress_layout.count())):
            item = self.progress_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
            else:
                self.progress_layout.removeItem(item)
        
        # Get selected habits
        selected_habits = []
        for i in range(self.checkbox_layout.count()):
            checkbox = self.checkbox_layout.itemAt(i).widget()
            if checkbox.isChecked():
                selected_habits.append(int(checkbox.objectName()))
        
        if not selected_habits:
            no_selection_label = QLabel("No habits selected")
            no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.progress_layout.addWidget(no_selection_label)
            return
        
        # Create and add combined plot
        plot = self.create_combined_plot(selected_habits)
        if plot:
            self.progress_layout.addWidget(plot)
        
        self.progress_layout.addStretch()

    def refresh_table(self):
        self.table.setRowCount(0)
        today = date.today()
        
        # Get all habits
        self.habit_tracker.cursor.execute("""
            SELECT id, name, type, target_value, default_value
            FROM habits
            ORDER BY name
        """)
        
        habits = self.habit_tracker.cursor.fetchall()
        
        self.table.setRowCount(len(habits))
        for row, (habit_id, name, habit_type, target, default_value) in enumerate(habits):
            # Set Name
            self.table.setItem(row, 0, QTableWidgetItem(name))
            
            # Set Type
            self.table.setItem(row, 1, QTableWidgetItem(habit_type))
            
            # Set Target - Modified to show 'Yes' for boolean habits
            if habit_type == 'boolean':
                target_display = 'Yes'  # Boolean habits always target 'Yes'
            else:
                target_display = str(target) if target else ''
            self.table.setItem(row, 2, QTableWidgetItem(target_display))
            
            # Set Default Value - Show 'Yes'/'No' for boolean habits
            if habit_type == 'boolean':
                default_display = 'Yes' if default_value == 1 else 'No'
            else:
                default_display = str(default_value)
            self.table.setItem(row, 3, QTableWidgetItem(default_display))
            
            # Get last 7 days of logs
            for i in range(7):
                col = i + 4  # offset for Name, Type, Target, and Default columns
                current_date = today - timedelta(days=6-i)
                
                self.habit_tracker.cursor.execute("""
                    SELECT value FROM habit_logs 
                    WHERE habit_id = ? AND date = ?
                """, (habit_id, current_date))
                
                log = self.habit_tracker.cursor.fetchone()
                value = log[0] if log else default_value  # Use default value if no log exists
                
                if habit_type == 'boolean':
                    # Create combobox for boolean habits
                    combo = QComboBox()
                    combo.addItems(['Yes', 'No'])
                    combo.setProperty('habit_id', habit_id)
                    combo.setProperty('date', current_date.strftime('%Y-%m-%d'))
                    
                    combo.setCurrentText('Yes' if value == 1 else 'No')
                    
                    combo.currentTextChanged.connect(self.on_boolean_value_changed)
                    self.table.setCellWidget(row, col, combo)
                else:
                    # For numeric habits, just show the value
                    value_display = str(value) if value is not None else ''
                    self.table.setItem(row, col, QTableWidgetItem(value_display))
        
        self.table.resizeColumnsToContents()
        
        # Only refresh checkboxes if they exist
        if self.checkbox_layout is not None:
            self.refresh_habit_checkboxes()

    def on_boolean_value_changed(self, text):
        combo = self.sender()
        habit_id = combo.property('habit_id')
        date_str = combo.property('date')
        
        value = 1 if text == 'Yes' else 0
        
        try:
            # First try to update existing record
            self.habit_tracker.cursor.execute("""
                UPDATE habit_logs 
                SET value = ? 
                WHERE habit_id = ? AND date = ?
            """, (value, habit_id, date_str))
            
            # If no record was updated (cursor.rowcount == 0), insert new record
            if self.habit_tracker.cursor.rowcount == 0:
                self.habit_tracker.cursor.execute("""
                    INSERT INTO habit_logs (habit_id, value, date)
                    VALUES (?, ?, ?)
                """, (habit_id, value, date_str))
            
            self.habit_tracker.conn.commit()
            
            # Only refresh the progress view
            self.refresh_progress_view()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Error', f'Error saving habit log: {str(e)}')

    def add_habit(self):
        name, ok = QInputDialog.getText(self, 'Add Habit', 'Enter habit name:')
        if ok and name:
            type_dialog = QMessageBox()
            type_dialog.setWindowTitle('Habit Type')
            type_dialog.setText('Choose habit type:')
            yes_no_button = type_dialog.addButton('Yes/No', QMessageBox.ButtonRole.AcceptRole)
            numeric_button = type_dialog.addButton('Numeric', QMessageBox.ButtonRole.RejectRole)
            
            type_dialog.exec()
            clicked_button = type_dialog.clickedButton()
            
            if clicked_button == yes_no_button:  # Yes/No selected
                habit_type = 'boolean'
                target_value = 1  # Yes is always the target for boolean habits
                
                # Get default value for boolean
                default_dialog = QMessageBox()
                default_dialog.setWindowTitle('Default Value')
                default_dialog.setText('Choose default value:')
                yes_button = default_dialog.addButton('Yes', QMessageBox.ButtonRole.YesRole)
                no_button = default_dialog.addButton('No', QMessageBox.ButtonRole.NoRole)
                
                default_dialog.exec()
                default_value = 1 if default_dialog.clickedButton() == yes_button else 0
                
            else:  # Numeric selected
                habit_type = 'numeric'
                target_value, ok = QInputDialog.getDouble(
                    self, 'Target Value', 
                    'Enter target value:', 
                    0, 0, 10000, 2
                )
                if not ok:
                    return
                
                default_value, ok = QInputDialog.getDouble(
                    self, 'Default Value', 
                    'Enter default value:', 
                    0, 0, 10000, 2
                )
                if not ok:
                    return
            
            try:
                self.habit_tracker.cursor.execute(
                    "INSERT INTO habits (name, type, target_value, default_value) VALUES (?, ?, ?, ?)",
                    (name, habit_type, target_value, default_value)
                )
                self.habit_tracker.conn.commit()
                self.refresh_table()
                QMessageBox.information(self, 'Success', f'Added habit: {name}')
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error adding habit: {str(e)}')
    
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
            # Don't show success message for automatic updates
            if self.sender() and isinstance(self.sender(), QPushButton):
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