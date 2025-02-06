import os
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime
from plot_utils import create_habit_progress_plot

class WallpaperGenerator:
    def __init__(self, habit_tracker):
        self.habit_tracker = habit_tracker
        self.wallpaper_dir = 'wallpapers'
        os.makedirs(self.wallpaper_dir, exist_ok=True)
        
        # Fixed resolution for wallpaper
        self.width = 3546
        self.height = 2234
        
        # Calculate safe area (60% of height in the middle)
        self.padding_percent = 0.20  # 20% padding top and bottom
        self.safe_height = int(self.height * (1 - 2 * self.padding_percent))  # 60% of height
        
        # Calculate the optimal figure size for wallpaper
        self.dpi = 200
        self.figsize = (self.width/self.dpi, self.height/self.dpi)
    
    def update_wallpaper(self):
        # Get all habits
        self.habit_tracker.cursor.execute("SELECT id FROM habits ORDER BY name")
        habits = self.habit_tracker.cursor.fetchall()
        habit_ids = [h[0] for h in habits]
        
        if not habit_ids:
            return
        
        # Create the plot using shared logic
        fig, ax = create_habit_progress_plot(
            self.habit_tracker,
            habit_ids,
            figsize=self.figsize,
            dpi=self.dpi
        )
        
        # Adjust legend position and size for wallpaper
        ax.legend(bbox_to_anchor=(1.02, 0.5),  # Center legend vertically
                 loc='center left',
                 borderaxespad=0,
                 frameon=True,
                 fancybox=True,
                 shadow=True,
                 fontsize=12)
        
        # Adjust layout to ensure content stays in safe area (middle 60%)
        fig.tight_layout(rect=[0.02,                    # Left padding
                              self.padding_percent,      # Bottom padding (20%)
                              0.92,                      # Right padding for legend (reduced)
                              1 - self.padding_percent]) # Top padding (20%)
        
        # Clean up old wallpapers
        for file in os.listdir(self.wallpaper_dir):
            if file.startswith('wallpaper_') and file.endswith('.png'):
                try:
                    os.remove(os.path.join(self.wallpaper_dir, file))
                except:
                    pass
        
        # Save new wallpaper with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        wallpaper_path = os.path.join(self.wallpaper_dir, f'wallpaper_{timestamp}.png')
        
        # Save with dark background
        fig.patch.set_facecolor('#1E1E1E')
        fig.savefig(wallpaper_path, 
                   dpi=self.dpi,
                   bbox_inches=None,
                   facecolor='#1E1E1E',  # Ensure dark background is saved
                   edgecolor='none',
                   pad_inches=0)
        plt.close(fig)
        
        # Ensure exact resolution with PIL
        img = Image.open(wallpaper_path)
        if img.size != (self.width, self.height):
            img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            # Convert to RGBA to ensure transparency is handled correctly
            img = img.convert('RGBA')
            img.save(wallpaper_path)
        
        # Set wallpaper using system command
        os.system(f"osascript -e 'tell application \"System Events\" to set picture of every desktop to \"{os.path.abspath(wallpaper_path)}\"'") 