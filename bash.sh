#!/bin/bash
echo "服务监听 5002 端口的进程信息："
sudo ss -tulnp | grep :5002

echo ""
echo "对应的可执行文件路径："
for pid in $(sudo lsof -t -i :5002); do
    echo "PID: $pid -> $(sudo readlink -f /proc/$pid/exe)"
done