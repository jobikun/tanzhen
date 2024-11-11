import time
from plyer import notification

def set_reminder(title, message, minutes):
    """设置定时提醒"""
    seconds = minutes * 60
    time.sleep(seconds)
    
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

# 使用示例
set_reminder(
    "休息提醒", 
    "该休息一下眼睛了！",
    30  # 30分钟后提醒
) 