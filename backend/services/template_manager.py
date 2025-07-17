import os
from typing import List, Dict, Any
from models.document_models import TemplateInfo, DOCUMENT_TYPES

class TemplateManager:
    """模板管理服务"""
    
    def __init__(self):
        self.templates_dir = "../frontend/templates"
        self.template_cache = {}
        self._load_templates()
        print(f"模板目录: {os.path.abspath(self.templates_dir)}")
    
    def _load_templates(self):
        """加载所有模板信息"""
        print("开始加载模板...")
        
        # 检查模板目录是否存在
        if not os.path.exists(self.templates_dir):
            print(f"警告: 模板目录不存在: {self.templates_dir}")
            os.makedirs(self.templates_dir, exist_ok=True)
        
        # 列出模板目录中的文件
        existing_files = os.listdir(self.templates_dir)
        print(f"模板目录中的文件: {existing_files}")
        
        # 加载所有模板
        for doc_type, info in DOCUMENT_TYPES.items():
            template_filename = f"{doc_type}.docx"
            template_path = os.path.join(self.templates_dir, template_filename)
            
            # 检查模板文件是否存在
            file_exists = os.path.exists(template_path)
            print(f"模板 {template_filename}: {'存在' if file_exists else '不存在'}")
            
            # 即使文件不存在也添加到缓存中，以便前端可以显示
            self.template_cache[doc_type] = TemplateInfo(
                id=doc_type,
                name=info["name"],
                description=info["description"],
                category="党政机关公文",
                file_path=template_path,
                preview_image=f"/static/previews/{doc_type}.png"
            )
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """获取所有可用模板"""
        templates = []
        for template_id, template_info in self.template_cache.items():
            templates.append({
                "id": template_info.id,
                "name": template_info.name,
                "description": template_info.description,
                "category": template_info.category,
                "preview_image": template_info.preview_image
            })
        return templates
    
    def get_template_by_id(self, template_id: str) -> TemplateInfo:
        """根据ID获取模板信息"""
        if template_id not in self.template_cache:
            raise ValueError(f"模板不存在: {template_id}")
        return self.template_cache[template_id]
    
    def get_template_requirements(self, template_id: str) -> Dict[str, Any]:
        """获取模板所需的字段信息"""
        base_fields = {
            "title": {"name": "标题", "required": True, "type": "text"},
            "sender": {"name": "发文机关", "required": True, "type": "text"},
            "content": {"name": "正文内容", "required": True, "type": "textarea"},
            "date": {"name": "发文日期", "required": False, "type": "date"}
        }
        
        # 根据不同公文类型添加特定字段
        specific_fields = self._get_specific_fields(template_id)
        base_fields.update(specific_fields)
        
        return base_fields
    
    def _get_specific_fields(self, template_id: str) -> Dict[str, Any]:
        """获取特定公文类型的字段"""
        specific_fields = {}
        
        if template_id in ["qingshi"]:  # 请示
            specific_fields.update({
                "recipient": {"name": "收文机关", "required": True, "type": "text"},
                "urgency_level": {"name": "紧急程度", "required": False, "type": "select", 
                                "options": ["特急", "急件", "一般"]}
            })
        
        elif template_id in ["baogao"]:  # 报告
            specific_fields.update({
                "report_type": {"name": "报告类型", "required": False, "type": "select",
                              "options": ["工作报告", "情况报告", "答复报告"]}
            })
        
        elif template_id in ["tongzhi"]:  # 通知
            specific_fields.update({
                "execution_time": {"name": "执行时间", "required": False, "type": "date"},
                "contact_person": {"name": "联系人", "required": False, "type": "text"}
            })
        
        return specific_fields