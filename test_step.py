#!/usr/bin/env python3
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ppt_parser import parse_ppt

print("=" * 50)
print("测试 1: 解析 PPTX 文件")
print("=" * 50)

ppt_file = "input/1民法典总则编.pptx"
temp_dir = "temp_test"

if not os.path.exists(ppt_file):
    print(f"找不到文件: {ppt_file}")
    sys.exit(1)

try:
    slides = parse_ppt(ppt_file, temp_dir)
    print(f"成功解析了 {len(slides)} 张幻灯片")
    for i, slide in enumerate(slides):
        print(f"  幻灯片 {i+1}:")
        print(f"    图片: {os.path.basename(slide.image_path)}")
        print(f"    备注: {slide.notes_text[:50]}..." if slide.notes_text else "    备注: (空)")
    
    print("\n✓ PPT 解析测试通过!\n")
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("测试 2: 检查 FFmpeg")
print("=" * 50)

from video_merger import check_ffmpeg

ffmpeg_ok = check_ffmpeg()
if ffmpeg_ok:
    print("✓ FFmpeg 可用")
else:
    print("✗ FFmpeg 未找到，请确保 FFmpeg 在 PATH 中")

print("\n" + "=" * 50)
print("测试 3: 测试语音合成")
print("=" * 50)

from aliyun_tts import synthesize_speech, get_audio_duration

test_text = "这是一个测试语音合成的句子。"
test_audio = os.path.join(temp_dir, "test_audio.wav")

try:
    result = synthesize_speech(test_text, test_audio)
    if os.path.exists(test_audio):
        print(f"✓ 音频文件已生成: {test_audio}")
        duration = get_audio_duration(test_audio)
        print(f"  时长: {duration:.2f} 秒")
    else:
        print("✗ 音频文件未生成")
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("测试完成!")
print("=" * 50)
