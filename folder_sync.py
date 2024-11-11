import os
import shutil
import hashlib
from datetime import datetime

def get_file_hash(filepath):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sync_folders(source_dir, target_dir):
    """同步两个文件夹的内容"""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # 记录操作日志
    log_file = f"sync_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(log_file, 'w', encoding='utf-8') as log:
        # 同步源文件夹到目标文件夹
        for root, dirs, files in os.walk(source_dir):
            relative_path = os.path.relpath(root, source_dir)
            target_root = os.path.join(target_dir, relative_path)
            
            # 创建目标子文件夹
            for dir_name in dirs:
                target_dir_path = os.path.join(target_root, dir_name)
                if not os.path.exists(target_dir_path):
                    os.makedirs(target_dir_path)
                    log.write(f"创建文件夹: {target_dir_path}\n")
            
            # 复制/更新文件
            for file_name in files:
                source_file = os.path.join(root, file_name)
                target_file = os.path.join(target_root, file_name)
                
                if not os.path.exists(target_file):
                    shutil.copy2(source_file, target_file)
                    log.write(f"复制文件: {target_file}\n")
                else:
                    # 比较文件哈希值，不同则更新
                    if get_file_hash(source_file) != get_file_hash(target_file):
                        shutil.copy2(source_file, target_file)
                        log.write(f"更新文件: {target_file}\n")
    
    print(f"同步完成！详细日志请查看: {log_file}")

# 使用示例
sync_folders('源文件夹路径', '目标文件夹路径') 