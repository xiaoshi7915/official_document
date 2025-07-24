"""
SQLite初始化模块
统一管理SQLite版本兼容性问题，消除重复代码
"""

import sys
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def init_sqlite():
    """统一的SQLite初始化函数"""
    try:
        # 查找虚拟环境路径
        venv_path = Path(__file__).parent.parent / "venv"
        site_packages = list(venv_path.glob("lib/python*/site-packages"))
        
        if site_packages:
            pysqlite3_path = site_packages[0] / "pysqlite3"
            if pysqlite3_path.exists():
                sys.path.insert(0, str(pysqlite3_path))
                logger.info(f"找到pysqlite3路径: {pysqlite3_path}")
        
        # 尝试导入pysqlite3
        try:
            import pysqlite3
            import sqlite3
            # 替换sqlite3模块
            sys.modules['sqlite3'] = pysqlite3
            logger.info("✓ 已切换到pysqlite3")
            print("✓ 已切换到pysqlite3")
        except ImportError:
            logger.warning("⚠ pysqlite3导入失败，使用系统sqlite3")
            print("⚠ pysqlite3导入失败，使用系统sqlite3")
        
        # 验证sqlite3版本
        import sqlite3
        version = sqlite3.sqlite_version
        logger.info(f"当前使用的SQLite版本: {version}")
        print(f"当前使用的SQLite版本: {version}")
        
        return sqlite3
        
    except Exception as e:
        logger.error(f"SQLite初始化失败: {e}")
        raise

def get_sqlite_version():
    """获取当前SQLite版本"""
    try:
        import sqlite3
        return sqlite3.sqlite_version
    except Exception:
        return "unknown"

def check_sqlite_compatibility():
    """检查SQLite兼容性"""
    try:
        import sqlite3
        version = sqlite3.sqlite_version
        major, minor, patch = map(int, version.split('.'))
        
        # 检查版本是否满足最低要求
        if major < 3 or (major == 3 and minor < 7):
            logger.warning(f"SQLite版本过低: {version}，建议使用3.7或更高版本")
            return False
        
        logger.info(f"SQLite版本兼容性检查通过: {version}")
        return True
        
    except Exception as e:
        logger.error(f"SQLite兼容性检查失败: {e}")
        return False 