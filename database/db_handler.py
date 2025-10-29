import asyncpg
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from config import Config
from .models import UserSettings, ActiveUser, TaskQueue, VideoToolsState


class DatabaseHandler:
    """
    PostgreSQL Database Handler for Video Tools Bot
    Manages all database operations including user settings, task queue, and active users
    """
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def init_pool(self):
        """Initialize the database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                Config.DATABASE_URL,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            await self.create_tables()
            print("✅ Database connection pool initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing database pool: {e}")
            raise
    
    async def close_pool(self):
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()
            print("Database connection pool closed")
    
    async def create_tables(self):
        """Create all necessary database tables"""
        async with self.pool.acquire() as conn:
            # User Settings Table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    send_as_document BOOLEAN DEFAULT TRUE,
                    thumbnail_file_id TEXT,
                    custom_filename TEXT,
                    metadata JSONB DEFAULT '{}',
                    download_mode TEXT DEFAULT 'telegram',
                    upload_mode TEXT DEFAULT 'telegram',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Active Users Table (for hold/active mode tracking)
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS active_users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    chat_id BIGINT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    activated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, chat_id)
                )
            ''')
            
            # Task Queue Table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS task_queue (
                    task_id TEXT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    chat_id BIGINT NOT NULL,
                    task_type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    progress REAL DEFAULT 0.0,
                    started_at TIMESTAMP DEFAULT NOW(),
                    file_name TEXT,
                    file_size BIGINT,
                    eta TEXT,
                    error TEXT,
                    completed_at TIMESTAMP
                )
            ''')
            
            # Video Tools State Table (for tracking user's current tool and settings)
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS video_tools_state (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    chat_id BIGINT NOT NULL,
                    selected_tool TEXT,
                    merge_mode TEXT,
                    encoding_preset TEXT,
                    encoding_settings JSONB DEFAULT '{}',
                    watermark_text TEXT,
                    trim_start TEXT,
                    trim_end TEXT,
                    sample_duration INTEGER DEFAULT 30,
                    pending_files JSONB DEFAULT '[]',
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, chat_id)
                )
            ''')
            
            # Create indexes for better performance
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_active_users_user ON active_users(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_active_users_chat ON active_users(chat_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_task_queue_user ON task_queue(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_task_queue_status ON task_queue(status)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_video_tools_user ON video_tools_state(user_id)')
            
            print("✅ Database tables created successfully")
    
    # ==================== USER SETTINGS OPERATIONS ====================
    
    async def get_user_settings(self, user_id: int) -> UserSettings:
        """Get user settings or create default if not exists"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT * FROM user_settings WHERE user_id = $1', user_id)
            
            if row:
                return UserSettings(
                    user_id=row['user_id'],
                    username=row['username'],
                    send_as_document=row['send_as_document'],
                    thumbnail_file_id=row['thumbnail_file_id'],
                    custom_filename=row['custom_filename'],
                    metadata=row['metadata'] or {},
                    download_mode=row['download_mode'],
                    upload_mode=row['upload_mode'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            else:
                # Create default settings
                default_settings = UserSettings(user_id=user_id)
                await self.save_user_settings(default_settings)
                return default_settings
    
    async def save_user_settings(self, settings: UserSettings):
        """Save or update user settings"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO user_settings 
                (user_id, username, send_as_document, thumbnail_file_id, custom_filename, 
                 metadata, download_mode, upload_mode, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
                ON CONFLICT (user_id) 
                DO UPDATE SET
                    username = $2,
                    send_as_document = $3,
                    thumbnail_file_id = $4,
                    custom_filename = $5,
                    metadata = $6,
                    download_mode = $7,
                    upload_mode = $8,
                    updated_at = NOW()
            ''', settings.user_id, settings.username, settings.send_as_document,
                settings.thumbnail_file_id, settings.custom_filename, 
                json.dumps(settings.metadata), settings.download_mode, settings.upload_mode)
    
    async def update_user_setting(self, user_id: int, key: str, value: Any):
        """Update a specific user setting"""
        settings = await self.get_user_settings(user_id)
        setattr(settings, key, value)
        settings.updated_at = datetime.now()
        await self.save_user_settings(settings)
    
    # ==================== ACTIVE USERS OPERATIONS ====================
    
    async def is_user_active(self, user_id: int, chat_id: int) -> bool:
        """Check if user is in active mode for a specific chat"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT is_active FROM active_users WHERE user_id = $1 AND chat_id = $2',
                user_id, chat_id
            )
            return row['is_active'] if row else False
    
    async def activate_user(self, user_id: int, chat_id: int):
        """Activate user for a specific chat"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO active_users (user_id, chat_id, is_active, activated_at)
                VALUES ($1, $2, TRUE, NOW())
                ON CONFLICT (user_id, chat_id)
                DO UPDATE SET is_active = TRUE, activated_at = NOW()
            ''', user_id, chat_id)
    
    async def deactivate_user(self, user_id: int, chat_id: int):
        """Deactivate user for a specific chat"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE active_users 
                SET is_active = FALSE 
                WHERE user_id = $1 AND chat_id = $2
            ''', user_id, chat_id)
    
    # ==================== TASK QUEUE OPERATIONS ====================
    
    async def add_task(self, task: TaskQueue):
        """Add a new task to the queue"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO task_queue 
                (task_id, user_id, chat_id, task_type, status, progress, file_name, file_size)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ''', task.task_id, task.user_id, task.chat_id, task.task_type, 
                task.status, task.progress, task.file_name, task.file_size)
    
    async def update_task_progress(self, task_id: str, progress: float, eta: Optional[str] = None):
        """Update task progress"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE task_queue 
                SET progress = $1, eta = $2 
                WHERE task_id = $3
            ''', progress, eta, task_id)
    
    async def update_task_status(self, task_id: str, status: str, error: Optional[str] = None):
        """Update task status"""
        async with self.pool.acquire() as conn:
            completed_at = datetime.now() if status in ['completed', 'failed', 'cancelled'] else None
            await conn.execute('''
                UPDATE task_queue 
                SET status = $1, error = $2, completed_at = $3
                WHERE task_id = $4
            ''', status, error, completed_at, task_id)
    
    async def get_user_active_task(self, user_id: int) -> Optional[TaskQueue]:
        """Get user's currently active task"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM task_queue 
                WHERE user_id = $1 AND status IN ('pending', 'processing')
                ORDER BY started_at DESC
                LIMIT 1
            ''', user_id)
            
            if row:
                return TaskQueue(
                    task_id=row['task_id'],
                    user_id=row['user_id'],
                    chat_id=row['chat_id'],
                    task_type=row['task_type'],
                    status=row['status'],
                    progress=row['progress'],
                    started_at=row['started_at'],
                    file_name=row['file_name'],
                    file_size=row['file_size'],
                    eta=row['eta'],
                    error=row['error'],
                    completed_at=row['completed_at']
                )
            return None
    
    async def get_all_active_tasks(self, chat_id: Optional[int] = None) -> List[TaskQueue]:
        """Get all active tasks, optionally filtered by chat"""
        async with self.pool.acquire() as conn:
            if chat_id:
                rows = await conn.fetch('''
                    SELECT * FROM task_queue 
                    WHERE chat_id = $1 AND status IN ('pending', 'processing')
                    ORDER BY started_at ASC
                ''', chat_id)
            else:
                rows = await conn.fetch('''
                    SELECT * FROM task_queue 
                    WHERE status IN ('pending', 'processing')
                    ORDER BY started_at ASC
                ''')
            
            tasks = []
            for row in rows:
                tasks.append(TaskQueue(
                    task_id=row['task_id'],
                    user_id=row['user_id'],
                    chat_id=row['chat_id'],
                    task_type=row['task_type'],
                    status=row['status'],
                    progress=row['progress'],
                    started_at=row['started_at'],
                    file_name=row['file_name'],
                    file_size=row['file_size'],
                    eta=row['eta'],
                    error=row['error'],
                    completed_at=row['completed_at']
                ))
            return tasks
    
    async def remove_task(self, task_id: str):
        """Remove a task from the queue"""
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM task_queue WHERE task_id = $1', task_id)
    
    # ==================== VIDEO TOOLS STATE OPERATIONS ====================
    
    async def get_video_tools_state(self, user_id: int, chat_id: int) -> VideoToolsState:
        """Get video tools state or create default"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM video_tools_state 
                WHERE user_id = $1 AND chat_id = $2
            ''', user_id, chat_id)
            
            if row:
                return VideoToolsState(
                    user_id=row['user_id'],
                    chat_id=row['chat_id'],
                    selected_tool=row['selected_tool'],
                    merge_mode=row['merge_mode'],
                    encoding_preset=row['encoding_preset'],
                    encoding_settings=row['encoding_settings'] or {},
                    watermark_text=row['watermark_text'],
                    trim_start=row['trim_start'],
                    trim_end=row['trim_end'],
                    sample_duration=row['sample_duration'],
                    pending_files=row['pending_files'] or [],
                    updated_at=row['updated_at']
                )
            else:
                return VideoToolsState(user_id=user_id, chat_id=chat_id)
    
    async def save_video_tools_state(self, state: VideoToolsState):
        """Save or update video tools state"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO video_tools_state 
                (user_id, chat_id, selected_tool, merge_mode, encoding_preset, encoding_settings,
                 watermark_text, trim_start, trim_end, sample_duration, pending_files, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
                ON CONFLICT (user_id, chat_id)
                DO UPDATE SET
                    selected_tool = $3,
                    merge_mode = $4,
                    encoding_preset = $5,
                    encoding_settings = $6,
                    watermark_text = $7,
                    trim_start = $8,
                    trim_end = $9,
                    sample_duration = $10,
                    pending_files = $11,
                    updated_at = NOW()
            ''', state.user_id, state.chat_id, state.selected_tool, state.merge_mode,
                state.encoding_preset, json.dumps(state.encoding_settings), state.watermark_text,
                state.trim_start, state.trim_end, state.sample_duration, json.dumps(state.pending_files))
    
    async def clear_video_tools_state(self, user_id: int, chat_id: int):
        """Clear video tools state for a user"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM video_tools_state 
                WHERE user_id = $1 AND chat_id = $2
            ''', user_id, chat_id)


# Global database handler instance
db_handler = DatabaseHandler()
