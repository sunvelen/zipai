from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from dotenv import load_dotenv
from ai_model.inference.model_inference import SkinAnalyzer
import logging

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__, 
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)
CORS(app)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///skin_analysis.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MODEL_PATH'] = os.getenv('MODEL_PATH', 'ai_model/inference/models/skin_analysis_model.h5')

# 初始化扩展
db = SQLAlchemy(app)
jwt = JWTManager(app)

# 初始化AI模型
try:
    skin_analyzer = SkinAnalyzer(app.config['MODEL_PATH'])
    logger.info("AI模型加载成功")
except Exception as e:
    logger.error(f"AI模型加载失败: {str(e)}")
    skin_analyzer = None

# 数据模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyses = db.relationship('SkinAnalysis', backref='user', lazy=True)
    profile = db.relationship('UserProfile', backref='user', uselist=False, lazy=True)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    skin_type = db.Column(db.String(20))
    concerns = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SkinAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Float, nullable=False)
    moisture = db.Column(db.Float, nullable=False)
    oil = db.Column(db.Float, nullable=False)
    sensitivity = db.Column(db.Float, nullable=False)
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 路由：主页
@app.route('/')
def index():
    return render_template('index.html')

# 路由：用户注册
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

# 路由：用户登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

# 路由：获取用户资料
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if profile:
        return jsonify({
            'age': profile.age,
            'gender': profile.gender,
            'skin_type': profile.skin_type,
            'concerns': profile.concerns
        })
    return jsonify({}), 404

# 路由：更新用户资料
@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
    
    profile.age = data.get('age')
    profile.gender = data.get('gender')
    profile.skin_type = data.get('skin_type')
    profile.concerns = data.get('concerns')
    
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

# 路由：健康检查
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': skin_analyzer is not None
    })

# 路由：皮肤分析
@app.route('/api/analyze', methods=['POST'])
@jwt_required()
def analyze_skin():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # 保存上传的图片
        filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 使用AI模型进行分析
        if skin_analyzer:
            result = skin_analyzer.analyze_image_file(file_path)
        else:
            # 如果模型未加载，使用模拟数据
            result = {
                'score': 85,
                'moisture': 75,
                'oil': 45,
                'sensitivity': 30,
                'recommendations': '建议使用补水保湿产品，避免刺激性护肤品。'
            }
        
        # 保存分析结果
        analysis = SkinAnalysis(
            user_id=get_jwt_identity(),
            image_path=file_path,
            **result
        )
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"皮肤分析失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 路由：获取历史记录
@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    analyses = SkinAnalysis.query.filter_by(user_id=user_id).order_by(SkinAnalysis.created_at.desc()).all()
    
    history = [{
        'id': analysis.id,
        'created_at': analysis.created_at.isoformat(),
        'score': analysis.score,
        'moisture': analysis.moisture,
        'oil': analysis.oil,
        'sensitivity': analysis.sensitivity,
        'recommendations': analysis.recommendations
    } for analysis in analyses]
    
    return jsonify(history)

if __name__ == '__main__':
    try:
        # 创建必要的目录
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        logger.info(f"Created upload folder: {app.config['UPLOAD_FOLDER']}")
        
        # 创建数据库表
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
        
        # 获取端口配置
        port = int(os.getenv('PORT', 3000))
        
        # 打印服务器配置信息
        logger.info("=== Server Configuration ===")
        logger.info(f"Starting server on port {port}")
        logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
        logger.info(f"Model path: {app.config['MODEL_PATH']}")
        logger.info(f"Debug mode: {app.debug}")
        logger.info("==========================")
        
        # 启动服务器
        app.run(host='127.0.0.1', port=port, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        raise