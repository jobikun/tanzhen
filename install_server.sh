#!/bin/bash

echo "=== 开始安装系统监控服务端 ==="

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
pip install flask psutil requests

# 创建服务端程序
echo "创建服务端程序..."
cat > probe_server.py << 'EOF'
# 这里粘贴 probe_server.py 的完整代码
EOF

# 创建服务文件
echo "创建系统服务..."
sudo bash -c 'cat > /etc/systemd/system/probe-server.service << EOF
[Unit]
Description=System Monitor Server
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$HOME/linux-probe/venv/bin/python $HOME/linux-probe/probe_server.py
WorkingDirectory=$HOME/linux-probe
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

# 启动服务
echo "启动服务..."
sudo systemctl daemon-reload
sudo systemctl start probe-server
sudo systemctl enable probe-server

echo "=== 安装完成！ ==="
echo "服务端已启动，访问地址: http://本机IP:5000"
echo "默认管理员账号: admin"
echo "默认密码: admin123"
echo "请及时修改默认密码！" 