from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, date, timedelta

def create_habit_progress_plot(habit_tracker, selected_habits, figsize=(12, 6), dpi=100):
    """
    Create a plot showing progress for selected habits.
    Used by both GUI and wallpaper generator.
    """
    # Create figure with specified size
    fig = Figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)
    
    # Colors for different habits with better contrast
    colors = ['#1f77b4', '#d62728', '#2ca02c', '#9467bd', '#ff7f0e', '#8c564b', '#e377c2']
    
    # Reduced offset for subtle separation
    offset = 0.02
    
    # Find the earliest start date among all habits
    start_date = date.today()
    end_date = date.today()
    
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
        
        # Get logs
        habit_tracker.cursor.execute("""
            SELECT DISTINCT date, value 
            FROM habit_logs 
            WHERE habit_id = ?
            GROUP BY date
            ORDER BY date
        """, (habit_id,))
        logs = dict(habit_tracker.cursor.fetchall())
        
        dates = []
        values = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current_str = current.strftime('%Y-%m-%d')
            value = logs.get(current_str, default_value)
            if habit_type == 'boolean':
                values.append(value + (i * offset))
            else:
                values.append(value)
            current += timedelta(days=1)
        
        # Plot data
        if habit_type == 'boolean':
            ax.step(dates, values, where='mid', 
                   label=f'{habit_name} (Actual)',
                   color=color, 
                   alpha=0.7,
                   linewidth=3,
                   marker='o',
                   markersize=6,
                   markerfacecolor='white')
            if target_value:
                ax.axhline(y=target_value + (i * offset), 
                          color=color, 
                          linestyle='--', 
                          label=f'{habit_name} (Target)',
                          alpha=0.5,
                          linewidth=2)
        else:
            ax.plot(dates, values, 
                   label=f'{habit_name} (Actual)',
                   color=color, 
                   alpha=0.7,
                   linewidth=3,
                   marker='o',
                   markersize=6,
                   markerfacecolor='white')
            if target_value:
                ax.axhline(y=target_value, 
                          color=color, 
                          linestyle='--', 
                          label=f'{habit_name} (Target)',
                          alpha=0.5,
                          linewidth=2)
    
    # Customize plot
    ax.set_title('Habit Progress', fontsize=16, pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.grid(True, alpha=0.2)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    fig.autofmt_xdate()
    
    return fig, ax 