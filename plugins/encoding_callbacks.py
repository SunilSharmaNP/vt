from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_handler import db_handler
from config import Config


def register_encoding_callbacks(app: Client):
    """Register encoding-related callback handlers"""
    
    @app.on_callback_query(filters.regex("^encode_"))
    async def handle_encoding_callbacks(client: Client, callback_query: CallbackQuery):
        """Handle encoding preset selection"""
        data = callback_query.data
        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id
        
        # Get video tools state
        state = await db_handler.get_video_tools_state(user_id, chat_id)
        
        # Preset mappings
        preset_map = {
            "encode_1080p": "1080p",
            "encode_1080p_hevc": "1080p_hevc",
            "encode_720p": "720p",
            "encode_720p_hevc": "720p_hevc",
            "encode_480p": "480p",
            "encode_480p_hevc": "480p_hevc",
            "encode_360p": "360p"
        }
        
        if data in preset_map:
            preset_name = preset_map[data]
            state.encoding_preset = preset_name
            state.encoding_settings = Config.ENCODING_PRESETS[preset_name].copy()
            await db_handler.save_video_tools_state(state)
            
            preset_info = Config.ENCODING_PRESETS[preset_name]
            
            keyboard = [
                [InlineKeyboardButton("⚙️ Customize Settings", callback_data="encode_customize")],
                [InlineKeyboardButton("✅ Use These Settings", callback_data="encode_confirm")],
                [InlineKeyboardButton("« Back", callback_data="tool_encoding")]
            ]
            
            await callback_query.edit_message_text(
                f"🎥 <b>ENCODING PRESET: {preset_name.upper()}</b>\n\n"
                f"📐 <b>Resolution:</b> {preset_info['resolution']}\n"
                f"🎬 <b>Video Codec:</b> {preset_info['codec']}\n"
                f"📊 <b>Video Bitrate:</b> {preset_info['video_bitrate']}\n"
                f"🎵 <b>Audio Bitrate:</b> {preset_info['audio_bitrate']}\n"
                f"⚡ <b>CRF:</b> {preset_info['crf']}\n"
                f"🚀 <b>Preset:</b> {preset_info['preset']}\n\n"
                "You can customize these settings or use them as-is:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "encode_custom":
            state.encoding_preset = "custom"
            state.encoding_settings = {
                "resolution": None,
                "video_codec": "libx264",
                "audio_codec": "aac",
                "crf": "23",
                "audio_bitrate": "128k",
                "preset": "medium",
                "pixel_format": "yuv420p"
            }
            await db_handler.save_video_tools_state(state)
            
            keyboard = [
                [InlineKeyboardButton("📐 Resolution", callback_data="custom_resolution")],
                [InlineKeyboardButton("🎬 Video Codec", callback_data="custom_video_codec")],
                [InlineKeyboardButton("🎵 Audio Codec", callback_data="custom_audio_codec")],
                [InlineKeyboardButton("⚡ CRF Quality", callback_data="custom_crf")],
                [InlineKeyboardButton("📊 Audio Bitrate", callback_data="custom_audio_bitrate")],
                [InlineKeyboardButton("🚀 Encoding Preset", callback_data="custom_preset")],
                [InlineKeyboardButton("🎨 Pixel Format", callback_data="custom_pixel_format")],
                [InlineKeyboardButton("✅ Done - Send Video", callback_data="encode_confirm")],
                [InlineKeyboardButton("« Back", callback_data="tool_encoding")]
            ]
            
            await callback_query.edit_message_text(
                "⚙️ <b>CUSTOM ENCODING SETTINGS</b>\n\n"
                "Configure each setting below:\n\n"
                "📐 Resolution: Keep original\n"
                "🎬 Video Codec: libx264\n"
                "🎵 Audio Codec: aac\n"
                "⚡ CRF: 23 (Medium quality)\n"
                "📊 Audio Bitrate: 128k\n"
                "🚀 Preset: medium\n"
                "🎨 Pixel Format: yuv420p\n\n"
                "Click a button to change, or 'Done' when ready:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "encode_confirm":
            keyboard = [[InlineKeyboardButton("« Back to Video Tools", callback_data="menu_videotools")]]
            
            await callback_query.edit_message_text(
                "✅ <b>Encoding Settings Confirmed!</b>\n\n"
                "Now send me the video file you want to encode.\n\n"
                "I'll process it with your selected settings.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        await callback_query.answer()
    
    @app.on_callback_query(filters.regex("^custom_"))
    async def handle_custom_encoding_callbacks(client: Client, callback_query: CallbackQuery):
        """Handle custom encoding setting selections"""
        data = callback_query.data
        
        # Show options for each custom setting
        if data == "custom_resolution":
            keyboard = [
                [InlineKeyboardButton("Keep Original", callback_data="set_res_original")],
                [InlineKeyboardButton("1920x1080", callback_data="set_res_1920x1080")],
                [InlineKeyboardButton("1280x720", callback_data="set_res_1280x720")],
                [InlineKeyboardButton("854x480", callback_data="set_res_854x480")],
                [InlineKeyboardButton("640x360", callback_data="set_res_640x360")],
                [InlineKeyboardButton("« Back", callback_data="encode_custom")]
            ]
            await callback_query.edit_message_text(
                "📐 <b>SELECT RESOLUTION</b>\n\nChoose output resolution:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "custom_video_codec":
            keyboard = [
                [InlineKeyboardButton("H.264 (libx264)", callback_data="set_vcodec_libx264")],
                [InlineKeyboardButton("H.265/HEVC (libx265)", callback_data="set_vcodec_libx265")],
                [InlineKeyboardButton("VP9 (libvpx-vp9)", callback_data="set_vcodec_libvpx-vp9")],
                [InlineKeyboardButton("« Back", callback_data="encode_custom")]
            ]
            await callback_query.edit_message_text(
                "🎬 <b>SELECT VIDEO CODEC</b>\n\nChoose video codec:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "custom_audio_codec":
            keyboard = [
                [InlineKeyboardButton("AAC", callback_data="set_acodec_aac")],
                [InlineKeyboardButton("Opus", callback_data="set_acodec_libopus")],
                [InlineKeyboardButton("MP3", callback_data="set_acodec_libmp3lame")],
                [InlineKeyboardButton("« Back", callback_data="encode_custom")]
            ]
            await callback_query.edit_message_text(
                "🎵 <b>SELECT AUDIO CODEC</b>\n\nChoose audio codec:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "custom_crf":
            keyboard = [
                [InlineKeyboardButton("Best (18/23)", callback_data="set_crf_best")],
                [InlineKeyboardButton("High (21/26)", callback_data="set_crf_high")],
                [InlineKeyboardButton("Medium (23/28)", callback_data="set_crf_medium")],
                [InlineKeyboardButton("Low (26/31)", callback_data="set_crf_low")],
                [InlineKeyboardButton("Potato (30/35)", callback_data="set_crf_potato")],
                [InlineKeyboardButton("« Back", callback_data="encode_custom")]
            ]
            await callback_query.edit_message_text(
                "⚡ <b>SELECT CRF QUALITY</b>\n\n"
                "Lower = Better quality, larger file\n"
                "Higher = Lower quality, smaller file\n\n"
                "Choose quality level:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "custom_audio_bitrate":
            keyboard = [
                [InlineKeyboardButton("64k", callback_data="set_abitrate_64k")],
                [InlineKeyboardButton("96k", callback_data="set_abitrate_96k")],
                [InlineKeyboardButton("128k", callback_data="set_abitrate_128k")],
                [InlineKeyboardButton("192k", callback_data="set_abitrate_192k")],
                [InlineKeyboardButton("256k", callback_data="set_abitrate_256k")],
                [InlineKeyboardButton("320k", callback_data="set_abitrate_320k")],
                [InlineKeyboardButton("« Back", callback_data="encode_custom")]
            ]
            await callback_query.edit_message_text(
                "📊 <b>SELECT AUDIO BITRATE</b>\n\nChoose audio bitrate:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "custom_preset":
            keyboard = [
                [InlineKeyboardButton("Ultra Fast", callback_data="set_preset_ultrafast")],
                [InlineKeyboardButton("Very Fast", callback_data="set_preset_veryfast")],
                [InlineKeyboardButton("Fast", callback_data="set_preset_fast")],
                [InlineKeyboardButton("Medium", callback_data="set_preset_medium")],
                [InlineKeyboardButton("Slow", callback_data="set_preset_slow")],
                [InlineKeyboardButton("Very Slow", callback_data="set_preset_veryslow")],
                [InlineKeyboardButton("« Back", callback_data="encode_custom")]
            ]
            await callback_query.edit_message_text(
                "🚀 <b>SELECT ENCODING PRESET</b>\n\n"
                "Faster = Quicker encoding, larger file\n"
                "Slower = Better compression, smaller file\n\n"
                "Choose preset:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "custom_pixel_format":
            keyboard = [
                [InlineKeyboardButton("yuv420p (Most compatible)", callback_data="set_pixfmt_yuv420p")],
                [InlineKeyboardButton("yuv422p", callback_data="set_pixfmt_yuv422p")],
                [InlineKeyboardButton("yuv444p", callback_data="set_pixfmt_yuv444p")],
                [InlineKeyboardButton("« Back", callback_data="encode_custom")]
            ]
            await callback_query.edit_message_text(
                "🎨 <b>SELECT PIXEL FORMAT</b>\n\nChoose pixel format:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        await callback_query.answer()
    
    print("✅ Encoding callback handlers registered")
