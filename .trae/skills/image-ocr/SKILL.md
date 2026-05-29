---
name: "image-ocr"
description: "Extract text from images using local OCR. Invoke when user wants to extract text from images or screenshots."
---

# Image OCR Tool

This skill extracts text from images using local OCR engines (PaddleOCR or EasyOCR) with excellent Chinese and English support.

## Features

- 🔤 Extract text from images (PNG, JPG, BMP, etc.)
- 🇨🇳 Excellent Chinese and English support
- 📝 Save extracted text to files
- 📁 Batch processing of multiple images
- 🔄 Auto-fallback between PaddleOCR and EasyOCR
- 💾 No network dependency after model download

## When to Use

Invoke this skill when:
- User asks to extract text from images
- User wants OCR on screenshots or photos
- User mentions extracting text from documents
- User has images with Chinese or mixed English text

## Usage

### Single Image OCR

```bash
python image_ocr.py input.png
```

### Save to File

```bash
python image_ocr.py input.png -o output.txt
```

### Batch Process Directory

```bash
python image_ocr.py --dir ./images --output-dir ./texts
```

## Requirements

- FFmpeg is not required for this tool
- Python dependencies:
  - PaddleOCR + PaddlePaddle (recommended for Chinese)
  - OR EasyOCR
- First run will auto-download OCR models (~100-200MB)

## OCR Engine Priority

1. **PaddleOCR** (default, better Chinese support)
2. **EasyOCR** (fallback option)

## Install Dependencies

```bash
# Option 1: Install PaddleOCR (recommended)
pip install paddleocr paddlepaddle

# Option 2: Install EasyOCR
pip install easyocr
```

## Supported Formats

- PNG
- JPG/JPEG
- BMP
- TIFF
- WEBP

## Notes

- First run will download model files automatically
- Models are cached for future use
- Both simplified Chinese and English work best
- Works with printed text, handwritten less accurate
