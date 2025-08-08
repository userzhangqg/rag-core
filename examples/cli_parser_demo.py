#!/usr/bin/env python3
"""
命令行文件解析演示程序

这个demo演示如何使用DocumentProcessingPipeline从命令行输入文件进行解析，
并打印详细的解析结果，包括文档结构、分块信息等。
"""

import sys
import argparse
from pathlib import Path
import json
from typing import Dict, Any, List

# 添加项目根目录到Python路径
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline.preprocessing_pipeline import DocumentProcessingPipeline
from conf.config import RAGConfig
from utils.logger import setup_logger


def print_document_info(chunks: List[Dict[str, Any]], file_path: str, detailed: bool = False) -> None:
    """打印文档解析信息
    
    Args:
        chunks: 文档分块列表
        file_path: 文件路径
        detailed: 是否显示详细信息
    """
    print(f"\n{'='*80}")
    print(f"文件解析结果: {file_path}")
    print(f"{'='*80}")
    
    if not chunks:
        print("⚠️  未解析到任何内容")
        return
    
    print(f"📊 总计分块数量: {len(chunks)}")
    print()
    
    # 打印文件级别元数据
    first_chunk = chunks[0]
    file_metadata = {
        k: v for k, v in first_chunk['metadata'].items() 
        if k in ['source_file', 'file_name', 'file_size', 'document_type']
    }
    
    print("📁 文件信息:")
    for key, value in file_metadata.items():
        print(f"   {key}: {value}")
    print()
    
    # 打印完整解析文本
    print("📄 完整解析文本:")
    full_text = "\n".join([chunk['text'] for chunk in chunks])
    print(full_text)
    print()
    
    # 如果启用详细模式，打印每个分块的详细信息
    if detailed:
        # 打印每个分块的详细信息
        for idx, chunk in enumerate(chunks, 1):
            print(f"🔍 分块 #{idx}:")
            print(f"   文本长度: {len(chunk['text'])} 字符")
            
            # 打印分块元数据
            relevant_metadata = {
                k: v for k, v in chunk['metadata'].items() 
                if k not in ['source_file', 'file_name', 'file_size', 'document_type']
            }
            
            if relevant_metadata:
                print("   元数据:")
                for key, value in relevant_metadata.items():
                    if key == 'text':
                        continue  # 跳过文本内容
                    print(f"     {key}: {value}")
            
            # 打印文本内容预览
            text_preview = chunk['text'][:200].replace('\n', ' ')
            if len(chunk['text']) > 200:
                text_preview += "..."
            print(f"   内容预览: {text_preview}")
            print(f"{'-'*60}")


def print_pipeline_config(pipeline: DocumentProcessingPipeline) -> None:
    """打印管道配置信息"""
    print(f"\n{'='*80}")
    print("管道配置信息")
    print(f"{'='*80}")
    
    info = pipeline.get_pipeline_info()
    
    print("🔧 解析器配置:")
    for key, value in info['parser_config'].items():
        print(f"   {key}: {value}")
    
    print("\n✂️  分块器配置:")
    for key, value in info['chunker_config'].items():
        print(f"   {key}: {value}")
    
    print(f"\n🏷️  元数据启用: {info['enable_metadata']}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="命令行文件解析演示程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli_parser_demo.py /path/to/document.pdf
  python cli_parser_demo.py /path/to/file.md --verbose
  python cli_parser_demo.py ./documents/ --recursive
  python cli_parser_demo.py test.docx --output result.json
        """
    )
    
    parser.add_argument(
        'input_path',
        help='要解析的文件路径或目录路径'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='递归处理目录中的文件'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        default='*',
        help='文件匹配模式（仅对目录有效，默认: *）'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志信息'
    )
    
    parser.add_argument(
        '--detailed', '-d',
        action='store_true',
        help='显示每个分块的详细信息'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='将结果保存到JSON文件'
    )
    
    parser.add_argument(
        '--config',
        help='使用自定义配置文件'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    # if args.verbose:
    #     setup_logger(level='DEBUG')
    # else:
    #     setup_logger(level='INFO')
    
    try:
        # 初始化配置
        if args.config:
            config = RAGConfig.from_config_file(args.config)
        else:
            config = RAGConfig.from_config_file()

        print(config)
        setup_logger(config)
        
        # 创建处理管道
        pipeline = DocumentProcessingPipeline(config)
        
        # 打印配置信息
        print_pipeline_config(pipeline)
        
        input_path = Path(args.input_path)
        
        if not input_path.exists():
            print(f"❌ 错误: 路径不存在: {input_path}")
            sys.exit(1)
        
        all_results = {}
        
        if input_path.is_file():
            # 处理单个文件
            print(f"\n🚀 开始解析文件: {input_path}")
            chunks = pipeline.process_file(str(input_path))
            print_document_info(chunks, str(input_path), args.detailed)
            all_results[str(input_path)] = chunks
            
        elif input_path.is_dir():
            # 处理目录
            print(f"\n🚀 开始处理目录: {input_path}")
            results = pipeline.process_directory(
                str(input_path),
                file_pattern=args.pattern,
                recursive=args.recursive
            )
            
            for file_path, chunks in results.items():
                print_document_info(chunks, file_path, args.detailed)
                all_results[file_path] = chunks
        
        # 保存结果到文件
        if args.output:
            output_data = {}
            for file_path, chunks in all_results.items():
                output_data[file_path] = [
                    {
                        'text': chunk['text'],
                        'metadata': chunk['metadata']
                    }
                    for chunk in chunks
                ]
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 结果已保存到: {args.output}")
    
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()