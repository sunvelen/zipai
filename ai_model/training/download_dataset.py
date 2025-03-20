import os
import requests
import zipfile
from pathlib import Path
import logging
import json
import shutil
from urllib.request import urlretrieve
import time
from kaggle.api.kaggle_api_extended import KaggleApi

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_kaggle_dataset():
    """从 Kaggle 下载皮肤数据集"""
    try:
        # 设置路径
        base_dir = Path(__file__).parent.parent.parent
        dataset_dir = base_dir / 'datasets' / 'skin_samples'
        
        # 创建数据集目录
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 Kaggle API
        api = KaggleApi()
        api.authenticate()
        
        # 下载数据集
        logger.info("开始下载皮肤数据集...")
        # 使用 Skin Cancer MNIST: HAM10000 数据集
        api.dataset_download_files('kmader/skin-cancer-mnist-ham10000', 
                                 path=str(dataset_dir),
                                 unzip=True)
        
        # 创建数据集信息文件
        dataset_info = {
            "source": "Kaggle - Skin Cancer MNIST: HAM10000",
            "dataset_url": "https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000",
            "description": "包含10000张皮肤病变图片的数据集，用于皮肤癌诊断",
            "categories": ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
        }
        
        with open(dataset_dir / "dataset_info.json", "w", encoding="utf-8") as f:
            json.dump(dataset_info, f, ensure_ascii=False, indent=2)
        
        logger.info("数据集下载完成")
        return dataset_dir
        
    except Exception as e:
        logger.error(f"数据集下载失败: {str(e)}")
        raise

def create_dummy_images():
    """如果无法下载图片，创建虚拟图片用于测试"""
    import numpy as np
    from PIL import Image

    categories = ["normal", "dry", "oily"]
    for category in categories:
        category_dir = Path(__file__).parent.parent.parent / 'datasets' / 'skin_samples' / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # 为每个类别创建两张测试图片
        for i in range(2):
            # 创建随机颜色的图片
            img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(category_dir / f"{category}_{i+1}.jpg")
            logger.info(f"创建测试图片: {category}_{i+1}.jpg")

def create_sample_dataset():
    """创建示例数据集"""
    try:
        # 尝试从 Kaggle 下载数据集
        try:
            return download_kaggle_dataset()
        except Exception as e:
            logger.error(f"从 Kaggle 下载失败: {str(e)}")
            logger.info("使用测试图片替代...")
            create_dummy_images()
            
            # 创建数据集信息文件
            base_dir = Path(__file__).parent.parent.parent
            dataset_dir = base_dir / 'datasets' / 'skin_samples'
            dataset_info = {
                "source": "测试数据集",
                "description": "随机生成的测试图片",
                "categories": ["normal", "dry", "oily"]
            }
            
            with open(dataset_dir / "dataset_info.json", "w", encoding="utf-8") as f:
                json.dump(dataset_info, f, ensure_ascii=False, indent=2)
            
            return dataset_dir
            
    except Exception as e:
        logger.error(f"创建数据集失败: {str(e)}")
        raise

if __name__ == "__main__":
    create_sample_dataset() 