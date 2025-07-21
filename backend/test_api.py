import requests
import json

# 测试API端点
BASE_URL = "http://localhost:5002"

def test_get_templates():
    """测试获取模板列表"""
    print("测试获取模板列表...")
    response = requests.get(f"{BASE_URL}/api/templates")
    if response.status_code == 200:
        data = response.json()
        print(f"成功获取 {len(data['data'])} 个模板")
        for template in data['data'][:3]:  # 显示前3个
            print(f"  - {template['name']}: {template['description']}")
    else:
        print(f"获取模板失败: {response.status_code}")

def test_generate_title():
    """测试生成标题"""
    print("\n测试生成标题...")
    test_content = """
    根据市委、市政府关于加强城市管理工作的要求，为进一步提升我市城市管理水平，
    现就相关工作安排通知如下：一是加强市容环境整治，二是完善基础设施建设，
    三是提高服务质量水平。请各相关部门认真贯彻执行。
    """
    
    response = requests.post(f"{BASE_URL}/api/generate-title", 
                           json={"content": test_content})
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"生成的标题: {data['title']}")
        else:
            print(f"生成标题失败: {data['message']}")
    else:
        print(f"API调用失败: {response.status_code}")

def test_generate_content():
    """测试生成内容"""
    print("\n测试生成内容...")
    response = requests.post(f"{BASE_URL}/api/generate-content", 
                           json={
                               "topic": "关于加强办公室安全管理的工作安排",
                               "document_type": "通知"
                           })
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"生成的内容: {data['content'][:200]}...")
        else:
            print(f"生成内容失败: {data['message']}")
    else:
        print(f"API调用失败: {response.status_code}")

def test_generate_document():
    """测试生成文档"""
    print("\n测试生成文档...")
    test_data = {
        "template_type": "tongzhi",
        "content": "根据上级要求，现就相关工作通知如下：\n\n一、工作要求\n请各部门高度重视...\n\n二、时间安排\n本通知自发布之日起执行。",
        "metadata": {
            "title": "关于加强工作管理的通知",
            "sender": "某某市人民政府办公室",
            "recipient": "各区县政府，市政府各部门",
            "senderCode": "市政办发",
            "year": "2025",
            "serialNumber": "1",
            "date": "2025年1月21日",
            "urgencyLevel": "一般",
            "securityLevel": "一般",
            "format_type": "plain"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/generate", json=test_data)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"文档生成成功，下载链接: {data['download_url']}")
        else:
            print(f"文档生成失败: {data['message']}")
    else:
        print(f"API调用失败: {response.status_code}")

if __name__ == "__main__":
    print("开始测试API功能...")
    
    # 测试各个API端点
    test_get_templates()
    test_generate_title()
    test_generate_content()
    test_generate_document()
    
    print("\n测试完成！")