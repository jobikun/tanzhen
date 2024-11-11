#!/bin/bash

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
plain='\033[0m'

# 选择安装类型
echo -e "${yellow}请选择安装类型:${plain}"
echo -e "${green}1. 服务端${plain}"
echo -e "${green}2. 客户端${plain}"
read -p "请输入[1-2]: " choose

case $choose in
    1)
        # 安装服务端
        echo -e "${yellow}开始安装服务端...${plain}"
        
        # 安装Go
        if ! command -v go &> /dev/null; then
            echo -e "${yellow}正在安装Go...${plain}"
            wget https://golang.org/dl/go1.21.0.linux-amd64.tar.gz
            sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
            echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
            source ~/.bashrc
            rm go1.21.0.linux-amd64.tar.gz
        fi
        
        # 创建工作目录
        mkdir -p ~/monitor/server
        cd ~/monitor/server
        
        # 创建server.go
        echo -e "${yellow}创建服务端程序...${plain}"
        cat > server.go << 'EOF'
        # 这里是server.go的完整代码
EOF
        
        # 初始化Go模块
        go mod init monitor
        go get github.com/gin-gonic/gin
        go get github.com/gin-contrib/sessions
        
        # 编译
        go build -o monitor-server
        
        # 创建服务
        echo -e "${yellow}创建系统服务...${plain}"
        sudo bash -c 'cat > /etc/systemd/system/monitor-server.service << EOF
[Unit]
Description=Monitor Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/monitor/server
ExecStart=$HOME/monitor/server/monitor-server
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

        # 启动服务
        sudo systemctl daemon-reload
        sudo systemctl start monitor-server
        sudo systemctl enable monitor-server
        
        # 生成密钥
        CLIENT_SECRET=$(generate_secret)
        echo "生成客户端连接密钥: $CLIENT_SECRET"
        
        # 修改server.go中的密钥
        sed -i "s/your-secret-key-here/$CLIENT_SECRET/g" server.go
        
        # 保存密钥到配置文件
        echo "CLIENT_SECRET=$CLIENT_SECRET" > ~/monitor/server/config.env
        
        echo -e "${green}服务端安装完成！${plain}"
        echo -e "${yellow}访问地址: http://本机IP:5000${plain}"
        echo -e "${yellow}用户名: admin${plain}"
        echo -e "${yellow}密码: admin123${plain}"
        ;;
        
    2)
        # 安装客户端
        echo -e "${yellow}开始安装客户端...${plain}"
        
        # 获取服务器地址
        read -p "请输入服务器IP: " server_ip
        if [ -z "$server_ip" ]; then
            echo -e "${red}错误：服务器IP不能为空${plain}"
            exit 1
        fi
        
        # 安装Go
        if ! command -v go &> /dev/null; then
            echo -e "${yellow}正在安装Go...${plain}"
            wget https://golang.org/dl/go1.21.0.linux-amd64.tar.gz
            sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
            echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
            source ~/.bashrc
            rm go1.21.0.linux-amd64.tar.gz
        fi
        
        # 创建工作目录
        mkdir -p ~/monitor/client
        cd ~/monitor/client
        
        # 创建client.go
        echo -e "${yellow}创建客户端程序...${plain}"
        cat > client.go << 'EOF'
        # 这里是client.go的完整代码
EOF
        
        # 初始化Go模块
        go mod init monitor
        go get github.com/shirou/gopsutil
        
        # 编译
        go build -o monitor-client
        
        # 创建服务
        echo -e "${yellow}创建系统服务...${plain}"
        sudo bash -c 'cat > /etc/systemd/system/monitor-client.service << EOF
[Unit]
Description=Monitor Client
After=network.target

[Service]
Type=simple
User=$USER
Environment="SERVER_URL=http://'$server_ip':5000"
WorkingDirectory=$HOME/monitor/client
ExecStart=$HOME/monitor/client/monitor-client
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

        # 获取服务器密钥
        read -p "请输入服务端提供的密钥: " client_secret
        if [ -z "$client_secret" ]; then
            echo -e "${red}错误：密钥不能为空${plain}"
            exit 1
        fi
        
        # 修改客户端环境变量
        echo "CLIENT_SECRET=$client_secret" >> /etc/systemd/system/monitor-client.service
        
        # 启动服务
        sudo systemctl daemon-reload
        sudo systemctl start monitor-client
        sudo systemctl enable monitor-client
        
        echo -e "${green}客户端安装完成！${plain}"
        ;;
        
    *)
        echo -e "${red}请输入正确的数字 [1-2]${plain}"
        ;;
esac 