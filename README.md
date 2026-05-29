# 🎬 视频处理工具集

这是一个强大的视频处理工具集，包含三个实用的技能（Skills），帮助你高效处理各种视频任务。

## 📦 包含的工具

### 1️⃣ PPT转视频工具 (ppt-to-video)

将PowerPoint演示文稿一键转换为带配音的MP4视频。

**核心功能：**
- 📊 智能解析PPT幻灯片和备注
- 🎙️ 阿里云TTS高质量语音合成
- 📝 自动生成卡拉OK风格字幕
- ✨ 页面切换动画特效
- 📁 批量转换支持

**快速开始：**
```bash
# 单个文件
python main.py input.pptx output.mp4

# 批量转换
.\batch_convert.ps1
```

**[详细文档](skills_promotion/ppt-to-video-promotion.md)**

---

### 2️⃣ 视频合并工具 (video-merger)

快速、简单、保持高质量地将多个视频文件合并成一个。

**核心功能：**
- 🎬 智能扫描并排序视频文件
- ⚡ FFmpeg流复制极速合并
- 🔄 自动降级重编码处理不兼容格式
- 📁 支持多种视频格式（MP4、MKV、AVI、MOV等）
- 💾 无损画质保持

**快速开始：**
```bash
# 合并文件夹中的所有视频
python merge_videos.py folder ./my_videos -o output.mp4

# 合并指定视频列表
python merge_videos.py list video1.mp4 video2.mp4 -o output.mp4
```

**[详细文档](skills_promotion/video-merger-promotion.md)**

---

### 3️⃣ 视频音频替换工具 (audio-replacer)

智能替换视频音频，保持时长完美对齐。

**核心功能：**
- 🎯 OpenAI Whisper本地ASR识别
- 🎙️ 阿里云TTS高质量语音合成
- ⏱️ 智能时长精确对齐
- 🔊 无损音质提升
- 📁 批量处理支持

**快速开始：**
```bash
# 自动识别+合成
python audio_replacer.py input.mp4 output.mp4

# 使用手动文本
python audio_replacer.py input.mp4 output.mp4 --text "要合成的文本"

# 批量处理
.\batch_audio_replace.ps1 -InputDir "input" -OutputDir "output"
```

**[详细文档](skills_promotion/audio-replacer-promotion.md)**

---

## 🚀 安装

### 环境要求

- Python 3.8+
- FFmpeg（加入PATH环境变量）

### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 配置文件

复制 `config.json.template` 为 `config.json`，并填入你的阿里云凭证：

```json
{
  "aliyun": {
    "access_key_id": "你的AccessKeyID",
    "access_key_secret": "你的AccessKeySecret",
    "app_key": "你的AppKey",
    "voice": "xiaoyun",
    "speech_rate": 0,
    "pitch_rate": 0
  }
}
```

---

## 🎯 适用场景

| 场景 | 推荐工具 |
|------|---------|
| 课程制作 | ppt-to-video |
| 视频整理 | video-merger |
| 音质提升 | audio-replacer |
| 批量处理 | 所有工具均支持 |

---

## 💡 技术亮点

- 🎨 **本地优先**：减少云服务依赖，保护隐私
- ⚡ **高效处理**：FFmpeg加持，处理速度快
- 🔧 **灵活配置**：丰富的配置选项满足个性化需求
- 📊 **详细日志**：完善的日志记录便于问题排查

---

## 📚 相关资源

- [PPT转视频详细文档](skills_promotion/ppt-to-video-promotion.md)
- [视频合并详细文档](skills_promotion/video-merger-promotion.md)
- [音频替换详细文档](skills_promotion/audio-replacer-promotion.md)

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

**让视频处理变得简单高效！** 🚀
