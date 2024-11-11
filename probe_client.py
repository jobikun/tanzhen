import psutil
import time
import json
from datetime import datetime
import socket
import requests
import platform

class ProbeClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.hostname = socket.gethostname()
        self.ip = self._get_ip()
        self.system = platform.system()
        
    def _get_ip(self):
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'
    
    def get_cpu_info(self):
        """获取CPU信息"""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        return {
            'cpu_percent': cpu_percent,
            'cpu_count': psutil.cpu_count(),
            'cpu_freq_current': round(cpu_freq.current, 2) if cpu_freq else None,
            'cpu_freq_max': round(cpu_freq.max, 2) if cpu_freq else None
        }
    
    def get_memory_info(self):
        """获取内存信息"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            'memory_total': round(memory.total / (1024**3), 2),
            'memory_used': round(memory.used / (1024**3), 2),
            'memory_percent': memory.percent,
            'swap_total': round(swap.total / (1024**3), 2),
            'swap_used': round(swap.used / (1024**3), 2),
            'swap_percent': swap.percent
        }
    
    def get_disk_info(self):
        """获取磁盘信息"""
        disk_partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'total_size': round(usage.total / (1024**3), 2),
                    'used': round(usage.used / (1024**3), 2),
                    'free': round(usage.free / (1024**3), 2),
                    'percent': usage.percent
                })
            except PermissionError:
                continue
        return disk_partitions
    
    def get_network_info(self):
        """获取网络信息"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': round(net_io.bytes_sent / (1024**2), 2),
            'bytes_recv': round(net_io.bytes_recv / (1024**2), 2),
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'connections': len(psutil.net_connections())
        }
    
    def collect_metrics(self):
        """收集所有系统指标"""
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'hostname': self.hostname,
            'ip': self.ip,
            'system': self.system,
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info()
        }
    
    def report_metrics(self):
        """向服务器报告指标"""
        try:
            metrics = self.collect_metrics()
            response = requests.post(f"{self.server_url}/report", json=metrics)
            if response.status_code == 200:
                print(f"[{metrics['timestamp']}] 数据上报成功")
            else:
                print(f"[{metrics['timestamp']}] 数据上报失败: {response.status_code}")
        except Exception as e:
            print(f"上报失败: {str(e)}")
    
    def run(self, interval=60):
        """运行客户端探针"""
        print(f"探针客户端启动 - {self.hostname}({self.ip})")
        print(f"上报间隔：{interval}秒")
        
        while True:
            try:
                self.report_metrics()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n探针停止运行")
                break
            except Exception as e:
                print(f"发生错误: {str(e)}")
                time.sleep(interval)

if __name__ == "__main__":
    SERVER_URL = "http://localhost:5000"  # 修改为你的服务器地址
    client = ProbeClient(SERVER_URL)
    client.run() 