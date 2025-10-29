import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuration class for the Video Tools Bot
    All settings are loaded from environment variables
    """
    
    # Telegram Bot Configuration
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    
    # Owner Information
    OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "owner")
    
    # Authorized Groups and Admin Users
    AUTHORIZED_GROUPS_STR = os.environ.get("AUTHORIZED_GROUPS", "")
    AUTHORIZED_GROUPS = [int(x.strip()) for x in AUTHORIZED_GROUPS_STR.split(",") if x.strip()]
    
    ADMIN_USERS_STR = os.environ.get("ADMIN_USERS", "")
    ADMIN_USERS = [int(x.strip()) for x in ADMIN_USERS_STR.split(",") if x.strip()]
    
    # Database Configuration
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    
    # Optional Configuration
    LOG_CHANNEL = os.environ.get("LOG_CHANNEL", None)
    if LOG_CHANNEL:
        try:
            LOG_CHANNEL = int(LOG_CHANNEL)
        except:
            LOG_CHANNEL = None
    
    GOFILE_TOKEN = os.environ.get("GOFILE_TOKEN", "")
    
    # Bot Settings
    MAX_CONCURRENT_TASKS = int(os.environ.get("MAX_CONCURRENT_TASKS", "5"))
    DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "downloads")
    UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")
    THUMBNAIL_DIR = os.environ.get("THUMBNAIL_DIR", "thumbnails")
    
    # FFmpeg Encoding Presets
    ENCODING_PRESETS = {
        "1080p": {
            "resolution": "1920x1080",
            "video_bitrate": "4M",
            "audio_bitrate": "192k",
            "crf": "23",
            "preset": "medium",
            "codec": "libx264"
        },
        "1080p_hevc": {
            "resolution": "1920x1080",
            "video_bitrate": "3M",
            "audio_bitrate": "192k",
            "crf": "28",
            "preset": "medium",
            "codec": "libx265"
        },
        "720p": {
            "resolution": "1280x720",
            "video_bitrate": "2.5M",
            "audio_bitrate": "128k",
            "crf": "23",
            "preset": "medium",
            "codec": "libx264"
        },
        "720p_hevc": {
            "resolution": "1280x720",
            "video_bitrate": "2M",
            "audio_bitrate": "128k",
            "crf": "28",
            "preset": "medium",
            "codec": "libx265"
        },
        "480p": {
            "resolution": "854x480",
            "video_bitrate": "1.5M",
            "audio_bitrate": "96k",
            "crf": "23",
            "preset": "medium",
            "codec": "libx264"
        },
        "480p_hevc": {
            "resolution": "854x480",
            "video_bitrate": "1M",
            "audio_bitrate": "96k",
            "crf": "28",
            "preset": "medium",
            "codec": "libx265"
        },
        "360p": {
            "resolution": "640x360",
            "video_bitrate": "800k",
            "audio_bitrate": "64k",
            "crf": "23",
            "preset": "medium",
            "codec": "libx264"
        }
    }
    
    # CRF Quality Settings
    CRF_VALUES = {
        "best": {"h264": "18", "hevc": "23"},
        "high": {"h264": "21", "hevc": "26"},
        "medium": {"h264": "23", "hevc": "28"},
        "low": {"h264": "26", "hevc": "31"},
        "potato": {"h264": "30", "hevc": "35"}
    }
    
    # FFmpeg Presets
    FFMPEG_PRESETS = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"]
    
    # Audio Bitrates
    AUDIO_BITRATES = ["64k", "96k", "128k", "192k", "256k", "320k"]
    
    # Video Codecs
    VIDEO_CODECS = ["libx264", "libx265", "libvpx-vp9"]
    
    # Audio Codecs
    AUDIO_CODECS = ["aac", "libopus", "libmp3lame"]
    
    # Pixel Formats
    PIXEL_FORMATS = ["yuv420p", "yuv422p", "yuv444p"]
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        if not cls.API_ID or cls.API_ID == 0:
            errors.append("API_ID is required")
        if not cls.API_HASH:
            errors.append("API_HASH is required")
        if not cls.OWNER_ID or cls.OWNER_ID == 0:
            errors.append("OWNER_ID is required")
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [cls.DOWNLOAD_DIR, cls.UPLOAD_DIR, cls.THUMBNAIL_DIR, "temp", "logs"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Validate configuration on import
Config.validate()
Config.create_directories()
