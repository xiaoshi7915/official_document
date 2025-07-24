#!/bin/bash

echo "配置防火墙规则..."

# 检查firewalld状态
if systemctl is-active --quiet firewalld; then
    echo "firewalld服务正在运行"
    
    # 开放端口
    firewall-cmd --permanent --add-port=5003/tcp
    firewall-cmd --permanent --add-port=8081/tcp
    
    # 重新加载配置
    firewall-cmd --reload
    
    echo "防火墙规则已配置"
else
    echo "firewalld未运行，尝试使用iptables"
    
    # 使用iptables
    iptables -I INPUT -p tcp --dport 5003 -j ACCEPT
    iptables -I INPUT -p tcp --dport 8081 -j ACCEPT
    
    # 保存规则
    service iptables save 2>/dev/null || echo "无法保存iptables规则"
    
    echo "iptables规则已配置"
fi

echo "防火墙配置完成" 