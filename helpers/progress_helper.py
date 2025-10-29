import time
from typing import Optional
from datetime import datetime, timedelta


class ProgressHelper:
    """
    Progress Tracking Helper
    Helps track and format progress for tasks
    """
    
    def __init__(self, task_id: str, total: Optional[float] = None):
        self.task_id = task_id
        self.total = total
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_progress = 0
    
    def update(self, current: float):
        """Update progress"""
        self.current = current
        self.last_update_time = time.time()
    
    def get_progress_percentage(self) -> float:
        """Get progress as percentage"""
        if not self.total or self.total == 0:
            return 0
        return (self.current / self.total) * 100
    
    def get_progress_bar(self, length: int = 20) -> str:
        """Get visual progress bar"""
        percentage = self.get_progress_percentage()
        filled_length = int(length * percentage / 100)
        bar = '█' * filled_length + '░' * (length - filled_length)
        return f"[{bar}] {percentage:.1f}%"
    
    def get_eta(self) -> Optional[str]:
        """Get estimated time remaining"""
        try:
            elapsed_time = time.time() - self.start_time
            if self.current == 0 or not self.total:
                return None
            
            progress = self.current / self.total
            if progress == 0:
                return None
            
            total_estimated_time = elapsed_time / progress
            remaining_time = total_estimated_time - elapsed_time
            
            if remaining_time < 0:
                return "Finishing..."
            
            return self.format_time(remaining_time)
        except:
            return None
    
    def get_speed(self) -> Optional[str]:
        """Get current processing speed"""
        try:
            elapsed = time.time() - self.last_update_time
            if elapsed == 0:
                return None
            
            progress_diff = self.current - self.last_progress
            speed = progress_diff / elapsed
            
            self.last_progress = self.current
            
            if speed < 1:
                return f"{speed*1000:.2f} KB/s"
            else:
                return f"{speed:.2f} MB/s"
        except:
            return None
    
    def get_elapsed_time(self) -> str:
        """Get elapsed time"""
        elapsed = time.time() - self.start_time
        return self.format_time(elapsed)
    
    @staticmethod
    def format_time(seconds: float) -> str:
        """Format time in seconds to readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def get_progress_text(self, include_bar: bool = True) -> str:
        """Get complete progress text"""
        parts = []
        
        if include_bar:
            parts.append(self.get_progress_bar())
        
        percentage = self.get_progress_percentage()
        parts.append(f"{percentage:.1f}%")
        
        eta = self.get_eta()
        if eta:
            parts.append(f"ETA: {eta}")
        
        elapsed = self.get_elapsed_time()
        parts.append(f"Elapsed: {elapsed}")
        
        return " | ".join(parts)
    
    @staticmethod
    def create_task_status_message(tasks: list) -> str:
        """Create a formatted message showing all active tasks"""
        if not tasks:
            return "📭 <b>No active tasks</b>\n\nAll tasks completed!"
        
        message = f"🔄 <b>Active Tasks</b> ({len(tasks)})\n\n"
        
        for idx, task in enumerate(tasks, 1):
            task_type = task.task_type.replace('_', ' ').title()
            user_id = task.user_id
            progress = task.progress or 0
            status = task.status.upper()
            
            # Progress bar
            bar_length = 15
            filled = int(bar_length * progress / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            message += f"<b>#{idx}</b> {task_type}\n"
            message += f"👤 User: <code>{user_id}</code>\n"
            message += f"📊 [{bar}] {progress:.1f}%\n"
            message += f"⏱ Status: {status}\n"
            
            if task.eta:
                message += f"⏰ ETA: {task.eta}\n"
            
            if task.file_name:
                message += f"📄 File: {task.file_name}\n"
            
            message += "\n"
        
        return message
