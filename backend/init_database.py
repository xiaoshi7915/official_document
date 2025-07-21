import mysql.connector
import json

# 数据库配置
DB_CONFIG = {
    'host': '47.118.250.53',
    'port': 3306,
    'database': 'official_doc',
    'user': 'official_doc',
    'password': 'admin123456!'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
        return None

def init_database():
    """初始化数据库表"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 创建公文类型表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_types (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT
            )
        """)
        
        # 创建公文字段表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_fields (
                id INT AUTO_INCREMENT PRIMARY KEY,
                field_name VARCHAR(100) NOT NULL,
                field_key VARCHAR(100) NOT NULL,
                field_type VARCHAR(50) NOT NULL,
                field_category VARCHAR(50) NOT NULL,
                is_required BOOLEAN DEFAULT FALSE,
                parent_field_id INT,
                document_type_id VARCHAR(50),
                FOREIGN KEY (parent_field_id) REFERENCES document_fields(id),
                FOREIGN KEY (document_type_id) REFERENCES document_types(id)
            )
        """)
        
        # 创建用户生成的公文表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                document_type_id VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (document_type_id) REFERENCES document_types(id)
            )
        """)
        
        # 插入15种公文类型
        document_types = [
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
        
        for doc_type in document_types:
            cursor.execute("""
                INSERT IGNORE INTO document_types (id, name, description) 
                VALUES (%s, %s, %s)
            """, doc_type)
        
        # 插入公文字段定义（以报告为例）
        document_fields = [
            # 版头字段
            ('份号', 'copyNumber', 'text', '版头', False, None, 'baogao'),
            ('密级', 'securityLevel', 'select', '版头', True, None, 'baogao'),
            ('保密期限', 'securityPeriod', 'text', '版头', False, None, 'baogao'),
            ('紧急程度', 'urgencyLevel', 'select', '版头', False, None, 'baogao'),
            ('发文机关名称', 'sender', 'text', '版头', True, None, 'baogao'),
            ('标志', 'senderSymbol', 'text', '版头', False, None, 'baogao'),
            ('发文机关代字', 'senderCode', 'text', '版头', False, None, 'baogao'),
            ('年份', 'year', 'text', '版头', False, None, 'baogao'),
            ('发文顺序号', 'serialNumber', 'text', '版头', False, None, 'baogao'),
            
            # 主体字段
            ('标题', 'title', 'text', '主体', True, None, 'baogao'),
            ('主送机关', 'recipient', 'text', '主体', False, None, 'baogao'),
            ('正文', 'content', 'textarea', '主体', True, None, 'baogao'),
            
            # 发文机关或签发人署名
            ('发文机关署名', 'senderSignature', 'text', '署名', False, None, 'baogao'),
            ('成文日期', 'date', 'date', '署名', True, None, 'baogao'),
            ('附注', 'notes', 'text', '署名', False, None, 'baogao'),
            
            # 版记
            ('抄送机关', 'copyTo', 'textarea', '版记', False, None, 'baogao'),
            
            # 印发机关和印发日期
            ('印发机关', 'printingOrg', 'text', '印发', False, None, 'baogao'),
            ('印发日期', 'printingDate', 'date', '印发', False, None, 'baogao')
        ]
        
        for field in document_fields:
            cursor.execute("""
                INSERT IGNORE INTO document_fields 
                (field_name, field_key, field_type, field_category, is_required, parent_field_id, document_type_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, field)
        
        conn.commit()
        print("数据库初始化成功")
        return True
        
    except Exception as e:
        print(f"数据库初始化错误: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_database()