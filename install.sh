#!/bin/bash

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "Python3 未安装，正在安装..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

# 安装虚拟环境
if ! command -v virtualenv &> /dev/null; then
    echo "正在安装virtualenv..."
    pip3 install virtualenv
fi

# 创建虚拟环境
echo "创建虚拟环境..."
virtualenv venv
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -e .

# 创建配置目录
mkdir -p ~/.config/linux-system-probe

# 创建默认配置文件
cat > ~/.config/linux-system-probe/config.ini << EOF
[server]
host = 0.0.0.0
port = 5000
secret_key = change-this-to-your-secret-key

[client]
server_url = http://localhost:5000
report_interval = 60

[admin]
username = admin
password = admin123
EOF

# 创建系统服务文件
echo "创建系统服务..."

# 服务端服务
sudo cat > /etc/systemd/system/probe-server.service << EOF
[Unit]
Description=Linux System Probe Server
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$PWD/venv/bin/probe-server
WorkingDirectory=$PWD
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 客户端服务
sudo cat > /etc/systemd/system/probe-client.service << EOF
[Unit]
Description=Linux System Probe Client
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$PWD/venv/bin/probe-client
WorkingDirectory=$PWD
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
sudo systemctl daemon-reload

echo "安装完成！"
echo "启动服务端: sudo systemctl start probe-server"
echo "启动客户端: sudo systemctl start probe-client"
echo "查看服务端状态: sudo systemctl status probe-server"
echo "查看客户端状态: sudo systemctl status probe-client"
echo "设置开机自启: sudo systemctl enable probe-server probe-client" 