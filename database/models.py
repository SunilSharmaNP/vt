from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class UserSettings:
    """Model for user settings"""
    user_id: int
    username: Optional[str] = None
    send_as_document: bool = True
    thumbnail_file_id: Optional[str] = None
    custom_filename: Optional[str] = None
    metadata: Optional[Dict[str, str]] = field(default_factory=dict)
    download_mode: str = "telegram"
    upload_mode: str = "telegram"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'send_as_document': self.send_as_document,
            'thumbnail_file_id': self.thumbnail_file_id,
            'custom_filename': self.custom_filename,
            'metadata': self.metadata,
            'download_mode': self.download_mode,
            'upload_mode': self.upload_mode,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


@dataclass
class ActiveUser:
    """Model for tracking active users in groups"""
    user_id: int
    chat_id: int
    is_active: bool = True
    activated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'user_id': self.user_id,
            'chat_id': self.chat_id,
            'is_active': self.is_active,
            'activated_at': self.activated_at
        }


@dataclass
class TaskQueue:
    """Model for task queue management"""
    task_id: str
    user_id: int
    chat_id: int
    task_type: str
    status: str = "pending"
    progress: float = 0.0
    started_at: datetime = field(default_factory=datetime.now)
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    eta: Optional[str] = None
    error: Optional[str] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'task_id': self.task_id,
            'user_id': self.user_id,
            'chat_id': self.chat_id,
            'task_type': self.task_type,
            'status': self.status,
            'progress': self.progress,
            'started_at': self.started_at,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'eta': self.eta,
            'error': self.error,
            'completed_at': self.completed_at
        }


@dataclass
class VideoToolsState:
    """Model for tracking user's video tools state"""
    user_id: int
    chat_id: int
    selected_tool: Optional[str] = None
    merge_mode: Optional[str] = None
    encoding_preset: Optional[str] = None
    encoding_settings: Optional[Dict[str, Any]] = field(default_factory=dict)
    watermark_text: Optional[str] = None
    trim_start: Optional[str] = None
    trim_end: Optional[str] = None
    sample_duration: int = 30
    pending_files: list = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'user_id': self.user_id,
            'chat_id': self.chat_id,
            'selected_tool': self.selected_tool,
            'merge_mode': self.merge_mode,
            'encoding_preset': self.encoding_preset,
            'encoding_settings': self.encoding_settings,
            'watermark_text': self.watermark_text,
            'trim_start': self.trim_start,
            'trim_end': self.trim_end,
            'sample_duration': self.sample_duration,
            'pending_files': self.pending_files,
            'updated_at': self.updated_at
        }
