import os
import sys
from crontab import CronTab
import getpass

class CronManager:
    def __init__(self):
        self.user = getpass.getuser()
        self.cron = CronTab(user=self.user)
        self.job_comment = 'habit_wallpaper_update'
        
        # Get paths
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_path = os.path.join(self.project_dir, 'update_wallpaper.py')
        self.venv_python = sys.executable
        
        # Make script executable
        os.chmod(self.script_path, 0o755)
    
    def set_update_frequency(self, minutes):
        """Set wallpaper update frequency in minutes"""
        # Remove existing job if any
        self.remove_job()
        
        # Create command that changes directory before running script
        command = f'cd {self.project_dir} && {self.venv_python} {self.script_path}'
        
        job = self.cron.new(command=command,
                           comment=self.job_comment)
        
        # Set environment
        job.env['PYTHONPATH'] = self.project_dir
        
        # Set schedule using proper cron syntax
        if minutes == 1:
            job.setall('* * * * *')  # Every minute
        elif minutes == 60:
            job.setall('0 * * * *')  # Every hour at minute 0
        elif minutes == 720:  # 12 hours
            job.setall('0 */12 * * *')  # Every 12 hours at minute 0
        elif minutes == 1440:  # 24 hours
            job.setall('0 0 * * *')  # Every day at 00:00
        
        self.cron.write()
    
    def remove_job(self):
        """Remove the wallpaper update cron job"""
        self.cron.remove_all(comment=self.job_comment)
        self.cron.write()
    
    def is_job_active(self):
        """Check if wallpaper update job exists"""
        return any(job.comment == self.job_comment for job in self.cron)
    
    def get_current_frequency(self):
        """Get current update frequency in minutes"""
        for job in self.cron:
            if job.comment == self.job_comment:
                # Check if it runs every minute
                if job.slices[0] == '*':  # First slice is minutes
                    return 1
                # Check if it runs every hour
                elif job.slices[0] == '0' and job.slices[1] == '*':
                    return 60
                # Check if it runs every 12 hours
                elif job.slices[0] == '0' and job.slices[1] == '*/12':
                    return 720
                # Check if it runs daily
                elif job.slices[0] == '0' and job.slices[1] == '0':
                    return 1440
        return None 