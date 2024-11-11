from PyPDF2 import PdfMerger
import os

def merge_pdfs(directory, output_filename):
    """合并指定文件夹中的所有PDF文件"""
    merger = PdfMerger()
    
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            merger.append(os.path.join(directory, filename))
    
    merger.write(output_filename)
    merger.close()
    print(f'PDF文件已合并为: {output_filename}')

# 使用示例
directory = "PDF文件夹路径"
merge_pdfs(directory, "合并后的文件.pdf") 