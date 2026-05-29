import os
import sys
import argparse
import tempfile
import shutil
import logging
from pathlib import Path
from typing import List

from config import load_config, get_config_dict
from ppt_parser import parse_ppt, PPTSlide
from aliyun_tts import synthesize_speech, get_audio_duration
from subtitle_generator import generate_subtitle
from video_merger_solid import merge_to_video_rock_solid

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments(args=None):
    parser = argparse.ArgumentParser(
        description='Convert PPTX to MP4 with TTS voiceover and subtitles'
    )
    
    parser.add_argument('input', type=str, help='Input PPTX file path')
    parser.add_argument('-o', '--output', type=str,
                       default=None, help='Output MP4 file path')
    parser.add_argument('-c', '--config', type=str,
                       default='config.json', help='Configuration file path')
    parser.add_argument('-v', '--voice', type=str,
                       default=None, help='Voice name for TTS')
    parser.add_argument('-q', '--quality', type=str, choices=['low', 'medium', 'high'],
                       default='medium', help='Video quality')
    parser.add_argument('--no-subtitle', action='store_true',
                       help='Disable subtitle generation')
    parser.add_argument('--keep-temp', action='store_true',
                       help='Keep temporary files for debugging')
    parser.add_argument('-l', '--log-level', type=str,
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    parsed = parser.parse_args(args)
    
    if parsed.output is None:
        input_name = Path(parsed.input).stem
        parsed.output = f"{input_name}_video.mp4"
    
    return parsed


def process_pptx(input_path: str, output_path: str, config, args):
    from video_merger_solid import check_ffmpeg
    if not check_ffmpeg():
        logger.error("FFmpeg is not installed or not in PATH.")
        logger.error("Please install FFmpeg from https://ffmpeg.org/")
        sys.exit(1)
    
    temp_dir = tempfile.mkdtemp(prefix='ppttovideo_')
    logger.info(f"Using temporary directory: {temp_dir}")
    
    try:
        logger.info(f"Parsing PPTX file: {input_path}")
        slides_dir = os.path.join(temp_dir, 'slides')
        slides = parse_ppt(input_path, slides_dir)
        logger.info(f"Extracted {len(slides)} slides")
        
        logger.info("Synthesizing speech...")
        audio_files = []
        durations = []
        texts = []
        
        for i, slide in enumerate(slides, 1):
            logger.info(f"Processing slide {i}/{len(slides)}")
            
            if not slide.notes_text:
                logger.warning(f"Slide {i} has no notes text, creating silent segment")
                audio_path = os.path.join(temp_dir, f"audio_{i:03d}.mp3")
                try:
                    subprocess.run([
                        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                        '-t', '2', '-c:a', 'libmp3lame', audio_path
                    ], capture_output=True, check=True)
                except:
                    pass
                audio_files.append(audio_path)
                durations.append(2.0)
                texts.append("")
                continue
            
            audio_path = os.path.join(temp_dir, f"audio_{i:03d}.mp4")
            
            voice = args.voice or config.voice
            speech_rate = config.speech_rate
            pitch_rate = config.pitch_rate
            audio_format = config.aliyun_format
            sample_rate = config.aliyun_sample_rate
            
            synthesize_speech(
                text=slide.notes_text,
                output_path=audio_path,
                access_key_id=config.aliyun_access_key_id,
                access_key_secret=config.aliyun_access_key_secret,
                app_key=config.aliyun_app_key,
                voice=voice,
                speech_rate=speech_rate,
                pitch_rate=pitch_rate,
                audio_format=audio_format,
                sample_rate=sample_rate
            )
            
            duration = get_audio_duration(audio_path)
            audio_files.append(audio_path)
            durations.append(duration)
            texts.append(slide.notes_text)
            
            logger.info(f"Slide {i}: duration={duration:.2f}s")
        
        logger.info("Generating subtitle file...")
        subtitle_file = ""
        if not args.no_subtitle and config.subtitle_enabled:
            subtitle_file = os.path.join(temp_dir, 'subtitle.ass')
            generate_subtitle(texts, durations, subtitle_file)
            logger.info(f"Subtitle saved to: {subtitle_file}")
        
        logger.info("Merging into video...")
        resolution = config.video_resolution
        fps = config.video_fps
        
        full_config = get_config_dict(config)
        
        if args.no_subtitle:
            full_config['subtitle']['enabled'] = False
        
        merge_to_video_rock_solid(
            slides=slides,
            audio_files=audio_files,
            output_path=output_path,
            resolution=resolution,
            fps=fps,
            config=full_config
        )
        
        logger.info(f"Video saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        if not args.keep_temp:
            logger.info("Cleaning up temporary files...")
            shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            logger.info(f"Temporary files kept at: {temp_dir}")


def main():
    args = parse_arguments()
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    config = load_config(args.config)
    
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)
    
    process_pptx(args.input, args.output, config, args)
    logger.info("Processing completed successfully!")


if __name__ == "__main__":
    import subprocess
    main()
