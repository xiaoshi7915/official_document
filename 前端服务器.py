#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的前端服务器
支持SPA路由和API代理
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import urllib.error
import json
from urllib.parse import urlparse

# 后端API地址
BACKEND_URL = "http://localhost:5003"
# 前端静态文件目录
FRONTEND_DIR = "/opt/official_ai_writer/official_document/frontend/dist"

class ImprovedHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        try:
            # 解析URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # 如果是API请求，转发到后端
            if path.startswith('/api/'):
                self.proxy_to_backend('GET', path, parsed_url.query)
                return
            
            # 如果是静态资源（assets、templates等），直接提供
            if path.startswith('/assets/') or path.startswith('/templates/'):
                self.serve_static_file(path)
                return
            
            # 其他所有请求都返回index.html（SPA路由支持）
            self.serve_spa_file(path)
            
        except Exception as e:
            print(f"GET请求处理错误: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def do_POST(self):
        """处理POST请求"""
        try:
            # 解析URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # 如果是API请求，转发到后端
            if path.startswith('/api/'):
                self.proxy_to_backend('POST', path, parsed_url.query)
                return
            
            # 其他POST请求返回404
            self.send_error(404, "Not Found")
            
        except Exception as e:
            print(f"POST请求处理错误: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def proxy_to_backend(self, method, path, query):
        """将请求代理到后端"""
        try:
            # 构建后端URL
            backend_url = f"{BACKEND_URL}{path}"
            if query:
                backend_url += f"?{query}"
            
            print(f"代理请求: {method} {backend_url}")
            
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = None
            if content_length > 0:
                post_data = self.rfile.read(content_length)
            
            # 构建请求
            req = urllib.request.Request(backend_url, data=post_data, method=method)
            
            # 复制请求头
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'content-length']:
                    req.add_header(header, value)
            
            # 发送请求到后端
            with urllib.request.urlopen(req) as response:
                # 读取响应
                response_data = response.read()
                
                # 发送响应头
                self.send_response(response.status)
                for header, value in response.getheaders():
                    if header.lower() not in ['transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                # 发送响应体
                self.wfile.write(response_data)
                
        except urllib.error.HTTPError as e:
            print(f"后端HTTP错误: {e.code} {e.reason}")
            self.send_error(e.code, e.reason)
        except urllib.error.URLError as e:
            print(f"后端连接错误: {e}")
            self.send_error(502, f"Bad Gateway: {e}")
        except Exception as e:
            print(f"代理错误: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def serve_static_file(self, path):
        """提供静态文件"""
        try:
            # URL解码路径
            decoded_path = urllib.parse.unquote(path)
            
            # 构建文件路径
            file_path = os.path.join(FRONTEND_DIR, decoded_path.lstrip('/'))
            
            # 检查文件是否存在
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                print(f"文件不存在: {file_path}")
                self.send_error(404, "File not found")
                return
            
            # 获取文件扩展名
            _, ext = os.path.splitext(file_path)
            
            # 设置MIME类型
            mime_types = {
                '.html': 'text/html',
                '.js': 'application/javascript',
                '.css': 'text/css',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon',
                '.json': 'application/json',
                '.woff': 'font/woff',
                '.woff2': 'font/woff2',
                '.ttf': 'font/ttf',
                '.eot': 'application/vnd.ms-fontobject'
            }
            
            content_type = mime_types.get(ext, 'application/octet-stream')
            
            # 读取文件
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            print(f"静态文件服务错误: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def serve_spa_file(self, path):
        """提供SPA文件（所有路由都返回index.html）"""
        try:
            # 总是返回index.html
            file_path = os.path.join(FRONTEND_DIR, 'index.html')
            
            if not os.path.exists(file_path):
                self.send_error(404, "index.html not found")
                return
            
            # 读取文件
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            print(f"SPA文件服务错误: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    """主函数"""
    port = 8081
    
    # 检查前端目录是否存在
    if not os.path.exists(FRONTEND_DIR):
        print(f"错误: 前端目录不存在: {FRONTEND_DIR}")
        print("请先构建前端项目: cd frontend && npm run build")
        sys.exit(1)
    
    # 检查后端是否运行
    try:
        import urllib.request
        urllib.request.urlopen(f"{BACKEND_URL}/api/templates", timeout=5)
        print(f"✓ 后端服务正常: {BACKEND_URL}")
    except Exception as e:
        print(f"⚠ 后端服务可能未运行: {BACKEND_URL}")
        print(f"错误: {e}")
    
    print(f"启动改进的前端服务器...")
    print(f"前端目录: {FRONTEND_DIR}")
    print(f"后端地址: {BACKEND_URL}")
    print(f"监听端口: {port}")
    print(f"访问地址: http://localhost:{port}")
    print(f"支持SPA路由和API代理")
    
    # 启动服务器
    server = HTTPServer(('0.0.0.0', port), ImprovedHandler)
    print(f"服务器已启动，按 Ctrl+C 停止")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")

if __name__ == '__main__':
    main() 