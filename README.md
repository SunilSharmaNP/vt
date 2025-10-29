# 🎬 Advanced Professional Video Tools Telegram Bot

A powerful and feature-rich Telegram bot for professional video processing with advanced authorization controls.

## ✨ Features

### 🔥 Video Processing Tools

- **Video Merge** - Merge multiple videos or add audio/subtitles
  - Video + Video (merge 2 or more videos)
  - Video + Audio (add audio track)
  - Video + Subtitles (add subtitle file)
  
- **Video Encoding** - Professional encoding with quality presets
  - 1080p, 720p, 480p, 360p presets
  - H.264 and H.265/HEVC codecs
  - Custom encoding settings (CRF, bitrate, preset, etc.)
  
- **Format Conversion** - Convert between document and video
  
- **Video Watermark** - Add custom text watermarks
  
- **Video Trimming** - Cut videos by specific time ranges
  
- **Sample Generation** - Create first/middle/last 30s samples
  
- **MediaInfo** - Extract detailed media information

### 🔐 Authorization System

- **Group-Based Access Control** - Works only in authorized groups
- **Hold/Active Mode** - Users activate bot per-group with /start
- **Admin Privileges** - Admin users can use all features in private chat
- **Owner Contact Display** - Shows owner info for unauthorized access

### ⚙️ User Settings

- Send as Document or Video
- Custom Thumbnail support
- Custom Filename
- Metadata (title, author, artist)
- Download Mode (Telegram/URL)
- Upload Mode (Telegram/GoFile for large files)

### 📊 Advanced Features

- Real-time progress tracking
- Task queue management
- One task per user concurrency control
- Automatic cleanup
- FFmpeg powered processing
- PostgreSQL database for persistence

## 🚀 Setup

### Prerequisites

- Python 3.11+
- FFmpeg
- PostgreSQL database
- Telegram Bot Token
- Telegram API ID and Hash

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd video-tools-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up environment variables**

Required variables:
```env
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
OWNER_ID=your_telegram_user_id
OWNER_USERNAME=your_username
AUTHORIZED_GROUPS=-100123456789,-100987654321
ADMIN_USERS=123456789,987654321
DATABASE_URL=postgresql://user:password@host:port/dbname
```

Optional variables:
```env
LOG_CHANNEL=-100123456789
GOFILE_TOKEN=your_gofile_token_here
MAX_CONCURRENT_TASKS=5
```

5. **Run the bot**
```bash
python bot.py
```

## 📖 Usage

### For Users

1. **In Groups (Regular Users)**
   - Send `/start` in an authorized group to activate the bot
   - Use buttons to configure settings
   - Select a video tool
   - Send your video files
   - Click "Stop Bot" to deactivate

2. **In Private Chat (Admin Only)**
   - Admins can use all features in private chat
   - Regular users can only view menus and settings

### Commands

- `/start` - Activate bot / Show main menu
- `/help` - Show help and usage guide
- `/settings` - Open settings menu
- `/s` - Show active tasks (groups only)

### Authorization Levels

1. **Owner** - Full access everywhere
2. **Admin Users** - Full access in private chat and groups
3. **Regular Users** - Access only in authorized groups after activation

## 🎯 How It Works

### Hold/Active Mode

The bot uses a unique hold/active mode system:

- **Hold Mode** (Default): Bot ignores messages from user
- **Active Mode**: Bot responds to user's commands
- Users activate bot with `/start` command in groups
- Each user has independent active/hold status
- Click "Stop Bot" to return to hold mode

### Task Queue System

- One task per user at a time
- Multiple users can have concurrent tasks
- Real-time progress tracking
- Use `/s` command to see all active tasks in group

## 🛠️ Configuration

### Encoding Presets

The bot includes optimized presets for different quality levels:

- **1080p H.264**: 4M bitrate, CRF 23
- **1080p HEVC**: 3M bitrate, CRF 28
- **720p H.264**: 2.5M bitrate, CRF 23
- **720p HEVC**: 2M bitrate, CRF 28
- **480p H.264**: 1.5M bitrate, CRF 23
- **480p HEVC**: 1M bitrate, CRF 28
- **360p H.264**: 800k bitrate, CRF 23
- **Custom**: Configure all settings manually

### File Upload

- Files under 2GB: Upload to Telegram
- Files over 2GB: Automatic upload to GoFile
- User can choose upload mode in settings

## 📦 Dependencies

- **pyrogram** - Telegram MTProto API client
- **python-telegram-bot** - Telegram Bot API
- **ffmpeg-python** - FFmpeg wrapper
- **asyncpg** - Async PostgreSQL
- **aiohttp** - Async HTTP requests
- **pymediainfo** - Media information extraction
- **yt-dlp** - Video downloads from URLs
- **Pillow** - Image processing

## 🔧 System Requirements

- Linux/Unix system (recommended)
- FFmpeg 4.4 or higher
- Python 3.11+
- Minimum 2GB RAM
- Sufficient storage for temporary files

## 📝 Project Structure

```
├── bot.py                 # Main entry point
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── database/
│   ├── __init__.py
│   ├── db_handler.py    # Database operations
│   └── models.py        # Data models
├── helpers/
│   ├── __init__.py
│   ├── auth_helper.py   # Authentication
│   ├── file_helper.py   # File operations
│   ├── ffmpeg_helper.py # FFmpeg operations
│   ├── mediainfo_helper.py # Media info extraction
│   └── progress_helper.py  # Progress tracking
└── plugins/
    ├── __init__.py
    ├── commands.py      # Command handlers
    └── callbacks.py     # Callback handlers
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 💬 Support

For support or questions, contact the bot owner:
- Username: Configured in `OWNER_USERNAME`
- User ID: Configured in `OWNER_ID`

## 🙏 Acknowledgments

- FFmpeg for powerful video processing
- Pyrogram for excellent Telegram API wrapper
- PostgreSQL for robust database support

---

**Made with ❤️ for professional video processing**
