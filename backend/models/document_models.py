from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DocumentMetadata(BaseModel):
    """公文元数据"""
    title: str  # 标题
    sender: str  # 发文机关
    recipient: Optional[str] = None  # 收文机关
    document_number: Optional[str] = None  # 文号
    urgency_level: Optional[str] = "一般"  # 紧急程度
    security_level: Optional[str] = "一般"  # 密级
    date: Optional[str] = None  # 发文日期
    author: Optional[str] = None  # 起草人
    department: Optional[str] = None  # 部门

class DocumentRequest(BaseModel):
    """文档生成请求"""
    content: str  # 文档内容（Markdown或纯文本）
    template_type: str  # 模板类型
    metadata: DocumentMetadata  # 文档元数据
    format_type: Optional[str] = "markdown"  # 输入格式类型

class DocumentResponse(BaseModel):
    """文档生成响应"""
    success: bool
    message: str
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    error_details: Optional[str] = None

class TemplateInfo(BaseModel):
    """模板信息"""
    id: str
    name: str
    description: str
    category: str
    file_path: str
    preview_image: Optional[str] = None

# 15种公文类型定义
DOCUMENT_TYPES = {
    "baogao": {"name": "报告", "description": "向上级机关汇报工作、反映情况、回复询问"},
    "gongbao": {"name": "公报", "description": "公开发布重要决议、决定或重大事件"},
    "gonggao": {"name": "公告", "description": "向国内外宣布重要事项或者法定事项"},
    "hansong": {"name": "函送", "description": "向有关单位送交公文或资料"},
    "jiyao": {"name": "纪要", "description": "记载会议主要情况和议定事项"},
    "jueding": {"name": "决定", "description": "对重要事项或重大行动作出安排"},
    "jueyi": {"name": "决议", "description": "会议讨论通过的重要事项的决策"},
    "minglin": {"name": "命令", "description": "依照有关法律公布行政法规和规章、宣布施行重大强制性措施"},
    "pifu": {"name": "批复", "description": "答复下级机关请示事项"},
    "qingshi": {"name": "请示", "description": "向上级机关请求指示或批准"},
    "tongbao": {"name": "通报", "description": "表彰先进、批评错误、传达重要精神或情况"},
    "tonggao": {"name": "通告", "description": "公开宣布重要事项或者法定事项"},
    "tongzhi": {"name": "通知", "description": "发布、传达要求下级机关执行和有关单位周知或者执行的事项"},
    "yian": {"name": "议案", "description": "正式提出审议事项的文书"},
    "yijian": {"name": "意见", "description": "对重要问题提出见解和处理办法"}
}