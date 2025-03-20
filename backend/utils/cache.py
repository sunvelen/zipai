from functools import wraps
import redis
import json
from typing import Any, Callable, Optional
import os

class Cache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0))
        )
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        """
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """
        设置缓存数据
        """
        try:
            self.redis_client.setex(
                key,
                expire,
                json.dumps(value)
            )
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存数据
        """
        try:
            self.redis_client.delete(key)
            return True
        except Exception:
            return False
    
    def clear_pattern(self, pattern: str) -> bool:
        """
        清除匹配模式的缓存
        """
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception:
            return False

def cached(expire: int = 3600):
    """
    缓存装饰器
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = Cache()
            
            # 生成缓存键
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试获取缓存
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache.set(key, result, expire)
            
            return result
        return wrapper
    return decorator