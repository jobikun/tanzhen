#!/bin/bash

echo "=== 开始安装系统监控客户端 ==="

# 获取服务器地址
read -p "请输入服务器IP地址: " SERVER_IP
if [ -z "$SERVER_IP" ]; then
    echo "错误：服务器IP不能为空"
    exit 1
fi

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "正在安装Python3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

# 创建工作目录
echo "创建工作目录..."
mkdir -p ~/linux-probe
cd ~/linux-probe

# 创建虚拟环境
echo "创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install psutil requests

# 创建客户端程序
echo "创建客户端程序..."
cat > probe_client.py << 'EOF'
# 这里粘贴 probe_client.py 的完整代码
EOF

# 修改服务器地址
sed -i "s|SERVER_URL = \"http://localhost:5000\"|SERVER_URL = \"http://$SERVER_IP:5000\"|g" probe_client.py

# 创建服务文件
echo "创建系统服务..."
sudo bash -c 'cat > /etc/systemd/system/probe-client.service << EOF
[Unit]
Description=System Monitor Client
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$HOME/linux-probe/venv/bin/python $HOME/linux-probe/probe_client.py
WorkingDirectory=$HOME/linux-probe
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

# 启动服务
echo "启动服务..."
sudo systemctl daemon-reload
sudo systemctl start probe-client
sudo systemctl enable probe-client

echo "=== 安装完成！ ==="
echo "客户端已启动并设置为开机自启"
echo "查看状态: sudo systemctl status probe-client" 