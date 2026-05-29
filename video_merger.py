import os
import subprocess
import re
from typing import List, Tuple, Dict, Any, NamedTuple
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


def create_concat_list(segment_files: List[str], output_path: str) -> str:
    """创建 FFmpeg 合并列表文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for file_path in segment_files:
            abs_path = os.path.abspath(file_path).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
    return output_path


def split_text_into_lines(text: str, max_chars_per_line: int = 20) -> List[str]:
    """
    将文本自动拆分成多行
    
    Args:
        text: 输入文本
        max_chars_per_line: 每行最大字符数
    
    Returns:
        文本行列表
    """
    # 首先按换行符拆分
    lines = text.split('\n')
    result = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 然后按标点符号和字数进一步拆分
        # 先尝试按标点符号分割
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
                
                # 如果单个部分就超过了，继续拆分
                if len(part) > max_chars_per_line:
                    # 按字符拆分
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
    
    Args:
        lines: 文本行列表
        total_duration: 总时长
    
    Returns:
        列表，每个元素为 (文本行, 起始时间, 结束时间)
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
    
    # 修正最后一行的结束时间
    if result:
        result[-1] = (result[-1][0], result[-1][1], total_duration)
    
    return result


def distribute_time_to_chars(text: str, line_duration: float) -> List[Tuple[str, float, float]]:
    """
    将行时长分配给每个字符
    
    Args:
        text: 文本行
        line_duration: 这一行的总时长
    
    Returns:
        列表，每个元素为 (字符, 起始时间, 结束时间)
    """
    if len(text) == 0:
        return []
    
    char_duration = line_duration / len(text)
    result = []
    
    for i, char in enumerate(text):
        start_time = i * char_duration
        end_time = (i + 1) * char_duration
        result.append((char, start_time, end_time))
    
    return result


def draw_karaoke_subtitle(img: Image.Image,
                          line: str,
                          char_progress: float,
                          y_position: int,
                          config: Dict[str, Any]) -> Image.Image:
    """
    绘制卡拉OK字幕
    
    Args:
        img: 图片对象
        line: 当前显示的行
        char_progress: 字符进度 (0.0 ~ 1.0)
        y_position: 字幕Y坐标
        config: 字幕配置
    
    Returns:
        绘制后的图片
    """
    draw = ImageDraw.Draw(img)
    font_size = config.get('font_size', 48)
    text_color = config.get('color', 'white')
    highlight_color = config.get('highlight_color', 'yellow')
    border_color = config.get('border_color', 'black')
    border_width = config.get('border_width', 3)
    
    # 加载字体
    font_paths = [
        r'C:\\Windows\\Fonts\\simhei.ttf',
        r'C:\\Windows\\Fonts\\msyh.ttc',
        r'C:\\Windows\\Fonts\\simsun.ttc',
    ]
    
    font = None
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        except:
            continue
    
    if font is None:
        font = ImageFont.load_default()
    
    # 计算文本宽度和起始位置
    bbox = draw.textbbox((0, 0), line, font=font)
    text_width = bbox[2] - bbox[0]
    x = (img.width - text_width) // 2
    
    # 计算已经高亮的字符数
    total_chars = len(line)
    highlight_chars = int(total_chars * char_progress)
    
    # 绘制整个文本（白色）
    # 先画边框
    for dx in range(-border_width, border_width + 1):
        for dy in range(-border_width, border_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y_position + dy), line, font=font, fill=border_color)
    draw.text((x, y_position), line, font=font, fill=text_color)
    
    # 绘制高亮部分（黄色）
    if highlight_chars > 0:
        highlight_text = line[:highlight_chars]
        highlight_bbox = draw.textbbox((0, 0), highlight_text, font=font)
        
        # 使用半透明的方式叠加高亮
        # 或者直接重写已经高亮的部分
        for dx in range(-border_width, border_width + 1):
            for dy in range(-border_width, border_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y_position + dy), highlight_text, font=font, fill=border_color)
        draw.text((x, y_position), highlight_text, font=font, fill=highlight_color)
    
    return img


def draw_single_line_subtitle(img: Image.Image,
                              line: str,
                              y_position: int,
                              config: Dict[str, Any]) -> Image.Image:
    """
    绘制单行字幕（无卡拉OK效果）
    
    Args:
        img: 图片对象
        line: 当前显示的行
        y_position: 字幕Y坐标
        config: 字幕配置
    
    Returns:
        绘制后的图片
    """
    draw = ImageDraw.Draw(img)
    font_size = config.get('font_size', 48)
    text_color = config.get('color', 'white')
    border_color = config.get('border_color', 'black')
    border_width = config.get('border_width', 3)
    
    # 加载字体
    font_paths = [
        r'C:\\Windows\\Fonts\\simhei.ttf',
        r'C:\\Windows\\Fonts\\msyh.ttc',
        r'C:\\Windows\\Fonts\\simsun.ttc',
    ]
    
    font = None
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        except:
            continue
    
    if font is None:
        font = ImageFont.load_default()
    
    # 计算文本宽度和起始位置
    bbox = draw.textbbox((0, 0), line, font=font)
    text_width = bbox[2] - bbox[0]
    x = (img.width - text_width) // 2
    
    # 绘制
    for dx in range(-border_width, border_width + 1):
        for dy in range(-border_width, border_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y_position + dy), line, font=font, fill=border_color)
    draw.text((x, y_position), line, font=font, fill=text_color)
    
    return img


def calculate_y_position(img: Image.Image, config: Dict[str, Any]) -> int:
    """
    计算字幕Y位置
    
    Args:
        img: 图片
        config: 字幕配置
    
    Returns:
        Y坐标
    """
    position = config.get('position', 'bottom')
    vertical_offset = config.get('vertical_offset', 60)
    font_size = config.get('font_size', 48)
    
    if position == 'bottom':
        return img.height - vertical_offset - font_size
    elif position == 'top':
        return vertical_offset
    else:  # center
        return (img.height - font_size) // 2


def generate_frames_for_slide(slide,
                              duration: float,
                              temp_dir: str,
                              config: Dict[str, Any],
                              fps: int = 30) -> List[str]:
    """
    为单页幻灯片生成一系列帧（支持逐行逐字卡拉OK）
    
    Args:
        slide: PPT幻灯片对象
        duration: 这一页的总时长
        temp_dir: 临时目录
        config: 配置
        fps: 帧率
    
    Returns:
        帧文件列表
    """
    subtitle_enabled = config.get('subtitle', {}).get('enabled', True)
    karaoke_enabled = config.get('subtitle', {}).get('karaoke_enabled', True)
    subtitle_config = config.get('subtitle', {})
    
    frame_files = []
    total_frames = int(duration * fps)
    if total_frames < 1:
        total_frames = 1
    
    if not subtitle_enabled or not slide.notes_text:
        # 无字幕或无文本，直接返回原图
        img = Image.open(slide.image_path)
        frame_path = os.path.join(temp_dir, f"frame_00000.png")
        img.save(frame_path)
        frame_files.append(frame_path)
        return frame_files
    
    # 拆分行
    lines = split_text_into_lines(slide.notes_text)
    if not lines:
        img = Image.open(slide.image_path)
        frame_path = os.path.join(temp_dir, f"frame_00000.png")
        img.save(frame_path)
        frame_files.append(frame_path)
        return frame_files
    
    # 分配时间给每行
    line_timings = distribute_time_to_lines(lines, duration)
    
    # 计算Y位置
    base_img = Image.open(slide.image_path)
    y_pos = calculate_y_position(base_img, subtitle_config)
    
    # 逐帧生成
    for frame_idx in range(total_frames):
        current_time = frame_idx / fps
        
        # 找到当前应该显示的行
        current_line = ""
        line_progress = 0.0
        
        for line, line_start, line_end in line_timings:
            if line_start <= current_time <= line_end:
                current_line = line
                line_duration = line_end - line_start
                if line_duration > 0:
                    line_progress = (current_time - line_start) / line_duration
                break
        
        # 复制基础图像
        img = base_img.copy()
        
        if current_line:
            if karaoke_enabled:
                # 卡拉OK模式
                img = draw_karaoke_subtitle(img, current_line, line_progress, y_pos, subtitle_config)
            else:
                # 普通单行模式
                img = draw_single_line_subtitle(img, current_line, y_pos, subtitle_config)
        
        # 保存帧
        frame_path = os.path.join(temp_dir, f"frame_{frame_idx:05d}.png")
        img.save(frame_path)
        frame_files.append(frame_path)
    
    return frame_files


def generate_transition_frames(frame1_path: str, frame2_path: str,
                              output_dir: str, num_frames: int = 10,
                              transition_type: str = 'fade') -> List[str]:
    """
    生成转场过渡帧
    
    Args:
        frame1_path: 第一帧图片路径
        frame2_path: 第二帧图片路径
        output_dir: 输出目录
        num_frames: 过渡帧数量
        transition_type: 转场类型
    
    Returns:
        过渡帧文件路径列表
    """
    frame_files = []
    
    img1 = Image.open(frame1_path)
    img2 = Image.open(frame2_path)
    
    # 确保图片尺寸一致
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
    
    for i in range(num_frames):
        alpha = i / (num_frames - 1)
        
        if transition_type == 'fade':
            blended = Image.blend(img1, img2, alpha)
        elif transition_type == 'slide_left':
            w, h = img1.size
            offset = int(w * alpha)
            blended = Image.new('RGB', (w, h))
            blended.paste(img1, (0, 0))
            blended.paste(img2, (-offset, 0))
        elif transition_type == 'slide_right':
            w, h = img1.size
            offset = int(w * alpha)
            blended = Image.new('RGB', (w, h))
            blended.paste(img1, (0, 0))
            blended.paste(img2, (offset, 0))
        else:
            blended = Image.blend(img1, img2, alpha)
        
        output_path = os.path.join(output_dir, f'transition_{i:03d}.png')
        blended.save(output_path)
        frame_files.append(output_path)
    
    return frame_files


def merge_to_video(slides,
                  audio_files: List[str],
                  subtitle_file: str,
                  output_path: str,
                  resolution: Tuple[int, int] = (1280, 720),
                  fps: int = 30,
                  config: Dict[str, Any] = None) -> str:
    """
    将幻灯片、音频和字幕合并为视频（支持高级卡拉OK字幕）
    
    Args:
        slides: 幻灯片列表
        audio_files: 音频文件列表
        subtitle_file: 字幕文件（未使用，保留兼容性）
        output_path: 输出路径
        resolution: 分辨率
        fps: 帧率
        config: 配置
    
    Returns:
        输出视频路径
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
    frames_dir = os.path.join(temp_dir, 'all_frames')
    segments_dir = os.path.join(temp_dir, 'segments')
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(segments_dir, exist_ok=True)
    
    all_frame_files = []
    previous_last_frame = None
    
    for slide_idx, (slide, audio_file) in enumerate(zip(slides, audio_files)):
        print(f"Processing slide {slide_idx + 1}/{len(slides)}...")
        
        # 获取这一页的时长
        duration = 3.0
        try:
            from aliyun_tts import get_audio_duration
            duration = get_audio_duration(audio_file)
        except:
            pass
        duration = max(2.0, duration)
        
        # 为这一页生成所有帧（包含字幕）
        slide_frames_dir = os.path.join(frames_dir, f'slide_{slide_idx:03d}')
        os.makedirs(slide_frames_dir, exist_ok=True)
        
        slide_frame_files = generate_frames_for_slide(
            slide=slide,
            duration=duration,
            temp_dir=slide_frames_dir,
            config=config,
            fps=fps
        )
        
        # 如果需要转场，而且不是第一页
        if transition_enabled and previous_last_frame and slide_frame_files:
            print(f"  Generating transition...")
            transition_frames_dir = os.path.join(frames_dir, f'transition_{slide_idx:03d}')
            os.makedirs(transition_frames_dir, exist_ok=True)
            
            transition_frames = generate_transition_frames(
                previous_last_frame,
                slide_frame_files[0],
                transition_frames_dir,
                num_frames=int(transition_duration * fps),
                transition_type=transition_type
            )
            all_frame_files.extend(transition_frames)
        
        # 添加这一页的帧
        all_frame_files.extend(slide_frame_files)
        
        # 记住这一页的最后一帧
        if slide_frame_files:
            previous_last_frame = slide_frame_files[-1]
    
    # 创建帧列表文件
    frame_list_file = os.path.join(temp_dir, 'frame_list.txt')
    with open(frame_list_file, 'w', encoding='utf-8') as f:
        for frame in all_frame_files:
            abs_path = os.path.abspath(frame).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
            f.write(f"duration {1.0/fps}\n")
        # 最后一帧再重复一次确保时长正确
        if all_frame_files:
            abs_path = os.path.abspath(all_frame_files[-1]).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
    
    # 先合成无声视频
    temp_video_no_audio = os.path.join(segments_dir, 'temp_no_audio.mp4')
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', frame_list_file,
        '-vf', f'fps={fps},scale={width}:{height}',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'medium',
        temp_video_no_audio
    ]
    print("Generating silent video from frames...")
    subprocess.run(cmd, capture_output=True, check=True)
    
    # 现在合并音频
    # 先把所有音频合并成一个
    all_audio_file = os.path.join(segments_dir, 'all_audio.mp3')
    
    if len(audio_files) > 1:
        audio_concat_list = os.path.join(segments_dir, 'audio_concat_list.txt')
        with open(audio_concat_list, 'w', encoding='utf-8') as f:
            for audio in audio_files:
                abs_path = os.path.abspath(audio).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', audio_concat_list,
            '-c:a', 'libmp3lame',
            '-q:a', '2',
            all_audio_file
        ]
        subprocess.run(cmd, capture_output=True, check=True)
    elif audio_files:
        shutil.copy(audio_files[0], all_audio_file)
    
    # 最后把视频和音频合并
    if os.path.exists(all_audio_file):
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_video_no_audio,
            '-i', all_audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            output_path
        ]
        print("Merging audio and video...")
        subprocess.run(cmd, capture_output=True, check=True)
    else:
        shutil.copy(temp_video_no_audio, output_path)
    
    return output_path
