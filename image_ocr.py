#!/usr/bin/env python3
"""
图片文字提取工具 (OCR)
使用本地PaddleOCR或easyocr进行文字识别
"""

import os
import argparse
import logging
from pathlib import Path
from typing import Optional, List, Tuple

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_text_from_image(image_path: str, output_path: Optional[str] = None) -> str:
    """
    从图片中提取文字
    
    Args:
        image_path: 图片文件路径
        output_path: 输出文本文件路径（可选）
    
    Returns:
        提取的文字
    """
    try:
        # 尝试使用PaddleOCR
        try:
            from paddleocr import PaddleOCR
            logger.info("正在加载PaddleOCR模型...")
            ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            logger.info(f"正在识别图片: {image_path}")
            result = ocr.ocr(image_path, cls=True)
            
            text_lines = []
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) > 1:
                        text = line[1][0]
                        text_lines.append(text)
            
            extracted_text = '\n'.join(text_lines)
            logger.info(f"✅ 成功提取 {len(extracted_text)} 个字符")
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                logger.info(f"📝 文本已保存到: {output_path}")
            
            return extracted_text
            
        except ImportError:
            logger.warning("PaddleOCR未安装，尝试使用easyocr...")
            pass
        
        # 尝试使用easyocr
        try:
            import easyocr
            logger.info("正在加载EasyOCR模型...")
            reader = easyocr.Reader(['ch_sim', 'en'])
            logger.info(f"正在识别图片: {image_path}")
            result = reader.readtext(image_path)
            
            text_lines = []
            for detection in result:
                if len(detection) > 1:
                    text_lines.append(detection[1])
            
            extracted_text = '\n'.join(text_lines)
            logger.info(f"✅ 成功提取 {len(extracted_text)} 个字符")
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                logger.info(f"📝 文本已保存到: {output_path}")
            
            return extracted_text
            
        except ImportError:
            logger.error("未安装OCR库！")
            logger.info("请运行: pip install paddleocr paddlepaddle")
            logger.info("或者: pip install easyocr")
            return ""
            
    except Exception as e:
        logger.error(f"图片文字提取失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return ""

def batch_extract_images(input_dir: str, output_dir: str) -> None:
    """
    批量提取图片文字
    
    Args:
        input_dir: 输入图片目录
        output_dir: 输出文本目录
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp']
    
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(input_dir).glob(f'*{ext}'))
        image_files.extend(Path(input_dir).glob(f'*{ext.upper()}'))
    
    if not image_files:
        logger.warning(f"在 {input_dir} 中未找到图片文件")
        return
    
    logger.info(f"找到 {len(image_files)} 个图片文件")
    
    for img_path in image_files:
        output_file = os.path.join(output_dir, f"{img_path.stem}.txt")
        logger.info(f"\n处理: {img_path.name}")
        extract_text_from_image(str(img_path), output_file)

def main():
    parser = argparse.ArgumentParser(
        description="图片文字提取工具 (OCR)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单个图片
  python image_ocr.py input.png
  
  # 单个图片并保存到文件
  python image_ocr.py input.png -o output.txt
  
  # 批量处理
  python image_ocr.py --dir ./images --output ./texts
        """
    )
    
    parser.add_argument('image', type=str, nargs='?', help='输入图片文件路径')
    parser.add_argument('-o', '--output', type=str, help='输出文本文件路径')
    parser.add_argument('--dir', type=str, help='批量处理的图片目录')
    parser.add_argument('--output-dir', type=str, help='批量处理的输出目录')
    
    args = parser.parse_args()
    
    if args.dir:
        output_dir = args.output_dir or args.dir
        batch_extract_images(args.dir, output_dir)
    elif args.image:
        if not os.path.exists(args.image):
            logger.error(f"文件不存在: {args.image}")
            return
        extract_text_from_image(args.image, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
