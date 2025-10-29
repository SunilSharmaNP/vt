import os
import subprocess
import asyncio
from typing import Optional, Dict, Any, Callable
from config import Config
import re


class FFmpegHelper:
    """
    FFmpeg Operations Helper
    Handles all video processing operations: merge, encode, convert, watermark, trim, sample
    """
    
    @staticmethod
    async def merge_videos(
        video_files: list,
        output_path: str,
        audio_file: Optional[str] = None,
        subtitle_file: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Merge multiple videos into one
        Optionally add audio track or subtitle file
        """
        try:
            # Create concat file list
            concat_file = os.path.join("temp", "concat_list.txt")
            with open(concat_file, 'w') as f:
                for video in video_files:
                    f.write(f"file '{os.path.abspath(video)}'\n")
            
            # Build FFmpeg command
            cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file]
            
            # Add audio if provided
            if audio_file:
                cmd.extend(['-i', audio_file])
            
            # Add subtitle if provided
            if subtitle_file:
                cmd.extend(['-i', subtitle_file])
            
            # Mapping and codec settings
            # Map all streams from the first input (concatenated video)
            cmd.extend(['-map', '0'])
            
            # Add additional audio track if provided
            if audio_file:
                cmd.extend(['-map', '1:a'])
            
            # Add subtitle stream if provided
            if subtitle_file:
                if audio_file:
                    cmd.extend(['-map', '2:s'])
                else:
                    cmd.extend(['-map', '1:s'])
            
            # Copy all streams without re-encoding
            cmd.extend(['-c', 'copy', '-y', output_path])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up concat file
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            return process.returncode == 0
        except Exception as e:
            print(f"Error merging videos: {e}")
            return False
    
    @staticmethod
    async def encode_video(
        input_file: str,
        output_path: str,
        preset: str = "medium",
        crf: str = "23",
        resolution: Optional[str] = None,
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        audio_bitrate: str = "128k",
        pixel_format: str = "yuv420p",
        ffmpeg_preset: str = "medium",
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Encode video with custom settings"""
        try:
            cmd = ['ffmpeg', '-i', input_file]
            
            # Video codec settings
            cmd.extend(['-c:v', video_codec])
            
            # CRF for quality
            if video_codec in ['libx264', 'libx265']:
                cmd.extend(['-crf', crf])
            elif video_codec == 'libvpx-vp9':
                cmd.extend(['-crf', crf, '-b:v', '0'])
            
            # Encoding preset
            if video_codec in ['libx264', 'libx265']:
                cmd.extend(['-preset', ffmpeg_preset])
            
            # Resolution
            if resolution:
                cmd.extend(['-vf', f'scale={resolution}'])
            
            # Pixel format
            cmd.extend(['-pix_fmt', pixel_format])
            
            # Audio codec settings
            cmd.extend(['-c:a', audio_codec, '-b:a', audio_bitrate])
            
            # Output file
            cmd.extend(['-y', output_path])
            
            # Execute command with progress tracking
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Read stderr for progress
            if progress_callback:
                duration = await FFmpegHelper.get_video_duration(input_file)
                async for line in process.stderr:
                    line_str = line.decode('utf-8', errors='ignore')
                    # Parse FFmpeg progress
                    if 'time=' in line_str and duration:
                        time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line_str)
                        if time_match:
                            hours, minutes, seconds = map(float, time_match.groups())
                            current_time = hours * 3600 + minutes * 60 + seconds
                            progress = (current_time / duration) * 100
                            await progress_callback(progress)
            
            await process.wait()
            return process.returncode == 0
        except Exception as e:
            print(f"Error encoding video: {e}")
            return False
    
    @staticmethod
    async def convert_format(
        input_file: str,
        output_path: str,
        output_format: str
    ) -> bool:
        """Convert video format"""
        try:
            cmd = [
                'ffmpeg', '-i', input_file,
                '-c', 'copy',
                '-y', output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.wait()
            return process.returncode == 0
        except Exception as e:
            print(f"Error converting format: {e}")
            return False
    
    @staticmethod
    async def add_watermark(
        input_file: str,
        output_path: str,
        watermark_text: str,
        position: str = "bottom_right",
        font_size: int = 24
    ) -> bool:
        """Add text watermark to video"""
        try:
            # Position mappings
            positions = {
                "top_left": "x=10:y=10",
                "top_right": "x=w-tw-10:y=10",
                "bottom_left": "x=10:y=h-th-10",
                "bottom_right": "x=w-tw-10:y=h-th-10",
                "center": "x=(w-tw)/2:y=(h-th)/2"
            }
            
            pos = positions.get(position, positions["bottom_right"])
            
            cmd = [
                'ffmpeg', '-i', input_file,
                '-vf', f"drawtext=text='{watermark_text}':fontsize={font_size}:fontcolor=white:borderw=2:bordercolor=black:{pos}",
                '-c:a', 'copy',
                '-y', output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.wait()
            return process.returncode == 0
        except Exception as e:
            print(f"Error adding watermark: {e}")
            return False
    
    @staticmethod
    async def trim_video(
        input_file: str,
        output_path: str,
        start_time: str,
        end_time: Optional[str] = None,
        duration: Optional[str] = None
    ) -> bool:
        """Trim video by time"""
        try:
            cmd = ['ffmpeg', '-i', input_file, '-ss', start_time]
            
            if end_time:
                cmd.extend(['-to', end_time])
            elif duration:
                cmd.extend(['-t', duration])
            
            cmd.extend(['-c', 'copy', '-y', output_path])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.wait()
            return process.returncode == 0
        except Exception as e:
            print(f"Error trimming video: {e}")
            return False
    
    @staticmethod
    async def create_sample(
        input_file: str,
        output_path: str,
        sample_type: str = "first",
        duration: int = 30
    ) -> bool:
        """
        Create sample from video
        sample_type: 'first', 'middle', 'last'
        """
        try:
            total_duration = await FFmpegHelper.get_video_duration(input_file)
            if not total_duration:
                return False
            
            # Calculate start time based on sample type
            if sample_type == "first":
                start_time = "0"
            elif sample_type == "middle":
                start_time = str(max(0, (total_duration / 2) - (duration / 2)))
            elif sample_type == "last":
                start_time = str(max(0, total_duration - duration))
            else:
                start_time = "0"
            
            cmd = [
                'ffmpeg', '-ss', start_time, '-i', input_file,
                '-t', str(duration),
                '-c', 'copy',
                '-y', output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.wait()
            return process.returncode == 0
        except Exception as e:
            print(f"Error creating sample: {e}")
            return False
    
    @staticmethod
    async def get_video_duration(file_path: str) -> Optional[float]:
        """Get video duration in seconds"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            duration_str = stdout.decode().strip()
            
            return float(duration_str) if duration_str else None
        except Exception as e:
            print(f"Error getting video duration: {e}")
            return None
    
    @staticmethod
    def extract_audio(input_file: str, output_path: str) -> bool:
        """Extract audio from video"""
        try:
            cmd = [
                'ffmpeg', '-i', input_file,
                '-vn', '-acodec', 'copy',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return False
    
    @staticmethod
    def get_video_info(file_path: str) -> Optional[Dict[str, Any]]:
        """Get basic video information using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,codec_name,bit_rate,duration',
                '-of', 'json',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            return None
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
