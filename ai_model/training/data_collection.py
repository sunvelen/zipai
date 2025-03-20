import os
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from sklearn.model_selection import train_test_split

class SkinDataCollector:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.image_dir = os.path.join(data_dir, 'images')
        self.label_file = os.path.join(data_dir, 'labels.csv')
        
        # 创建必要的目录
        os.makedirs(self.image_dir, exist_ok=True)
        
    def collect_image(self, image, label_data):
        """
        收集单张图像及其标签数据
        """
        # 生成唯一文件名
        filename = f"skin_{len(os.listdir(self.image_dir))}.jpg"
        filepath = os.path.join(self.image_dir, filename)
        
        # 保存图像
        cv2.imwrite(filepath, image)
        
        # 更新标签文件
        label_data['image_path'] = filename
        self._update_labels(label_data)
        
        return filename
    
    def _update_labels(self, label_data):
        """
        更新标签CSV文件
        """
        if os.path.exists(self.label_file):
            df = pd.read_csv(self.label_file)
        else:
            df = pd.DataFrame()
        
        df = df.append(label_data, ignore_index=True)
        df.to_csv(self.label_file, index=False)
    
    def prepare_training_data(self, test_size=0.2):
        """
        准备训练数据
        """
        if not os.path.exists(self.label_file):
            raise FileNotFoundError("标签文件不存在，请先收集数据")
        
        # 读取标签数据
        df = pd.read_csv(self.label_file)
        
        # 准备图像路径和标签
        X = df['image_path'].values
        y = df[['skin_score', 'moisture_level', 'oil_level', 'sensitivity']].values
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test
        }
    
    def preprocess_image(self, image):
        """
        图像预处理
        """
        # 调整大小
        image = cv2.resize(image, (224, 224))
        
        # 标准化
        image = image.astype(np.float32) / 255.0
        
        # 数据增强
        augmented = self._apply_augmentation(image)
        
        return augmented
    
    def _apply_augmentation(self, image):
        """
        应用数据增强
        """
        augmented = []
        
        # 原始图像
        augmented.append(image)
        
        # 水平翻转
        augmented.append(cv2.flip(image, 1))
        
        # 亮度调整
        augmented.append(cv2.convertScaleAbs(image, alpha=1.2, beta=0))
        
        # 对比度调整
        augmented.append(cv2.convertScaleAbs(image, alpha=1.0, beta=10))
        
        return np.array(augmented) 