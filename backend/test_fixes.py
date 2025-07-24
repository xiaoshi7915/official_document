#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复的问题
验证所有修复是否正常工作
"""

import requests
import json
import sys

def test_signin_route():
    """测试signin路由"""
    print("🔍 测试signin路由...")
    
    try:
        # 测试GET请求
        response = requests.get('http://localhost:5003/signin')
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'redirect':
                print("✅ signin GET请求正常")
            else:
                print("❌ signin GET请求响应格式错误")
                return False
        else:
            print(f"❌ signin GET请求失败: {response.status_code}")
            return False
        
        # 测试POST请求
        response = requests.post('http://localhost:5003/signin', 
                               json={'username': 'test', 'password': 'test'})
        if response.status_code == 200:
            data = response.json()
            if data.get('success') == True:
                print("✅ signin POST请求正常")
            else:
                print("❌ signin POST请求响应格式错误")
                return False
        else:
            print(f"❌ signin POST请求失败: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ signin路由测试异常: {e}")
        return False

def test_404_error_handling():
    """测试404错误处理"""
    print("🔍 测试404错误处理...")
    
    try:
        response = requests.get('http://localhost:5003/invalid-path')
        if response.status_code == 404:
            data = response.json()
            if 'error' in data and 'available_paths' in data:
                print("✅ 404错误处理正常")
                return True
            else:
                print("❌ 404错误处理响应格式错误")
                return False
        else:
            print(f"❌ 404错误处理失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 404错误处理测试异常: {e}")
        return False

def test_existing_apis():
    """测试现有API是否正常"""
    print("🔍 测试现有API...")
    
    try:
        # 测试模板API
        response = requests.get('http://localhost:5003/api/templates')
        if response.status_code == 200:
            print("✅ 模板API正常")
        else:
            print(f"❌ 模板API失败: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 现有API测试异常: {e}")
        return False

def test_logging():
    """测试日志配置"""
    print("🔍 检查日志配置...")
    
    try:
        # 测试统一的日志管理器
        from utils.logger import get_logger, setup_logging
        setup_logging()
        
        # 测试不同模块的日志记录器
        app_logger = get_logger('backend.app')
        route_logger = get_logger('backend.routes.test')
        service_logger = get_logger('backend.services.test')
        
        print("✅ 统一日志管理器工作正常")
        
        # 检查werkzeug日志级别
        import logging
        werkzeug_logger = logging.getLogger('werkzeug')
        if werkzeug_logger.level == logging.WARNING:
            print("✅ werkzeug日志级别设置正确")
        else:
            print(f"⚠️ werkzeug日志级别: {werkzeug_logger.level}")
            
        return True
        
    except Exception as e:
        print(f"❌ 日志配置检查异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试修复的问题...")
    print("=" * 50)
    
    tests = [
        ("signin路由", test_signin_route),
        ("404错误处理", test_404_error_handling),
        ("现有API", test_existing_apis),
        ("日志配置", test_logging)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！修复成功！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 