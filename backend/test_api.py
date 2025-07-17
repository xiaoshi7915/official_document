#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
用于测试党政机关公文生成服务的各个接口
"""

import requests
import json
import os
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000"

def test_root():
    """测试根路径"""
    print("测试根路径...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_get_templates():
    """测试获取模板列表"""
    print("\n测试获取模板列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/templates")
        print(f"状态码: {response.status_code}")
        templates = response.json()
        print(f"模板数量: {len(templates)}")
        for template in templates[:3]:  # 只显示前3个
            print(f"- {template['name']}: {template['description']}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_generate_document():
    """测试生成文档"""
    print("\n测试生成文档...")
    try:
        # 测试数据
        test_data = {
            "content": """# 关于加强办公管理的通知

各部门：

为进一步规范办公秩序，提高工作效率，现就有关事项通知如下：

## 一、办公时间管理
严格执行作息时间，按时上下班。

## 二、办公环境维护
保持办公区域整洁，节约用电用水。

## 三、文件管理
及时归档重要文件，做好保密工作。

请各部门认真贯彻执行。""",
            "template_type": "tongzhi",
            "metadata": {
                "title": "关于加强办公管理的通知",
                "sender": "××公司办公室",
                "recipient": "各部门",
                "document_number": "办发〔2025〕1号",
                "urgency_level": "一般",
                "security_level": "一般",
                "date": "2025年1月16日",
                "format_type": "markdown"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {result}")
        
        if response.status_code == 200 and result.get("success"):
            print(f"文档生成成功: {result.get('download_url')}")
            return True
        else:
            print(f"文档生成失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_upload_file():
    """测试文件上传"""
    print("\n测试文件上传...")
    try:
        # 创建测试文件
        test_content = """# 测试文档

这是一个测试用的Markdown文档。

## 主要内容
- 项目1
- 项目2
- 项目3

感谢使用本系统。"""
        
        test_file_path = "test_upload.md"
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # 上传文件
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_upload.md", f, "text/markdown")}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"上传结果: {result.get('success', False)}")
        if result.get("content"):
            print(f"解析内容长度: {len(result['content'])} 字符")
        
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        
        return response.status_code == 200 and result.get("success")
        
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("党政机关公文生成服务 API 测试")
    print("=" * 50)
    
    tests = [
        ("根路径测试", test_root),
        ("模板列表测试", test_get_templates),
        ("文档生成测试", test_generate_document),
        ("文件上传测试", test_upload_file)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
        print(f"结果: {'✓ 通过' if success else '✗ 失败'}")
    
    print(f"\n{'='*50}")
    print("测试总结:")
    print(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常。")
    else:
        print("⚠️  部分测试失败，请检查系统配置。")

if __name__ == "__main__":
    main()