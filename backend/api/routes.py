from flask import Blueprint, request, jsonify
from services.skin_analysis import analyze_skin
from services.image_processing import process_image
from models.user import User, db
from models.analysis_result import AnalysisResult

api_bp = Blueprint('api', __name__)

@api_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    处理用户上传的皮肤图像并进行分析
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image_file = request.files['image']
    user_id = request.form.get('user_id')
    
    try:
        # 处理图像
        processed_image = process_image(image_file)
        
        # 分析皮肤
        analysis_result = analyze_skin(processed_image)
        
        # 保存结果
        if user_id:
            result = AnalysisResult(
                user_id=user_id,
                skin_score=analysis_result['score'],
                moisture_level=analysis_result['moisture'],
                oil_level=analysis_result['oil'],
                sensitivity=analysis_result['sensitivity'],
                recommendations=analysis_result['recommendations']
            )
            db.session.add(result)
            db.session.commit()
        
        return jsonify(analysis_result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):
    """
    获取用户的皮肤分析历史记录
    """
    try:
        results = AnalysisResult.query.filter_by(user_id=user_id).all()
        return jsonify([{
            'id': result.id,
            'date': result.created_at,
            'score': result.skin_score,
            'moisture': result.moisture_level,
            'oil': result.oil_level,
            'sensitivity': result.sensitivity,
            'recommendations': result.recommendations
        } for result in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/user', methods=['POST'])
def create_user():
    """
    创建新用户
    """
    data = request.get_json()
    try:
        user = User(
            username=data['username'],
            email=data['email']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully", "user_id": user.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500