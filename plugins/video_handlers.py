from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.auth_helper import AuthHelper
from helpers.file_helper import FileHelper
from helpers.ffmpeg_helper import FFmpegHelper
from helpers.mediainfo_helper import MediaInfoHelper
from database.db_handler import db_handler
from database.models import TaskQueue
import os
import uuid
from datetime import datetime


def register_video_handlers(app: Client):
    """Register video file handlers"""
    
    @app.on_message(filters.video | filters.document | filters.audio)
    async def handle_media_file(client: Client, message: Message):
        """Handle incoming media files"""
        user_id = message.from_user.id
        chat_id = message.chat.id
        is_private = message.chat.type == "private"
        
        # Check authorization
        can_use, reason = await AuthHelper.can_use_bot(user_id, chat_id, is_private)
        if not can_use:
            await message.reply_text(reason)
            return
        
        # Check if user has active task
        active_task = await db_handler.get_user_active_task(user_id)
        if active_task:
            await message.reply_text(
                "⚠️ <b>Task Already Running</b>\n\n"
                "You already have an active task. Please wait for it to complete.\n"
                f"Current task: {active_task.task_type.replace('_', ' ').title()}\n"
                f"Progress: {active_task.progress:.1f}%"
            )
            return
        
        # Get video tools state
        state = await db_handler.get_video_tools_state(user_id, chat_id)
        
        if not state.selected_tool:
            await message.reply_text(
                "⚠️ <b>No Tool Selected</b>\n\n"
                "Please select a video tool first using the 'Video Tools' menu.\n\n"
                "Use /start to open the main menu."
            )
            return
        
        # Get user settings
        settings = await db_handler.get_user_settings(user_id)
        
        # Handle based on selected tool
        if state.selected_tool == "mediainfo":
            await handle_mediainfo(client, message, settings)
        elif state.selected_tool == "merge":
            await handle_merge_file(client, message, state, settings)
        elif state.selected_tool == "encoding":
            await handle_encoding_file(client, message, state, settings)
        elif state.selected_tool == "convert":
            await handle_convert_file(client, message, settings)
        elif state.selected_tool == "trim":
            await handle_trim_file(client, message, state, settings)
        elif state.selected_tool == "sample":
            await handle_sample_file(client, message, state, settings)
        elif state.selected_tool == "watermark":
            await handle_watermark_file(client, message, state, settings)


async def handle_mediainfo(client, message, settings):
    """Handle MediaInfo extraction"""
    status_msg = await message.reply_text("📊 Extracting media information...")
    
    try:
        # Download file
        file_path = await FileHelper.download_telegram_file(client, message)
        if not file_path:
            await status_msg.edit_text("❌ Failed to download file")
            return
        
        # Extract MediaInfo
        media_info = MediaInfoHelper.get_media_info(file_path)
        if not media_info:
            await status_msg.edit_text("❌ Failed to extract media information")
            FileHelper.delete_file(file_path)
            return
        
        # Send MediaInfo
        await status_msg.edit_text(media_info)
        
        # Cleanup
        FileHelper.delete_file(file_path)
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")


async def handle_merge_file(client, message, state, settings):
    """Handle file for video merge"""
    # Add file to pending files list
    file_info = {
        'message_id': message.id,
        'file_type': 'video' if message.video else 'audio' if message.audio else 'document',
        'file_name': getattr(message.video or message.audio or message.document, 'file_name', f'file_{message.id}')
    }
    
    state.pending_files.append(file_info)
    await db_handler.save_video_tools_state(state)
    
    # Check merge mode requirements
    if state.merge_mode == "video_video":
        required = 2
        file_type = "videos"
    elif state.merge_mode == "video_audio":
        required = 2
        file_type = "video and audio"
    elif state.merge_mode == "video_subs":
        required = 2
        file_type = "video and subtitle"
    else:
        await message.reply_text("⚠️ Please select a merge mode first from Video Tools menu")
        return
    
    current_count = len(state.pending_files)
    
    if current_count < required:
        await message.reply_text(
            f"✅ File {current_count}/{required} received\n\n"
            f"Send {required - current_count} more {file_type} to start merging."
        )
    else:
        await message.reply_text(
            f"✅ All files received!\n\n"
            f"Starting merge process..."
        )
        # TODO: Start merge task
        await db_handler.clear_video_tools_state(message.from_user.id, message.chat.id)


async def handle_encoding_file(client, message, state, settings):
    """Handle file for video encoding"""
    if not state.encoding_preset:
        await message.reply_text(
            "⚠️ Please select an encoding preset first from Video Tools → Encoding menu"
        )
        return
    
    await message.reply_text(
        f"✅ Video received!\n\n"
        f"Encoding with preset: {state.encoding_preset}\n"
        f"Starting encoding process..."
    )
    # TODO: Start encoding task


async def handle_convert_file(client, message, settings):
    """Handle file for format conversion"""
    await message.reply_text(
        "✅ File received!\n\n"
        "Starting format conversion..."
    )
    # TODO: Start conversion task


async def handle_trim_file(client, message, state, settings):
    """Handle file for video trimming"""
    if not state.trim_start or not state.trim_end:
        await message.reply_text(
            "⚠️ Please set trim times first\n\n"
            "Send times in format: HH:MM:SS-HH:MM:SS\n"
            "Example: 00:00:10-00:05:30"
        )
        return
    
    await message.reply_text(
        f"✅ Video received!\n\n"
        f"Trimming from {state.trim_start} to {state.trim_end}\n"
        f"Starting trim process..."
    )
    # TODO: Start trim task


async def handle_sample_file(client, message, state, settings):
    """Handle file for sample generation"""
    await message.reply_text(
        "✅ Video received!\n\n"
        "Generating video samples...",
        reply_markup=None
    )
    # TODO: Start sample generation task


async def handle_watermark_file(client, message, state, settings):
    """Handle file for watermark"""
    if not state.watermark_text:
        await message.reply_text(
            "⚠️ Please send watermark text first\n\n"
            "Example: 'My Watermark'"
        )
        return
    
    await message.reply_text(
        f"✅ Video received!\n\n"
        f"Adding watermark: {state.watermark_text}\n"
        f"Starting watermark process..."
    )
    # TODO: Start watermark task


    @app.on_message(filters.text & ~filters.command([""]))
    async def handle_text_input(client: Client, message: Message):
        """Handle text input for settings and configurations"""
        user_id = message.from_user.id
        chat_id = message.chat.id
        text = message.text.strip()
        
        # Get video tools state
        state = await db_handler.get_video_tools_state(user_id, chat_id)
        
        # Check if waiting for watermark text
        if state.selected_tool == "watermark" and not state.watermark_text:
            state.watermark_text = text
            await db_handler.save_video_tools_state(state)
            await message.reply_text(
                f"✅ Watermark text set: {text}\n\n"
                "Now send me the video file to add the watermark."
            )
            return
        
        # Check if waiting for trim times
        if state.selected_tool == "trim" and "-" in text:
            parts = text.split("-")
            if len(parts) == 2:
                state.trim_start = parts[0].strip()
                state.trim_end = parts[1].strip()
                await db_handler.save_video_tools_state(state)
                await message.reply_text(
                    f"✅ Trim times set\n\n"
                    f"Start: {state.trim_start}\n"
                    f"End: {state.trim_end}\n\n"
                    "Now send me the video file to trim."
                )
                return
    
    print("✅ Video handlers registered")
