
# tests/test_main.py
import argparse
from main import parse_arguments

def test_parse_arguments_defaults():
    args = parse_arguments(['input.pptx'])
    assert args.input == 'input.pptx'
    assert args.output == 'input_video.mp4'
    assert args.config == 'config.json'

def test_parse_arguments_custom():
    args = parse_arguments([
        'lecture.pptx',
        '-o', 'lecture_video.mp4',
        '-c', 'custom_config.json',
        '--voice', 'zhixia',
        '--keep-temp'
    ])
    assert args.input == 'lecture.pptx'
    assert args.output == 'lecture_video.mp4'
    assert args.config == 'custom_config.json'
    assert args.voice == 'zhixia'
    assert args.keep_temp == True
