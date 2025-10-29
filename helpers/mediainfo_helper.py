import os
from pymediainfo import MediaInfo
from typing import Optional
import humanize


class MediaInfoHelper:
    """
    MediaInfo Extraction Helper
    Formats media information in Anime-Leech bot style
    """
    
    @staticmethod
    def get_media_info(file_path: str) -> Optional[str]:
        """
        Extract and format media information
        Returns formatted string similar to Anime-Leech bot
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            media_info = MediaInfo.parse(file_path)
            
            # Build formatted output
            output = []
            output.append("📊 <b>MEDIA INFO</b>\n")
            
            # File information
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            output.append(f"📁 <b>File Name:</b> {file_name}")
            output.append(f"💾 <b>File Size:</b> {humanize.naturalsize(file_size)}\n")
            
            # General track information
            for track in media_info.tracks:
                if track.track_type == "General":
                    output.append("🎬 <b>GENERAL</b>")
                    if track.format:
                        output.append(f"  ├ <b>Format:</b> {track.format}")
                    if track.duration:
                        duration_sec = int(float(track.duration) / 1000)
                        hours, remainder = divmod(duration_sec, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        output.append(f"  ├ <b>Duration:</b> {hours:02d}:{minutes:02d}:{seconds:02d}")
                    if track.overall_bit_rate:
                        bitrate = humanize.naturalsize(int(track.overall_bit_rate), gnu=True) + "/s"
                        output.append(f"  └ <b>Bitrate:</b> {bitrate}\n")
            
            # Video tracks
            video_tracks = [t for t in media_info.tracks if t.track_type == "Video"]
            for idx, track in enumerate(video_tracks, 1):
                output.append(f"🎥 <b>VIDEO #{idx}</b>")
                if track.codec_id:
                    output.append(f"  ├ <b>Codec:</b> {track.codec_id}")
                if track.format:
                    output.append(f"  ├ <b>Format:</b> {track.format}")
                if track.width and track.height:
                    output.append(f"  ├ <b>Resolution:</b> {track.width}x{track.height}")
                if track.frame_rate:
                    output.append(f"  ├ <b>Frame Rate:</b> {float(track.frame_rate):.2f} fps")
                if track.bit_rate:
                    bitrate = humanize.naturalsize(int(track.bit_rate), gnu=True) + "/s"
                    output.append(f"  ├ <b>Bitrate:</b> {bitrate}")
                if track.bit_depth:
                    output.append(f"  ├ <b>Bit Depth:</b> {track.bit_depth} bit")
                if track.color_space:
                    output.append(f"  ├ <b>Color Space:</b> {track.color_space}")
                if track.chroma_subsampling:
                    output.append(f"  └ <b>Chroma Subsampling:</b> {track.chroma_subsampling}\n")
                else:
                    # Remove last ├ and replace with └
                    if output and output[-1].startswith("  ├"):
                        output[-1] = output[-1].replace("├", "└")
                    output.append("")
            
            # Audio tracks
            audio_tracks = [t for t in media_info.tracks if t.track_type == "Audio"]
            for idx, track in enumerate(audio_tracks, 1):
                title = f" - {track.title}" if track.title else ""
                lang = f" [{track.language}]" if track.language else ""
                output.append(f"🔊 <b>AUDIO #{idx}{title}{lang}</b>")
                if track.format:
                    output.append(f"  ├ <b>Format:</b> {track.format}")
                if track.codec_id:
                    output.append(f"  ├ <b>Codec:</b> {track.codec_id}")
                if track.channel_s:
                    output.append(f"  ├ <b>Channels:</b> {track.channel_s}")
                if track.sampling_rate:
                    output.append(f"  ├ <b>Sampling Rate:</b> {int(track.sampling_rate)} Hz")
                if track.bit_rate:
                    bitrate = humanize.naturalsize(int(track.bit_rate), gnu=True) + "/s"
                    output.append(f"  └ <b>Bitrate:</b> {bitrate}\n")
                else:
                    if output and output[-1].startswith("  ├"):
                        output[-1] = output[-1].replace("├", "└")
                    output.append("")
            
            # Subtitle tracks
            text_tracks = [t for t in media_info.tracks if t.track_type == "Text"]
            if text_tracks:
                for idx, track in enumerate(text_tracks, 1):
                    title = f" - {track.title}" if track.title else ""
                    lang = f" [{track.language}]" if track.language else ""
                    output.append(f"💬 <b>SUBTITLE #{idx}{title}{lang}</b>")
                    if track.format:
                        output.append(f"  └ <b>Format:</b> {track.format}\n")
            
            # Remove last empty line
            while output and output[-1] == "":
                output.pop()
            
            return "\n".join(output)
        except Exception as e:
            print(f"Error getting media info: {e}")
            return None
    
    @staticmethod
    def get_simple_info(file_path: str) -> Optional[dict]:
        """
        Get simple media information as dictionary
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            media_info = MediaInfo.parse(file_path)
            info = {
                'file_name': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'duration': None,
                'width': None,
                'height': None,
                'video_codec': None,
                'audio_codec': None,
                'bitrate': None
            }
            
            for track in media_info.tracks:
                if track.track_type == "General":
                    if track.duration:
                        info['duration'] = float(track.duration) / 1000
                    if track.overall_bit_rate:
                        info['bitrate'] = int(track.overall_bit_rate)
                
                elif track.track_type == "Video":
                    info['width'] = track.width
                    info['height'] = track.height
                    info['video_codec'] = track.format
                
                elif track.track_type == "Audio":
                    info['audio_codec'] = track.format
            
            return info
        except Exception as e:
            print(f"Error getting simple media info: {e}")
            return None
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to HH:MM:SS"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
