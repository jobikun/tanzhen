from flask import Flask, request, jsonify, session, redirect, url_for
import json
from datetime import datetime
import os
from collections import defaultdict
from functools import wraps
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 请修改为随机的密钥

# 存储所有客户端数据
clients_data = defaultdict(list)
# 存储客户端最后上报时间
clients_last_seen = {}

# 管理员配置
ADMIN_CONFIG = {
    'admin': hashlib.sha256('admin123'.encode()).hexdigest()  # 默认密码：admin123
}

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录处理"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in ADMIN_CONFIG and \
           ADMIN_CONFIG[username] == hashlib.sha256(password.encode()).hexdigest():
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        
        return '''
            <script>alert('用户名或密码错误！'); window.location.href='/login';</script>
        '''
    
    return '''
    <html>
        <head>
            <title>管理员登录</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .login-form {
                    max-width: 300px;
                    margin: 50px auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                input {
                    width: 100%;
                    padding: 8px;
                    margin: 8px 0;
                    box-sizing: border-box;
                }
                button {
                    width: 100%;
                    padding: 10px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <div class="login-form">
                <h2>管理员登录</h2>
                <form method="post">
                    <input type="text" name="username" placeholder="用户名" required>
                    <input type="password" name="password" placeholder="密码" required>
                    <button type="submit">登录</button>
                </form>
            </div>
        </body>
    </html>
    '''

@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        username = session['username']
        
        if ADMIN_CONFIG[username] != hashlib.sha256(old_password.encode()).hexdigest():
            return '''
                <script>alert('原密码错误！'); window.location.href='/change_password';</script>
            '''
        
        if new_password != confirm_password:
            return '''
                <script>alert('两次输入的新密码不一致！'); window.location.href='/change_password';</script>
            '''
        
        ADMIN_CONFIG[username] = hashlib.sha256(new_password.encode()).hexdigest()
        return '''
            <script>alert('密码修改成功！'); window.location.href='/';</script>
        '''
    
    return '''
    <html>
        <head>
            <title>修改密码</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .password-form {
                    max-width: 300px;
                    margin: 50px auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                input {
                    width: 100%;
                    padding: 8px;
                    margin: 8px 0;
                    box-sizing: border-box;
                }
                button {
                    width: 100%;
                    padding: 10px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <div class="password-form">
                <h2>修改密码</h2>
                <form method="post">
                    <input type="password" name="old_password" placeholder="原密码" required>
                    <input type="password" name="new_password" placeholder="新密码" required>
                    <input type="password" name="confirm_password" placeholder="确认新密码" required>
                    <button type="submit">修改</button>
                </form>
                <p><a href="/">返回首页</a></p>
            </div>
        </body>
    </html>
    '''

@app.route('/report', methods=['POST'])
def report():
    """接收客户端上报的数据"""
    try:
        data = request.get_json()
        client_ip = data['ip']
        
        clients_data[client_ip].append(data)
        if len(clients_data[client_ip]) > 100:
            clients_data[client_ip].pop(0)
            
        clients_last_seen[client_ip] = datetime.now()
        
        save_to_file(data)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/clients', methods=['GET'])
@login_required
def get_clients():
    """获取所有客户端列表"""
    clients = []
    for ip, last_seen in clients_last_seen.items():
        latest_data = clients_data[ip][-1] if clients_data[ip] else None
        if latest_data:
            clients.append({
                'ip': ip,
                'hostname': latest_data['hostname'],
                'system': latest_data['system'],
                'last_seen': last_seen.strftime('%Y-%m-%d %H:%M:%S'),
                'status': '在线' if (datetime.now() - last_seen).seconds < 180 else '离线'
            })
    return jsonify(clients)

@app.route('/client/<ip>', methods=['GET'])
@login_required
def get_client_data(ip):
    """获取指定客户端的详细数据"""
    if ip in clients_data:
        return jsonify(clients_data[ip][-1])
    return jsonify({"error": "Client not found"}), 404

def save_to_file(data):
    """保存数据到文件"""
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"logs/probe_{date_str}.json"
    
    os.makedirs('logs', exist_ok=True)
    
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

@app.route('/')
@login_required
def index():
    """Web控制台主页"""
    return '''
    <html>
        <head>
            <title>系统探针控制台</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                .user-info {
                    text-align: right;
                }
                .client { border: 1px solid #ddd; padding: 10px; margin: 10px 0; }
                .online { color: green; }
                .offline { color: red; }
                .button {
                    padding: 5px 10px;
                    margin-left: 10px;
                    text-decoration: none;
                    color: white;
                    background-color: #4CAF50;
                    border-radius: 4px;
                }
                .button.logout {
                    background-color: #f44336;
                }
            </style>
            <script>
                function updateClients() {
                    fetch('/clients')
                        .then(response => response.json())
                        .then(clients => {
                            const container = document.getElementById('clients');
                            container.innerHTML = '';
                            clients.forEach(client => {
                                const div = document.createElement('div');
                                div.className = 'client';
                                div.innerHTML = `
                                    <h3>${client.hostname} (${client.ip})</h3>
                                    <p>系统: ${client.system}</p>
                                    <p>最后上报: ${client.last_seen}</p>
                                    <p>状态: <span class="${client.status === '在线' ? 'online' : 'offline'}">${client.status}</span></p>
                                    <button onclick="showDetails('${client.ip}')">查看详情</button>
                                `;
                                container.appendChild(div);
                            });
                        });
                }
                
                function showDetails(ip) {
                    fetch(`/client/${ip}`)
                        .then(response => response.json())
                        .then(data => {
                            alert(JSON.stringify(data, null, 2));
                        });
                }
                
                setInterval(updateClients, 30000);
                document.addEventListener('DOMContentLoaded', updateClients);
            </script>
        </head>
        <body>
            <div class="header">
                <h1>系统探针控制台</h1>
                <div class="user-info">
                    欢迎，''' + session.get('username', '') + '''
                    <a href="/change_password" class="button">修改密码</a>
                    <a href="/logout" class="button logout">退出</a>
                </div>
            </div>
            <div id="clients"></div>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 