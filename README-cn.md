# PPTtoVideo

一个将 PPTX 文件转换为带 TTS 语音朗读和字幕的 MP4 视频的命令行工具。

## 功能特点

- 解析 PPTX 文件并提取幻灯片及备注
- 使用阿里云 TTS API 生成语音
- 创建 ASS 字幕文件
- 使用 FFmpeg 将幻灯片、音频和字幕合并为 MP4 视频

## 系统要求

- Python 3.10+
- FFmpeg（必须在系统 PATH 中）
- 阿里云 NLS API 凭证

## 安装步骤

1. 克隆项目仓库
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 安装 FFmpeg：
   - Windows：从 https://ffmpeg.org/ 下载并添加到 PATH
   - macOS：`brew install ffmpeg`
   - Linux：`sudo apt install ffmpeg`

## 配置说明

编辑 `config.json` 文件，设置你的阿里云凭证：

```json
{
  "aliyun": {
    "access_key_id": "你的AccessKey_ID",
    "access_key_secret": "你的AccessKey_Secret",
    "app_key": "你的AppKey",
    "voice": "xiaoyun"
  }
}
```

## 使用方法

基本用法：
```bash
python main.py input.pptx
```

指定输出文件：
```bash
python main.py input.pptx -o output.mp4
```

使用自定义配置文件：
```bash
python main.py input.pptx -c my_config.json
```

禁用字幕：
```bash
python main.py input.pptx --no-subtitle
```

保留临时文件（用于调试）：
```bash
python main.py input.pptx --keep-temp
```

## 批量转换

使用 PowerShell 脚本批量转换 input 文件夹下的所有 PPT 文件：

```powershell
# 方式1：使用提供的批处理脚本
.\batch_convert.ps1
```

或者使用单行命令循环处理：

```powershell
# 方式2：单行命令
Get-ChildItem "input\*.pptx" | ForEach-Object { python main.py $_.FullName -o "output\$($_.BaseName).mp4" }
```

## 命令行选项

- `input`：输入 PPTX 文件（必需）
- `-o, --output`：输出 MP4 文件（默认：input_video.mp4）
- `-c, --config`：配置文件路径（默认：config.json）
- `-v, --voice`：指定 TTS 语音名称
- `-q, --quality`：视频质量（low/medium/high）
- `--no-subtitle`：禁用字幕生成
- `--keep-temp`：保留临时文件
- `-l, --log-level`：日志级别（DEBUG/INFO/WARNING/ERROR）

## 测试

运行测试：
```bash
pytest tests/
```

## 许可证

MIT
