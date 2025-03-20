import cv2
import numpy as np
from .image_processing import extract_skin_features, analyze_skin_texture

def analyze_skin(image):
    """
    分析皮肤状态并返回结果
    """
    # 提取皮肤特征
    skin, skin_mask = extract_skin_features(image)
    
    # 分析皮肤纹理
    texture = analyze_skin_texture(skin)
    
    # 计算皮肤评分
    skin_score = calculate_skin_score(skin, texture)
    
    # 分析水分含量
    moisture_level = analyze_moisture_level(skin)
    
    # 分析油脂含量
    oil_level = analyze_oil_level(skin)
    
    # 分析敏感度
    sensitivity = analyze_sensitivity(skin)
    
    # 生成建议
    recommendations = generate_recommendations(skin_score, moisture_level, oil_level, sensitivity)
    
    return {
        'score': skin_score,
        'moisture': moisture_level,
        'oil': oil_level,
        'sensitivity': sensitivity,
        'recommendations': recommendations
    }

def calculate_skin_score(skin, texture):
    """
    计算皮肤评分
    """
    # 这里使用简单的评分算法，实际项目中应该使用更复杂的模型
    # 基于纹理、颜色均匀度等因素
    score = min(100, max(0, texture / 1000 * 100))
    return round(score, 2)

def analyze_moisture_level(skin):
    """
    分析皮肤水分含量
    """
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(skin, cv2.COLOR_BGR2HSV)
    
    # 基于亮度通道分析水分含量
    brightness = np.mean(hsv[:,:,2])
    moisture = min(100, max(0, brightness / 2.55))
    
    return round(moisture, 2)

def analyze_oil_level(skin):
    """
    分析皮肤油脂含量
    """
    # 转换为灰度图
    gray = cv2.cvtColor(skin, cv2.COLOR_BGR2GRAY)
    
    # 基于图像亮度分布分析油脂含量
    oil_level = np.percentile(gray, 75) / 2.55
    return round(oil_level, 2)

def analyze_sensitivity(skin):
    """
    分析皮肤敏感度
    """
    # 转换为LAB颜色空间
    lab = cv2.cvtColor(skin, cv2.COLOR_BGR2LAB)
    
    # 基于颜色分布分析敏感度
    sensitivity = np.std(lab[:,:,1]) / 2.55
    return round(sensitivity, 2)

def generate_recommendations(score, moisture, oil, sensitivity):
    """
    根据分析结果生成建议
    """
    recommendations = []
    
    # 基于水分含量的建议
    if moisture < 30:
        recommendations.append("建议使用保湿产品，增加皮肤水分含量")
    elif moisture > 70:
        recommendations.append("皮肤水分充足，建议保持当前护理习惯")
    
    # 基于油脂含量的建议
    if oil > 70:
        recommendations.append("皮肤油脂分泌较多，建议使用控油产品")
    elif oil < 30:
        recommendations.append("皮肤偏干，建议使用滋润型产品")
    
    # 基于敏感度的建议
    if sensitivity > 70:
        recommendations.append("皮肤较为敏感，建议使用温和型产品，避免刺激性成分")
    
    # 基于总体评分的建议
    if score < 60:
        recommendations.append("建议改善日常护理习惯，保持规律作息")
    elif score > 80:
        recommendations.append("皮肤状态良好，建议继续保持当前护理习惯")
    
    return "\n".join(recommendations)