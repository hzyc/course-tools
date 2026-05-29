---
name: "audio-replacer"
description: "Replace video audio with Whisper ASR + Aliyun TTS while preserving duration. Invoke when user wants to replace or regenerate video audio."
---

# Video Audio Replacer

This skill extracts audio from a video, recognizes speech content with Whisper ASR (offline, no file size limits), regenerates high-quality audio with Aliyun TTS, and replaces the audio back into the video while maintaining perfect duration alignment.

## Features

- 🔊 Extract audio from video files (compressed MP3 format)
- 🎯 Local Whisper ASR for accurate speech recognition (no file size limits!)
- 🎙️ Aliyun TTS for high-quality voice synthesis
- ⏱️ Smart duration alignment with audio speed adjustment
- 🎬 Replace audio while keeping original video quality
- 📝 Manual text input support (skip ASR)
- 📁 Batch processing support
- 🚀 Offline ASR with Whisper (fast, reliable, no API limits)

## When to Use

Invoke this skill when:
- User asks to replace video audio
- User wants to regenerate narration with TTS
- User mentions improving/upgrading video audio quality
- User wants to change the voice in a video
- User has long videos (over 2MB audio) that exceed cloud ASR limits

## Usage

### Full ASR + TTS Pipeline (Default - Local Whisper)

```bash
python audio_replacer.py input.mp4 output.mp4
```

### Use Manual Text (Skip ASR)

```bash
python audio_replacer.py input.mp4 output.mp4 --text "This is the narration text"
```

### Read Text from File

```bash
python audio_replacer.py input.mp4 output.mp4 --text-file script.txt
```

### Custom Voice

```bash
python audio_replacer.py input.mp4 output.mp4 --voice xiaogang
```

## Available Voices

| Voice | Gender | Description |
|-------|--------|-------------|
| xiaoyun | Female | Xiaoyun (default) |
| xiaogang | Male | Xiaogang |
| aixia | Female | Aixia |
| aiqi | Female | Aiqi |
| aijia | Female | Aijia |
| aixiaomei | Female | Aixiaomei |
| aiwei | Male | Aiwei |
| aibao | Male | Aibao |

## Batch Processing

```powershell
# Process all videos in a folder
.\batch_audio_replace.ps1 -InputDir "output" -OutputDir "output_replaced"

# With custom voice
.\batch_audio_replace.ps1 -InputDir "output" -OutputDir "output_replaced" -Voice "xiaogang"
```

## Configuration

Edit `config.json` to customize:
- Aliyun TTS credentials
- Default voice, speech rate, pitch
- Audio format and quality

## Requirements

- FFmpeg must be installed and in PATH
- Aliyun account with TTS services enabled
- Python dependencies installed (including openai-whisper and torch)
- First run will auto-download Whisper base model (~139MB)

## How It Works

1. Extracts audio from source video (compressed MP3 format)
2. Gets video duration
3. Recognizes speech content via local Whisper ASR (or uses manual text)
4. Synthesizes new audio with Aliyun TTS
5. Adjusts new audio speed to match original duration
6. Merges new audio with original video

## Duration Alignment

Uses FFmpeg's `atempo` filter to adjust audio speed while preserving quality:
- Single-step adjustment limited to 0.5x - 2.0x range
- Multi-step adjustment for larger changes
- Preserves natural-sounding audio

## Why Local Whisper ASR?

- ✅ No file size limits (processes any duration audio)
- ✅ No network dependency (offline after model download)
- ✅ Excellent Chinese speech recognition
- ✅ No API rate limits or costs
- ✅ Fast and reliable
