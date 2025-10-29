from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from helpers.auth_helper import AuthHelper
from database.db_handler import db_handler
from config import Config


def register_callback_handlers(app: Client):
    """Register all callback query handlers"""
    
    @app.on_callback_query(filters.regex("^menu_"))
    async def handle_menu_callbacks(client: Client, callback_query: CallbackQuery):
        """Handle menu navigation callbacks"""
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        if data == "menu_main":
            # Main menu
            keyboard = [
                [InlineKeyboardButton("ℹ️ About", callback_data="menu_about"),
                 InlineKeyboardButton("❓ Help", callback_data="menu_help")],
                [InlineKeyboardButton("⚙️ User Settings", callback_data="menu_settings")],
                [InlineKeyboardButton("🎬 Video Tools", callback_data="menu_videotools")],
            ]
            
            await callback_query.edit_message_text(
                "🏠 <b>Main Menu</b>\n\n"
                "Choose an option below:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "menu_about":
            # About section
            about_text = (
                "ℹ️ <b>ABOUT THIS BOT</b>\n\n"
                "🎬 <b>Advanced Professional Video Tools Bot</b>\n\n"
                
                "<b>✨ FEATURES:</b>\n\n"
                
                "<b>1️⃣ Video Merge</b>\n"
                "  • Merge multiple videos into one\n"
                "  • Add audio tracks to videos\n"
                "  • Add subtitle files to videos\n"
                "  • Preserve all streams\n\n"
                
                "<b>2️⃣ Video Encoding</b>\n"
                "  • Quality presets: 1080p, 720p, 480p, 360p\n"
                "  • H.264 and H.265/HEVC codecs\n"
                "  • Custom encoding settings\n"
                "  • CRF quality control\n"
                "  • Multiple audio codecs\n\n"
                
                "<b>3️⃣ Format Conversion</b>\n"
                "  • Document to Video\n"
                "  • Video to Document\n\n"
                
                "<b>4️⃣ Video Watermark</b>\n"
                "  • Add custom text watermark\n"
                "  • Multiple position options\n"
                "  • Adjustable font size\n\n"
                
                "<b>5️⃣ Video Trimming</b>\n"
                "  • Trim video by time\n"
                "  • Specify start and end time\n"
                "  • HH:MM:SS format\n\n"
                
                "<b>6️⃣ Sample Video</b>\n"
                "  • Generate first 30s sample\n"
                "  • Generate middle 30s sample\n"
                "  • Generate last 30s sample\n"
                "  • Custom duration support\n\n"
                
                "<b>7️⃣ MediaInfo</b>\n"
                "  • Detailed media information\n"
                "  • Codec details\n"
                "  • Audio/Video streams info\n"
                "  • Subtitle tracks info\n\n"
                
                "<b>🔐 AUTHORIZATION:</b>\n"
                "  • Works in authorized groups only\n"
                "  • Admin users have full access\n"
                "  • Hold/Active mode system\n\n"
                
                "<b>⚡ PERFORMANCE:</b>\n"
                "  • FFmpeg powered processing\n"
                "  • Real-time progress tracking\n"
                "  • Queue management system\n"
                "  • GoFile upload for large files\n\n"
                
                f"👤 <b>Owner:</b> @{Config.OWNER_USERNAME}\n"
                f"🆔 <b>Owner ID:</b> <code>{Config.OWNER_ID}</code>"
            )
            
            keyboard = [[InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]]
            
            await callback_query.edit_message_text(
                about_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "menu_help":
            # Help section
            help_text = (
                "❓ <b>HELP & GUIDE</b>\n\n"
                
                "<b>📋 HOW TO USE:</b>\n\n"
                
                "<b>Step 1: Configure Your Settings</b>\n"
                "Click 'User Settings' and configure:\n"
                "  • Send as document or video\n"
                "  • Upload thumbnail (optional)\n"
                "  • Set custom filename (optional)\n"
                "  • Add metadata (optional)\n"
                "  • Choose download mode\n"
                "  • Choose upload mode\n\n"
                
                "<b>Step 2: Select Video Tool</b>\n"
                "Click 'Video Tools' and choose:\n"
                "  • What operation you want to perform\n"
                "  • Configure tool-specific settings\n\n"
                
                "<b>Step 3: Send Your Files</b>\n"
                "Send the required files based on selected tool:\n"
                "  • Video Merge: Send 2+ videos (or video+audio, video+subs)\n"
                "  • Encoding: Send 1 video\n"
                "  • Other tools: Send 1 video\n\n"
                
                "<b>🔔 IMPORTANT NOTES:</b>\n"
                "  ✓ One task at a time per user\n"
                "  ✓ Bot works in authorized groups only\n"
                "  ✓ Use /start to activate bot in groups\n"
                "  ✓ Use 'Stop Bot' to deactivate\n"
                "  ✓ Files >2GB upload to GoFile\n"
                "  ✓ Default settings work great!\n\n"
                
                "<b>📝 COMMANDS:</b>\n"
                "/start - Activate bot / Show main menu\n"
                "/help - Show this help message\n"
                "/settings - Open settings menu\n"
                "/s - Show active tasks (groups only)\n\n"
                
                f"Need help? Contact @{Config.OWNER_USERNAME}"
            )
            
            keyboard = [[InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]]
            
            await callback_query.edit_message_text(
                help_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "menu_settings":
            # User settings menu
            settings = await db_handler.get_user_settings(user_id)
            
            settings_text = (
                "⚙️ <b>USER SETTINGS</b>\n\n"
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
                    f"📄 {'Document' if settings.send_as_document else 'Video'}",
                    callback_data="setting_toggle_document"
                )],
                [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="setting_thumbnail")],
                [InlineKeyboardButton("📝 Set Filename", callback_data="setting_filename")],
                [InlineKeyboardButton("📋 Set Metadata", callback_data="setting_metadata")],
                [InlineKeyboardButton(
                    f"⬇️ Download: {settings.download_mode}",
                    callback_data="setting_download_mode"
                )],
                [InlineKeyboardButton(
                    f"⬆️ Upload: {settings.upload_mode}",
                    callback_data="setting_upload_mode"
                )],
                [InlineKeyboardButton("« Back", callback_data="menu_main")]
            ]
            
            await callback_query.edit_message_text(
                settings_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "menu_videotools":
            # Video tools menu
            tools_text = (
                "🎬 <b>VIDEO TOOLS</b>\n\n"
                "Select a tool to use:\n\n"
                "🔗 <b>Video Merge:</b> Merge videos or add audio/subs\n"
                "🎥 <b>Video Encoding:</b> Encode with quality presets\n"
                "🔄 <b>Convert Format:</b> Document ↔ Video\n"
                "💧 <b>Watermark:</b> Add text watermark\n"
                "✂️ <b>Trim Video:</b> Cut video by time\n"
                "📹 <b>Sample Video:</b> Generate short samples\n"
                "📊 <b>MediaInfo:</b> Extract detailed info\n\n"
                "👇 Choose a tool:"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔗 Video Merge", callback_data="tool_merge")],
                [InlineKeyboardButton("🎥 Video Encoding", callback_data="tool_encoding")],
                [InlineKeyboardButton("🔄 Convert Format", callback_data="tool_convert")],
                [InlineKeyboardButton("💧 Watermark", callback_data="tool_watermark")],
                [InlineKeyboardButton("✂️ Trim Video", callback_data="tool_trim")],
                [InlineKeyboardButton("📹 Sample Video", callback_data="tool_sample")],
                [InlineKeyboardButton("📊 MediaInfo", callback_data="tool_mediainfo")],
                [InlineKeyboardButton("« Back", callback_data="menu_main")]
            ]
            
            await callback_query.edit_message_text(
                tools_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        await callback_query.answer()
    
    @app.on_callback_query(filters.regex("^tool_"))
    async def handle_tool_callbacks(client: Client, callback_query: CallbackQuery):
        """Handle video tool selection callbacks"""
        data = callback_query.data
        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id
        
        # Get video tools state
        state = await db_handler.get_video_tools_state(user_id, chat_id)
        
        if data == "tool_merge":
            # Video merge submenu
            state.selected_tool = "merge"
            await db_handler.save_video_tools_state(state)
            
            keyboard = [
                [InlineKeyboardButton("📹+📹 Video + Video", callback_data="merge_video_video")],
                [InlineKeyboardButton("📹+🔊 Video + Audio", callback_data="merge_video_audio")],
                [InlineKeyboardButton("📹+💬 Video + Subtitles", callback_data="merge_video_subs")],
                [InlineKeyboardButton("« Back", callback_data="menu_videotools")]
            ]
            
            await callback_query.edit_message_text(
                "🔗 <b>VIDEO MERGE</b>\n\n"
                "Select merge mode:\n\n"
                "📹+📹 <b>Video + Video:</b> Merge 2 or more videos\n"
                "📹+🔊 <b>Video + Audio:</b> Add audio track to video\n"
                "📹+💬 <b>Video + Subs:</b> Add subtitles to video\n\n"
                "Choose a mode:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "tool_encoding":
            # Video encoding quality presets
            state.selected_tool = "encoding"
            await db_handler.save_video_tools_state(state)
            
            keyboard = [
                [InlineKeyboardButton("1080p H.264", callback_data="encode_1080p")],
                [InlineKeyboardButton("1080p HEVC", callback_data="encode_1080p_hevc")],
                [InlineKeyboardButton("720p H.264", callback_data="encode_720p")],
                [InlineKeyboardButton("720p HEVC", callback_data="encode_720p_hevc")],
                [InlineKeyboardButton("480p H.264", callback_data="encode_480p")],
                [InlineKeyboardButton("480p HEVC", callback_data="encode_480p_hevc")],
                [InlineKeyboardButton("360p H.264", callback_data="encode_360p")],
                [InlineKeyboardButton("⚙️ Custom Quality", callback_data="encode_custom")],
                [InlineKeyboardButton("« Back", callback_data="menu_videotools")]
            ]
            
            await callback_query.edit_message_text(
                "🎥 <b>VIDEO ENCODING</b>\n\n"
                "Select encoding quality:\n\n"
                "Choose a preset or use custom settings:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data in ["tool_convert", "tool_watermark", "tool_trim", "tool_sample", "tool_mediainfo"]:
            # Simple tools - just set the tool and wait for file
            tool_names = {
                "tool_convert": "convert",
                "tool_watermark": "watermark",
                "tool_trim": "trim",
                "tool_sample": "sample",
                "tool_mediainfo": "mediainfo"
            }
            
            tool_messages = {
                "convert": "🔄 <b>FORMAT CONVERSION</b>\n\nSend a video file to convert between document and video format.",
                "watermark": "💧 <b>ADD WATERMARK</b>\n\nFirst, send me the watermark text you want to add to the video.\nExample: 'My Watermark'",
                "trim": "✂️ <b>TRIM VIDEO</b>\n\nSend me the start and end time in format:\nHH:MM:SS-HH:MM:SS\n\nExample: 00:00:10-00:05:30",
                "sample": "📹 <b>SAMPLE VIDEO</b>\n\nSend a video file and I'll generate samples.\nYou can choose: First 30s, Middle 30s, or Last 30s",
                "mediainfo": "📊 <b>MEDIAINFO</b>\n\nSend a video file and I'll extract detailed media information."
            }
            
            state.selected_tool = tool_names[data]
            await db_handler.save_video_tools_state(state)
            
            keyboard = [[InlineKeyboardButton("« Back", callback_data="menu_videotools")]]
            
            await callback_query.edit_message_text(
                tool_messages[tool_names[data]],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        await callback_query.answer()
    
    @app.on_callback_query(filters.regex("^stop_bot$"))
    async def stop_bot_callback(client: Client, callback_query: CallbackQuery):
        """Handle stop bot callback"""
        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id
        
        await AuthHelper.deactivate_user(user_id, chat_id)
        
        await callback_query.answer("Bot deactivated for you in this chat", show_alert=True)
        await callback_query.message.delete()
    
    @app.on_callback_query(filters.regex("^setting_"))
    async def handle_setting_callbacks(client: Client, callback_query: CallbackQuery):
        """Handle user setting callbacks"""
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        settings = await db_handler.get_user_settings(user_id)
        
        if data == "setting_toggle_document":
            settings.send_as_document = not settings.send_as_document
            await db_handler.save_user_settings(settings)
            await callback_query.answer(
                f"Changed to: {'Document' if settings.send_as_document else 'Video'}",
                show_alert=False
            )
            
            # Refresh settings menu
            await callback_query.message.edit_reply_markup(
                reply_markup=callback_query.message.reply_markup
            )
        
        elif data == "setting_thumbnail":
            await callback_query.answer(
                "Send me a photo to set as thumbnail",
                show_alert=True
            )
        
        elif data == "setting_filename":
            await callback_query.answer(
                "Send me the custom filename you want to use",
                show_alert=True
            )
        
        elif data == "setting_metadata":
            await callback_query.answer(
                "Send metadata in format: title|author|artist",
                show_alert=True
            )
        
        elif data == "setting_download_mode":
            new_mode = "url" if settings.download_mode == "telegram" else "telegram"
            settings.download_mode = new_mode
            await db_handler.save_user_settings(settings)
            await callback_query.answer(
                f"Download mode changed to: {new_mode.upper()}",
                show_alert=False
            )
        
        elif data == "setting_upload_mode":
            new_mode = "gofile" if settings.upload_mode == "telegram" else "telegram"
            settings.upload_mode = new_mode
            await db_handler.save_user_settings(settings)
            await callback_query.answer(
                f"Upload mode changed to: {new_mode.upper()}",
                show_alert=False
            )
    
    print("✅ Callback handlers registered")
