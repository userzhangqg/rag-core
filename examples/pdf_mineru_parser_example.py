#!/usr/bin/env python3
"""
MinerU VLM PDF解析器使用示例

本示例展示了如何使用MinerU VLM解析器处理PDF文件，包括：
1. 基本使用
2. 批量处理
3. 异步处理
4. 不同后端配置
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.parser.pdf_mineru_parser import MineruVLMParser, MineruPipelineParser


def example_basic_usage():
    """示例1：基本使用"""
    print("=== 示例1: 基本使用 ===")
    
    # 配置VLM解析器
    parser = MineruVLMParser(
        backend="vlm-sglang-client",
        server_url="http://172.28.86.42:30000",
        lang=["ch", "en"],
        formula_enable=True,
        table_enable=True
    )
    
    # 示例PDF路径（请替换为实际路径）
    pdf_path = "data/test-pdfs/AI Agent工作流平台选型对比.pdf"
    output_dir = "mineru-output/sample"
    
    if os.path.exists(pdf_path):
        result = parser.process_single_pdf(pdf_path, output_dir)
        print(f"处理结果: {result['status']}")
        if result['status'] == 'success':
            print(f"Markdown文件: {os.path.join(output_dir, 'content.md')}")
    else:
        print(f"示例文件不存在: {pdf_path}")


def example_batch_processing():
    """示例2：批量处理"""
    print("\n=== 示例2: 批量处理 ===")
    
    parser = MineruVLMParser(
        backend="vlm-sglang-client",
        server_url="http://172.28.86.42:30000",
        lang=["ch"]
    )
    
    # 示例PDF目录（请替换为实际路径）
    pdfs_dir = "data/test-pdfs"
    output_base_dir = "./output/batch"
    
    if os.path.exists(pdfs_dir):
        result = parser.process_batch_pdfs(
            pdfs_dir=pdfs_dir,
            output_base_dir=output_base_dir,
            skip_existing=True
        )
        
        print(f"总文件数: {result['total_pdfs']}")
        print(f"成功处理: {result['processed_pdfs']}")
        print(f"失败: {result['failed_pdfs']}")
        print(f"跳过: {result['skipped_pdfs']}")
        
        # 显示失败文件
        for r in result['results']:
            if r['status'] == 'error':
                print(f"  失败文件: {r['pdf_filename']} - {r['error']}")
    else:
        print(f"示例目录不存在: {pdfs_dir}")


async def example_async_processing():
    """示例3：异步处理"""
    print("\n=== 示例3: 异步处理 ===")
    
    parser = MineruVLMParser(
        backend="vlm-sglang-client",
        server_url="http://172.28.86.42:30000",
        lang=["en"]
    )
    
    # 示例PDF目录
    pdfs_dir = "data/test-pdfs"
    output_base_dir = "./output/async"
    
    if os.path.exists(pdfs_dir):
        result = await parser.aprocess_batch_pdfs(
            pdfs_dir=pdfs_dir,
            output_base_dir=output_base_dir
        )
        
        print(f"异步处理完成")
        print(f"总文件数: {result['total_pdfs']}")
        print(f"成功处理: {result['processed_pdfs']}")
    else:
        print(f"示例目录不存在: {pdfs_dir}")


def example_different_backends():
    """示例4：不同后端配置"""
    print("\n=== 示例4: 不同后端配置 ===")
    
    # 配置1: VLM远程服务
    vlm_parser = MineruVLMParser(
        backend="vlm-sglang-client",
        server_url="http://172.28.86.42:30000",
        lang=["ch", "en"]
    )
    
    # 配置2: 传统pipeline
    pipeline_parser = MineruPipelineParser(
        lang=["ch"],
        formula_enable=True,
        table_enable=True
    )
    
    pdf_path = "data/test-pdfs/AI Agent工作流平台选型对比.pdf"
    
    if os.path.exists(pdf_path):
        # 使用VLM后端
        print("使用VLM后端...")
        result1 = vlm_parser.get_markdown_content(pdf_path)
        
        # 使用pipeline后端
        print("使用pipeline后端...")
        result2 = pipeline_parser.get_markdown_content(pdf_path)
        
        if result1 and result2:
            print(f"VLM结果长度: {len(result1)} 字符")
            print(f"Pipeline结果长度: {len(result2)} 字符")
    else:
        print(f"示例文件不存在: {pdf_path}")


def example_quick_content_extraction():
    """示例5：快速内容提取"""
    print("\n=== 示例5: 快速内容提取 ===")
    
    parser = MineruVLMParser(
        backend="vlm-sglang-client",
        server_url="http://172.28.86.42:30000",
        lang=["ch"]
    )
    
    pdf_path = "data/test-pdfs/AI Agent工作流平台选型对比.pdf"
    
    if os.path.exists(pdf_path):
        # 快速获取内容，不保存文件
        content = parser.get_markdown_content(pdf_path)
        
        if content:
            print("提取的内容预览:")
            print("-" * 50)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 50)
            print(f"总字符数: {len(content)}")
        else:
            print("内容提取失败")
    else:
        print(f"示例文件不存在: {pdf_path}")


def example_configuration_file():
    """示例6：使用配置文件"""
    print("\n=== 示例6: 使用配置文件 ===")
    
    # 创建配置
    config = {
        "backend": "vlm-sglang-client",
        "server_url": "http://172.28.86.42:30000",
        "lang": ["ch", "en"],
        "formula_enable": True,
        "table_enable": True,
        "parse_method": "auto"
    }
    
    # 保存配置
    with open("parser_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # 读取配置
    with open("parser_config.json", "r", encoding="utf-8") as f:
        loaded_config = json.load(f)
    
    # 使用配置创建解析器
    parser = MineruVLMParser(**loaded_config)
    
    print("配置已保存并加载")
    print(f"配置内容: {json.dumps(loaded_config, ensure_ascii=False, indent=2)}")


def example_error_handling():
    """示例7：错误处理"""
    print("\n=== 示例7: 错误处理 ===")
    
    parser = MineruVLMParser(
        backend="vlm-sglang-client",
        server_url="http://172.28.86.42:30001",  # 错误的服务器地址
        lang=["ch"]
    )
    
    pdf_path = "data/test-pdfs/AI Agent工作流平台选型对比.pdf"
    
    if os.path.exists(pdf_path):
        result = parser.process_single_pdf(pdf_path, "./output/error_test")
        
        if result["status"] == "error":
            print(f"预期错误: {result['error']}")
            print("错误处理示例完成")
        else:
            print("意外成功")
    else:
        print(f"示例文件不存在: {pdf_path}")


def create_sample_test():
    """创建示例测试文件"""
    print("\n=== 创建示例测试文件 ===")
    
    # 创建测试目录
    test_dir = "./test_pdfs"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建简单的测试说明
    readme_content = """
    # 测试说明
    
    请将您的PDF测试文件放入此目录，然后运行示例脚本。
    
    ## 支持的文件格式
    - .pdf
    
    ## 测试建议
    1. 包含中英文混合内容的PDF
    2. 包含表格的PDF
    3. 包含公式的PDF
    4. 扫描版的PDF
    
    ## 运行测试
    ```bash
    python example_usage.py
    ```
    """
    
    with open(os.path.join(test_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"测试目录已创建: {test_dir}")
    print("请将PDF文件放入此目录进行测试")


def example_parser():
    """示例6：使用解析器"""
    print("\n=== 示例6: 使用解析器 ===")
    
    parser = MineruVLMParser(
        backend="vlm-sglang-client",
        server_url="http://172.28.86.42:30000",
        lang=["ch"]
    )
    
    pdf_path = "data/test-pdfs/AI Agent工作流平台选型对比.pdf"
    
    if os.path.exists(pdf_path):
        # 快速获取内容，不保存文件
        documents = parser.parser(pdf_path)
        
        if documents:
            print(f"解析出 {len(documents)} 个文档")
            for doc in documents:
                print(f"文档内容长度: {len(doc.page_content)} 字符")
                print(f"文档元数据: {doc.metadata}")
                print(f"文档内容预览: {doc.page_content[:200]}...")
                print("-" * 50)
        else:
            print("内容提取失败")
    else:
        print(f"示例文件不存在: {pdf_path}")


def main():
    """主函数"""
    print("MinerU VLM PDF解析器示例")
    print("=" * 50)
    
    # 创建测试环境
    create_sample_test()
    
    # 运行示例
    try:
        # example_basic_usage()
        # example_batch_processing()
        
        # # 异步示例
        # if os.path.exists("/path/to/pdfs"):  # 仅当目录存在时运行
        #     asyncio.run(example_async_processing())
        
        # example_different_backends()
        # example_quick_content_extraction()
        # example_configuration_file()
        # example_error_handling()
        example_parser()
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        print("请确保MinerU已正确安装且VLM服务可访问")
    
    print("\n" + "=" * 50)
    print("示例运行完成")
    print("请查看测试目录中的README.md获取更多信息")


if __name__ == "__main__":
    main()