import json
import tempfile
from pathlib import Path
from config import Config, load_config

def test_load_default_config():
    config = Config()
    assert config.aliyun_access_key_id == ""
    assert config.video_resolution == (1280, 720)

def test_load_from_json():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "aliyun": {
                "access_key_id": "test_key",
                "voice": "zhixia"
            },
            "video": {
                "resolution": "1920x1080"
            }
        }, f)
        temp_path = f.name
    
    config = load_config(temp_path)
    assert config.aliyun_access_key_id == "test_key"
    assert config.voice == "zhixia"
    assert config.video_resolution == (1920, 1080)
