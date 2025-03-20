import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from model_trainer import SkinAnalysisModel
from data_collection_script import DataCollectionScript

class ModelTrainer:
    def __init__(self):
        self.model = SkinAnalysisModel()
        self.data_script = DataCollectionScript()
        self.history = None
    
    def train_model(self, epochs: int = 50, batch_size: int = 32):
        """
        训练模型
        """
        # 准备训练数据
        train_data, val_data = self.data_script.prepare_training_dataset()
        
        # 加载和预处理数据
        X_train, y_train = self._prepare_data(train_data)
        X_val, y_val = self._prepare_data(val_data)
        
        # 训练模型
        self.history = self.model.train(
            train_data=(X_train, y_train),
            val_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size
        )
        
        # 保存模型
        self.model.save_model('models/skin_analysis_model.h5')
        
        # 生成训练报告
        self._generate_training_report()
    
    def evaluate_model(self, test_data: pd.DataFrame):
        """
        评估模型性能
        """
        # 准备测试数据
        X_test, y_test = self._prepare_data(test_data)
        
        # 评估模型
        metrics = self.model.evaluate((X_test, y_test))
        
        # 生成评估报告
        self._generate_evaluation_report(metrics)
        
        return metrics
    
    def _prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        准备训练数据
        """
        # 加载图像
        X = []
        for image_path in data['image_path']:
            image = cv2.imread(os.path.join('data/images', image_path))
            X.append(image)
        
        X = np.array(X)
        
        # 准备标签
        y = data[['skin_score', 'moisture_level', 'oil_level', 'sensitivity']].values
        
        return X, y
    
    def _generate_training_report(self):
        """
        生成训练报告
        """
        report = {
            'training_history': self.history.history,
            'final_metrics': {
                'loss': self.history.history['loss'][-1],
                'val_loss': self.history.history['val_loss'][-1],
                'mae': self.history.history['mae'][-1],
                'val_mae': self.history.history['val_mae'][-1]
            }
        }
        
        # 保存报告
        self._save_report(report, 'training_report.json')
        
        # 绘制训练曲线
        self._plot_training_curves()
    
    def _generate_evaluation_report(self, metrics: Dict):
        """
        生成评估报告
        """
        report = {
            'metrics': metrics,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 保存报告
        self._save_report(report, 'evaluation_report.json')
        
        # 绘制评估图表
        self._plot_evaluation_charts(metrics)
    
    def _save_report(self, report: Dict, filename: str):
        """
        保存报告
        """
        import json
        os.makedirs('reports', exist_ok=True)
        with open(os.path.join('reports', filename), 'w') as f:
            json.dump(report, f, indent=4)
    
    def _plot_training_curves(self):
        """
        绘制训练曲线
        """
        plt.figure(figsize=(12, 4))
        
        # 损失曲线
        plt.subplot(1, 2, 1)
        plt.plot(self.history.history['loss'], label='Training Loss')
        plt.plot(self.history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # MAE曲线
        plt.subplot(1, 2, 2)
        plt.plot(self.history.history['mae'], label='Training MAE')
        plt.plot(self.history.history['val_mae'], label='Validation MAE')
        plt.title('Model MAE')
        plt.xlabel('Epoch')
        plt.ylabel('MAE')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('reports/training_curves.png')
        plt.close()
    
    def _plot_evaluation_charts(self, metrics: Dict):
        """
        绘制评估图表
        """
        plt.figure(figsize=(10, 6))
        
        # 绘制各项指标的对比图
        labels = list(metrics.keys())
        values = list(metrics.values())
        
        plt.bar(labels, values)
        plt.title('Model Performance Metrics')
        plt.xlabel('Metrics')
        plt.ylabel('Values')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('reports/evaluation_charts.png')
        plt.close()
    
    def optimize_hyperparameters(self):
        """
        优化超参数
        """
        from sklearn.model_selection import GridSearchCV
        from tensorflow.keras.wrappers.scikit_learn import KerasRegressor
        
        def create_model(learning_rate=0.001, dropout_rate=0.5):
            model = SkinAnalysisModel()
            model.model.optimizer.learning_rate = learning_rate
            return model.model
        
        # 定义参数网格
        param_grid = {
            'learning_rate': [0.001, 0.0005, 0.0001],
            'dropout_rate': [0.3, 0.5, 0.7],
            'batch_size': [16, 32, 64],
            'epochs': [30, 50, 100]
        }
        
        # 创建KerasRegressor
        model = KerasRegressor(build_fn=create_model)
        
        # 网格搜索
        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            cv=3,
            n_jobs=-1,
            verbose=1
        )
        
        # 准备数据
        train_data, _ = self.data_script.prepare_training_dataset()
        X_train, y_train = self._prepare_data(train_data)
        
        # 执行网格搜索
        grid_result = grid_search.fit(X_train, y_train)
        
        # 保存最佳参数
        best_params = grid_result.best_params_
        self._save_report(best_params, 'best_hyperparameters.json')
        
        return best_params