import os
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
from data_collection import SkinDataCollector
from typing import Dict, List, Tuple

class DataCollectionScript:
    def __init__(self):
        self.collector = SkinDataCollector()
        self.annotation_file = 'data/annotations.csv'
        self.validation_file = 'data/validation.csv'
        
    def collect_user_data(self, image: np.ndarray, user_info: Dict) -> str:
        """
        收集用户数据
        """
        # 生成唯一ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_id = f"user_{user_info['id']}_{timestamp}"
        
        # 收集图像
        filename = self.collector.collect_image(image, {
            'user_id': user_id,
            'timestamp': timestamp,
            'age': user_info['age'],
            'gender': user_info['gender'],
            'skin_type': user_info['skin_type']
        })
        
        return filename
    
    def annotate_data(self, image_path: str, annotations: Dict) -> None:
        """
        标注数据
        """
        if not os.path.exists(self.annotation_file):
            df = pd.DataFrame(columns=[
                'image_path', 'skin_score', 'moisture_level', 'oil_level',
                'sensitivity', 'annotator_id', 'timestamp'
            ])
            df.to_csv(self.annotation_file, index=False)
        
        # 添加标注
        annotations['image_path'] = image_path
        annotations['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        df = pd.read_csv(self.annotation_file)
        df = df.append(annotations, ignore_index=True)
        df.to_csv(self.annotation_file, index=False)
    
    def validate_data(self, image_path: str, validation_data: Dict) -> None:
        """
        验证数据
        """
        if not os.path.exists(self.validation_file):
            df = pd.DataFrame(columns=[
                'image_path', 'is_valid', 'validation_notes',
                'validator_id', 'timestamp'
            ])
            df.to_csv(self.validation_file, index=False)
        
        # 添加验证结果
        validation_data['image_path'] = image_path
        validation_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        df = pd.read_csv(self.validation_file)
        df = df.append(validation_data, ignore_index=True)
        df.to_csv(self.validation_file, index=False)
    
    def prepare_training_dataset(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        准备训练数据集
        """
        # 读取标注和验证数据
        annotations_df = pd.read_csv(self.annotation_file)
        validation_df = pd.read_csv(self.validation_file)
        
        # 合并数据
        merged_df = pd.merge(
            annotations_df,
            validation_df[['image_path', 'is_valid']],
            on='image_path'
        )
        
        # 只保留验证通过的数据
        valid_data = merged_df[merged_df['is_valid'] == True]
        
        # 划分训练集和验证集
        train_data = valid_data.sample(frac=0.8, random_state=42)
        val_data = valid_data.drop(train_data.index)
        
        return train_data, val_data
    
    def update_training_set(self, new_data: pd.DataFrame) -> None:
        """
        更新训练集
        """
        # 读取现有训练集
        train_file = 'data/training_set.csv'
        if os.path.exists(train_file):
            existing_data = pd.read_csv(train_file)
            # 合并新数据
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            updated_data = new_data
        
        # 保存更新后的训练集
        updated_data.to_csv(train_file, index=False)
        
        # 记录更新日志
        self._log_update(updated_data.shape[0])
    
    def _log_update(self, total_samples: int) -> None:
        """
        记录更新日志
        """
        log_file = 'data/update_log.csv'
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_samples': total_samples
        }
        
        if os.path.exists(log_file):
            df = pd.read_csv(log_file)
            df = df.append(log_entry, ignore_index=True)
        else:
            df = pd.DataFrame([log_entry])
        
        df.to_csv(log_file, index=False)
    
    def generate_data_report(self) -> Dict:
        """
        生成数据报告
        """
        report = {
            'total_samples': 0,
            'valid_samples': 0,
            'invalid_samples': 0,
            'annotations_per_image': 0,
            'data_distribution': {}
        }
        
        # 读取数据
        annotations_df = pd.read_csv(self.annotation_file)
        validation_df = pd.read_csv(self.validation_file)
        
        # 计算统计信息
        report['total_samples'] = len(annotations_df)
        report['valid_samples'] = len(validation_df[validation_df['is_valid'] == True])
        report['invalid_samples'] = len(validation_df[validation_df['is_valid'] == False])
        
        # 计算每个图像的标注数量
        report['annotations_per_image'] = annotations_df.groupby('image_path').size().mean()
        
        # 计算数据分布
        report['data_distribution'] = {
            'skin_types': annotations_df['skin_type'].value_counts().to_dict(),
            'age_groups': pd.cut(annotations_df['age'], bins=[0, 20, 30, 40, 50, 100]).value_counts().to_dict(),
            'gender': annotations_df['gender'].value_counts().to_dict()
        }
        
        return report 