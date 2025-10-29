from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helpers.auth_helper import AuthHelper
from helpers.progress_helper import ProgressHelper
from database.db_handler import db_handler
from config import Config


def register_command_handlers(app: Client):
    """Register all command handlers"""
    
    @app.on_message(filters.command("start") & filters.private)
    async def start_private(client: Client, message: Message):
        """Handle /start command in private chat"""
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name
        
        # Check if user is admin
        is_admin = AuthHelper.is_admin(user_id)
        
        # Create welcome message
        welcome_text = (
            f"👋 <b>Welcome {username}!</b>\n\n"
            "🎬 <b>Advanced Video Tools Bot</b>\n\n"
            "I'm a professional video processing bot with powerful features:\n\n"
            "✅ Video Merge (video+video, video+audio, video+subs)\n"
            "✅ Video Encoding (1080p, 720p, 480p, 360p with H.264/HEVC)\n"
            "✅ Format Conversion (document ↔ video)\n"
            "✅ Watermark on Videos\n"
            "✅ Video Trimming\n"
            "✅ Sample Video Generation\n"
            "✅ MediaInfo Extraction\n\n"
        )
        
        if is_admin:
            welcome_text += "🔑 <b>Admin Access Granted</b>\nYou can use all features in private chat!\n\n"
        else:
            welcome_text += (
                "⚠️ <b>Note for Regular Users:</b>\n"
                "You can view menus and configure settings here, but tasks can only be performed in authorized groups.\n\n"
                f"📌 To get access, contact: @{Config.OWNER_USERNAME}\n\n"
            )
        
        welcome_text += "💡 <b>Quick Start:</b>\n1. Configure your settings\n2. Select a video tool\n3. Send your video file\n\n👇 Choose an option below:"
        
        # Create keyboard
        keyboard = [
            [InlineKeyboardButton("ℹ️ About", callback_data="menu_about"),
             InlineKeyboardButton("❓ Help", callback_data="menu_help")],
            [InlineKeyboardButton("⚙️ User Settings", callback_data="menu_settings")],
            [InlineKeyboardButton("🎬 Video Tools", callback_data="menu_videotools")],
        ]
        
        await message.reply_text(
            welcome_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @app.on_message(filters.command("start") & filters.group)
    async def start_group(client: Client, message: Message):
        """Handle /start command in group chat"""
        user_id = message.from_user.id
        chat_id = message.chat.id
        username = message.from_user.username or message.from_user.first_name
        
        # Check if group is authorized
        if not AuthHelper.is_authorized_group(chat_id) and not AuthHelper.is_admin(user_id):
            await message.reply_text(
                "⚠️ <b>Unauthorized Group</b>\n\n"
                "This group is not authorized to use this bot.\n\n"
                f"👤 Contact: @{Config.OWNER_USERNAME}\n"
                f"🆔 Owner ID: <code>{Config.OWNER_ID}</code>"
            )
            return
        
        # Activate user
        await AuthHelper.activate_user(user_id, chat_id)
        
        keyboard = [
            [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
             InlineKeyboardButton("🎬 Video Tools", callback_data="menu_videotools")],
            [InlineKeyboardButton("🛑 Stop Bot", callback_data="stop_bot")]
        ]
        
        await message.reply_text(
            f"✅ <b>Bot Activated!</b>\n\n"
            f"Hey {username}, the bot is now active for you in this group.\n\n"
            "You can now:\n"
            "• Configure your settings\n"
            "• Select video tools\n"
            "• Start processing videos\n\n"
            "Use the buttons below to get started:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @app.on_message(filters.command("help"))
    async def help_command(client: Client, message: Message):
        """Handle /help command"""
        help_text = (
            "📖 <b>HOW TO USE THIS BOT</b>\n\n"
            
            "<b>🔹 STEP 1: Configure Settings</b>\n"
            "• Click 'User Settings' button\n"
            "• Set your preferences:\n"
            "  - Send as document/video\n"
            "  - Upload custom thumbnail\n"
            "  - Set custom filename\n"
            "  - Add metadata\n"
            "  - Choose download mode (Telegram/URL)\n"
            "  - Choose upload mode (Telegram/GoFile)\n\n"
            
            "<b>🔹 STEP 2: Select Video Tool</b>\n"
            "• Click 'Video Tools' button\n"
            "• Choose your task:\n"
            "  - Video Merge\n"
            "  - Video Encoding\n"
            "  - Format Conversion\n"
            "  - Add Watermark\n"
            "  - Trim Video\n"
            "  - Sample Video\n"
            "  - MediaInfo\n\n"
            
            "<b>🔹 STEP 3: Send Your File</b>\n"
            "• For Video Merge:\n"
            "  - video+video: Send 2+ videos\n"
            "  - video+audio: Send 1 video + 1 audio\n"
            "  - video+subs: Send 1 video + subtitle file\n\n"
            "• For Encoding:\n"
            "  - Select quality preset or custom settings\n"
            "  - Send 1 video file\n\n"
            "• For other tools:\n"
            "  - Configure settings if needed\n"
            "  - Send your video file\n\n"
            
            "<b>📝 COMMANDS</b>\n"
            "/start - Start the bot\n"
            "/help - Show this help\n"
            "/settings - Open settings menu\n"
            "/s - Show active tasks (in groups)\n\n"
            
            "<b>💡 TIPS</b>\n"
            "• One task at a time per user\n"
            "• Default settings work great!\n"
            "• Use custom settings for advanced options\n"
            "• Files larger than 2GB will upload to GoFile\n\n"
            
            f"Need assistance? Contact @{Config.OWNER_USERNAME}"
        )
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="menu_main")]]
        
        await message.reply_text(
            help_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @app.on_message(filters.command("settings"))
    async def settings_command(client: Client, message: Message):
        """Handle /settings command"""
        user_id = message.from_user.id
        
        # Get user settings
        settings = await db_handler.get_user_settings(user_id)
        
        settings_text = (
            "⚙️ <b>YOUR SETTINGS</b>\n\n"
            f"📄 <b>Send As:</b> {'Document' if settings.send_as_document else 'Video'}\n"
            f"🖼 <b>Thumbnail:</b> {'✅ Set' if settings.thumbnail_file_id else '❌ Not Set'}\n"
            f"📝 <b>Custom Filename:</b> {'✅ Set' if settings.custom_filename else '❌ Not Set'}\n"
            f"📋 <b>Metadata:</b> {'✅ Set' if settings.metadata else '❌ Not Set'}\n"
            f"⬇️ <b>Download Mode:</b> {settings.download_mode.upper()}\n"
            f"⬆️ <b>Upload Mode:</b> {settings.upload_mode.upper()}\n\n"
            "Click a button below to change settings:"
        )
        
        keyboard = [
            [InlineKeyboardButton(
                f"📄 Send as: {'Document' if settings.send_as_document else 'Video'}",
                callback_data="setting_toggle_document"
            )],
            [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="setting_thumbnail")],
            [InlineKeyboardButton("📝 Set Filename", callback_data="setting_filename")],
            [InlineKeyboardButton("📋 Set Metadata", callback_data="setting_metadata")],
            [InlineKeyboardButton(
                f"⬇️ Download: {settings.download_mode.upper()}",
                callback_data="setting_download_mode"
            )],
            [InlineKeyboardButton(
                f"⬆️ Upload: {settings.upload_mode.upper()}",
                callback_data="setting_upload_mode"
            )],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="menu_main")]
        ]
        
        await message.reply_text(
            settings_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @app.on_message(filters.command("s") & filters.group)
    async def show_tasks(client: Client, message: Message):
        """Handle /s command - show active tasks in group"""
        chat_id = message.chat.id
        
        # Get all active tasks for this chat
        tasks = await db_handler.get_all_active_tasks(chat_id)
        
        status_message = ProgressHelper.create_task_status_message(tasks)
        
        await message.reply_text(status_message)
    
    print("✅ Command handlers registered")
