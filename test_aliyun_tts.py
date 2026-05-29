#!/usr/bin/env python3
"""
测试阿里云TTS
"""
import os
import sys
import tempfile

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config
from aliyun_tts import AliyunTTS, synthesize_speech


def test_aliyun_tts():
    """测试阿里云TTS"""
    print("=" * 60)
    print("  阿里云TTS测试")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    print(f"✅ 配置加载成功")
    print(f"   Access Key ID: {config.aliyun_access_key_id[:10]}...")
    print(f"   App Key: {config.aliyun_app_key}")
    print(f"   默认音色: {config.voice}")
    print()
    
    # 测试文本
    test_text = "你好，这是阿里云语音合成的测试声音。欢迎使用PPT转视频工具！"
    
    # 输出文件
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_aliyun_tts.wav")
    
    print(f"📝 测试文本: {test_text}")
    print(f"📤 输出文件: {output_path}")
    print()
    
    # 直接测试
    try:
        tts = AliyunTTS(
            config.aliyun_access_key_id,
            config.aliyun_access_key_secret,
            config.aliyun_app_key
        )
        
        result = tts.synthesize(
            test_text,
            output_path,
            voice=config.voice,
            speech_rate=config.speech_rate,
            pitch_rate=config.pitch_rate
        )
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print()
            print("=" * 60)
            print(f"✅ 测试成功！")
            print(f"📊 音频大小: {file_size} 字节")
            print(f"📁 文件路径: {os.path.abspath(output_path)}")
            print("=" * 60)
            return True
        else:
            print("❌ 文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_aliyun_tts()
    sys.exit(0 if success else 1)
