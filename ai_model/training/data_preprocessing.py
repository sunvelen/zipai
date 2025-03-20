import os
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from sklearn.model_selection import train_test_split
import logging

class DataPreprocessor:
    def __init__(self, data_dir, output_dir):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data_preprocessing.log'),
                logging.StreamHandler()
            ]
        )
    
    def create_directories(self):
        """创建必要的目录"""
        dirs = [
            os.path.join(self.output_dir, 'processed'),
            os.path.join(self.output_dir, 'train'),
            os.path.join(self.output_dir, 'val'),
            os.path.join(self.output_dir, 'test')
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def preprocess_image(self, image_path):
        """预处理单张图片"""
        try:
            # 读取图片
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # 调整大小
            img = cv2.resize(img, (224, 224))
            
            # 颜色空间转换
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # 标准化
            img = img.astype(np.float32) / 255.0
            
            return img
        except Exception as e:
            logging.error(f"处理图片 {image_path} 时出错: {str(e)}")
            return None
    
    def process_dataset(self, dataset_name):
        """处理整个数据集"""
        logging.info(f"开始处理数据集: {dataset_name}")
        
        # 创建输出目录
        self.create_directories()
        
        # 根据数据集类型选择处理方法
        if dataset_name == 'celeba':
            self.process_celeba()
        elif dataset_name == 'ffhq':
            self.process_ffhq()
        elif dataset_name == 'lfw':
            self.process_lfw()
        else:
            raise ValueError(f"不支持的数据集: {dataset_name}")
    
    def process_celeba(self):
        """处理 CelebA 数据集"""
        logging.info("开始处理CelebA数据集...")
        
        # 创建输出目录
        self.create_directories()
        
        # 读取属性文件
        attr_file = os.path.join(self.data_dir, 'list_attr_celeba.txt')
        if not os.path.exists(attr_file):
            raise FileNotFoundError("找不到 CelebA 属性文件")
        
        # 读取图片列表
        img_list_file = os.path.join(self.data_dir, 'list_eval_partition.txt')
        if not os.path.exists(img_list_file):
            raise FileNotFoundError("找不到 CelebA 图片列表文件")
        
        # 读取属性文件
        attributes = pd.read_csv(attr_file, delim_whitespace=True, skiprows=1)
        
        # 处理数据
        processed_data = []
        with open(img_list_file, 'r') as f:
            for line in f:
                img_name, partition = line.strip().split()
                img_path = os.path.join(self.data_dir, 'img_align_celeba', img_name)
                
                if os.path.exists(img_path):
                    processed_img = self.preprocess_image(img_path)
                    if processed_img is not None:
                        # 获取图片的属性
                        img_attrs = attributes.loc[img_name]
                        
                        processed_data.append({
                            'image': processed_img,
                            'partition': int(partition),
                            'filename': img_name,
                            'attributes': img_attrs.to_dict()
                        })
        
        # 保存处理后的数据
        self.save_processed_data(processed_data)
        
        # 保存属性统计信息
        self.save_attribute_stats(attributes)
    
    def process_ffhq(self):
        """处理 FFHQ 数据集"""
        img_dir = os.path.join(self.data_dir, 'thumbnails128x128')
        if not os.path.exists(img_dir):
            raise FileNotFoundError("找不到 FFHQ 图片目录")
        
        processed_data = []
        for img_name in os.listdir(img_dir):
            if img_name.endswith('.png'):
                img_path = os.path.join(img_dir, img_name)
                processed_img = self.preprocess_image(img_path)
                if processed_img is not None:
                    processed_data.append({
                        'image': processed_img,
                        'partition': 0,  # FFHQ 默认用于训练
                        'filename': img_name
                    })
        
        # 保存处理后的数据
        self.save_processed_data(processed_data)
    
    def process_lfw(self):
        """处理 LFW 数据集"""
        img_dir = os.path.join(self.data_dir, 'lfw')
        if not os.path.exists(img_dir):
            raise FileNotFoundError("找不到 LFW 图片目录")
        
        processed_data = []
        for person_dir in os.listdir(img_dir):
            person_path = os.path.join(img_dir, person_dir)
            if os.path.isdir(person_path):
                for img_name in os.listdir(person_path):
                    if img_name.endswith('.jpg'):
                        img_path = os.path.join(person_path, img_name)
                        processed_img = self.preprocess_image(img_path)
                        if processed_img is not None:
                            processed_data.append({
                                'image': processed_img,
                                'partition': 0,  # LFW 默认用于训练
                                'filename': img_name
                            })
        
        # 保存处理后的数据
        self.save_processed_data(processed_data)
    
    def save_processed_data(self, processed_data):
        """保存处理后的数据"""
        # 划分训练集、验证集和测试集
        train_data, val_data, test_data = self.split_dataset(processed_data)
        
        # 保存数据集
        self.save_dataset(train_data, 'train')
        self.save_dataset(val_data, 'val')
        self.save_dataset(test_data, 'test')
        
        # 保存数据集信息
        self.save_dataset_info(train_data, val_data, test_data)
        
        # 保存属性数据
        self.save_attributes(train_data, val_data, test_data)
    
    def split_dataset(self, data):
        """划分数据集"""
        # 首先分离测试集
        train_val_data, test_data = train_test_split(
            data, test_size=0.1, random_state=42
        )
        
        # 然后分离训练集和验证集
        train_data, val_data = train_test_split(
            train_val_data, test_size=0.2, random_state=42
        )
        
        return train_data, val_data, test_data
    
    def save_dataset(self, data, split_name):
        """保存数据集"""
        output_dir = os.path.join(self.output_dir, split_name)
        for item in data:
            img_path = os.path.join(output_dir, item['filename'])
            cv2.imwrite(img_path, (item['image'] * 255).astype(np.uint8))
    
    def save_dataset_info(self, train_data, val_data, test_data):
        """保存数据集信息"""
        info = {
            'total_samples': len(train_data) + len(val_data) + len(test_data),
            'train_samples': len(train_data),
            'val_samples': len(val_data),
            'test_samples': len(test_data)
        }
        
        info_df = pd.DataFrame([info])
        info_df.to_csv(os.path.join(self.output_dir, 'dataset_info.csv'), index=False)
    
    def save_attributes(self, train_data, val_data, test_data):
        """保存属性数据"""
        for split_name, data in [('train', train_data), ('val', val_data), ('test', test_data)]:
            attributes = []
            for item in data:
                attr_dict = item['attributes']
                attr_dict['filename'] = item['filename']
                attributes.append(attr_dict)
            
            attr_df = pd.DataFrame(attributes)
            attr_df.to_csv(os.path.join(self.output_dir, f'{split_name}_attributes.csv'), index=False)
    
    def save_attribute_stats(self, attributes):
        """保存属性统计信息"""
        stats = {
            'total_attributes': len(attributes.columns),
            'total_samples': len(attributes),
            'attribute_names': list(attributes.columns)
        }
        
        # 计算每个属性的正样本比例
        for attr in attributes.columns:
            positive_ratio = (attributes[attr] == 1).mean()
            stats[f'{attr}_positive_ratio'] = positive_ratio
        
        stats_df = pd.DataFrame([stats])
        stats_df.to_csv(os.path.join(self.output_dir, 'attribute_stats.csv'), index=False)

if __name__ == '__main__':
    # 使用示例
    preprocessor = DataPreprocessor(
        data_dir='datasets/celeba',
        output_dir='datasets/celeba/processed'
    )
    
    # 处理CelebA数据集
    preprocessor.process_celeba()