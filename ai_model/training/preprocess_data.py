import os
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def preprocess_image(image_path, target_size=(224, 224)):
    """预处理单张图片"""
    try:
        # 读取图片
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 调整大小
        img = cv2.resize(img, target_size)
        
        # 归一化
        img = img.astype(np.float32) / 255.0
        
        return img
    except Exception as e:
        logger.error(f"图片预处理失败 {image_path}: {str(e)}")
        return None

def prepare_dataset(data_dir, output_dir):
    """准备数据集"""
    try:
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 这里需要实现数据集准备逻辑
        # 1. 读取数据集元数据
        # 2. 预处理图片
        # 3. 保存处理后的数据
        
        logger.info("数据集准备完成")
        
    except Exception as e:
        logger.error(f"数据集准备失败: {str(e)}")
        raise

if __name__ == "__main__":
    data_dir = "datasets/ham10000"
    output_dir = "datasets/processed"
    prepare_dataset(data_dir, output_dir) 