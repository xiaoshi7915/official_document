import os
import base64
import tempfile
import subprocess
import docx2txt
from docx import Document
from typing import Dict, Any, List, Optional
from .docx_converter import DocxConverter

class TemplatePreviewService:
    """模板预览服务"""
    
    def __init__(self, templates_dir: str):
        self.templates_dir = templates_dir
        self.docx_converter = DocxConverter()
    
    def get_template_content(self, template_id: str) -> Dict[str, Any]:
        """获取模板文件内容"""
        template_path = os.path.join(self.templates_dir, f"{template_id}.docx")
        
        if not os.path.exists(template_path):
            print(f"模板文件不存在: {template_path}")
            return {
                "success": False,
                "message": f"模板文件不存在: {template_id}.docx",
                "content": None
            }
        
        try:
            # 提取文本内容
            text_content = docx2txt.process(template_path)
            
            # 转换为HTML
            html_content, html_error = self.docx_converter.docx_to_html(template_path)
            
            # 提取文档结构
            structure, structure_error = self.docx_converter.extract_docx_structure(template_path)
            
            # 尝试转换为图片（如果环境支持）
            try:
                image_content, image_error = self.docx_converter.docx_to_image(template_path)
            except:
                image_content, image_error = None, "转换图片功能不可用"
            
            return {
                "success": True,
                "message": "模板内容获取成功",
                "content": text_content,
                "html_content": html_content,
                "html_error": html_error,
                "image_content": image_content,
                "image_error": image_error,
                "structure": structure,
                "structure_error": structure_error,
                "template_id": template_id
            }
        except Exception as e:
            print(f"读取模板文件出错: {str(e)}")
            return {
                "success": False,
                "message": f"读取模板文件出错: {str(e)}",
                "content": None
            }
    
    def _get_alignment(self, paragraph) -> str:
        """获取段落对齐方式"""
        try:
            if paragraph.alignment == 0:
                return "left"
            elif paragraph.alignment == 1:
                return "center"
            elif paragraph.alignment == 2:
                return "right"
            elif paragraph.alignment == 3:
                return "justify"
            else:
                return "left"
        except:
            return "left"