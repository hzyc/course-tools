
# tests/test_subtitle.py
import tempfile
import os
from subtitle_generator import generate_subtitle, SubtitleStyle

def test_generate_subtitle_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        texts = ["第一段文字", "第二段文字"]
        durations = [2.5, 3.0]
        output_path = os.path.join(tmpdir, "subtitle.ass")
        
        result = generate_subtitle(texts, durations, output_path)
        assert result == output_path
        assert os.path.exists(output_path)
        
        # Verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "第一段文字" in content
            assert "第二段文字" in content

def test_subtitle_style_class():
    style = SubtitleStyle(
        font="Arial",
        font_size=36,
        color="yellow",
        position="top"
    )
    assert style.font == "Arial"
    assert style.font_size == 36

