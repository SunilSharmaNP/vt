from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_handler import db_handler


def register_merge_callbacks(app: Client):
    """Register merge-related callback handlers"""
    
    @app.on_callback_query(filters.regex("^merge_"))
    async def handle_merge_callbacks(client: Client, callback_query: CallbackQuery):
        """Handle video merge mode selection"""
        data = callback_query.data
        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id
        
        # Get video tools state
        state = await db_handler.get_video_tools_state(user_id, chat_id)
        
        if data == "merge_video_video":
            state.merge_mode = "video_video"
            state.pending_files = []
            await db_handler.save_video_tools_state(state)
            
            keyboard = [[InlineKeyboardButton("« Back to Video Tools", callback_data="menu_videotools")]]
            
            await callback_query.edit_message_text(
                "🔗 <b>VIDEO + VIDEO MERGE</b>\n\n"
                "📹 Send 2 or more video files to merge them into one.\n\n"
                "<b>Instructions:</b>\n"
                "1. Send your first video\n"
                "2. Send your second video\n"
                "3. (Optional) Send more videos\n"
                "4. I'll merge them automatically\n\n"
                "✨ All video streams will be preserved in the output.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "merge_video_audio":
            state.merge_mode = "video_audio"
            state.pending_files = []
            await db_handler.save_video_tools_state(state)
            
            keyboard = [[InlineKeyboardButton("« Back to Video Tools", callback_data="menu_videotools")]]
            
            await callback_query.edit_message_text(
                "🔊 <b>VIDEO + AUDIO MERGE</b>\n\n"
                "Add an audio track to your video.\n\n"
                "<b>Instructions:</b>\n"
                "1. Send your video file\n"
                "2. Send your audio file\n"
                "3. I'll merge them automatically\n\n"
                "✨ The original audio will be preserved, and the new audio will be added as an additional track.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "merge_video_subs":
            state.merge_mode = "video_subs"
            state.pending_files = []
            await db_handler.save_video_tools_state(state)
            
            keyboard = [[InlineKeyboardButton("« Back to Video Tools", callback_data="menu_videotools")]]
            
            await callback_query.edit_message_text(
                "💬 <b>VIDEO + SUBTITLES MERGE</b>\n\n"
                "Add subtitle file to your video.\n\n"
                "<b>Instructions:</b>\n"
                "1. Send your video file\n"
                "2. Send your subtitle file (.srt, .ass, .vtt)\n"
                "3. I'll merge them automatically\n\n"
                "✨ Subtitles will be embedded in the video file.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        await callback_query.answer()
    
    print("✅ Merge callback handlers registered")
