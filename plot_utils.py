from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt

def create_habit_progress_plot(habit_tracker, selected_habits, figsize=(12, 6), dpi=100):
    """
    Create a plot showing progress for selected habits.
    Used by both GUI and wallpaper generator.
    """
    # Create figure with dark background
    plt.style.use('dark_background')
    fig = Figure(figsize=figsize, dpi=dpi)
    
    # Set consistent dark background for both figure and plot area
    background_color = '#1E1E1E'
    fig.patch.set_facecolor(background_color)
    
    ax = fig.add_subplot(111)
    ax.set_facecolor(background_color)  # Match the main background
    
    # Adjust figure margins
    fig.tight_layout(pad=3.0)
    
    # Soft, muted colors for habits with good contrast
    colors = [
        '#81A1C1',  # Soft blue
        '#B48EAD',  # Soft purple
        '#A3BE8C',  # Soft green
        '#EBCB8B',  # Soft yellow
        '#D08770',  # Soft orange
        '#88C0D0',  # Light blue
        '#BF616A',  # Soft red
    ]
    
    # Reduced offset for subtle separation
    offset = 0.02
    
    # Find the earliest start date among all habits
    start_date = date.today()
    end_date = date.today()
    
    # Get global start date for x-axis range
    for habit_id in selected_habits:
        habit_tracker.cursor.execute("""
            SELECT MIN(date) FROM habit_logs WHERE habit_id = ?
        """, (habit_id,))
        first_date = habit_tracker.cursor.fetchone()[0]
        if first_date:
            start_date = min(start_date, datetime.strptime(first_date, '%Y-%m-%d').date())
    
    # Plot each habit
    for i, habit_id in enumerate(selected_habits):
        color = colors[i % len(colors)]
        
        # Get habit info
        habit_tracker.cursor.execute("""
            SELECT name, type, target_value, default_value 
            FROM habits WHERE id = ?
        """, (habit_id,))
        habit_name, habit_type, target_value, default_value = habit_tracker.cursor.fetchone()
        
        # Get logs for this habit
        habit_tracker.cursor.execute("""
            SELECT DISTINCT date, value 
            FROM habit_logs 
            WHERE habit_id = ?
            GROUP BY date
            ORDER BY date
        """, (habit_id,))
        logs = dict(habit_tracker.cursor.fetchall())
        
        # Get habit's own start date
        habit_start = None
        if logs:
            habit_start = datetime.strptime(min(logs.keys()), '%Y-%m-%d').date()
        else:
            continue  # Skip habits with no logs
        
        dates = []
        values = []
        current = habit_start  # Start from habit's own start date
        while current <= end_date:
            dates.append(current)
            current_str = current.strftime('%Y-%m-%d')
            values.append(logs.get(current_str, default_value))
            current += timedelta(days=1)
        
        # Plot data with updated styling
        if habit_type == 'boolean':
            ax.step(dates, values, where='mid', 
                   label=f'{habit_name} (Actual)',
                   color=color, 
                   alpha=0.8,
                   linewidth=2.5,
                   marker='o',
                   markersize=5,
                   markerfacecolor=background_color,  # Match background
                   markeredgecolor=color)
            if target_value:
                ax.axhline(y=target_value + (i * offset), 
                          color=color, 
                          linestyle='--', 
                          label=f'{habit_name} (Target)',
                          alpha=0.4,
                          linewidth=1.5)
        else:
            ax.plot(dates, values, 
                   label=f'{habit_name} (Actual)',
                   color=color, 
                   alpha=0.8,
                   linewidth=2.5,
                   marker='o',
                   markersize=5,
                   markerfacecolor=background_color,  # Match background
                   markeredgecolor=color)
            if target_value:
                ax.axhline(y=target_value, 
                          color=color, 
                          linestyle='--', 
                          label=f'{habit_name} (Target)',
                          alpha=0.4,
                          linewidth=1.5)
    
    # Set x-axis range to show all habits
    ax.set_xlim(start_date - timedelta(days=0.5), end_date + timedelta(days=0.5))
    
    # Customize plot with dark mode styling
    ax.set_title('Habit Progress', 
                fontsize=16, 
                pad=20, 
                color='#D8DEE9')  # Light gray text
    ax.set_xlabel('Date', 
                 fontsize=12, 
                 color='#D8DEE9')
    ax.set_ylabel('Value', 
                 fontsize=12, 
                 color='#D8DEE9')
    
    # Grid styling
    ax.grid(True, 
            alpha=0.08,  # Slightly reduced opacity
            color='#D8DEE9', 
            linestyle='-', 
            linewidth=0.5)
    
    # Tick styling
    ax.tick_params(axis='both', 
                  colors='#D8DEE9',  # Light gray text
                  labelsize=10)
    
    # Spine styling
    for spine in ax.spines.values():
        spine.set_color('#404040')  # Darker gray for borders
    
    # Legend styling
    ax.legend(facecolor=background_color,
             edgecolor='#404040',
             labelcolor='#D8DEE9',
             framealpha=0.9)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    
    # Rotate and align the tick labels so they look better
    fig.autofmt_xdate()
    
    # Add padding between plot edge and content
    ax.margins(x=0.02)
    
    # Update the layout to ensure everything fits
    fig.tight_layout(rect=[0.02, 0.02, 0.92, 0.98])
    
    return fig, ax 