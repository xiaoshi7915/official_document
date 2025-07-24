#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的模块化日志管理器
提供统一的日志配置和管理功能
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class LoggerManager:
    """统一的日志管理器"""
    
    _instance = None
    _initialized = False
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self):
        """设置全局日志配置"""
        # 创建logs目录
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # 清除现有的处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 控制台处理器 - 只显示重要信息
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 自定义格式器
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # 文件处理器 - 记录详细信息
        log_file = log_dir / f'backend_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # 添加处理器到根日志记录器
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        # 设置特定模块的日志级别
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        
        # 设置项目模块的默认日志级别
        self._module_levels = {
            'backend': logging.INFO,
            'backend.routes': logging.INFO,
            'backend.services': logging.INFO,
            'backend.models': logging.INFO,
            'backend.utils': logging.INFO,
        }
        
        # 应用模块级别配置
        for module, level in self._module_levels.items():
            logging.getLogger(module).setLevel(level)
    
    def get_logger(self, name: str, level: Optional[int] = None) -> logging.Logger:
        """获取指定名称的日志记录器"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            
            # 设置日志级别
            if level is not None:
                logger.setLevel(level)
            else:
                # 根据模块名称设置默认级别
                for module, module_level in self._module_levels.items():
                    if name.startswith(module):
                        logger.setLevel(module_level)
                        break
            
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def set_module_level(self, module: str, level: int):
        """设置指定模块的日志级别"""
        self._module_levels[module] = level
        logger = logging.getLogger(module)
        logger.setLevel(level)
    
    def get_all_loggers(self) -> Dict[str, logging.Logger]:
        """获取所有已创建的日志记录器"""
        return self._loggers.copy()
    
    def reset_logging(self):
        """重置日志配置"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        self._loggers.clear()
        self._initialized = False
        self._setup_logging()

# 全局日志管理器实例
_logger_manager = LoggerManager()

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """获取日志记录器的便捷函数"""
    return _logger_manager.get_logger(name, level)

def set_module_level(module: str, level: int):
    """设置模块日志级别的便捷函数"""
    _logger_manager.set_module_level(module, level)

def setup_logging():
    """初始化日志系统的便捷函数"""
    return _logger_manager

# 预定义的日志记录器
def get_app_logger() -> logging.Logger:
    """获取应用主日志记录器"""
    return get_logger('backend.app')

def get_route_logger(route_name: str) -> logging.Logger:
    """获取路由日志记录器"""
    return get_logger(f'backend.routes.{route_name}')

def get_service_logger(service_name: str) -> logging.Logger:
    """获取服务日志记录器"""
    return get_logger(f'backend.services.{service_name}')

def get_model_logger(model_name: str) -> logging.Logger:
    """获取模型日志记录器"""
    return get_logger(f'backend.models.{model_name}')

def get_util_logger(util_name: str) -> logging.Logger:
    """获取工具日志记录器"""
    return get_logger(f'backend.utils.{util_name}') 