import os
import subprocess
import re
from typing import List, Tuple, Dict, Any
from pathlib import Path
import tempfile
import shutil
from PIL import Image, ImageDraw, ImageFont


def check_ffmpeg() -> bool:
    """检查 FFmpeg 是否已安装并可访问"""
    try:
        subprocess.run(['ffmpeg', '-version'],
                      capture_output=True,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def split_text_into_lines(text: str, max_chars_per_line: int = 20) -> List[str]:
    """
    将文本自动拆分成多行
    """
    lines = text.split('\n')
    result = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = re.split(r'([，。？！,.!?])', line)
        
        current_line = ""
        for part in parts:
            if not part:
                continue
            
            if len(current_line + part) <= max_chars_per_line:
                current_line += part
            else:
                if current_line:
                    result.append(current_line)
                
                if len(part) > max_chars_per_line:
                    for i in range(0, len(part), max_chars_per_line):
                        result.append(part[i:i+max_chars_per_line])
                    current_line = ""
                else:
                    current_line = part
        
        if current_line:
            result.append(current_line)
    
    return result


def distribute_time_to_lines(lines: List[str], total_duration: float) -> List[Tuple[str, float, float]]:
    """
    将总时长按字符数比例分配给每行
    """
    total_chars = sum(len(line) for line in lines)
    if total_chars == 0:
        return [(line, 0, total_duration) for line in lines]
    
    result = []
    current_time = 0.0
    
    for line in lines:
        line_duration = (len(line) / total_chars) * total_duration
        result.append((line, current_time, current_time + line_duration))
        current_time += line_duration
    
    if result:
        result[-1] = (result[-1][0], result[-1][1], total_duration)
    
    return result


def generate_advanced_subtitle(lines_with_times: List[Tuple[str, float, float]],
                              output_file: str,
                              config: Dict[str, Any] = None):
    """
    生成高级ASS字幕文件，支持卡拉OK逐字高亮效果
    """
    if config is None:
        config = {}
    
    font_name = config.get('font', 'Microsoft YaHei')
    font_size = config.get('font_size', 48)
    text_color = config.get('color', 'white')
    highlight_color = config.get('highlight_color', 'yellow')
    border_color = config.get('border_color', 'black')
    position = config.get('position', 'bottom')
    vertical_offset = config.get('vertical_offset', 60)
    
    color_map = {
        'white': '&H00FFFFFF',
        'yellow': '&H00FFFF00',
        'black': '&H00000000',
        'red': '&H000000FF',
        'green': '&H0000FF00',
        'blue': '&H00FF0000'
    }
    
    color_ass = color_map.get(text_color.lower(), '&H00FFFFFF')
    highlight_ass = color_map.get(highlight_color.lower(), '&H00FFFF00')
    
    alignment = 2 if position == 'bottom' else 8 if position == 'top' else 5
    margin_v = vertical_offset
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('[Script Info]\n')
        f.write('ScriptType: v4.00+\n')
        f.write('WrapStyle: 0\n')
        f.write('PlayResX: 1280\n')
        f.write('PlayResY: 720\n\n')
        
        f.write('[V4+ Styles]\n')
        f.write('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n')
        f.write(f'Style: Default,{font_name},{font_size},{color_ass},{highlight_ass},&H00000000,&H80000000,1,0,0,0,100,100,0,0,3,3,0,{alignment},10,10,{margin_v},1\n\n')
        
        f.write('[Events]\n')
        f.write('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
        
        for line_text, start_time, end_time in lines_with_times:
            start_str = format_time_ass(start_time)
            end_str = format_time_ass(end_time)
            duration = end_time - start_time
            
            if duration <= 0:
                continue
            
            f.write(f'Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,')
            
            total_chars = len(line_text)
            if total_chars == 0:
                f.write('\\N\n')
                continue
            
            for i, char in enumerate(line_text):
                char_start = (i / total_chars) * 100
                char_end = ((i + 1) / total_chars) * 100
                f.write(f'{{\\k{int(char_end - char_start)}}}{char}')
            
            f.write('\\N\n')
    
    return output_file


def format_time_ass(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def merge_to_video_efficient(slides,
                           audio_files: List[str],
                           output_path: str,
                           resolution: Tuple[int, int] = (1280, 720),
                           fps: int = 24,
                           config: Dict[str, Any] = None):
    """
    高效的视频合成方式，使用FFmpeg滤镜处理字幕
    """
    if config is None:
        config = {}
    
    if not check_ffmpeg():
        raise RuntimeError("FFmpeg 未安装或不在 PATH 中。")
    
    width, height = resolution
    subtitle_config = config.get('subtitle', {})
    transition_config = config.get('transition', {})
    transition_enabled = transition_config.get('enabled', True)
    transition_type = transition_config.get('type', 'fade')
    transition_duration = transition_config.get('duration', 0.3)
    
    temp_dir = os.path.dirname(output_path) or '.'
    segments_dir = os.path.join(temp_dir, 'segments_efficient')
    os.makedirs(segments_dir, exist_ok=True)
    
    segment_files = []
    
    for idx, (slide, audio_file) in enumerate(zip(slides, audio_files)):
        print(f"处理第 {idx+1}/{len(slides)} 个幻灯片...")
        
        segment_path = os.path.join(segments_dir, f'segment_{idx:03d}.mp4')
        
        duration = 3.0
        try:
            from aliyun_tts import get_audio_duration
            duration = get_audio_duration(audio_file)
        except:
            pass
        duration = max(2.0, duration)
        
        # 为这一页生成字幕
        subtitle_path = None
        if subtitle_config.get('enabled', True) and slide.notes_text:
            lines = split_text_into_lines(slide.notes_text)
            lines_with_times = distribute_time_to_lines(lines, duration)
            subtitle_path = os.path.join(segments_dir, f'subtitle_{idx:03d}.ass')
            generate_advanced_subtitle(lines_with_times, subtitle_path, subtitle_config)
        
        # 使用FFmpeg合成
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', slide.image_path
        ]
        
        if os.path.exists(audio_file):
            cmd.extend(['-i', audio_file])
        
        filter_parts = [
            f'scale={width}:{height}:force_original_aspect_ratio=decrease',
            f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
            'setsar=1'
        ]
        
        if subtitle_path and os.path.exists(subtitle_path):
            filter_parts.append(f"ass='{subtitle_path.replace(chr(92), chr(92)+chr(92))}'")
        
        cmd.extend([
            '-vf', ','.join(filter_parts),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p'
        ])
        
        if os.path.exists(audio_file):
            cmd.extend([
                '-c:a', 'aac',
                '-b:a', '192k'
            ])
        
        cmd.extend([
            '-t', str(duration),
            '-shortest',
            segment_path
        ])
        
        subprocess.run(cmd, capture_output=True, check=True)
        segment_files.append(segment_path)
    
    if len(segment_files) == 1:
        shutil.move(segment_files[0], output_path)
    else:
        concat_file = os.path.join(segments_dir, 'concat.txt')
        with open(concat_file, 'w', encoding='utf-8') as f:
            for sf in segment_files:
                abs_path = os.path.abspath(sf).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            output_path
        ]
        
        print("合并最终视频...")
        subprocess.run(cmd, capture_output=True, check=True)
    
    return output_path
