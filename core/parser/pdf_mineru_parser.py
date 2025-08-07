"""
使用mineru进行pdf文件解析 - 基于VLM后端和URL调用
"""
import os
import json
import asyncio
import traceback
from typing import Optional, List, Dict, Any, Union, Tuple
from pathlib import Path
import logging


from langchain_core.documents.base import Document
from mineru.backend.vlm.vlm_analyze import doc_analyze as vlm_doc_analyze
from mineru.backend.vlm.vlm_analyze import aio_doc_analyze as aio_vlm_doc_analyze
from mineru.data.data_reader_writer import FileBasedDataWriter
from mineru.cli.common import read_fn


from mineru.utils.enum_class import MakeMode

from core.parser.base import BaseParser


class MineruParser(BaseParser):
    """
    MinerU PDF解析器的基类
    包含共有的方法和属性，供VLM和Pipeline后端继承
    """
    
    supported_extensions = [".pdf"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = kwargs
    
    def _prepare_output_dirs(self, output_dir: str) -> tuple:
        """准备输出目录结构"""
        os.makedirs(output_dir, exist_ok=True)
        images_dir_path = os.path.join(output_dir, "images")
        os.makedirs(images_dir_path, exist_ok=True)
        
        image_writer = FileBasedDataWriter(images_dir_path)
        md_writer = FileBasedDataWriter(output_dir)
        
        return image_writer, md_writer, images_dir_path
    
    def _parse_pdf_to_documents(self, pdf_path: str, parser_type: str, backend: str = "", server_url: str = "") -> List[Document]:
        """从PDF文件路径解析为Document对象，根据text_level合并逻辑连贯的文本块"""
        self.logger.debug(f"Loading PDF file: {pdf_path}")
        try:
            # 获取markdown内容
            md_content, content_list = self.get_content(pdf_path)
            if not content_list:
                raise ValueError("content_list is empty, failed to extract content from PDF")
            
            documents = []
            current_text = ""
            current_metadata = None
            
            # 根据content_list创建Document对象，合并逻辑连贯的文本块
            for i, item in enumerate(content_list):
                if item.get('type') != 'text' or not item.get('text'):
                    continue
                
                text = item['text'].strip()
                if not text:
                    continue
                
                text_level = item.get('text_level', 0)
                
                # 如果是标题(text_level=1)或者当前没有累积文本，开始新的文本块
                if text_level == 1 or not current_text:
                    # 先保存之前的文本块
                    if current_text and current_metadata:
                        doc = Document(
                            page_content=current_text.strip(),
                            metadata=current_metadata
                        )
                        documents.append(doc)
                    
                    # 开始新的文本块
                    current_text = text
                    current_metadata = {
                        "source": pdf_path,
                        "type": "pdf",
                        "parser": parser_type,
                        "text_level": text_level,
                        "page_idx": item.get('page_idx', 0),
                        "content_type": item.get('type', 'text'),
                        "start_index": i
                    }
                    
                    # 添加特定后端的元数据
                    if backend:
                        current_metadata["backend"] = backend
                    if server_url:
                        current_metadata["server_url"] = server_url
                
                # 如果是正文(text_level=0或无值)，合并到当前文本块
                else:
                    if current_text:
                        # 添加换行符保持格式
                        if not current_text.endswith('\n'):
                            current_text += '\n'
                        current_text += text
                    else:
                        current_text = text
            
            # 保存最后一个文本块
            if current_text and current_metadata:
                doc = Document(
                    page_content=current_text.strip(),
                    metadata=current_metadata
                )
                documents.append(doc)
            
            self.logger.debug(f"Successfully created {len(documents)} Documents from PDF with merged text blocks")
            return documents
            
        except Exception as e:
            self.logger.error(f"Failed to parse PDF file {pdf_path}: {str(e)}")
            raise
    
    def _parse_content_to_documents(self, content: str, parser_type: str, backend: str = "", server_url: str = "") -> List[Document]:
        """从内容字符串解析为Document对象"""
        self.logger.debug("Parsing PDF content from string")
        try:
            # 使用临时文件处理内容字符串
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
                self.logger.debug(f"Temporary content file created: {tmp_file_path}")
            
            try:
                # 解析临时文件
                documents = self._parse_pdf_to_documents(tmp_file_path, parser_type, backend, server_url)
                return documents
            finally:
                # 清理临时文件
                os.unlink(tmp_file_path)
                self.logger.debug("Temporary content file cleaned up")
                
        except Exception as e:
            self.logger.error(f"Failed to parse PDF content: {str(e)}")
            raise
    
    def _parse_bytes_to_documents(self, content: bytes, parser_type: str, backend: str = "", server_url: str = "") -> List[Document]:
        """从字节流解析为Document对象"""
        self.logger.debug(f"Parsing PDF from {len(content)} bytes")
        try:
            # 使用临时文件处理字节流
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
                self.logger.debug(f"Temporary PDF file created: {tmp_file_path}")
            
            try:
                # 解析临时文件
                documents = self._parse_pdf_to_documents(tmp_file_path, parser_type, backend, server_url)
                return documents
            finally:
                # 清理临时文件
                os.unlink(tmp_file_path)
                self.logger.debug("Temporary PDF file cleaned up")
                
        except Exception as e:
            self.logger.error(f"Failed to parse PDF bytes: {str(e)}")
            raise


class MineruVLMParser(MineruParser):
    """
    基于MinerU VLM后端的PDF解析器
    支持通过URL调用远程VLM服务进行PDF解析
    """
    
    def __init__(
        self,
        backend: str = "vlm-sglang-client",
        server_url: str = "http://localhost:30000",
        model_path: Optional[str] = None,
        parse_method: str = "auto",
        formula_enable: bool = True,
        table_enable: bool = True,
        lang: List[str] = None,
        **kwargs
    ):
        """
        初始化MinerU VLM解析器
        
        Args:
            backend: VLM后端类型，可选：
                - "sglang-client": 通过URL调用sglang服务（默认）
                - "transformers": 本地transformers模型
                - "sglang-engine": 本地sglang引擎
            server_url: VLM服务器URL，当backend为"sglang-client"时必需
            model_path: 本地模型路径，当使用本地后端时必需
            parse_method: 解析方法，可选：auto, txt, ocr
            formula_enable: 是否启用公式解析
            table_enable: 是否启用表格解析
            lang: 支持的语言列表
            **kwargs: 其他传递给VLM后端的参数
        """
        super().__init__(**kwargs)
        self.backend = backend
        self.server_url = server_url
        self.model_path = model_path
        self.parse_method = parse_method
        self.formula_enable = formula_enable
        self.table_enable = table_enable
        self.lang = lang or ["ch", "en"]
        
        self.logger.info(f"Initialized MineruVLMParser with backend: {backend}, server_url: {server_url}")
    
    def process_single_pdf(
        self,
        pdf_path: str,
        output_dir: str,
        generate_visualizations: bool = True,
        target_lang: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用VLM后端处理单个PDF文件
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            generate_visualizations: 是否生成可视化文件
            target_lang: 目标语言
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pdf_filename = os.path.basename(pdf_path)
        base_filename = os.path.splitext(pdf_filename)[0]
        
        target_lang = target_lang or self.lang[0]
        
        self.logger.info(f"Start processing PDF: {pdf_filename}，using language: {target_lang}")
        
        try:
            # 准备输出目录
            image_writer, md_writer, images_dir_path = self._prepare_output_dirs(output_dir)
            images_dir_name = os.path.basename(images_dir_path)
            
            # 读取PDF内容
            pdf_bytes = read_fn(pdf_path)
            self.logger.debug(f"Read PDF file: {len(pdf_bytes)} bytes")
            
            # 使用VLM后端
            backend_name = self.backend[4:]  # 移除"vlm-"前缀
            middle_json, infer_result = vlm_doc_analyze(
                pdf_bytes,
                image_writer=image_writer,
                backend=backend_name,
                server_url=self.server_url,
                model_path=self.model_path,
                **self.kwargs
            )
            
            # 使用VLM特定的内容生成
            from mineru.backend.vlm.vlm_middle_json_mkcontent import union_make as vlm_union_make
            
            pdf_info = middle_json["pdf_info"]
            md_content_str = vlm_union_make(pdf_info, MakeMode.MM_MD, images_dir_name)
            content_list = vlm_union_make(pdf_info, MakeMode.CONTENT_LIST, images_dir_name)
            
            # 写入结果文件
            md_writer.write_string("content.md", md_content_str)
            md_writer.write_string("content_list.json", json.dumps(content_list, ensure_ascii=False, indent=4))
            md_writer.write_string("middle.json", json.dumps(middle_json, ensure_ascii=False, indent=4))
            
            self.logger.info(f"Successfully processed PDF: {pdf_filename}，using language: {target_lang}")
            
            return {
                "status": "success",
                "pdf_filename": pdf_filename,
                "output_dir": output_dir,
                "markdown_content": md_content_str,
                "content_list": content_list,
                "middle_json": middle_json,
                "used_language": target_lang,
                "backend": self.backend,
                "server_url": self.server_url
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process PDF {pdf_filename}，using language: {target_lang}: {str(e)}")
            return {
                "status": "error",
                "pdf_filename": pdf_filename,
                "error": str(e)
            }
    
    async def aprocess_single_pdf(
        self,
        pdf_path: str,
        output_dir: str,
        generate_visualizations: bool = True,
        target_lang: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        异步处理单个PDF文件（使用VLM后端）
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            generate_visualizations: 是否生成可视化文件
            target_lang: 目标语言
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pdf_filename = os.path.basename(pdf_path)
        base_filename = os.path.splitext(pdf_filename)[0]
        
        target_lang = target_lang or self.lang[0]
        
        self.logger.info(f"Start async processing PDF: {pdf_filename}，using language: {target_lang}")
        
        try:
            # 准备输出目录
            image_writer, md_writer, images_dir_path = self._prepare_output_dirs(output_dir)
            images_dir_name = os.path.basename(images_dir_path)
            
            # 读取PDF内容
            pdf_bytes = read_fn(pdf_path)
            self.logger.debug(f"Read PDF file: {len(pdf_bytes)} bytes")

            # 使用VLM后端异步处理
            backend_name = self.backend[4:]  # 移除"vlm-"前缀
            middle_json, infer_result = await aio_vlm_doc_analyze(
                pdf_bytes,
                image_writer=image_writer,
                backend=backend_name,
                server_url=self.server_url,
                model_path=self.model_path,
                **self.kwargs
            )
            
            # 使用VLM特定的内容生成
            from mineru.backend.vlm.vlm_middle_json_mkcontent import union_make as vlm_union_make
            
            pdf_info = middle_json["pdf_info"]
            md_content_str = vlm_union_make(pdf_info, MakeMode.MM_MD, images_dir_name)
            content_list = vlm_union_make(pdf_info, MakeMode.CONTENT_LIST, images_dir_name)
            
            # 写入结果文件
            md_writer.write_string("content.md", md_content_str)
            md_writer.write_string("content_list.json", json.dumps(content_list, ensure_ascii=False, indent=4))
            md_writer.write_string("middle.json", json.dumps(middle_json, ensure_ascii=False, indent=4))
            
            self.logger.info(f"Successfully processed PDF: {pdf_filename}，using language: {target_lang}")
            
            return {
                "status": "success",
                "pdf_filename": pdf_filename,
                "output_dir": output_dir,
                "markdown_content": md_content_str,
                "content_list": content_list,
                "middle_json": middle_json,
                "used_language": target_lang,
                "backend": self.backend,
                "server_url": self.server_url
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process PDF {pdf_filename}，using language: {target_lang}: {str(e)}")
            return {
                "status": "error",
                "pdf_filename": pdf_filename,
                "error": str(e)
            }
    
    def process_batch_pdfs(
        self,
        pdfs_dir: str,
        output_base_dir: str,
        generate_visualizations: bool = True,
        skip_existing: bool = True,
        target_lang: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量处理PDF文件
        
        Args:
            pdfs_dir: 包含PDF文件的目录
            output_base_dir: 输出基础目录
            generate_visualizations: 是否生成可视化文件
            skip_existing: 是否跳过已处理的文件
            target_lang: 目标语言
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 批量处理结果
        """
        if not os.path.exists(pdfs_dir):
            self.logger.error(f"Directory not found: {pdfs_dir}")
            return {
                "status": "error",
                "error": f"Directory not found: {pdfs_dir}"
            }
        
        # 获取所有PDF文件
        pdf_files = [f for f in os.listdir(pdfs_dir) if f.lower().endswith(".pdf")]
        total_pdfs = len(pdf_files)
        
        if total_pdfs == 0:
            logger.warning(f"No PDF files found in directory: {pdfs_dir}")
            return {
                "status": "warning",
                "message": f"No PDF files found in directory: {pdfs_dir}"
            }
        
        target_lang = target_lang or self.lang[0]
        self.logger.info(f"Start batch processing {total_pdfs} PDF files，using language: {target_lang}")
        
        processed_pdfs = 0
        failed_pdfs = 0
        skipped_pdfs = 0
        results = []
        
        # 创建输出基础目录
        os.makedirs(output_base_dir, exist_ok=True)
        
        for pdf_file in pdf_files:
            base_filename = os.path.splitext(pdf_file)[0]
            pdf_path = os.path.join(pdfs_dir, pdf_file)
            output_dir = os.path.join(output_base_dir, base_filename)
            
            # 检查是否已处理
            if skip_existing:
                md_file = os.path.join(output_dir, "content.md")
                if os.path.exists(md_file):
                    self.logger.info(f"PDF {pdf_file} has been processed，skip...")
                    skipped_pdfs += 1
                    continue
            
            # 处理单个PDF
            result = self.process_single_pdf(
                pdf_path, output_dir, generate_visualizations, target_lang, **kwargs
            )
            
            results.append(result)
            
            if result["status"] == "success":
                processed_pdfs += 1
            else:
                failed_pdfs += 1
        
        self.logger.info(f"Batch processing completed. Processed: {processed_pdfs}，Failed: {failed_pdfs}，Skipped: {skipped_pdfs}")
        
        return {
            "status": "complete",
            "total_pdfs": total_pdfs,
            "processed_pdfs": processed_pdfs,
            "failed_pdfs": failed_pdfs,
            "skipped_pdfs": skipped_pdfs,
            "results": results,
            "used_language": target_lang,
            "backend": self.backend,
            "server_url": self.server_url
        }
    
    async def aprocess_batch_pdfs(
        self,
        pdfs_dir: str,
        output_base_dir: str,
        generate_visualizations: bool = True,
        skip_existing: bool = True,
        target_lang: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        异步批量处理PDF文件
        
        Args:
            pdfs_dir: 包含PDF文件的目录
            output_base_dir: 输出基础目录
            generate_visualizations: 是否生成可视化文件
            skip_existing: 是否跳过已处理的文件
            target_lang: 目标语言
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 批量处理结果
        """
        if not os.path.exists(pdfs_dir):
            self.logger.error(f"Directory not found: {pdfs_dir}")
            return {
                "status": "error",
                "error": f"Directory not found: {pdfs_dir}"
            }
        
        # 获取所有PDF文件
        pdf_files = [f for f in os.listdir(pdfs_dir) if f.lower().endswith(".pdf")]
        total_pdfs = len(pdf_files)
        
        if total_pdfs == 0:
            logger.warning(f"No PDF files found in directory: {pdfs_dir}")
            return {
                "status": "warning",
                "message": f"No PDF files found in directory: {pdfs_dir}"
            }
        
        target_lang = target_lang or self.lang[0]
        self.logger.info(f"Start async batch processing {total_pdfs} PDF files，using language: {target_lang}")
        
        processed_pdfs = 0
        failed_pdfs = 0
        skipped_pdfs = 0
        results = []
        
        # 创建输出基础目录
        os.makedirs(output_base_dir, exist_ok=True)
        
        # 异步处理所有PDF
        tasks = []
        for pdf_file in pdf_files:
            base_filename = os.path.splitext(pdf_file)[0]
            pdf_path = os.path.join(pdfs_dir, pdf_file)
            output_dir = os.path.join(output_base_dir, base_filename)
            
            # 检查是否已处理
            if skip_existing:
                md_file = os.path.join(output_dir, "content.md")
                if os.path.exists(md_file):
                    self.logger.info(f"PDF {pdf_file} has been processed，skip...")
                    skipped_pdfs += 1
                    continue
            
            # 创建异步任务
            task = self.aprocess_single_pdf(
                pdf_path, output_dir, generate_visualizations, target_lang, **kwargs
            )
            tasks.append(task)
        
        # 执行所有异步任务
        if tasks:
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    failed_pdfs += 1
                    self.logger.error(f"Async processing failed: {str(result)}")
                else:
                    results.append(result)
                    if result["status"] == "success":
                        processed_pdfs += 1
                    else:
                        failed_pdfs += 1
        
        self.logger.info(f"Async batch processing completed. Processed: {processed_pdfs}，Failed: {failed_pdfs}，Skipped: {skipped_pdfs}")
        
        return {
            "status": "complete",
            "total_pdfs": total_pdfs,
            "processed_pdfs": processed_pdfs,
            "failed_pdfs": failed_pdfs,
            "skipped_pdfs": skipped_pdfs,
            "results": results,
            "used_language": target_lang,
            "backend": self.backend,
            "server_url": self.server_url
        }
    
    def get_content(
        self,
        pdf_path: str,
        target_lang: str = None,
        **kwargs
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        使用VLM后端快速获取PDF的markdown内容（不保存文件）

        Args:
            pdf_path: PDF文件路径
            target_lang: 目标语言
            **kwargs: 其他参数

        Returns:
            Tuple[str, List[Dict[str, Any]]]: (markdown内容, content列表)
        """
        try:
            target_lang = target_lang or self.lang[0]
            
            # 读取PDF内容
            pdf_bytes = read_fn(pdf_path)
            
            # 使用临时写入器
            temp_writer = FileBasedDataWriter("/tmp")

            backend_name = self.backend[4:]

            # middle_json, infer_result = vlm_doc_analyze(
            #     pdf_bytes,
            #     image_writer=temp_writer,
            #     backend=backend_name,
            #     server_url=self.server_url,
            #     model_path=self.model_path,
            #     **self.kwargs
            # )
            
            # from mineru.backend.vlm.vlm_middle_json_mkcontent import union_make as vlm_union_make
            # pdf_info = middle_json["pdf_info"]
            # md_content_str = vlm_union_make(pdf_info, MakeMode.MM_MD, "images")
            # content_list = vlm_union_make(pdf_info, MakeMode.CONTENT_LIST, "images")
            
            self.logger.info(f"Starting a loop to process PDF file: {pdf_path}")
            if asyncio.get_event_loop() is None:
                result = asyncio.run(self.aprocess_single_pdf(pdf_path, "/tmp", True, target_lang))
            else:
                import threading

                loop = asyncio.new_event_loop()
                threading.Thread(target=lambda: (asyncio.set_event_loop(loop), loop.run_forever()), daemon=True).start()
                future = asyncio.run_coroutine_threadsafe(self.aprocess_single_pdf(pdf_path, "/tmp", True, target_lang), loop)
                result = future.result()
            md_content_str = result["markdown_content"]
            content_list = result["content_list"]
            
            return md_content_str, content_list
            
        except Exception as e:
            self.logger.error(f"Error getting content from {pdf_path}: {str(e)}")
            self.logger.error(traceback.format_exc())
            return None, []

    def parse(self, source: Union[str, bytes], source_type: str = "file") -> List[Document]:
        """
        解析PDF文件内容，将json内容转换为Document对象
        
        Args:
            source: 文件路径、文件内容或字节流
            source_type: "file"表示文件路径, "content"表示内容字符串, "bytes"表示字节流
            
        Returns:
            List[Document]: 解析后的文档列表
        """
        self.logger.debug(f"Starting PDF parsing with MineruVLMParser, source_type: {source_type}")
        
        if source_type == "file":
            return self._parse_pdf_to_documents(str(source), "mineru_vlm", self.backend, self.server_url)
        elif source_type == "content":
            return self._parse_content_to_documents(str(source), "mineru_vlm", self.backend, self.server_url)
        elif source_type == "bytes":
            return self._parse_bytes_to_documents(source, "mineru_vlm", self.backend, self.server_url)
        else:
            error_msg = "source_type must be 'file', 'content' or 'bytes'"
            self.logger.error(error_msg)
            raise ValueError(error_msg)


class MineruPipelineParser(MineruParser):
    """
    基于MinerU Pipeline后端的PDF解析器
    继承自MineruParser，复用基类的共有方法
    """
    
    def __init__(
        self,
        lang: List[str] = None,
        parse_method: str = "auto",
        formula_enable: bool = True,
        table_enable: bool = True,
        **kwargs
    ):
        """
        初始化MinerU Pipeline解析器
        
        Args:
            lang: 支持的语言列表
            parse_method: 解析方法
            formula_enable: 是否启用公式解析
            table_enable: 是否启用表格解析
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        self.lang = lang or ["ch", "en"]
        self.parse_method = parse_method
        self.formula_enable = formula_enable
        self.table_enable = table_enable
        
        self.logger.info("Initialized MineruPipelineParser")
    
    def process_single_pdf(
        self,
        pdf_path: str,
        output_dir: str,
        generate_visualizations: bool = True,
        target_lang: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用pipeline后端处理单个PDF文件
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            generate_visualizations: 是否生成可视化文件
            target_lang: 目标语言
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pdf_filename = os.path.basename(pdf_path)
        base_filename = os.path.splitext(pdf_filename)[0]
        
        target_lang = target_lang or self.lang[0]
        
        self.logger.info(f"Start processing PDF: {pdf_filename}，using language: {target_lang}")
        
        try:
            # 准备输出目录
            image_writer, md_writer, images_dir_path = self._prepare_output_dirs(output_dir)
            images_dir_name = os.path.basename(images_dir_path)
            
            # 读取PDF内容
            pdf_bytes = read_fn(pdf_path)
            self.logger.debug(f"Read PDF file: {len(pdf_bytes)} bytes")
            
            # 使用pipeline后端处理
            from mineru.backend.pipeline.model_json_to_middle_json import result_to_middle_json as pipeline_result_to_middle_json
            from mineru.backend.pipeline.pipeline_analyze import doc_analyze as pipeline_doc_analyze
            from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_union_make
            
            infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = pipeline_doc_analyze(
                [pdf_bytes],
                [target_lang],
                parse_method=self.parse_method,
                formula_enable=self.formula_enable,
                table_enable=self.table_enable
            )
            
            model_list = infer_results[0]
            images_list = all_image_lists[0]
            pdf_doc = all_pdf_docs[0]
            _lang = lang_list[0]
            _ocr_enable = ocr_enabled_list[0]
            
            middle_json = pipeline_result_to_middle_json(
                model_list, images_list, pdf_doc, image_writer, _lang, _ocr_enable, True
            )
            
            pdf_info = middle_json["pdf_info"]
            md_content_str = pipeline_union_make(pdf_info, MakeMode.MM_MD, images_dir_name)
            content_list = pipeline_union_make(pdf_info, MakeMode.CONTENT_LIST, images_dir_name)
            
            # 写入结果文件
            md_writer.write_string("content.md", md_content_str)
            md_writer.write_string("content_list.json", json.dumps(content_list, ensure_ascii=False, indent=4))
            md_writer.write_string("middle.json", json.dumps(middle_json, ensure_ascii=False, indent=4))
            
            self.logger.info(f"Successfully processed PDF: {pdf_filename}")
            
            return {
                "status": "success",
                "pdf_filename": pdf_filename,
                "output_dir": output_dir,
                "markdown_content": md_content_str,
                "content_list": content_list,
                "middle_json": middle_json,
                "used_language": target_lang,
                "backend": "pipeline",
                "server_url": "N/A"
            }
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {pdf_filename}: {str(e)}")
            return {
                "status": "error",
                "pdf_filename": pdf_filename,
                "error": str(e)
            }
    
    def get_content(
        self,
        pdf_path: str,
        target_lang: str = None,
        **kwargs
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        使用pipeline后端快速获取PDF的markdown内容
        
        Args:
            pdf_path: PDF文件路径
            target_lang: 目标语言
            **kwargs: 其他参数
            
        Returns:
            Tuple[str, List[Dict[str, Any]]]: (markdown内容, content列表)
        """
        try:
            target_lang = target_lang or self.lang[0]
            
            # 读取PDF内容
            pdf_bytes = read_fn(pdf_path)
            
            # 使用临时写入器
            temp_writer = FileBasedDataWriter("/tmp")
            
            # 使用pipeline后端处理
            from mineru.backend.pipeline.pipeline_analyze import doc_analyze as pipeline_doc_analyze
            from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_union_make
            from mineru.backend.pipeline.model_json_to_middle_json import result_to_middle_json as pipeline_result_to_middle_json
            
            infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = pipeline_doc_analyze(
                [pdf_bytes],
                [target_lang],
                parse_method=self.parse_method,
                formula_enable=self.formula_enable,
                table_enable=self.table_enable
            )
            
            model_list = infer_results[0]
            images_list = all_image_lists[0]
            pdf_doc = all_pdf_docs[0]
            _lang = lang_list[0]
            _ocr_enable = ocr_enabled_list[0]
            
            middle_json = pipeline_result_to_middle_json(
                model_list, images_list, pdf_doc, temp_writer, _lang, _ocr_enable, True
            )
            
            pdf_info = middle_json["pdf_info"]
            md_content_str = pipeline_union_make(pdf_info, MakeMode.MM_MD, "images")
            content_list = pipeline_union_make(pdf_info, MakeMode.CONTENT_LIST, "images")
            
            self.logger.debug(f"Successfully retrieved PDF content: {len(md_content_str)} characters, {len(content_list)} content items")
            return md_content_str, content_list
            
        except Exception as e:
            self.logger.error(f"Error retrieving PDF content: {str(e)}")
            raise

    
    def process_batch_pdfs(
        self,
        pdfs_dir: str,
        output_base_dir: str,
        generate_visualizations: bool = True,
        skip_existing: bool = True,
        target_lang: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量处理PDF文件
        
        Args:
            pdfs_dir: 包含PDF文件的目录
            output_base_dir: 输出基础目录
            generate_visualizations: 是否生成可视化文件
            skip_existing: 是否跳过已处理的文件
            target_lang: 目标语言
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 批量处理结果
        """
        if not os.path.exists(pdfs_dir):
            self.logger.error(f"Directory not found: {pdfs_dir}")
            return {
                "status": "error",
                "error": f"Directory not found: {pdfs_dir}"
            }
        
        # 获取所有PDF文件
        pdf_files = [f for f in os.listdir(pdfs_dir) if f.lower().endswith(".pdf")]
        total_pdfs = len(pdf_files)
        
        if total_pdfs == 0:
            self.logger.warning(f"No PDF files found in {pdfs_dir}")
            return {
                "status": "warning",
                "message": f"No PDF files found in {pdfs_dir}"
            }
        
        target_lang = target_lang or self.lang[0]
        self.logger.info(f"Batch processing {total_pdfs} PDF files in {pdfs_dir} using language: {target_lang}")
        
        processed_pdfs = 0
        failed_pdfs = 0
        skipped_pdfs = 0
        results = []
        
        # 创建输出基础目录
        os.makedirs(output_base_dir, exist_ok=True)
        
        for pdf_file in pdf_files:
            base_filename = os.path.splitext(pdf_file)[0]
            pdf_path = os.path.join(pdfs_dir, pdf_file)
            output_dir = os.path.join(output_base_dir, base_filename)
            
            # 检查是否已处理
            if skip_existing:
                md_file = os.path.join(output_dir, "content.md")
                if os.path.exists(md_file):
                    self.logger.info(f"PDF {pdf_file} has already been processed, skipping...")
                    skipped_pdfs += 1
                    continue
            
            # 处理单个PDF
            result = self.process_single_pdf(
                pdf_path, output_dir, generate_visualizations, target_lang, **kwargs
            )
            
            results.append(result)
            
            if result["status"] == "success":
                processed_pdfs += 1
            else:
                failed_pdfs += 1
        
        self.logger.info(f"Batch processing completed. Processed: {processed_pdfs}, Failed: {failed_pdfs}, Skipped: {skipped_pdfs}")
        
        return {
            "status": "complete",
            "total_pdfs": total_pdfs,
            "processed_pdfs": processed_pdfs,
            "failed_pdfs": failed_pdfs,
            "skipped_pdfs": skipped_pdfs,
            "results": results,
            "used_language": target_lang,
            "backend": "pipeline",
            "server_url": "N/A"
        }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="MinerU PDF Parser")
    parser.add_argument("--pdf", type=str, help="单个PDF文件路径")
    parser.add_argument("--dir", type=str, help="PDF文件目录")
    parser.add_argument("--output", type=str, default="./output", help="输出目录")
    parser.add_argument("--backend", type=str, default="sglang-client", 
                       choices=["sglang-client", "transformers", "sglang-engine", "pipeline"],
                       help="解析后端")
    parser.add_argument("--server-url", type=str, default="http://localhost:8000", 
                       help="VLM服务器URL")
    parser.add_argument("--lang", type=str, default="ch", help="目标语言")
    parser.add_argument("--async", action="store_true", help="使用异步处理")
    
    args = parser.parse_args()
    
    # 初始化解析器
    pdf_parser = MineruVLMParser(
        backend=f"vlm-{args.backend}" if args.backend != "pipeline" else "pipeline",
        server_url=args.server_url,
        lang=[args.lang]
    )
    
    if args.pdf:
        # 处理单个PDF
        result = pdf_parser.process_single_pdf(args.pdf, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.dir:
        # 批量处理PDF
        if getattr(args, 'async', False):
            # 异步处理
            result = asyncio.run(pdf_parser.aprocess_batch_pdfs(args.dir, args.output))
        else:
            # 同步处理
            result = pdf_parser.process_batch_pdfs(args.dir, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("请提供 --pdf 或 --dir 参数")