import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import os
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_model():
    """创建CNN模型"""
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(7, activation='softmax')  # 7个类别
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def download_dataset():
    """下载HAM10000数据集"""
    # 这里需要实现数据集下载逻辑
    # 由于数据集较大，建议手动下载并放置到正确位置
    pass

def train_model():
    """训练模型"""
    try:
        # 创建模型
        model = create_model()
        logger.info("模型创建成功")

        # 保存模型
        model_path = Path(__file__).parent.parent / 'inference' / 'models'
        model_path.mkdir(parents=True, exist_ok=True)
        
        # 保存为SavedModel格式
        tf.saved_model.save(model, str(model_path))
        logger.info(f"模型已保存到: {model_path}")

    except Exception as e:
        logger.error(f"模型训练失败: {str(e)}")
        raise

if __name__ == "__main__":
    train_model() 