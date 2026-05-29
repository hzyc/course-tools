# PPT课件生成工具设计文档

**日期：** 2026-05-28  
**项目名称：** PPTtoVideo  
**项目类型：** 命令行工具  

---

## 1. 项目概述

### 1.1 目标
将PPTX文件转换为带有语音朗读和字幕的MP4视频。用户只需提供PPTX文件和阿里云API凭证，即可生成可自动播放的课件视频。

### 1.2 核心功能
- 解析PPTX文件，提取每页幻灯片和备注文字
- 调用阿里云TTS API将备注转换为语音
- 逐页渲染幻灯片为图片
- 合成带字幕的MP4视频，每页时长自动匹配语音长度

---

## 2. 技术架构

### 2.1 技术栈
- **语言：** Python 3.10+
- **PPT解析：** python-pptx
- **PPT渲染：** LibreOffice（无头模式）或 python-pptx 直接导出
- **语音合成：** 阿里云 NLS TTS API
- **视频合成：** FFmpeg
- **字幕生成：** FFmpeg ASS/Burn subtitle

### 2.2 系统架构

```
PPTX文件
    │
    ▼
┌─────────────────┐
│  PPT解析模块     │  提取幻灯片图片 + 备注文字
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  阿里云TTS模块    │  生成语音文件（MP3/WAV）
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  视频合成模块     │  FFmpeg 合并图片 + 音频 + 字幕
└────────┬────────┘
         │
         ▼
MP4视频文件
```

---

## 3. 核心模块设计

### 3.1 PPT解析模块 (ppt_parser.py)

**功能：**
- 读取PPTX文件
- 提取每张幻灯片的内容
- 提取每张幻灯片的备注文字
- 将幻灯片导出为图片

**接口：**
```python
class PPTSlide:
    slide_number: int
    image_path: str  # 导出的图片路径
    notes_text: str  # 备注文字

def parse_ppt(pptx_path: str, output_dir: str) -> List[PPTSlide]
```

**实现细节：**
- 使用 `python-pptx` 读取幻灯片
- 使用 `Presentation.slide_images` 导出图片
- 备注文本通过 `Slide.notes_slide.notes_text_frame.text` 获取

### 3.2 阿里云TTS模块 (aliyun_tts.py)

**功能：**
- 调用阿里云NLS API进行语音合成
- 支持配置语音参数（语速、音调、音量）
- 生成音频文件

**接口：**
```python
def synthesize_speech(
    text: str,
    output_path: str,
    voice: str = "xiaoyun",  # 默认女声
    speech_rate: int = 0,    # 语速 -500~500
    pitch_rate: int = 0       # 音调 -500~500
) -> str  # 返回音频文件路径
```

**配置参数（通过config.json）：**
- `access_key_id`: 阿里云 AccessKey ID
- `access_key_secret`: 阿里云 AccessKey Secret
- `app_key`: 阿里云 NLS AppKey
- `voice`: 语音名称（默认xiaoyun）
- `speech_rate`: 语速
- `pitch_rate`: 音调

### 3.3 字幕生成模块 (subtitle_generator.py)

**功能：**
- 根据语音时长生成字幕
- 支持ASS/SSA格式（支持样式）
- 计算每段字幕的时间戳

**接口：**
```python
def generate_subtitle(
    texts: List[str],
    durations: List[float],  # 每段文字对应的语音时长（秒）
    output_path: str,
    style: SubtitleStyle = None
) -> str  # 返回字幕文件路径
```

**字幕样式：**
- 字体：默认微软雅黑
- 字号：48
- 颜色：白色带黑色描边
- 位置：底部居中

### 3.4 视频合成模块 (video_merger.py)

**功能：**
- 使用FFmpeg将图片、音频、字幕合成为视频
- 每页幻灯片根据对应音频时长确定显示时长
- 输出720p MP4视频

**接口：**
```python
def merge_to_video(
    slides: List[PPTSlide],
    audio_files: List[str],
    subtitle_file: str,
    output_path: str,
    resolution: Tuple[int, int] = (1280, 720),
    fps: int = 1
) -> str  # 返回最终视频路径
```

**FFmpeg参数：**
- `-c:v libx264`: H.264编码
- `-c:a aac`: AAC音频编码
- `-preset medium`: 编码速度/质量平衡
- `-crf 23`: 视频质量

### 3.5 主程序 (main.py / cli.py)

**命令行接口：**
```bash
python ppt_to_video.py input.pptx -o output.mp4
python ppt_to_video.py input.pptx --config config.json
```

**参数：**
- `input`: 输入PPTX文件路径（必需）
- `-o, --output`: 输出MP4文件路径（默认：input_video.mp4）
- `-c, --config`: 配置文件路径（默认：config.json）
- `-v, --voice`: 指定语音名称
- `-q, --quality`: 视频质量（low/medium/high）
- `--no-subtitle`: 不生成字幕
- `--keep-temp`: 保留临时文件

---

## 4. 数据流

### 4.1 处理流程

```
1. 初始化
   ├─ 加载配置文件
   ├─ 检查FFmpeg是否可用
   └─ 创建临时工作目录

2. PPT解析
   ├─ 读取PPTX文件
   ├─ 提取每页幻灯片
   ├─ 提取备注文字
   └─ 导出幻灯片为PNG图片

3. 语音合成
   ├─ 遍历每页备注
   ├─ 调用阿里云TTS API
   ├─ 获取语音文件
   └─ 获取语音时长

4. 字幕生成
   ├─ 准备字幕文本
   ├─ 根据语音时长计算时间戳
   └─ 生成ASS字幕文件

5. 视频合成
   ├─ 准备FFmpeg输入文件
   ├─ 构建FFmpeg命令
   └─ 执行视频合成

6. 清理
   ├─ 删除临时文件
   └─ 输出最终视频
```

### 4.2 临时文件管理
- 临时文件保存在系统临时目录或指定的 `temp/` 文件夹
- 临时文件包括：幻灯片图片、中间音频文件、中间视频片段
- 可通过 `--keep-temp` 参数保留临时文件用于调试

---

## 5. 配置管理

### 5.1 config.json 格式
```json
{
  "aliyun": {
    "access_key_id": "your_access_key_id",
    "access_key_secret": "your_access_key_secret",
    "app_key": "your_app_key",
    "voice": "xiaoyun",
    "speech_rate": 0,
    "pitch_rate": 0
  },
  "video": {
    "resolution": "1280x720",
    "fps": 1,
    "quality": "medium"
  },
  "subtitle": {
    "enabled": true,
    "font": "Microsoft YaHei",
    "font_size": 48,
    "color": "white",
    "position": "bottom"
  }
}
```

---

## 6. 错误处理

### 6.1 常见错误及处理

| 错误类型 | 处理方式 |
|---------|---------|
| PPT文件不存在 | 提示错误并退出 |
| PPT文件损坏/不支持 | 提示具体错误信息 |
| 阿里云API调用失败 | 记录错误，重试3次后退出 |
| FFmpeg未安装 | 提示安装FFmpeg并退出 |
| 磁盘空间不足 | 检查可用空间，不足时警告 |
| 备注文字为空 | 跳过该页或生成静音段 |

### 6.2 日志记录
- 使用Python logging模块
- 日志级别可通过参数调整
- 日志输出到控制台和文件

---

## 7. 项目结构

```
PPTtovideo/
├── main.py              # 主程序入口
├── ppt_parser.py        # PPT解析模块
├── aliyun_tts.py         # 阿里云TTS模块
├── subtitle_generator.py # 字幕生成模块
├── video_merger.py       # 视频合成模块
├── config.py             # 配置管理模块
├── requirements.txt      # 依赖列表
├── config.json           # 默认配置文件
├── README.md             # 使用说明
└── docs/
    └── specs/            # 设计文档
```

---

## 8. 依赖项

```
python-pptx>=0.6.21
requests>=2.28.0
aliyun-openapi-nls-python>=1.0.0
Pillow>=9.0.0
```

---

## 9. 性能考虑

### 9.1 优化策略
- PPT渲染：使用LibreOffice无头模式批量渲染
- 语音合成：支持批量提交减少API调用次数
- 视频合成：分片处理，最后合并

### 9.2 预估耗时（基于10页PPT）
- PPT解析：5-10秒
- 语音合成：10-20秒（取决于网络）
- 视频合成：20-40秒
- **总计：约1-2分钟**

---

## 10. 使用示例

### 基本用法
```bash
python main.py lecture.pptx -o lecture_video.mp4
```

### 使用自定义配置
```bash
python main.py lecture.pptx -c my_config.json
```

### 指定语音和保留临时文件
```bash
python main.py lecture.pptx --voice zhixia --keep-temp
```

---

## 11. 后续扩展（可选）

- [ ] 支持批量处理文件夹
- [ ] 添加预览模式
- [ ] 支持自定义字幕样式
- [ ] 添加进度条显示
- [ ] 支持更多视频分辨率
- [ ] 添加水印功能
