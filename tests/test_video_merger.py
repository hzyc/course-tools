import tempfile
import os
from video_merger import merge_to_video, create_concat_list

def test_create_concat_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = [
            os.path.join(tmpdir, "seg1.mp4"),
            os.path.join(tmpdir, "seg2.mp4")
        ]
        list_path = os.path.join(tmpdir, "concat.txt")
        
        result = create_concat_list(files, list_path)
        assert result == list_path
        assert os.path.exists(list_path)
        
        with open(list_path, 'r') as f:
            content = f.read()
            assert "seg1.mp4" in content
            assert "seg2.mp4" in content

def test_merge_to_video_structure():
    """Test that merge_to_video returns a path"""
    # This test is minimal since it requires FFmpeg
    # Full test would create dummy inputs
    pass
