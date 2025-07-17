import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 模板目录
TEMPLATES_DIR = BASE_DIR / "templates"

# 输出目录
OUTPUT_DIR = BASE_DIR / "backend" / "output"

# 临时文件目录
TEMP_DIR = BASE_DIR / "backend" / "temp"

# 确保目录存在
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# 文档格式配置
DOCUMENT_CONFIG = {
    # 页面设置
    "page": {
        "width": 8.27,  # A4纸宽度(英寸)
        "height": 11.69,  # A4纸高度(英寸)
        "left_margin": 1.18,  # 左边距(英寸) 30mm
        "right_margin": 0.79,  # 右边距(英寸) 20mm
        "top_margin": 1.46,  # 上边距(英寸) 37mm
        "bottom_margin": 1.18,  # 下边距(英寸) 30mm
    },
    
    # 字体设置
    "fonts": {
        "title": {
            "name": "方正小标宋简体",
            "size": 22,
            "bold": True
        },
        "header": {
            "name": "方正小标宋简体", 
            "size": 22,
            "bold": True
        },
        "body": {
            "name": "仿宋",
            "size": 16,
            "bold": False
        },
        "number": {
            "name": "仿宋",
            "size": 16,
            "bold": False
        }
    },
    
    # 行距设置
    "line_spacing": 1.5,
    
    # 首行缩进
    "first_line_indent": 0.39  # 英寸，约2个字符
}

# 支持的文件格式
SUPPORTED_FORMATS = {
    "input": [".md", ".docx", ".doc", ".txt"],
    "output": [".docx"]
}

# 上传文件限制
UPLOAD_CONFIG = {
    "max_size": 10 * 1024 * 1024,  # 10MB
    "allowed_extensions": SUPPORTED_FORMATS["input"]
}