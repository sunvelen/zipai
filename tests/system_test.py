import unittest
import requests
import json
import time
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import os
from typing import Dict, List

class SystemTest(unittest.TestCase):
    def setUp(self):
        """
        测试前准备
        """
        self.base_url = 'http://localhost:5000'
        self.test_image = self._create_test_image()
        self.test_user = {
            'username': 'test_user',
            'email': 'test@example.com',
            'password': 'test_password'
        }
        self.token = None
    
    def _create_test_image(self) -> np.ndarray:
        """
        创建测试图像
        """
        # 创建一个简单的测试图像
        img = np.zeros((640, 480, 3), dtype=np.uint8)
        cv2.rectangle(img, (100, 100), (540, 380), (255, 255, 255), -1)
        return img
    
    def test_user_registration(self):
        """
        测试用户注册
        """
        response = requests.post(
            f'{self.base_url}/api/register',
            json=self.test_user
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.json())
    
    def test_user_login(self):
        """
        测试用户登录
        """
        response = requests.post(
            f'{self.base_url}/api/login',
            json={
                'email': self.test_user['email'],
                'password': self.test_user['password']
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access_token', data)
        self.assertIn('user', data)
        self.token = data['access_token']
    
    def test_skin_analysis(self):
        """
        测试皮肤分析功能
        """
        # 确保已登录
        if not self.token:
            self.test_user_login()
        
        # 将测试图像转换为字节流
        _, img_encoded = cv2.imencode('.jpg', self.test_image)
        files = {'image': ('test.jpg', img_encoded.tobytes(), 'image/jpeg')}
        
        # 发送分析请求
        response = requests.post(
            f'{self.base_url}/api/analyze',
            headers={'Authorization': f'Bearer {self.token}'},
            files=files
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('score', data)
        self.assertIn('moisture', data)
        self.assertIn('oil', data)
        self.assertIn('sensitivity', data)
        self.assertIn('recommendations', data)
    
    def test_performance(self):
        """
        测试系统性能
        """
        # 确保已登录
        if not self.token:
            self.test_user_login()
        
        start_time = time.time()
        num_requests = 10
        
        def make_request():
            _, img_encoded = cv2.imencode('.jpg', self.test_image)
            files = {'image': ('test.jpg', img_encoded.tobytes(), 'image/jpeg')}
            return requests.post(
                f'{self.base_url}/api/analyze',
                headers={'Authorization': f'Bearer {self.token}'},
                files=files
            )
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            responses = list(executor.map(lambda _: make_request(), range(num_requests)))
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / num_requests
        
        print(f'性能测试结果:')
        print(f'总请求数: {num_requests}')
        print(f'总时间: {total_time:.2f}秒')
        print(f'平均响应时间: {avg_time:.2f}秒')
        
        # 验证所有请求是否成功
        for response in responses:
            self.assertEqual(response.status_code, 200)
    
    def test_security(self):
        """
        测试系统安全性
        """
        # 测试未授权访问
        response = requests.get(f'{self.base_url}/api/history')
        self.assertEqual(response.status_code, 401)
        
        # 测试无效token
        response = requests.get(
            f'{self.base_url}/api/history',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        self.assertEqual(response.status_code, 401)
    
    def test_error_handling(self):
        """
        测试错误处理
        """
        # 测试无效图像
        if not self.token:
            self.test_user_login()
        
        files = {'image': ('test.txt', b'invalid image data', 'text/plain')}
        response = requests.post(
            f'{self.base_url}/api/analyze',
            headers={'Authorization': f'Bearer {self.token}'},
            files=files
        )
        
        self.assertEqual(response.status_code, 400)
    
    def _log_performance_metrics(self, metrics: Dict):
        """
        记录性能指标
        """
        log_file = 'tests/performance_log.json'
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': metrics
        })
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=4)
    
    def test_data_validation(self):
        """
        测试数据验证
        """
        # 测试无效的注册数据
        invalid_user = {
            'username': '',  # 空用户名
            'email': 'invalid_email',  # 无效邮箱
            'password': '123'  # 密码太短
        }
        
        response = requests.post(
            f'{self.base_url}/api/register',
            json=invalid_user
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_api_rate_limiting(self):
        """
        测试API速率限制
        """
        # 确保已登录
        if not self.token:
            self.test_user_login()
        
        # 快速发送多个请求
        for _ in range(20):
            response = requests.get(
                f'{self.base_url}/api/history',
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if response.status_code == 429:  # Too Many Requests
                break
        
        self.assertEqual(response.status_code, 429)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('rate_limit', data)

if __name__ == '__main__':
    unittest.main()