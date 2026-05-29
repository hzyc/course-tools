---
name: "ppt-to-video"
description: "Convert PPTX files to MP4 videos with Aliyun TTS voiceover and subtitles. Invoke when user wants to convert PowerPoint presentations to videos."
---

# PPT to Video Converter

This skill converts PowerPoint (PPTX) files to MP4 videos with Aliyun TTS voiceover narration and subtitles embedded in the video.

## Features

- 📊 Converts PPTX slides to images
- 🎙️ Uses Aliyun TTS for high-quality voice synthesis
- 📝 Generates and embeds subtitles
- ✨ Supports slide transition animations
- 🎬 Outputs in 720p HD resolution
- 📁 Batch conversion support

## When to Use

Invoke this skill when:
- User asks to convert PPT/PPTX to video
- User wants to create narrated presentation videos
- User mentions converting PowerPoint files to MP4

## Usage

### Single File Conversion

```bash
python main.py input.pptx output.mp4
```

### Batch Conversion

```bash
# Using PowerShell
.\batch_convert.ps1

# Or using Python
python batch_convert.py
```

## Configuration

Edit `config.json` to customize:
- Aliyun TTS credentials and voice settings
- Video resolution and quality
- Subtitle appearance
- Transition animation

## Requirements

- FFmpeg must be installed and in PATH
- Aliyun account with TTS services enabled
- Python dependencies installed

## Example

```bash
# Convert a single file
python main.py "input/1民法典总则编.pptx" "output/1民法典总则编.mp4"

# Batch convert all PPTX files in input folder
.\batch_convert.ps1
```
