"""
PdfSimpleParser 使用示例
演示如何使用 PdfSimpleParser 解析PDF文件
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.parser.pdf_simple_parser import PdfSimpleParser


def example_usage():
    """演示PdfSimpleParser的基本用法"""
    
    # 初始化解析器
    parser = PdfSimpleParser(max_chunk_size=1000)
    
    # 示例：从文件路径解析PDF
    print("=== 从文件路径解析PDF ===")
    pdf_path = "data/sample.pdf"  # 替换为你的PDF文件路径
    
    if os.path.exists(pdf_path):
        try:
            documents = parser.parse(pdf_path, source_type="file")
            print(f"成功解析 {len(documents)} 个文档")
            
            # 打印前几个文档的内容
            for i, doc in enumerate(documents[:3]):
                print(f"\n文档 {i+1}:")
                print(f"  内容长度: {len(doc.page_content)} 字符")
                print(f"  元数据: {doc.metadata}")
                print(f"  内容预览: {doc.page_content[:200]}...")
                
        except Exception as e:
            print(f"解析失败: {e}")
    else:
        print(f"文件不存在: {pdf_path}")
    
    # 示例：从字节流解析PDF
    print("\n=== 从字节流解析PDF ===")
    try:
        # 模拟字节流（这里需要实际的PDF字节数据）
        # with open("data/sample.pdf", "rb") as f:
        #     pdf_bytes = f.read()
        # documents = parser.parse(pdf_bytes, source_type="bytes")
        # print(f"从字节流解析成功: {len(documents)} 个文档")
        print("字节流解析示例 - 需要实际的PDF字节数据")
        
    except Exception as e:
        print(f"字节流解析失败: {e}")


def batch_process_directory():
    """批量处理目录中的PDF文件"""
    print("\n=== 批量处理目录中的PDF ===")
    
    directory = "data/test-pdfs"  # 测试目录
    if os.path.exists(directory):
        pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
        
        parser = PdfSimpleParser()
        
        for pdf_file in pdf_files:
            file_path = os.path.join(directory, pdf_file)
            try:
                print(f"处理文件: {pdf_file}")
                documents = parser.parse(file_path, source_type="file")
                print(f"  解析成功: {len(documents)} 个文档")
                print(f"  文档内容: {documents}...")
                
            except Exception as e:
                print(f"  解析失败: {e}")
    else:
        print(f"目录不存在: {directory}")


if __name__ == "__main__":
    example_usage()
    batch_process_directory()