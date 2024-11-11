import requests
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

def monitor_website(url, check_interval=300, email_config=None):
    """监控网站可用性
    
    Args:
        url: 要监控的网站URL
        check_interval: 检查间隔（秒）
        email_config: 邮件通知配置字典，包含：
            - smtp_server: SMTP服务器地址
            - smtp_port: SMTP端口
            - sender: 发件人邮箱
            - password: 发件人密码
            - receiver: 收件人邮箱
    """
    def send_alert(subject, message):
        if not email_config:
            return
        
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = email_config['sender']
        msg['To'] = email_config['receiver']
        
        try:
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender'], email_config['password'])
                server.send_message(msg)
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
    
    previous_status = None
    
    while True:
        try:
            response = requests.get(url, timeout=30)
            current_status = response.status_code == 200
            
            if previous_status is not None and previous_status != current_status:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if current_status:
                    message = f"网站 {url} 已恢复正常！\n时间：{timestamp}"
                    send_alert("网站恢复通知", message)
                else:
                    message = f"网站 {url} 无法访问！\n时间：{timestamp}"
                    send_alert("网站异常通知", message)
            
            previous_status = current_status
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 状态: {'正常' if current_status else '异常'}")
            
        except requests.RequestException as e:
            if previous_status is not None and previous_status:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                message = f"网站 {url} 访问出错：{str(e)}\n时间：{timestamp}"
                send_alert("网站异常通知", message)
            previous_status = False
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 错误: {str(e)}")
        
        time.sleep(check_interval)

# 使用示例
email_config = {
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'sender': 'your_email@example.com',
    'password': 'your_password',
    'receiver': 'receiver@example.com'
}

monitor_website('https://www.example.com', check_interval=300, email_config=email_config) 