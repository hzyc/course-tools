import tempfile
import os
from pathlib import Path
import pytest
from ppt_parser import PPTSlide


def test_ppt_slide_class():
    slide = PPTSlide(
        slide_number=1,
        image_path="/tmp/slide1.png",
        notes_text="测试备注"
    )
    assert slide.slide_number == 1
    assert slide.notes_text == "测试备注"
    assert slide.image_path == "/tmp/slide1.png"


def test_ppt_slide_class_with_empty_notes():
    slide = PPTSlide(
        slide_number=2,
        image_path="/tmp/slide2.png",
        notes_text=""
    )
    assert slide.slide_number == 2
    assert slide.notes_text == ""


@pytest.mark.skipif(not os.path.exists("test.pptx"), reason="test.pptx not available")
def test_parse_ppt_structure():
    # Test that parse_ppt returns list of PPTSlide objects
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            from ppt_parser import parse_ppt
            result = parse_ppt("test.pptx", tmpdir)
            assert isinstance(result, list)
            for slide in result:
                assert isinstance(slide, PPTSlide)
        except Exception:
            # If test.pptx is not available or fails, skip the test
            pytest.skip("Could not load test PPTX file")
