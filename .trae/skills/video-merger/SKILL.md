---
name: "video-merger"
description: "Merge multiple video files into one using FFmpeg. Invoke when user wants to concatenate or combine video files."
---

# Video Merger

This skill merges multiple video files into a single video file using FFmpeg with two modes: folder-based merging and list-based merging.

## Features

- 🎬 Merge videos by folder (auto-detects video files)
- 📋 Merge videos from explicit file list
- 📁 Supports multiple video formats (MP4, MKV, AVI, MOV, WMV, FLV, WebM)
- 🔀 Sort by filename or modification date
- ⚡ Fast merge with stream copy (no re-encoding)
- 🔄 Auto-fallback to re-encoding if stream copy fails

## When to Use

Invoke this skill when:
- User asks to merge/combine/concatenate videos
- User wants to join multiple video files
- User mentions combining video clips

## Usage

### Merge by Folder

```bash
# Merge all videos in a folder, sorted by name
python merge_videos.py folder ./my_videos -o output.mp4

# Sort by date modified
python merge_videos.py folder ./my_videos -o output.mp4 -s date
```

### Merge by List

```bash
# Merge specific files in order
python merge_videos.py list video1.mp4 video2.mp4 video3.mp4 -o output.mp4
```

## Sorting Options

- `name`: Sort alphabetically by filename (default)
- `date`: Sort by modification time (oldest first)

## Requirements

- FFmpeg must be installed and in PATH

## Examples

```bash
# Basic folder merge
python merge_videos.py folder ./output -o final_video.mp4

# Custom FFmpeg path
python merge_videos.py folder ./videos -o merged.mp4 --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe"

# List specific files
python merge_videos.py list part1.mp4 part2.mp4 part3.mp4 -o complete.mp4
```

## Notes

- Videos should have compatible codecs, resolution, and framerate for best results
- If stream copy fails, tool will automatically try re-encoding
- Re-encoding preserves quality but takes longer
