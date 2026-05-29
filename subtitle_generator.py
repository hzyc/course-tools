import os
from dataclasses import dataclass
from typing import List


@dataclass
class SubtitleStyle:
    font: str = "Microsoft YaHei"
    font_size: int = 48
    color: str = "white"
    position: str = "bottom"  # "top" or "bottom"
    border_style: int = 1  # 1 = outline


def format_time(seconds: float) -> str:
    """转换秒数为 SRT 时间格式 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def generate_subtitle(texts: List[str], 
                     durations: List[float],
                     output_path: str,
                     style: SubtitleStyle = None) -> str:
    """
    生成 SRT 字幕文件
    """
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    timestamps = []
    current_time = 0.0
    for duration in durations:
        start_time = current_time
        end_time = current_time + duration
        timestamps.append((start_time, end_time))
        current_time = end_time
    
    lines = []
    for i, (text, (start, end)) in enumerate(zip(texts, timestamps), 1):
        if not text:
            continue
        
        lines.append(str(i))
        lines.append(f"{format_time(start)} --> {format_time(end)}")
        lines.append(text)
        lines.append("")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return output_path
