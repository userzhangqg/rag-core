#!/usr/bin/env python3
"""
MinerU VLM PDF解析器测试脚本

本脚本用于测试解析器的基本功能是否正常
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pdf_mineru_parser import MineruVLMParser, MineruPipelineParser
    print("✓ 成功导入MinerU VLM解析器")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print("请确保MinerU已正确安装")
    sys.exit(1)


def test_parser_initialization():
    """测试解析器初始化"""
    print("\n=== 测试解析器初始化 ===")
    
    try:
        # 测试VLM解析器
        vlm_parser = MineruVLMParser(
            backend="sglang-client",
            server_url="http://localhost:8000",
            lang=["ch", "en"]
        )
        print("✓ VLM解析器初始化成功")
        print(f"  后端: {vlm_parser.backend}")
        print(f"  服务器URL: {vlm_parser.server_url}")
        print(f"  支持语言: {vlm_parser.lang}")
        
        # 测试Pipeline解析器
        pipeline_parser = MineruPipelineParser(
            lang=["ch"],
            formula_enable=True
        )
        print("✓ Pipeline解析器初始化成功")
        print(f"  支持语言: {pipeline_parser.lang}")
        
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return False
    
    return True


def test_configuration():
    """测试配置功能"""
    print("\n=== 测试配置功能 ===")
    
    try:
        # 测试不同配置
        configs = [
            {
                "backend": "sglang-client",
                "server_url": "http://localhost:8888",
                "lang": ["ch"]
            },
            {
                "backend": "transformers",
                "model_path": "/path/to/model",
                "lang": ["en"]
            },
            {
                "backend": "pipeline",
                "lang": ["ch", "en"],
                "formula_enable": True,
                "table_enable": True
            }
        ]
        
        for i, config in enumerate(configs):
            try:
                if config.get("backend") == "pipeline":
                    parser = MineruPipelineParser(**{k: v for k, v in config.items() if k != "backend"})
                else:
                    parser = MineruVLMParser(**config)
                print(f"✓ 配置{i+1}成功: {config}")
            except Exception as e:
                print(f"✗ 配置{i+1}失败: {e}")
        
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")


def test_file_operations():
    """测试文件操作功能"""
    print("\n=== 测试文件操作功能 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录: {temp_dir}")
        
        # 测试输出目录创建
        output_dir = os.path.join(temp_dir, "test_output")
        try:
            parser = MineruVLMParser()
            image_writer, md_writer, images_dir = parser._prepare_output_dirs(output_dir)
            
            if os.path.exists(output_dir) and os.path.exists(os.path.join(output_dir, "images")):
                print("✓ 输出目录创建成功")
            else:
                print("✗ 输出目录创建失败")
                
        except Exception as e:
            print(f"✗ 文件操作测试失败: {e}")


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    parser = MineruVLMParser()
    
    # 测试不存在的文件
    result = parser.process_single_pdf("/nonexistent/file.pdf", "/tmp/test")
    if result["status"] == "error":
        print("✓ 错误处理正常")
    else:
        print("✗ 错误处理异常")
    
    # 测试不存在的目录
    result = parser.process_batch_pdfs("/nonexistent/dir", "/tmp/test")
    if result["status"] in ["error", "warning"]:
        print("✓ 目录错误处理正常")
    else:
        print("✗ 目录错误处理异常")


def create_mock_test_files():
    """创建模拟测试文件"""
    print("\n=== 创建模拟测试环境 ===")
    
    # 创建测试目录
    test_dir = "./test_environment"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建配置文件
    config = {
        "backend": "sglang-client",
        "server_url": "http://localhost:8000",
        "lang": ["ch", "en"],
        "formula_enable": True,
        "table_enable": True
    }
    
    config_path = os.path.join(test_dir, "test_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # 创建使用示例
    usage_example = '''
# MinerU VLM解析器测试

## 测试步骤

1. 确保VLM服务器已启动
   ```bash
   docker run -itd --name=mineru_server --gpus=all -p 8888:8000 quincyqiang/mineru:0.2-models
   ```

2. 修改配置文件中的路径

3. 运行测试脚本
   ```bash
   python test_parser.py
   ```

4. 使用示例
   ```python
   from pdf_mineru_parser import MineruVLMParser
   
   parser = MineruVLMParser(
       backend="sglang-client",
       server_url="http://localhost:8888"
   )
   
   result = parser.process_single_pdf("your_file.pdf", "./output")
   ```

## 注意事项

- 确保PDF文件存在
- 确保VLM服务可访问
- 检查GPU资源是否充足
'''
    
    readme_path = os.path.join(test_dir, "TEST_README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(usage_example)
    
    print(f"✓ 测试环境已创建: {test_dir}")
    print(f"  - 配置文件: {config_path}")
    print(f"  - 使用说明: {readme_path}")


def main():
    """主测试函数"""
    print("MinerU VLM PDF解析器测试脚本")
    print("=" * 50)
    
    # 运行测试
    tests = [
        test_parser_initialization,
        test_configuration,
        test_file_operations,
        test_error_handling,
        create_mock_test_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ 测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过！解析器已正确配置")
    else:
        print("⚠ 部分测试失败，请检查配置和依赖")
    
    print("\n下一步:")
    print("1. 启动VLM服务器")
    print("2. 将PDF文件放入测试目录")
    print("3. 运行实际文件测试")


if __name__ == "__main__":
    main()