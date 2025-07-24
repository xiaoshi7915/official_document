import os

# 数据库配置
DB_CONFIG = {
    'host': '47.118.250.53',
    'port': 3306,
    'database': 'official_doc',
    'user': 'official_doc',
    'password': 'admin123456!'
}

# DeepSeek API配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-f637485083de48778da4a43d7d202742")

# 文件上传配置
UPLOAD_FOLDER = 'temp'
ALLOWED_EXTENSIONS = {'txt', 'md', 'docx', 'doc'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 15种公文类型定义
DOCUMENT_TYPES = [
    ('baogao', '报告', '向上级机关汇报工作、反映情况、回复询问'),
    ('gongbao', '公报', '公开发布重要决议、决定或重大事件'),
    ('gonggao', '公告', '向国内外宣布重要事项或者法定事项'),
    ('hansong', '函送', '向有关单位送交公文或资料'),
    ('jiyao', '纪要', '记载会议主要情况和议定事项'),
    ('jueding', '决定', '对重要事项或重大行动作出安排'),
    ('jueyi', '决议', '会议讨论通过的重要事项的决策'),
    ('minglin', '命令', '依照有关法律公布行政法规和规章、宣布施行重大强制性措施'),
    ('pifu', '批复', '答复下级机关请示事项'),
    ('qingshi', '请示', '向上级机关请求指示或批准'),
    ('tongbao', '通报', '表彰先进、批评错误、传达重要精神或情况'),
    ('tonggao', '通告', '公开宣布重要事项或者法定事项'),
    ('tongzhi', '通知', '发布、传达要求下级机关执行和有关单位周知或者执行的事项'),
    ('yian', '议案', '正式提出审议事项的文书'),
    ('yijian', '意见', '对重要问题提出见解和处理办法')
]

# 公文字段定义
DOCUMENT_FIELDS = [
    # 版头字段
    ('份号', 'copyNumber', 'text', '版头', False),
    ('密级', 'securityLevel', 'select', '版头', True),
    ('保密期限', 'securityPeriod', 'text', '版头', False),
    ('紧急程度', 'urgencyLevel', 'select', '版头', False),
    ('发文机关名称', 'sender', 'text', '版头', True),
    ('标志', 'senderSymbol', 'text', '版头', False),
    ('发文机关代字', 'senderCode', 'text', '版头', False),
    ('年份', 'year', 'text', '版头', False),
    ('发文顺序号', 'serialNumber', 'text', '版头', False),
    
    # 主体字段
    ('标题', 'title', 'text', '主体', True),
    ('主送机关', 'recipient', 'text', '主体', False),
    ('正文', 'content', 'textarea', '主体', True),
    
    # 发文机关或签发人署名
    ('发文机关署名', 'senderSignature', 'text', '署名', False),
    ('成文日期', 'date', 'date', '署名', True),
    ('附注', 'notes', 'text', '署名', False),
    
    # 版记
    ('抄送机关', 'copyTo', 'textarea', '版记', False),
    
    # 印发机关和印发日期
    ('印发机关', 'printingOrg', 'text', '印发', False),
    ('印发日期', 'printingDate', 'date', '印发', False)
]