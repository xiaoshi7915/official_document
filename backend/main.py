from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import tempfile
import uuid
from datetime import datetime

from services.document_processor import DocumentProcessor
from services.template_manager import TemplateManager
from models.document_models import DocumentRequest, DocumentResponse

app = FastAPI(
    title="党政机关公文生成智能体",
    description="基于GB/T9704-2012标准的公文自动生成API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入模板预览服务
from services.template_preview import TemplatePreviewService

# 初始化服务
document_processor = DocumentProcessor()
template_manager = TemplateManager()
template_preview_service = TemplatePreviewService(template_manager.templates_dir)

@app.get("/")
async def root():
    return {"message": "党政机关公文生成服务API"}

@app.get("/api/templates")
async def get_templates():
    """获取所有可用的公文模板"""
    return template_manager.get_available_templates()

@app.post("/api/generate", response_model=DocumentResponse)
async def generate_document(request: DocumentRequest):
    """根据输入内容和模板生成公文"""
    try:
        # 生成文档
        output_path = document_processor.generate_document(
            content=request.content,
            template_type=request.template_type,
            metadata=request.metadata.dict()
        )
        
        return DocumentResponse(
            success=True,
            message="文档生成成功",
            file_path=output_path,
            download_url=f"/api/download/{os.path.basename(output_path)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件并解析内容"""
    try:
        # 保存上传的文件
        temp_path = f"temp/{uuid.uuid4()}_{file.filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 解析文件内容
        parsed_content = document_processor.parse_uploaded_file(temp_path)
        
        # 清理临时文件
        os.remove(temp_path)
        
        return {
            "success": True,
            "content": parsed_content,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/template-preview/{template_id}")
async def get_template_preview(template_id: str):
    """获取模板预览内容"""
    try:
        preview_data = template_preview_service.get_template_content(template_id)
        return preview_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """下载生成的文档"""
    file_path = f"output/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)