#!/usr/bin/env python3
"""
下载图片并提取文字
"""

import os
import requests
import argparse
from urllib.parse import urlparse
from pathlib import Path

def download_image(url: str, save_path: str) -> bool:
    """
    下载图片
    
    Args:
        url: 图片URL
        save_path: 保存路径
    
    Returns:
        是否成功
    """
    try:
        print(f"正在下载图片: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 图片已保存到: {save_path}")
        return True
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

def extract_text_from_url(image_url: str) -> str:
    """
    从URL下载图片并提取文字
    
    Args:
        image_url: 图片URL
    
    Returns:
        提取的文字
    """
    # 创建临时目录
    temp_dir = "temp_ocr"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 解析URL获取文件名
    parsed = urlparse(image_url)
    filename = os.path.basename(parsed.path)
    if not filename:
        filename = "downloaded_image.png"
    save_path = os.path.join(temp_dir, filename)
    
    # 下载图片
    if not download_image(image_url, save_path):
        return ""
    
    # 提取文字
    try:
        from image_ocr import extract_text_from_image
        output_text = os.path.join(temp_dir, "extracted_text.txt")
        text = extract_text_from_image(save_path, output_text)
        return text
    except Exception as e:
        print(f"OCR失败: {e}")
        return ""

def main():
    parser = argparse.ArgumentParser(description="从URL下载图片并提取文字")
    parser.add_argument('url', type=str, help='图片URL')
    
    args = parser.parse_args()
    
    text = extract_text_from_url(args.url)
    if text:
        print("\n" + "="*50)
        print("提取的文字:")
        print("="*50)
        print(text)
        print("="*50)

if __name__ == "__main__":
    main()
