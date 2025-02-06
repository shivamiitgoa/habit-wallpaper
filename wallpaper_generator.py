import os
from PIL import Image, ImageDraw, ImageFont
import sqlite3
from datetime import datetime, date, timedelta

class WallpaperGenerator:
    def __init__(self):
        self.conn = sqlite3.connect('habits.db')
        self.cursor = self.conn.cursor()
        
        # Create wallpapers directory if it doesn't exist
        if not os.path.exists('wallpapers'):
            os.makedirs('wallpapers')

    def update_wallpaper(self):
        # Create a new image
        width = 2560  # Standard MacBook Pro resolution
        height = 1600
        image = Image.new('RGB', (width, height), color='#1a1a1a')
        draw = ImageDraw.Draw(image)

        # Get all habits
        self.cursor.execute("SELECT id, name, type FROM habits")
        habits = self.cursor.fetchall()

        if not habits:
            print("No habits to display.")
            return

        # Get last 50 days of logs
        end_date = date.today()
        start_date = end_date - timedelta(days=49)  # 49 to include today
        
        y_position = 50  # Start higher to fit more habits
        for habit_id, habit_name, habit_type in habits:
            # Draw habit name
            draw.text((50, y_position), habit_name, fill='white', font=self._get_font(20))
            
            # Get habit logs
            self.cursor.execute("""
                SELECT date, value FROM habit_logs 
                WHERE habit_id = ? AND date BETWEEN ? AND ?
                ORDER BY date
            """, (habit_id, start_date, end_date))
            logs = self.cursor.fetchall()
            
            # Create progress visualization
            self._draw_progress(draw, logs, habit_type, y_position + 30)
            
            y_position += 100  # Reduced spacing between habits

        # Save and set wallpaper
        wallpaper_path = os.path.join('wallpapers', f'habits_{date.today()}.png')
        image.save(wallpaper_path)
        
        os.system(f"osascript -e 'tell application \"Finder\" to set desktop picture to POSIX file \"{os.path.abspath(wallpaper_path)}\"'")
        print("Wallpaper updated successfully!")

    def _get_font(self, size):
        # You might need to adjust this path based on your system
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except:
            return ImageFont.load_default()

    def _draw_progress(self, draw, logs, habit_type, y_position):
        box_width = 40  # Smaller boxes
        box_height = 40
        spacing = 10
        x_start = 50

        # Draw grid of 5 rows with 10 days each
        for row in range(5):
            for col in range(10):
                day_index = row * 10 + col
                x = x_start + (col * (box_width + spacing))
                y = y_position + (row * (box_height + spacing))
                
                # Draw box outline
                draw.rectangle(
                    [x, y, x + box_width, y + box_height],
                    outline='white'
                )
                
                # Find log for this day
                current_date = date.today() - timedelta(days=49-day_index)
                log = next((log for log in logs if log[0] == current_date.strftime('%Y-%m-%d')), None)
                
                if log:
                    if habit_type == 'boolean':
                        if log[1] == 1:
                            draw.rectangle(
                                [x, y, x + box_width, y + box_height],
                                fill='#4CAF50'  # Green for completion
                            )
                    else:
                        # Get target value
                        self.cursor.execute(
                            "SELECT target_value FROM habits WHERE id = ?",
                            (habit_id,)
                        )
                        target = self.cursor.fetchone()[0]
                        
                        # Draw numeric value with color based on target
                        value_text = str(int(log[1]) if log[1].is_integer() else f"{log[1]:.1f}")
                        font = self._get_font(14)
                        
                        # Calculate color based on target (if target exists)
                        if target and target > 0:
                            progress = min(log[1] / target, 1.0)
                            # Color gradient from red to yellow to green
                            if progress < 0.5:
                                # Red to yellow
                                r = 255
                                g = int(255 * (progress * 2))
                                b = 0
                            else:
                                # Yellow to green
                                r = int(255 * (2 - progress * 2))
                                g = 255
                                b = 0
                            fill_color = f"#{r:02x}{g:02x}{b:02x}"
                            
                            # Fill box with color
                            draw.rectangle(
                                [x, y, x + box_width, y + box_height],
                                fill=fill_color
                            )
                        
                        # Center and draw the text
                        text_bbox = draw.textbbox((0, 0), value_text, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]
                        text_x = x + (box_width - text_width) // 2
                        text_y = y + (box_height - text_height) // 2
                        draw.text(
                            (text_x, text_y),
                            value_text,
                            fill='white' if target and target > 0 else 'white',
                            font=font
                        )
                
                # Draw date in smaller font below the box (only for the first row)
                if row == 0:
                    date_text = current_date.strftime('%d')  # Only show day
                    font = self._get_font(10)
                    text_bbox = draw.textbbox((0, 0), date_text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    draw.text(
                        (x + (box_width - text_width) // 2, y - 15),
                        date_text,
                        fill='white',
                        font=font
                    )

    def __del__(self):
        self.conn.close() 