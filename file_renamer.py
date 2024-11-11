import os

def batch_rename_files(directory, old_text, new_text):
    """批量重命名文件，将文件名中的指定文本替换为新文本"""
    for filename in os.listdir(directory):
        if old_text in filename:
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, filename.replace(old_text, new_text))
            os.rename(old_file, new_file)
            print(f'已将 {filename} 重命名为 {filename.replace(old_text, new_text)}')

# 使用示例
directory = "你的文件夹路径"
batch_rename_files(directory, "旧文本", "新文本") 