#!/usr/bin/env python3
"""
视频合并工具
使用ffmpeg合并多个视频文件
支持两种模式：
1. 按文件名排序合并
2. 按指定列表合并
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List
import argparse

def check_ffmpeg() -> bool:
    """检查ffmpeg是否可用"""
    try:
        subprocess.run(['ffmpeg', '-version'],
                   capture_output=True, check=True)
        return True
    except:
        return False

def merge_videos_by_folder(folder: str, output: str = "merged_output.mp4", sort_by: str = "name", ffmpeg_path: str = "ffmpeg"):
    """
    合并文件夹中的所有视频文件
    
    Args:
        folder: 包含视频文件的文件夹路径
        output: 输出文件名
        sort_by: 排序方式 (name/date)
        ffmpeg_path: ffmpeg可执行文件路径
    """
    folder_path = Path(folder)
    
    if not folder_path.exists():
        raise ValueError(f"文件夹不存在: {folder}")
    
    # 支持的视频扩展名
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']
    
    # 获取所有视频文件
    video_files = []
    for ext in video_extensions:
        video_files.extend(folder_path.glob(f"*{ext}"))
        video_files.extend(folder_path.glob(f"*{ext.upper()}"))
    
    if not video_files:
        print(f"❌ 在文件夹中未找到视频文件: {folder}")
        return False
    
    # 排序
    if sort_by == "date":
        video_files.sort(key=lambda x: x.stat().st_mtime)
    else:
        video_files.sort(key=lambda x: x.name)
    
    print(f"✅ 找到 {len(video_files)} 个视频文件:")
    for i, vf in enumerate(video_files, 1):
        print(f"  {i}. {vf.name}")
    
    # 创建ffmpeg合并列表文件
    list_file = folder_path / "merge_list.txt"
    
    with open(list_file, "w", encoding="utf-8") as f:
        for vf in video_files:
            # 使用绝对路径，避免路径问题
            abs_path = str(vf.absolute()).replace("\\", "/")
            f.write(f"file '{abs_path}'\n")
    
    print(f"\n📝 合并列表已创建: {list_file}")
    
    # 使用ffmpeg合并
    output_path = folder_path / output
    print(f"\n🎬 开始合并到: {output_path}")
    
    try:
        cmd = [
            ffmpeg_path,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",  # 不重新编码，快速合并
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=False, check=True)
        print(f"\n✅ 合并完成! 输出: {output_path}")
        
        # 清理临时文件
        try:
            list_file.unlink()
        except:
            pass
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 合并失败")
        print(f"错误代码: {e.returncode}")
        print(f"可能原因: 视频编码/分辨率/帧率不一致，需要重新编码中...")
        
        # 尝试重新编码合并
        print("\n🔄 尝试重新编码合并...")
        
        try:
            cmd = [
                ffmpeg_path,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-preset", "medium",
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=False, check=True)
            print(f"\n✅ 重新编码合并完成! 输出: {output_path}")
            
            try:
                list_file.unlink()
            except:
                pass
            
            return True
            
        except Exception as e2:
            print(f"\n❌ 重新编码也失败了: {e2}")
            return False


def merge_videos_by_list(file_list: List[str], output: str = "merged_output.mp4", ffmpeg_path: str = "ffmpeg"):
    """
    按指定列表合并视频文件
    
    Args:
        file_list: 视频文件路径列表
        output: 输出文件名
        ffmpeg_path: ffmpeg可执行文件路径
    """
    # 验证文件是否存在
    valid_files = []
    for f in file_list:
        fp = Path(f)
        if fp.exists():
            valid_files.append(fp)
        else:
            print(f"⚠️  文件不存在: {f}")
    
    if not valid_files:
        print("❌ 没有有效的视频文件")
        return False
    
    print(f"✅ 使用 {len(valid_files)} 个文件:")
    for i, vf in enumerate(valid_files, 1):
        print(f"  {i}. {vf.name}")
    
    # 创建临时目录
    temp_dir = Path(".temp_merge")
    temp_dir.mkdir(exist_ok=True)
    list_file = temp_dir / "merge_list.txt"
    
    with open(list_file, "w", encoding="utf-8") as f:
        for vf in valid_files:
            abs_path = str(vf.absolute()).replace("\\", "/")
            f.write(f"file '{abs_path}'\n")
    
    output_path = Path(output) if Path(output).is_absolute() else Path.cwd() / output
    
    print(f"\n🎬 开始合并到: {output_path}")
    
    try:
        cmd = [
            ffmpeg_path,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=False, check=True)
        print(f"\n✅ 合并完成! 输出: {output_path}")
        
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"\n❌ 合并失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="视频合并工具")
    
    subparsers = parser.add_subparsers(title="命令", dest="command")
    
    # 文件夹合并命令
    folder_parser = subparsers.add_parser("folder", help="合并文件夹中的所有视频")
    folder_parser.add_argument("folder", help="包含视频文件的文件夹路径")
    folder_parser.add_argument("-o", "--output", default="merged_output.mp4", help="输出文件名")
    folder_parser.add_argument("-s", "--sort", choices=["name", "date"], default="name", help="排序方式: name(按名称)/date(按日期)")
    folder_parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg可执行文件路径")
    
    # 列表合并命令
    list_parser = subparsers.add_parser("list", help="按列表合并视频")
    list_parser.add_argument("files", nargs="+", help="要合并的视频文件列表")
    list_parser.add_argument("-o", "--output", default="merged_output.mp4", help="输出文件名")
    list_parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg可执行文件路径")
    
    args = parser.parse_args()
    
    if not check_ffmpeg():
        print("❌ 未找到ffmpeg，请先安装ffmpeg并添加到PATH")
        sys.exit(1)
    
    if args.command == "folder":
        merge_videos_by_folder(args.folder, args.output, args.sort, args.ffmpeg)
    elif args.command == "list":
        merge_videos_by_list(args.files, args.output, args.ffmpeg)
    else:
        # 如果没有指定命令，显示帮助
        parser.print_help()


if __name__ == "__main__":
    main()
