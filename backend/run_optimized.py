#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的后端启动脚本
减少重复的SQLite初始化信息，优化日志记录
"""

import os
import sys
import logging
from pathlib import Path

# 设置环境变量，减少重复输出
os.environ['PYTHONUNBUFFERED'] = '1'

# 强制使用pysqlite3 - 只执行一次
def setup_sqlite():
    """设置SQLite配置，只执行一次"""
    try:
        import pysqlite3
        import sqlite3
        # 替换sqlite3模块
        sys.modules['sqlite3'] = pysqlite3
        print("✓ 已切换到pysqlite3")
        print(f"当前使用的SQLite版本: {sqlite3.sqlite_version}")
        return True
    except ImportError:
        print("⚠ pysqlite3导入失败，使用系统sqlite3")
        import sqlite3
        print(f"当前使用的SQLite版本: {sqlite3.sqlite_version}")
        return False

# 设置日志配置
def setup_logging():
    """设置优化的日志配置"""
    try:
        from utils.logger import setup_logging as setup_unified_logging
        setup_unified_logging()
    except ImportError:
        # 如果导入失败，使用简单配置
        import logging
        log_dir = Path(__file__).parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_dir / 'backend.log', encoding='utf-8')
            ]
        )
        
        # 设置特定模块的日志级别
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

if __name__ == '__main__':
    print("启动公文生成系统后端服务...")
    
    # 设置SQLite配置
    setup_sqlite()
    
    # 设置日志配置
    setup_logging()
    
    # 导入并启动Flask应用
    try:
        from main import app, DB_CONFIG, DEEPSEEK_API_KEY
        
        print("数据库配置:", DB_CONFIG['host'])
        print("DeepSeek API配置:", "已配置" if DEEPSEEK_API_KEY != "sk-your-api-key-here" else "未配置")
        
        # 启动Flask应用
        app.run(debug=True, host='0.0.0.0', port=5003)
        
    except ImportError as e:
        print(f"导入错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"启动错误: {e}")
        sys.exit(1) 