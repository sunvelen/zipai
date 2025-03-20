from flask import jsonify
from werkzeug.exceptions import HTTPException
import traceback
import logging
from typing import Dict, Any

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400, payload: Dict[str, Any] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class ErrorHandler:
    def __init__(self, app):
        self.app = app
        self.setup_error_handlers()
        self.setup_logging()
    
    def setup_error_handlers(self):
        """
        设置错误处理器
        """
        @self.app.errorhandler(APIError)
        def handle_api_error(error):
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
            return response
        
        @self.app.errorhandler(HTTPException)
        def handle_http_error(error):
            response = jsonify({
                'message': error.description,
                'code': error.code
            })
            response.status_code = error.code
            return response
        
        @self.app.errorhandler(Exception)
        def handle_generic_error(error):
            # 记录错误
            self.logger.error(f"Unhandled error: {str(error)}")
            self.logger.error(traceback.format_exc())
            
            response = jsonify({
                'message': 'Internal server error',
                'code': 500
            })
            response.status_code = 500
            return response
    
    def setup_logging(self):
        """
        设置日志记录
        """
        self.logger = logging.getLogger('skin_analysis')
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """
        记录错误信息
        """
        error_info = {
            'error': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        self.logger.error(error_info)
    
    def log_info(self, message: str, context: Dict[str, Any] = None):
        """
        记录信息
        """
        info = {
            'message': message,
            'context': context or {}
        }
        self.logger.info(info)
    
    def log_warning(self, message: str, context: Dict[str, Any] = None):
        """
        记录警告信息
        """
        warning = {
            'message': message,
            'context': context or {}
        }
        self.logger.warning(warning)
    
    def log_debug(self, message: str, context: Dict[str, Any] = None):
        """
        记录调试信息
        """
        debug = {
            'message': message,
            'context': context or {}
        }
        self.logger.debug(debug) 