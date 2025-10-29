import os
import aiohttp
import aiofiles
import requests
from typing import Optional, Tuple
from pyrogram import Client
from pyrogram.types import Message
from config import Config
import hashlib
import humanize


class FileHelper:
    """
    File Management Helper
    Handles file downloads from Telegram and URLs, uploads to Telegram and GoFile
    """
    
    @staticmethod
    async def download_telegram_file(client: Client, message: Message, custom_filename: Optional[str] = None) -> str:
        """Download file from Telegram"""
        try:
            if message.document:
                file_name = custom_filename or message.document.file_name or f"file_{message.id}"
                file_size = message.document.file_size
            elif message.video:
                file_name = custom_filename or message.video.file_name or f"video_{message.id}.mp4"
                file_size = message.video.file_size
            elif message.audio:
                file_name = custom_filename or message.audio.file_name or f"audio_{message.id}.mp3"
                file_size = message.audio.file_size
            else:
                return None
            
            download_path = os.path.join(Config.DOWNLOAD_DIR, file_name)
            
            # Download the file
            await client.download_media(
                message,
                file_name=download_path,
                progress=None  # TODO: Add progress callback
            )
            
            return download_path
        except Exception as e:
            print(f"Error downloading Telegram file: {e}")
            return None
    
    @staticmethod
    async def download_url_file(url: str, filename: Optional[str] = None) -> Optional[str]:
        """Download file from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    # Get filename from URL or Content-Disposition header
                    if not filename:
                        if 'Content-Disposition' in response.headers:
                            content_disp = response.headers['Content-Disposition']
                            if 'filename=' in content_disp:
                                filename = content_disp.split('filename=')[1].strip('"')
                        else:
                            filename = url.split('/')[-1] or f"download_{hashlib.md5(url.encode()).hexdigest()[:8]}"
                    
                    download_path = os.path.join(Config.DOWNLOAD_DIR, filename)
                    
                    # Download with progress
                    async with aiofiles.open(download_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(1024 * 1024):
                            await f.write(chunk)
                    
                    return download_path
        except Exception as e:
            print(f"Error downloading from URL: {e}")
            return None
    
    @staticmethod
    async def upload_to_telegram(
        client: Client,
        chat_id: int,
        file_path: str,
        caption: str = "",
        as_document: bool = True,
        thumbnail: Optional[str] = None,
        reply_to_message_id: Optional[int] = None
    ) -> Optional[Message]:
        """Upload file to Telegram"""
        try:
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Check if file is too large for Telegram (2GB limit)
            if file_size > 2 * 1024 * 1024 * 1024:
                return None
            
            if as_document:
                return await client.send_document(
                    chat_id=chat_id,
                    document=file_path,
                    caption=caption,
                    thumb=thumbnail,
                    reply_to_message_id=reply_to_message_id,
                    progress=None  # TODO: Add progress callback
                )
            else:
                # Determine media type based on extension
                ext = os.path.splitext(file_name)[1].lower()
                if ext in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                    return await client.send_video(
                        chat_id=chat_id,
                        video=file_path,
                        caption=caption,
                        thumb=thumbnail,
                        reply_to_message_id=reply_to_message_id,
                        progress=None  # TODO: Add progress callback
                    )
                elif ext in ['.mp3', '.m4a', '.ogg', '.flac']:
                    return await client.send_audio(
                        chat_id=chat_id,
                        audio=file_path,
                        caption=caption,
                        thumb=thumbnail,
                        reply_to_message_id=reply_to_message_id,
                        progress=None
                    )
                else:
                    # Fallback to document
                    return await client.send_document(
                        chat_id=chat_id,
                        document=file_path,
                        caption=caption,
                        thumb=thumbnail,
                        reply_to_message_id=reply_to_message_id,
                        progress=None
                    )
        except Exception as e:
            print(f"Error uploading to Telegram: {e}")
            return None
    
    @staticmethod
    def upload_to_gofile(file_path: str) -> Optional[Tuple[str, str]]:
        """
        Upload file to GoFile
        Returns: (download_url, file_name) or None if failed
        """
        try:
            # Get upload server
            server_response = requests.get("https://api.gofile.io/getServer")
            if server_response.status_code != 200:
                return None
            
            server_data = server_response.json()
            if server_data['status'] != 'ok':
                return None
            
            server = server_data['data']['server']
            
            # Upload file
            with open(file_path, 'rb') as f:
                files = {'file': f}
                headers = {}
                if Config.GOFILE_TOKEN:
                    headers['Authorization'] = f'Bearer {Config.GOFILE_TOKEN}'
                
                upload_response = requests.post(
                    f"https://{server}.gofile.io/uploadFile",
                    files=files,
                    headers=headers
                )
            
            if upload_response.status_code != 200:
                return None
            
            upload_data = upload_response.json()
            if upload_data['status'] != 'ok':
                return None
            
            download_url = upload_data['data']['downloadPage']
            file_name = os.path.basename(file_path)
            
            return (download_url, file_name)
        except Exception as e:
            print(f"Error uploading to GoFile: {e}")
            return None
    
    @staticmethod
    async def save_thumbnail(client: Client, message: Message, user_id: int) -> Optional[str]:
        """Save thumbnail from message"""
        try:
            if message.photo:
                filename = f"thumb_{user_id}.jpg"
                thumbnail_path = os.path.join(Config.THUMBNAIL_DIR, filename)
                
                await client.download_media(
                    message,
                    file_name=thumbnail_path
                )
                
                return filename
            elif message.document and message.document.mime_type.startswith('image/'):
                filename = f"thumb_{user_id}{os.path.splitext(message.document.file_name)[1]}"
                thumbnail_path = os.path.join(Config.THUMBNAIL_DIR, filename)
                
                await client.download_media(
                    message,
                    file_name=thumbnail_path
                )
                
                return filename
            return None
        except Exception as e:
            print(f"Error saving thumbnail: {e}")
            return None
    
    @staticmethod
    def get_thumbnail_path(thumbnail_filename: str) -> Optional[str]:
        """Get full path to thumbnail file"""
        if not thumbnail_filename:
            return None
        path = os.path.join(Config.THUMBNAIL_DIR, thumbnail_filename)
        return path if os.path.exists(path) else None
    
    @staticmethod
    def delete_file(file_path: str):
        """Delete a file safely"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    
    @staticmethod
    def cleanup_user_files(user_id: int):
        """Clean up all files for a specific user"""
        try:
            # Clean up downloads
            for file in os.listdir(Config.DOWNLOAD_DIR):
                if str(user_id) in file:
                    FileHelper.delete_file(os.path.join(Config.DOWNLOAD_DIR, file))
            
            # Clean up uploads
            for file in os.listdir(Config.UPLOAD_DIR):
                if str(user_id) in file:
                    FileHelper.delete_file(os.path.join(Config.UPLOAD_DIR, file))
        except Exception as e:
            print(f"Error cleaning up user files: {e}")
    
    @staticmethod
    def get_file_size_str(file_path: str) -> str:
        """Get human-readable file size"""
        try:
            size_bytes = os.path.getsize(file_path)
            return humanize.naturalsize(size_bytes)
        except:
            return "Unknown size"
    
    @staticmethod
    def get_video_duration(file_path: str) -> Optional[float]:
        """Get video duration in seconds"""
        try:
            import subprocess
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except Exception as e:
            print(f"Error getting video duration: {e}")
            return None
