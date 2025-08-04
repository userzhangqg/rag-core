#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Core API 使用示例

本示例展示如何使用RAG Core API进行文件上传和对话查询
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"


def upload_file_example(file_path: str):
    """文件上传示例"""
    url = f"{BASE_URL}/documents/upload"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"上传成功: {result}")
        return result
    else:
        print(f"上传失败: {response.status_code} - {response.text}")
        return None


def upload_text_example(text: str, source_name: str = "example_text"):
    """文本上传示例"""
    url = f"{BASE_URL}/documents/upload-text"
    
    data = {
        "content": text,
        "source_name": source_name
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"文本上传成功: {result}")
        return result
    else:
        print(f"文本上传失败: {response.status_code} - {response.text}")
        return None


def chat_query_example(query: str, stream: bool = False):
    """对话查询示例"""
    if stream:
        url = f"{BASE_URL}/chat/query-stream"
    else:
        url = f"{BASE_URL}/chat/query"
    
    data = {
        "query": query,
        "top_k": 5,
        "score_threshold": 0.0,
        "use_rerank": True,
        "stream": stream
    }
    
    if stream:
        # 流式响应
        response = requests.post(url, json=data, stream=True)
        print("流式响应:")
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8').replace('data: ', ''))
                    if 'chunk' in data:
                        print(data['chunk'], end='', flush=True)
                    elif 'done' in data:
                        print("\n响应完成")
                        break
                except:
                    continue
    else:
        # 非流式响应
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"查询结果: {result['response']}")
            return result
        else:
            print(f"查询失败: {response.status_code} - {response.text}")
            return None


def health_check_example():
    """健康检查示例"""
    url = f"{BASE_URL}/health"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        print(f"API健康状态: {result}")
        return result
    else:
        print(f"健康检查失败: {response.status_code} - {response.text}")
        return None


def main():
    """主函数 - 运行示例"""
    print("=== RAG Core API 使用示例 ===")
    
    # 1. 健康检查
    print("\n1. 检查API健康状态...")
    health_check_example()
    
    # 2. 上传示例文本
    print("\n2. 上传示例文本...")
    sample_text = """
    Python是一种高级编程语言，以其简洁和可读性而闻名。
    它支持多种编程范式，包括面向对象、命令式和函数式编程。
    Python的设计哲学强调代码的可读性和简洁的语法。
    """
    upload_text_example(sample_text, "python_intro")
    
    # 3. 对话查询
    print("\n3. 执行对话查询...")
    chat_query_example("Python的主要特点是什么？")
    
    # 4. 流式查询
    print("\n4. 执行流式查询...")
    chat_query_example("Python支持哪些编程范式？", stream=True)


if __name__ == "__main__":
    main()