import os
import subprocess
import re
from typing import List, Tuple, Dict, Any
from pathlib import Path
import tempfile
import shutil
from PIL import Image, ImageDraw, ImageFont


def check_ffmpeg() -> bool:
    try:
        subprocess.run(['ffmpeg', '-version'],
                      capture_output=True,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def draw_text_on_image(base_image_path: str, text: str, config: Dict[str, Any] = None):
    if config is None:
        config = {}
    
    font_name = config.get('font', 'Microsoft YaHei')
    font_size = config.get('font_size', 36)
    text_color = config.get('color', 'white')
    border_color = config.get('border_color', 'black')
    border_width = config.get('border_width', 3)
    position = config.get('position', 'bottom')
    vertical_offset = config.get('vertical_offset', 60)
    
    try:
        font = ImageFont.truetype(font_name, font_size)
    except:
        try:
            font = ImageFont.truetype('simhei.ttf', font_size)
        except:
            font = ImageFont.load_default()
    
    img = Image.open(base_image_path).convert('RGBA')
    draw = ImageDraw.Draw(img)
    
    lines = text.split('\n') if text else []
    if not lines:
        return img
    
    line_height = font_size + 8
    total_height = len(lines) * line_height
    
    if position == 'top':
        y = vertical_offset
    elif position == 'center':
        y = (img.height - total_height) // 2
    else:
        y = img.height - total_height - vertical_offset
    
    for line in lines:
        if not line:
            y += line_height
            continue
            
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img.width - text_width) // 2
        
        if border_width > 0:
            for dx in [-border_width, 0, border_width]:
                for dy in [-border_width, 0, border_width]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=border_color)
        
        draw.text((x, y), line, font=font, fill=text_color)
        y += line_height
    
    return img


def merge_to_video_rock_solid(slides,
                           audio_files: List[str],
                           output_path: str,
                           resolution: Tuple[int, int] = (1280, 720),
                           fps: int = 24,
                           config: Dict[str, Any] = None):
    if config is None:
        config = {}
    
    if not check_ffmpeg():
        raise RuntimeError("FFmpeg 未安装或不在 PATH 中。")
    
    width, height = resolution
    subtitle_config = config.get('subtitle', {})
    
    temp_dir = tempfile.mkdtemp(prefix='video_merger_')
    
    slides_dir = os.path.join(temp_dir, 'slides_with_subtitle')
    os.makedirs(slides_dir, exist_ok=True)
    
    segments_dir = os.path.join(temp_dir, 'segments')
    os.makedirs(segments_dir, exist_ok=True)
    
    segment_files = []
    
    for idx, (slide, audio_file) in enumerate(zip(slides, audio_files)):
        print(f"处理第 {idx+1}/{len(slides)} 个幻灯片...")
        
        duration = 3.0
        try:
            from aliyun_tts import get_audio_duration
            duration = get_audio_duration(audio_file)
        except:
            pass
        duration = max(2.0, duration)
        
        slide_img_path = os.path.join(slides_dir, f"slide_{idx:03d}_final.png")
        
        if subtitle_config.get('enabled', True) and slide.notes_text:
            img = draw_text_on_image(slide.image_path, slide.notes_text, subtitle_config)
            img.save(slide_img_path)
        else:
            base_img = Image.open(slide.image_path)
            base_img.save(slide_img_path)
        
        segment_path = os.path.join(segments_dir, f'segment_{idx:03d}.mp4')
        
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', slide_img_path
        ]
        
        if os.path.exists(audio_file):
            cmd.extend(['-i', audio_file])
        
        cmd.extend([
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,'\
                   f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1',
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
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    return output_path
