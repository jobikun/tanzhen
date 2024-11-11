import psutil
import time
import json
from datetime import datetime
import socket

class SystemMonitor:
    def __init__(self):
        self.hostname = socket.gethostname()
    
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
            'memory_total': round(memory.total / (1024**3), 2),  # GB
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
                    'total_size': round(usage.total / (1024**3), 2),  # GB
                    'used': round(usage.used / (1024**3), 2),
                    'free': round(usage.free / (1024**3), 2),
                    'percent': usage.percent
                })
            except PermissionError:
                continue
        return disk_partitions
    
    def get_network_info(self):
        """获取网络信息"""
        network_info = {}
        net_io = psutil.net_io_counters()
        network_info['bytes_sent'] = round(net_io.bytes_sent / (1024**2), 2)  # MB
        network_info['bytes_recv'] = round(net_io.bytes_recv / (1024**2), 2)
        network_info['packets_sent'] = net_io.packets_sent
        network_info['packets_recv'] = net_io.packets_recv
        
        # 获取网络连接数
        connections = len(psutil.net_connections())
        network_info['connections'] = connections
        
        return network_info
    
    def get_process_info(self):
        """获取进程信息"""
        process_list = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                process_list.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # 只返回CPU或内存使用率前10的进程
        process_list.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return process_list[:10]
    
    def collect_all_metrics(self):
        """收集所有系统指标"""
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'hostname': self.hostname,
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'top_processes': self.get_process_info()
        }
    
    def monitor(self, interval=60, output_file='system_metrics.json'):
        """持续监控系统状态
        
        Args:
            interval: 监控间隔（秒）
            output_file: 输出文件名
        """
        print(f"开始监控系统状态，数据将保存到 {output_file}")
        print(f"监控间隔：{interval}秒")
        
        while True:
            try:
                metrics = self.collect_all_metrics()
                
                # 将数据写入文件
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(metrics, ensure_ascii=False) + '\n')
                
                # 打印简要信息
                print(f"\n[{metrics['timestamp']}] 系统状态：")
                print(f"CPU使用率: {metrics['cpu']['cpu_percent']}%")
                print(f"内存使用率: {metrics['memory']['memory_percent']}%")
                print(f"网络流量 - 发送: {metrics['network']['bytes_sent']}MB " 
                      f"接收: {metrics['network']['bytes_recv']}MB")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n停止监控")
                break
            except Exception as e:
                print(f"发生错误: {str(e)}")
                time.sleep(interval)

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.monitor(interval=60) 