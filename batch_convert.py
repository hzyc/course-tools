#!/usr/bin/env python3
"""
批量转换PPT文件的Python脚本
更可靠、更简单的方式
支持跳过已完成的文件
"""

import os
import subprocess
from pathlib import Path

# 配置
INPUT_FOLDER = "d:/Code/PPTtovideo/input"
OUTPUT_FOLDER = "d:/Code/PPTtovideo/output"

def main():
    print("=" * 50)
    print("  PPT批量转视频工具")
    print("=" * 50)
    print()
    
    # 确保输出文件夹存在
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # 获取所有PPT文件
    input_path = Path(INPUT_FOLDER)
    ppt_files = sorted(list(input_path.glob("*.pptx")))
    
    if not ppt_files:
        print("❌ 未找到PPT文件！")
        return
    
    # 检查哪些已经完成
    to_process = []
    for ppt in ppt_files:
        output_file = Path(OUTPUT_FOLDER) / (ppt.stem + ".mp4")
        if output_file.exists():
            print(f"⏭️  跳过已完成：{ppt.name}")
        else:
            to_process.append(ppt)
    
    print()
    if not to_process:
        print("✅ 所有文件都已转换完成！")
        return
    
    print(f"🚀 需要转换 {len(to_process)} 个文件：")
    for ppt in to_process:
        print(f"  - {ppt.name}")
    print()
    
    # 逐个转换
    success = 0
    failed = 0
    
    for idx, ppt_file in enumerate(to_process, 1):
        print("-" * 50)
        print(f"[{idx}/{len(to_process)}] 正在处理：{ppt_file.name}")
        print("-" * 50)
        
        # 输出文件名
        output_file = Path(OUTPUT_FOLDER) / (ppt_file.stem + ".mp4")
        
        try:
            # 调用主程序
            result = subprocess.run([
                "python",
                "d:/Code/PPTtovideo/main.py",
                str(ppt_file),
                "-o",
                str(output_file)
            ], check=True)
            
            print(f"\n✅ {ppt_file.name} 转换完成！")
            print(f"   输出：{output_file}")
            success += 1
            
        except Exception as e:
            print(f"\n❌ {ppt_file.name} 转换失败！")
            print(f"   错误：{e}")
            failed += 1
        
        print()
    
    # 总结
    print("=" * 50)
    print("  批量转换完成！")
    print(f"  成功：{success}")
    print(f"  失败：{failed}")
    print(f"  跳过：{len(ppt_files) - len(to_process)}")
    print("=" * 50)

if __name__ == "__main__":
    main()
