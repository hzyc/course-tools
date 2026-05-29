import os
import sys
import subprocess
import tempfile
import shutil
import argparse
import logging
from pathlib import Path
from typing import Optional

from config import load_config
from asr_service import recognize_speech
from aliyun_tts import synthesize_speech, get_audio_duration

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_ffmpeg() -> bool:
    """检查FFmpeg是否可用"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False


def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """从视频中提取音频（压缩格式减小文件大小）"""
    try:
        # 输出为MP3压缩格式，采样率16kHz，单声道，比特率32kbps（进一步压缩）
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-acodec', 'libmp3lame',
            '-ar', '16000', '-ac', '1',
            '-b:a', '32k',
            output_audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, check=True)
        
        # 显示文件大小
        file_size = os.path.getsize(output_audio_path)
        logger.info(f"音频提取完成，文件大小: {file_size / 1024 / 1024:.2f} MB")
        return True
    except Exception as e:
        logger.error(f"提取音频失败: {e}")
        return False


def split_audio_into_segments(audio_path: str, temp_dir: str, max_segment_size_mb: float = 1.5) -> list:
    """将音频文件分割成小片段，每个片段不超过指定大小（MB）"""
    try:
        # 获取音频持续时间
        duration = get_audio_duration(audio_path)
        if duration <= 0:
            logger.error("无法获取音频时长")
            return []
        
        # 先计算音频文件大小
        file_size = os.path.getsize(audio_path)
        file_size_mb = file_size / 1024 / 1024
        
        # 如果文件本身不大，直接返回
        if file_size_mb <= max_segment_size_mb:
            logger.info(f"音频文件 {file_size_mb:.2f}MB，无需分段")
            return [audio_path]
        
        # 计算需要分割的段数
        num_segments = int(file_size_mb / max_segment_size_mb) + 1
        segment_duration = duration / num_segments
        
        logger.info(f"将音频分割为 {num_segments} 段，每段约 {segment_duration:.1f} 秒")
        
        segments = []
        for i in range(num_segments):
            start_time = i * segment_duration
            segment_path = os.path.join(temp_dir, f'segment_{i:03d}.mp3')
            
            cmd = [
                'ffmpeg', '-y',
                '-i', audio_path,
                '-ss', str(start_time),
                '-t', str(segment_duration + 0.1),  # 稍微长一点，避免边界问题
                '-acodec', 'libmp3lame',
                '-ar', '16000', '-ac', '1',
                '-b:a', '32k',
                segment_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, check=True)
            segments.append(segment_path)
            
            # 显示分段文件大小
            seg_size = os.path.getsize(segment_path) / 1024 / 1024
            logger.info(f"  分段 {i+1}/{num_segments}: {os.path.basename(segment_path)} ({seg_size:.2f} MB)")
        
        return segments
        
    except Exception as e:
        logger.error(f"分割音频失败: {e}")
        return []


def recognize_audio_segments(segments: list, access_key_id: str, access_key_secret: str, app_key: str) -> Optional[str]:
    """识别音频分段并合并结果"""
    full_text = ""
    
    for i, segment_path in enumerate(segments):
        logger.info(f"正在识别第 {i+1}/{len(segments)} 段...")
        segment_text = recognize_speech(
            audio_path=segment_path,
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            app_key=app_key
        )
        
        if segment_text:
            full_text += segment_text
            # 分段之间加个空格
            if not full_text.endswith(' '):
                full_text += ' '
    
    if full_text:
        logger.info(f"✅ 分段识别完成，总文本长度: {len(full_text)}")
        return full_text.strip()
    else:
        logger.error("所有分段识别失败")
        return None


def get_video_duration(video_path: str) -> float:
    """获取视频时长"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception as e:
        logger.warning(f"获取视频时长失败: {e}")
    return 0.0


def adjust_audio_duration(input_audio: str, target_duration: float, output_audio: str) -> bool:
    """调整音频时长到目标时长"""
    try:
        current_duration = get_audio_duration(input_audio)
        if current_duration <= 0:
            logger.warning("无法获取当前音频时长，跳过调整")
            shutil.copy(input_audio, output_audio)
            return True
        
        speed_ratio = current_duration / target_duration
        
        logger.info(f"音频时长: {current_duration:.2f}s -> {target_duration:.2f}s (倍率: {speed_ratio:.3f})")
        
        if abs(speed_ratio - 1.0) < 0.01:
            logger.info("时长差异小于1%，直接复制")
            shutil.copy(input_audio, output_audio)
            return True
        
        atempo_filters = []
        remaining_ratio = speed_ratio
        
        while remaining_ratio > 2.0 or remaining_ratio < 0.5:
            if remaining_ratio > 2.0:
                atempo_filters.append('atempo=2.0')
                remaining_ratio /= 2.0
            else:
                atempo_filters.append('atempo=0.5')
                remaining_ratio /= 0.5
        
        if remaining_ratio != 1.0:
            atempo_filters.append(f'atempo={remaining_ratio}')
        
        filter_str = ','.join(atempo_filters)
        
        cmd = [
            'ffmpeg', '-y', '-i', input_audio,
            '-filter:a', filter_str,
            '-ar', '44100', '-ac', '2',
            '-c:a', 'aac', '-b:a', '192k',
            output_audio
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=True, timeout=300)
        logger.info(f"音频时长调整完成")
        return True
        
    except Exception as e:
        logger.error(f"调整音频时长失败: {e}")
        return False


def synthesize_with_duration_control(text: str, target_duration: float, output_path: str, config) -> bool:
    """使用时长控制合成语音"""
    temp_dir = tempfile.mkdtemp(prefix='tts_duration_')
    
    try:
        base_audio = os.path.join(temp_dir, 'base_audio.wav')
        
        voice = config.voice
        speech_rate = config.speech_rate
        pitch_rate = config.pitch_rate
        audio_format = config.aliyun_format
        sample_rate = config.aliyun_sample_rate
        
        logger.info(f"正在合成基础音频...")
        synthesize_speech(
            text=text,
            output_path=base_audio,
            access_key_id=config.aliyun_access_key_id,
            access_key_secret=config.aliyun_access_key_secret,
            app_key=config.aliyun_app_key,
            voice=voice,
            speech_rate=speech_rate,
            pitch_rate=pitch_rate,
            audio_format=audio_format,
            sample_rate=sample_rate
        )
        
        if not os.path.exists(base_audio):
            logger.error("基础音频合成失败")
            return False
        
        logger.info(f"正在调整音频到目标时长: {target_duration:.2f}s")
        success = adjust_audio_duration(base_audio, target_duration, output_path)
        
        return success
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def replace_audio_in_video(video_path: str, new_audio_path: str, output_path: str) -> bool:
    """替换视频中的音频"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', new_audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            output_path
        ]
        
        logger.info(f"正在替换音频并生成新视频...")
        result = subprocess.run(cmd, capture_output=True, check=True, timeout=600)
        logger.info(f"✅ 视频音频替换完成: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"替换音频失败: {e}")
        return False


def process_video(input_video: str, output_video: str, config, 
                  skip_asr: bool = False, 
                  use_manual_text: Optional[str] = None,
                  manual_text_file: Optional[str] = None,
                  use_local_asr: bool = True) -> bool:
    """处理视频：提取音频->识别->TTS->替换"""
    
    if not check_ffmpeg():
        logger.error("FFmpeg未安装或不在PATH中")
        return False
    
    temp_dir = tempfile.mkdtemp(prefix='audio_replace_')
    logger.info(f"使用临时目录: {temp_dir}")
    
    try:
        # 使用MP3压缩格式减小文件大小
        extracted_audio = os.path.join(temp_dir, 'extracted.mp3')
        
        logger.info(f"=== 步骤1: 从视频提取音频 ===")
        if not extract_audio_from_video(input_video, extracted_audio):
            logger.error("音频提取失败")
            return False
        
        video_duration = get_video_duration(input_video)
        logger.info(f"视频时长: {video_duration:.2f}s")
        
        recognized_text = ""
        
        if use_manual_text:
            logger.info(f"=== 步骤2: 使用手动提供的文本 ===")
            recognized_text = use_manual_text
            logger.info(f"文本长度: {len(recognized_text)}")
        elif manual_text_file and os.path.exists(manual_text_file):
            logger.info(f"=== 步骤2: 从文件读取文本 ===")
            with open(manual_text_file, 'r', encoding='utf-8') as f:
                recognized_text = f.read()
            logger.info(f"文本长度: {len(recognized_text)}")
        elif not skip_asr:
            logger.info(f"=== 步骤2: 语音识别 ===")
            asr_app_key = config.aliyun_asr_app_key or config.aliyun_app_key
            
            # 直接使用本地ASR识别（更稳定）
            recognized_text = recognize_speech(
                audio_path=extracted_audio,
                use_local=use_local_asr,
                access_key_id=config.aliyun_access_key_id,
                access_key_secret=config.aliyun_access_key_secret,
                app_key=asr_app_key
            )
            
            if not recognized_text:
                logger.error("语音识别失败")
                return False
        
        if not recognized_text:
            logger.error("没有可用的文本进行TTS合成")
            return False
        
        text_file = os.path.join(temp_dir, 'recognized_text.txt')
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(recognized_text)
        logger.info(f"识别的文本已保存到: {text_file}")
        
        logger.info(f"=== 步骤3: TTS合成与时长控制 ===")
        new_audio = os.path.join(temp_dir, 'new_audio.aac')
        
        if not synthesize_with_duration_control(recognized_text, video_duration, new_audio, config):
            logger.error("TTS合成失败")
            return False
        
        logger.info(f"=== 步骤4: 替换音频 ===")
        if not replace_audio_in_video(input_video, new_audio, output_video):
            logger.error("音频替换失败")
            return False
        
        logger.info(f"✅ 处理完成！输出: {output_video}")
        return True
        
    except Exception as e:
        logger.error(f"处理过程出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description='视频音频替换工具：ASR识别 + TTS重新合成 + 时长对齐',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  1. 完整流程（本地ASR+阿里云TTS）:
     python audio_replacer.py input.mp4 output.mp4
  
  2. 使用手动文本:
     python audio_replacer.py input.mp4 output.mp4 --text "这是要合成的文本"
  
  3. 从文件读取文本:
     python audio_replacer.py input.mp4 output.mp4 --text-file myscript.txt
  
  4. 自定义配置:
     python audio_replacer.py input.mp4 output.mp4 --config myconfig.json
        '''
    )
    
    parser.add_argument('input', type=str, help='输入视频文件路径')
    parser.add_argument('output', type=str, help='输出视频文件路径')
    parser.add_argument('--config', type=str, default='config.json', help='配置文件路径 (默认: config.json)')
    parser.add_argument('--text', type=str, help='手动指定TTS文本（跳过ASR）')
    parser.add_argument('--text-file', type=str, help='从文件读取TTS文本（跳过ASR）')
    parser.add_argument('--voice', type=str, help='指定TTS音色（覆盖配置文件）')
    parser.add_argument('--local-asr', action='store_true', default=True, help='使用本地Whisper进行ASR识别（默认开启）')
    parser.add_argument('--log-level', type=str, 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='日志级别')
    
    args = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    if not os.path.exists(args.input):
        logger.error(f"输入文件不存在: {args.input}")
        sys.exit(1)
    
    config = load_config(args.config)
    
    if args.voice:
        config.voice = args.voice
    
    success = process_video(
        args.input, 
        args.output, 
        config,
        use_manual_text=args.text,
        manual_text_file=args.text_file,
        use_local_asr=args.local_asr
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
