#!/usr/bin/env python3
"""
MinerU VLM PDF解析器集成示例

展示如何将MinerU VLM解析器集成到RAG系统中
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

# 确保能导入解析器
try:
    from pdf_mineru_parser import MineruVLMParser, MineruPipelineParser
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pdf_mineru_parser import MineruVLMParser, MineruPipelineParser


class DocumentProcessor:
    """文档处理器，集成MinerU解析器到RAG系统"""
    
    def __init__(self, 
                 backend: str = "sglang-client",
                 server_url: str = "http://localhost:8000",
                 output_base_dir: str = "./processed_docs",
                 **kwargs):
        """
        初始化文档处理器
        
        Args:
            backend: 解析后端类型
            server_url: VLM服务器URL
            output_base_dir: 处理文档的输出基础目录
            **kwargs: 其他配置参数
        """
        self.parser = MineruVLMParser(
            backend=backend,
            server_url=server_url,
            **kwargs
        )
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
        
        # 处理记录
        self.processing_log = []
    
    async def process_document(self, 
                             file_path: str, 
                             doc_id: str = None,
                             metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理单个文档
        
        Args:
            file_path: 文档路径
            doc_id: 文档ID（可选，自动生成）
            metadata: 文档元数据
            
        Returns:
            处理结果包含文档信息和内容
        """
        doc_id = doc_id or str(len(self.processing_log))
        metadata = metadata or {}
        
        # 创建文档专用输出目录
        doc_output_dir = self.output_base_dir / f"doc_{doc_id}"
        doc_output_dir.mkdir(exist_ok=True)
        
        try:
            # 使用异步处理
            result = await self.parser.aprocess_single_pdf(
                pdf_path=file_path,
                output_dir=str(doc_output_dir),
                target_lang=metadata.get('language', 'ch')
            )
            
            # 构建RAG系统需要的格式
            rag_result = {
                "doc_id": doc_id,
                "file_path": file_path,
                "metadata": {
                    **metadata,
                    "processing_time": result.get("processing_time"),
                    "backend_used": result.get("backend"),
                    "server_url": result.get("server_url")
                },
                "content": {
                    "markdown": result.get("markdown_content"),
                    "structured": result.get("content_list"),
                    "raw_data": result.get("middle_json")
                },
                "status": result["status"],
                "error": result.get("error"),
                "output_dir": str(doc_output_dir)
            }
            
            # 保存处理记录
            self.processing_log.append(rag_result)
            
            # 保存RAG格式结果
            with open(doc_output_dir / "rag_result.json", "w", encoding="utf-8") as f:
                json.dump(rag_result, f, ensure_ascii=False, indent=2)
            
            return rag_result
            
        except Exception as e:
            error_result = {
                "doc_id": doc_id,
                "file_path": file_path,
                "metadata": metadata,
                "status": "error",
                "error": str(e),
                "output_dir": str(doc_output_dir)
            }
            
            self.processing_log.append(error_result)
            return error_result
    
    async def batch_process_documents(self, 
                                    file_paths: List[str],
                                    metadata_list: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        批量处理文档
        
        Args:
            file_paths: 文档路径列表
            metadata_list: 每个文档的元数据列表
            
        Returns:
            处理结果列表
        """
        metadata_list = metadata_list or [{}] * len(file_paths)
        
        # 创建处理任务
        tasks = []
        for i, (file_path, metadata) in enumerate(zip(file_paths, metadata_list)):
            doc_id = f"batch_{i}_{Path(file_path).stem}"
            task = self.process_document(file_path, doc_id, metadata)
            tasks.append(task)
        
        # 执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "doc_id": f"batch_{i}",
                    "file_path": file_paths[i],
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """获取处理摘要"""
        total = len(self.processing_log)
        successful = sum(1 for r in self.processing_log if r["status"] == "success")
        failed = total - successful
        
        return {
            "total_documents": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "processing_log": self.processing_log
        }
    
    def save_processing_summary(self, output_path: str = None):
        """保存处理摘要"""
        summary = self.get_processing_summary()
        output_path = output_path or self.output_base_dir / "processing_summary.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return str(output_path)


class VectorStoreAdapter:
    """向量存储适配器，将解析结果转换为向量存储格式"""
    
    @staticmethod
    def extract_chunks_from_result(result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从解析结果中提取文本块"""
        if result["status"] != "success":
            return []
        
        chunks = []
        content_list = result["content"]["structured"]
        
        for item in content_list:
            if item.get("type") == "text":
                chunk = {
                    "content": item.get("content", ""),
                    "metadata": {
                        "doc_id": result["doc_id"],
                        "page_idx": item.get("page_idx"),
                        "position": item.get("position"),
                        "type": "text"
                    }
                }
                chunks.append(chunk)
            
            elif item.get("type") == "table":
                chunk = {
                    "content": item.get("latex", ""),
                    "metadata": {
                        "doc_id": result["doc_id"],
                        "page_idx": item.get("page_idx"),
                        "position": item.get("position"),
                        "type": "table",
                        "html": item.get("html")
                    }
                }
                chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def create_vector_store_input(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """创建向量存储输入"""
        all_chunks = []
        
        for result in results:
            chunks = VectorStoreAdapter.extract_chunks_from_result(result)
            all_chunks.extend(chunks)
        
        return all_chunks


class SearchEngine:
    """简单的搜索接口，用于测试解析结果"""
    
    def __init__(self):
        self.documents = {}
        self.chunks = []
    
    def index_document(self, result: Dict[str, Any]):
        """索引文档"""
        if result["status"] != "success":
            return
        
        self.documents[result["doc_id"]] = result
        
        # 提取并索引文本块
        chunks = VectorStoreAdapter.extract_chunks_from_result(result)
        self.chunks.extend(chunks)
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """简单搜索（基于关键词匹配）"""
        results = []
        
        for chunk in self.chunks:
            if query.lower() in chunk["content"].lower():
                results.append({
                    "content": chunk["content"],
                    "metadata": chunk["metadata"],
                    "score": 1.0  # 简单的匹配分数
                })
        
        return results[:limit]


async def main():
    """主函数演示"""
    print("MinerU VLM PDF解析器集成示例")
    print("=" * 50)
    
    # 初始化文档处理器
    processor = DocumentProcessor(
        backend="sglang-client",
        server_url="http://localhost:8000",
        output_base_dir="./rag_documents",
        lang=["ch", "en"],
        formula_enable=True,
        table_enable=True
    )
    
    # 示例文件列表（请替换为实际文件）
    sample_files = [
        "/path/to/sample1.pdf",
        "/path/to/sample2.pdf"
    ]
    
    # 示例元数据
    sample_metadata = [
        {"title": "技术文档1", "category": "技术", "language": "ch"},
        {"title": "技术文档2", "category": "技术", "language": "ch"}
    ]
    
    # 检查文件是否存在
    existing_files = [f for f in sample_files if os.path.exists(f)]
    if not existing_files:
        print("⚠ 未找到示例PDF文件，创建测试环境...")
        
        # 创建测试目录
        test_dir = Path("./test_documents")
        test_dir.mkdir(exist_ok=True)
        
        print(f"请将PDF文件放入: {test_dir}")
        print("然后修改sample_files列表中的路径")
        return
    
    print(f"找到 {len(existing_files)} 个PDF文件")
    
    # 批量处理
    results = await processor.batch_process_documents(
        file_paths=existing_files,
        metadata_list=sample_metadata[:len(existing_files)]
    )
    
    # 保存处理摘要
    summary_path = processor.save_processing_summary()
    print(f"处理摘要已保存: {summary_path}")
    
    # 初始化搜索引擎
    search_engine = SearchEngine()
    for result in results:
        search_engine.index_document(result)
    
    print(f"已索引 {len(search_engine.chunks)} 个文本块")
    
    # 测试搜索
    while True:
        query = input("\n输入搜索查询 (输入 'exit' 退出): ").strip()
        if query.lower() == 'exit':
            break
        
        if query:
            results = search_engine.search(query, limit=3)
            print(f"\n找到 {len(results)} 个结果:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. 文档: {result['metadata']['doc_id']}")
                print(f"   内容: {result['content'][:100]}...")


if __name__ == "__main__":
    asyncio.run(main())