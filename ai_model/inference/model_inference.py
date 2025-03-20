import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import logging

class SkinAnalyzer:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        self.setup_logging()
        self.load_model()

    def setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_model(self):
        """加载预训练模型"""
        try:
            self.model = load_model(self.model_path)
            self.logger.info(f"成功加载模型: {self.model_path}")
        except Exception as e:
            self.logger.error(f"加载模型失败: {str(e)}")
            raise

    def preprocess_image(self, image):
        """预处理图像"""
        try:
            # 调整图像大小
            image = cv2.resize(image, (224, 224))
            # 转换为RGB格式
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            # 转换为数组并归一化
            image = img_to_array(image)
            image = image / 255.0
            # 添加批次维度
            image = np.expand_dims(image, axis=0)
            return image
        except Exception as e:
            self.logger.error(f"图像预处理失败: {str(e)}")
            raise

    def analyze_skin(self, image):
        """分析皮肤状况"""
        try:
            # 预处理图像
            processed_image = self.preprocess_image(image)
            
            # 模型预测
            predictions = self.model.predict(processed_image)[0]
            
            # 解析预测结果
            result = {
                'score': float(predictions[0] * 100),  # 肤质评分
                'moisture': float(predictions[1] * 100),  # 水分含量
                'oil': float(predictions[2] * 100),  # 油分含量
                'sensitivity': float(predictions[3] * 100),  # 敏感度
            }
            
            # 生成护理建议
            result['recommendations'] = self._generate_recommendations(result)
            
            self.logger.info(f"分析完成: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"皮肤分析失败: {str(e)}")
            raise

    def _generate_recommendations(self, result):
        """根据分析结果生成护理建议"""
        recommendations = []
        
        # 水分建议
        if result['moisture'] < 50:
            recommendations.append("建议使用补水保湿产品，增加皮肤水分含量。")
        elif result['moisture'] > 80:
            recommendations.append("皮肤水分充足，建议维持当前护理方案。")
            
        # 油分建议
        if result['oil'] < 30:
            recommendations.append("皮肤偏干，建议使用滋润型护肤品。")
        elif result['oil'] > 70:
            recommendations.append("皮肤偏油，建议使用控油产品，注意清洁。")
            
        # 敏感度建议
        if result['sensitivity'] > 50:
            recommendations.append("皮肤较为敏感，建议使用温和无刺激的护肤品。")
            
        # 综合建议
        if result['score'] < 60:
            recommendations.append("建议定期进行皮肤护理，改善肤质状况。")
        elif result['score'] > 80:
            recommendations.append("皮肤状况良好，建议保持当前护理习惯。")
            
        return " ".join(recommendations)

    def analyze_image_file(self, image_path):
        """分析图像文件"""
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
                
            # 转换为RGB格式
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 分析皮肤
            return self.analyze_skin(image)
            
        except Exception as e:
            self.logger.error(f"图像文件分析失败: {str(e)}")
            raise

def main():
    # 测试代码
    model_path = os.getenv('MODEL_PATH', 'models/skin_analysis_model.h5')
    analyzer = SkinAnalyzer(model_path)
    
    # 测试图像路径
    test_image_path = 'test_images/test.jpg'
    
    try:
        result = analyzer.analyze_image_file(test_image_path)
        print("分析结果:", result)
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == '__main__':
    main() 