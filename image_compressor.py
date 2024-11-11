from PIL import Image
import os

def compress_images(input_dir, output_dir, quality=70):
    """批量压缩图片文件
    
    Args:
        input_dir: 输入图片文件夹
        output_dir: 压缩后图片保存文件夹
        quality: 压缩质量(1-100)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for filename in os.listdir(input_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            with Image.open(input_path) as img:
                img.save(output_path, quality=quality, optimize=True)
            
            original_size = os.path.getsize(input_path) / 1024  # KB
            compressed_size = os.path.getsize(output_path) / 1024  # KB
            
            print(f'压缩 {filename}:')
            print(f'原始大小: {original_size:.2f}KB')
            print(f'压缩后大小: {compressed_size:.2f}KB')
            print(f'压缩率: {(1 - compressed_size/original_size)*100:.2f}%\n')

# 使用示例
compress_images('原始图片文件夹', '压缩后文件夹') 