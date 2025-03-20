import os
import yaml
import docker
from typing import Dict, List
import logging
from datetime import datetime
import json
import time

class DeploymentConfig:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        设置日志记录器
        """
        logger = logging.getLogger('deployment')
        logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler('logs/deployment.log')
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
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def create_docker_compose(self, config: Dict):
        """
        创建Docker Compose配置
        """
        compose_config = {
            'version': '3.8',
            'services': {
                'web': {
                    'build': '.',
                    'ports': ['5000:5000'],
                    'environment': {
                        'FLASK_ENV': 'production',
                        'REDIS_HOST': 'redis',
                        'REDIS_PORT': '6379',
                        'DATABASE_URL': 'postgresql://user:password@db:5432/skin_analysis'
                    },
                    'depends_on': ['redis', 'db']
                },
                'redis': {
                    'image': 'redis:latest',
                    'ports': ['6379:6379']
                },
                'db': {
                    'image': 'postgres:13',
                    'environment': {
                        'POSTGRES_USER': 'user',
                        'POSTGRES_PASSWORD': 'password',
                        'POSTGRES_DB': 'skin_analysis'
                    },
                    'volumes': ['postgres_data:/var/lib/postgresql/data']
                },
                'monitoring': {
                    'image': 'prom/prometheus:latest',
                    'ports': ['9090:9090'],
                    'volumes': ['./prometheus.yml:/etc/prometheus/prometheus.yml']
                },
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'ports': ['3000:3000'],
                    'environment': {
                        'GF_SECURITY_ADMIN_PASSWORD': 'admin'
                    },
                    'volumes': ['grafana_data:/var/lib/grafana']
                }
            },
            'volumes': {
                'postgres_data': {},
                'grafana_data': {}
            }
        }
        
        # 保存配置
        with open('docker-compose.yml', 'w') as f:
            yaml.dump(compose_config, f)
    
    def setup_monitoring(self):
        """
        设置监控系统
        """
        # 创建Prometheus配置
        prometheus_config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'scrape_configs': [
                {
                    'job_name': 'skin_analysis',
                    'static_configs': [
                        {
                            'targets': ['web:5000']
                        }
                    ]
                }
            ]
        }
        
        with open('prometheus.yml', 'w') as f:
            yaml.dump(prometheus_config, f)
        
        # 创建Grafana仪表板配置
        self._create_grafana_dashboard()
    
    def _create_grafana_dashboard(self):
        """
        创建Grafana仪表板
        """
        dashboard = {
            'dashboard': {
                'id': None,
                'title': 'Skin Analysis Dashboard',
                'panels': [
                    {
                        'title': 'API Response Time',
                        'type': 'graph',
                        'datasource': 'Prometheus',
                        'targets': [
                            {
                                'expr': 'rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])'
                            }
                        ]
                    },
                    {
                        'title': 'Error Rate',
                        'type': 'graph',
                        'datasource': 'Prometheus',
                        'targets': [
                            {
                                'expr': 'rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])'
                            }
                        ]
                    },
                    {
                        'title': 'Active Users',
                        'type': 'graph',
                        'datasource': 'Prometheus',
                        'targets': [
                            {
                                'expr': 'active_users'
                            }
                        ]
                    }
                ]
            }
        }
        
        os.makedirs('grafana/dashboards', exist_ok=True)
        with open('grafana/dashboards/skin_analysis.json', 'w') as f:
            json.dump(dashboard, f, indent=4)
    
    def deploy(self):
        """
        部署应用
        """
        try:
            # 构建和启动容器
            self.docker_client.containers.run(
                'docker-compose up -d',
                detach=True
            )
            
            self.logger.info('Application deployed successfully')
            
            # 等待服务启动
            time.sleep(10)
            
            # 检查服务状态
            self._check_service_status()
            
        except Exception as e:
            self.logger.error(f'Deployment failed: {str(e)}')
            raise
    
    def _check_service_status(self):
        """
        检查服务状态
        """
        services = ['web', 'redis', 'db', 'monitoring', 'grafana']
        
        for service in services:
            container = self.docker_client.containers.get(service)
            if container.status != 'running':
                self.logger.error(f'Service {service} is not running')
                raise Exception(f'Service {service} failed to start')
    
    def rollback(self):
        """
        回滚部署
        """
        try:
            # 停止所有容器
            self.docker_client.containers.run(
                'docker-compose down',
                detach=True
            )
            
            self.logger.info('Rollback completed successfully')
            
        except Exception as e:
            self.logger.error(f'Rollback failed: {str(e)}')
            raise
    
    def setup_auto_deploy(self):
        """
        设置自动部署
        """
        # 创建GitHub Actions工作流配置
        workflow_config = {
            'name': 'Deploy',
            'on': {
                'push': {
                    'branches': ['main']
                }
            },
            'jobs': {
                'deploy': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'uses': 'actions/checkout@v2'
                        },
                        {
                            'name': 'Deploy to production',
                            'run': |
                                docker-compose up -d
                                sleep 10
                                curl -f http://localhost:5000/health || exit 1
                    ]
                }
            }
        }
        
        os.makedirs('.github/workflows', exist_ok=True)
        with open('.github/workflows/deploy.yml', 'w') as f:
            yaml.dump(workflow_config, f)
    
    def setup_backup(self):
        """
        设置备份策略
        """
        backup_config = {
            'version': '3.8',
            'services': {
                'backup': {
                    'image': 'postgres:13',
                    'volumes': ['postgres_data:/var/lib/postgresql/data'],
                    'command': |
                        pg_dump -U user -d skin_analysis > /backup/backup_$(date +%Y%m%d).sql
                    'environment': {
                        'POSTGRES_USER': 'user',
                        'POSTGRES_PASSWORD': 'password'
                    }
                }
            },
            'volumes': {
                'postgres_data': {},
                'backup': {}
            }
        }
        
        with open('docker-compose.backup.yml', 'w') as f:
            yaml.dump(backup_config, f)