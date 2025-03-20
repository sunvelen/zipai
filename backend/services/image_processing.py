import cv2
import numpy as np
from PIL import Image
import io
from typing import Dict, Tuple

class ImageProcessor:
    def __init__(self):
        self.spectrum_filters = {
            'visible': None,  # 可见光
            'uv': np.array([0, 0, 1]),  # 紫外光
            'ir': np.array([1, 0, 0])   # 红外光
        }
    
    def process_image(self, image_file) -> np.ndarray:
        """
        处理上传的图像文件
        """
        # 读取图像
        image = Image.open(image_file)
        
        # 转换为OpenCV格式
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 图像预处理
        processed_image = self._preprocess_image(cv_image)
        
        return processed_image
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理
        """
        # 1. 调整大小
        image = cv2.resize(image, (640, 480))
        
        # 2. 降噪
        image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        
        # 3. 对比度增强
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        enhanced = cv2.merge((cl,a,b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def capture_multispectral(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        捕获多光谱图像
        """
        spectra = {}
        
        for spectrum, filter_array in self.spectrum_filters.items():
            if filter_array is None:
                # 可见光
                spectra[spectrum] = image
            else:
                # 应用光谱滤镜
                filtered = cv2.filter2D(image, -1, filter_array)
                spectra[spectrum] = filtered
        
        return spectra
    
    def extract_skin_features(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        提取皮肤特征
        """
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 定义肤色范围
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # 创建肤色掩码
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # 形态学操作改善掩码
        kernel = np.ones((5,5), np.uint8)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        
        # 应用掩码
        skin = cv2.bitwise_and(image, image, mask=skin_mask)
        
        return skin, skin_mask
    
    def analyze_skin_texture(self, image: np.ndarray) -> float:
        """
        分析皮肤纹理
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 计算局部方差作为纹理特征
        texture = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return texture
    
    def detect_skin_imperfections(self, image: np.ndarray) -> Dict[str, float]:
        """
        检测皮肤瑕疵
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用自适应阈值检测瑕疵
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # 计算瑕疵面积比例
        total_pixels = thresh.shape[0] * thresh.shape[1]
        imperfection_pixels = np.sum(thresh > 0)
        imperfection_ratio = imperfection_pixels / total_pixels
        
        return {
            'imperfection_ratio': imperfection_ratio,
            'severity': imperfection_ratio * 100  # 转换为百分比
        }
    
    def analyze_skin_color(self, image: np.ndarray) -> Dict[str, float]:
        """
        分析皮肤颜色
        """
        # 转换为LAB颜色空间
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # 计算颜色统计信息
        l, a, b = cv2.split(lab)
        
        return {
            'brightness': np.mean(l),
            'red_green': np.mean(a),
            'blue_yellow': np.mean(b),
            'color_variance': np.std(l)
        }
    
    def enhance_image_quality(self, image: np.ndarray) -> np.ndarray:
        """
        增强图像质量
        """
        # 锐化
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(image, -1, kernel)
        
        # 自适应直方图均衡化
        lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        enhanced = cv2.merge((cl,a,b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced