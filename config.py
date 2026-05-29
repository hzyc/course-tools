import json
import os
from dataclasses import dataclass
from typing import Tuple, Dict, Any

@dataclass
class Config:
    # Aliyun TTS settings
    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    aliyun_app_key: str = ""
    voice: str = "xiaoyun"
    speech_rate: int = 0
    pitch_rate: int = 0
    aliyun_format: str = "wav"
    aliyun_sample_rate: int = 24000
    aliyun_asr_app_key: str = ""
    
    # Video settings
    video_resolution: Tuple[int, int] = (1280, 720)
    video_fps: int = 30
    video_quality: str = "high"
    
    # Subtitle settings
    subtitle_enabled: bool = True
    subtitle_font: str = "Microsoft YaHei"
    subtitle_font_size: int = 48
    subtitle_color: str = "white"
    subtitle_highlight_color: str = "yellow"
    subtitle_border_color: str = "black"
    subtitle_border_width: int = 3
    subtitle_position: str = "bottom"
    subtitle_vertical_offset: int = 60
    subtitle_line_mode: str = "auto"
    subtitle_karaoke_enabled: bool = True
    
    # Transition settings
    transition_enabled: bool = True
    transition_type: str = "fade"
    transition_duration: float = 0.3

def load_config(config_path: str = "config.json") -> Config:
    if not os.path.exists(config_path):
        return Config()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    config = Config()
    
    if "aliyun" in data:
        aliyun = data["aliyun"]
        config.aliyun_access_key_id = aliyun.get("access_key_id", "")
        config.aliyun_access_key_secret = aliyun.get("access_key_secret", "")
        config.aliyun_app_key = aliyun.get("app_key", "")
        config.voice = aliyun.get("voice", "xiaoyun")
        config.speech_rate = aliyun.get("speech_rate", 0)
        config.pitch_rate = aliyun.get("pitch_rate", 0)
        config.aliyun_format = aliyun.get("format", "wav")
        config.aliyun_sample_rate = aliyun.get("sample_rate", 24000)
        config.aliyun_asr_app_key = aliyun.get("asr_app_key", "")
    
    if "video" in data:
        video = data["video"]
        if "resolution" in video:
            w, h = map(int, video["resolution"].split("x"))
            config.video_resolution = (w, h)
        config.video_fps = video.get("fps", 30)
        config.video_quality = video.get("quality", "medium")
    
    if "subtitle" in data:
        subtitle = data["subtitle"]
        config.subtitle_enabled = subtitle.get("enabled", True)
        config.subtitle_font = subtitle.get("font", "Microsoft YaHei")
        config.subtitle_font_size = subtitle.get("font_size", 48)
        config.subtitle_color = subtitle.get("color", "white")
        config.subtitle_highlight_color = subtitle.get("highlight_color", "yellow")
        config.subtitle_border_color = subtitle.get("border_color", "black")
        config.subtitle_border_width = subtitle.get("border_width", 3)
        config.subtitle_position = subtitle.get("position", "bottom")
        config.subtitle_vertical_offset = subtitle.get("vertical_offset", 60)
        config.subtitle_line_mode = subtitle.get("line_mode", "auto")
        config.subtitle_karaoke_enabled = subtitle.get("karaoke_enabled", True)
    
    if "transition" in data:
        transition = data["transition"]
        config.transition_enabled = transition.get("enabled", True)
        config.transition_type = transition.get("type", "fade")
        config.transition_duration = transition.get("duration", 0.3)
    
    return config

def get_config_dict(config: Config) -> Dict[str, Any]:
    """将Config对象转换为字典，用于传递给函数"""
    return {
        "subtitle": {
            "enabled": config.subtitle_enabled,
            "font": config.subtitle_font,
            "font_size": config.subtitle_font_size,
            "color": config.subtitle_color,
            "highlight_color": config.subtitle_highlight_color,
            "border_color": config.subtitle_border_color,
            "border_width": config.subtitle_border_width,
            "position": config.subtitle_position,
            "vertical_offset": config.subtitle_vertical_offset,
            "line_mode": config.subtitle_line_mode,
            "karaoke_enabled": config.subtitle_karaoke_enabled
        },
        "transition": {
            "enabled": config.transition_enabled,
            "type": config.transition_type,
            "duration": config.transition_duration
        }
    }
