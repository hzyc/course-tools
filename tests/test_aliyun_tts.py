import tempfile
import os
from aliyun_tts import synthesize_speech, get_audio_duration

def test_synthesize_speech_returns_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "test.mp3")
        result = synthesize_speech("测试文字", output_path)
        assert result == output_path
        assert os.path.exists(output_path)

def test_get_audio_duration():
    # Create a dummy audio file for testing
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        dummy_path = f.name
    
    try:
        duration = get_audio_duration(dummy_path)
        assert duration > 0
    finally:
        os.unlink(dummy_path)
