from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from models.user import User, db
from typing import Dict, Optional

class AuthService:
    def __init__(self):
        self.jwt_expires = timedelta(days=1)
    
    def register_user(self, username: str, email: str, password: str) -> Dict:
        """
        注册新用户
        """
        # 检查用户是否已存在
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already registered")
        
        if User.query.filter_by(username=username).first():
            raise ValueError("Username already taken")
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        return {
            "message": "User registered successfully",
            "user_id": user.id
        }
    
    def login_user(self, email: str, password: str) -> Dict:
        """
        用户登录
        """
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid email or password")
        
        # 创建访问令牌
        access_token = create_access_token(
            identity=user.id,
            expires_delta=self.jwt_expires
        )
        
        return {
            "access_token": access_token,
            "user_id": user.id,
            "username": user.username
        }
    
    @jwt_required()
    def get_current_user(self) -> Optional[User]:
        """
        获取当前用户信息
        """
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    
    def update_user_profile(self, user_id: int, data: Dict) -> Dict:
        """
        更新用户信息
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # 更新用户信息
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        
        return {
            "message": "Profile updated successfully",
            "user_id": user.id
        }
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict:
        """
        修改密码
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not check_password_hash(user.password_hash, old_password):
            raise ValueError("Invalid old password")
        
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return {
            "message": "Password changed successfully",
            "user_id": user.id
        }
    
    def reset_password(self, email: str) -> Dict:
        """
        重置密码
        """
        user = User.query.filter_by(email=email).first()
        if not user:
            raise ValueError("User not found")
        
        # 生成临时密码
        import secrets
        temp_password = secrets.token_urlsafe(8)
        user.password_hash = generate_password_hash(temp_password)
        
        db.session.commit()
        
        # TODO: 发送重置密码邮件
        
        return {
            "message": "Password reset email sent",
            "user_id": user.id
        }