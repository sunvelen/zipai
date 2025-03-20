import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import os
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

class SkinAnalysisModel:
    def __init__(self, input_shape=(224, 224, 3)):
        self.input_shape = input_shape
        self.model = self._build_model()
        
    def _build_model(self):
        """
        构建深度学习模型
        """
        model = models.Sequential([
            # 卷积层1
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # 卷积层2
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # 卷积层3
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # 全连接层
            layers.Flatten(),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            
            # 输出层
            layers.Dense(4, activation='linear')  # 4个输出：肤质评分、水分、油脂、敏感度
        ])
        
        # 编译模型
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train(self, train_data, val_data, epochs=50, batch_size=32):
        """
        训练模型
        """
        # 早停策略
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )
        
        # 学习率调度
        reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=0.0001
        )
        
        # 训练模型
        history = self.model.fit(
            train_data,
            validation_data=val_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, reduce_lr]
        )
        
        return history
    
    def evaluate(self, test_data):
        """
        评估模型性能
        """
        predictions = self.model.predict(test_data[0])
        true_values = test_data[1]
        
        # 计算各项指标
        metrics = {}
        for i, name in enumerate(['skin_score', 'moisture', 'oil', 'sensitivity']):
            mse = mean_squared_error(true_values[:, i], predictions[:, i])
            r2 = r2_score(true_values[:, i], predictions[:, i])
            metrics[name] = {
                'mse': mse,
                'r2': r2
            }
        
        return metrics
    
    def plot_training_history(self, history, save_path=None):
        """
        绘制训练历史
        """
        plt.figure(figsize=(12, 4))
        
        # 损失曲线
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # MAE曲线
        plt.subplot(1, 2, 2)
        plt.plot(history.history['mae'], label='Training MAE')
        plt.plot(history.history['val_mae'], label='Validation MAE')
        plt.title('Model MAE')
        plt.xlabel('Epoch')
        plt.ylabel('MAE')
        plt.legend()
        
        if save_path:
            plt.savefig(save_path)
        plt.close()
    
    def save_model(self, model_path):
        """
        保存模型
        """
        self.model.save(model_path)
    
    def load_model(self, model_path):
        """
        加载模型
        """
        self.model = models.load_model(model_path)