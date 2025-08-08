import re
from typing import List, Union, Optional, Dict, Tuple
from langchain_core.documents.base import Document
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from core.parser.base import BaseParser

class MarkdownParser(BaseParser):
    supported_extensions = [".md", ".markdown"]
    
    def __init__(self, remove_hyperlinks: bool = False, remove_images: bool = False, markdown_clean_html: bool = True, **kwargs):
        super().__init__(remove_hyperlinks=remove_hyperlinks, remove_images=remove_images, **kwargs)
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images
        self._markdown_clean_html = markdown_clean_html
        self._markdown_preserve_html_imgs = kwargs.get("markdown_preserve_html_imgs", False)
        self._markdown_preserve_html_tables = kwargs.get("markdown_preserve_html_tables", True)

    def parse(self, source: Union[str, bytes], source_type: str = "file") -> List[Document]:
        """
        解析markdown内容
        
        Args:
            source: 文件路径、文件内容或字节流
            source_type: "file"表示文件路径, "content"表示内容字符串, "bytes"表示字节流
            
        Returns:
            List[Document]: 解析后的文档列表
        """
        self.logger.debug(f"Starting markdown parsing with source_type: {source_type}")

        self.logger.debug(f"Parser Config: {self.config}")
        if self.config.get("parse_by_chapter", False):
            self.logger.debug("Parsing markdown with sections")
            return self.parse_with_sections(source, source_type)
        
        if source_type == "file":
            self.logger.debug(f"Parsing markdown from file: {source}")
            documents = self._parse_from_file(source)
        elif source_type == "content":
            self.logger.debug(f"Parsing markdown from content string (length: {len(source)} chars)")
            documents = self._parse_from_content(source)
        elif source_type == "bytes":
            self.logger.debug(f"Parsing markdown from bytes (size: {len(source)} bytes)")
            documents = self._parse_from_bytes(source)
        else:
            error_msg = "source_type must be 'file', 'content' or 'bytes'"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info(f"Successfully parsed markdown into {len(documents)} documents")
        for i, doc in enumerate(documents):
            self.logger.debug(f"Document {i+1}: content length={len(doc.page_content)}, metadata={list(doc.metadata.keys())}")
            
        return documents

    def _parse_from_file(self, filepath: str) -> List[Document]:
        """从文件路径解析markdown"""
        self.logger.debug(f"Loading markdown file: {filepath}")
        try:
            loader = UnstructuredMarkdownLoader(filepath, mode="elements")
            documents = loader.load()
            self.logger.debug(f"Loaded {len(documents)} documents from file")
            processed_docs = self._post_process_documents(documents)
            self.logger.debug(f"Post-processed into {len(processed_docs)} documents")
            return processed_docs
        except Exception as e:
            self.logger.error(f"Failed to parse markdown file {filepath}: {str(e)}")
            raise

    def _parse_from_content(self, content: str) -> List[Document]:
        """从内容字符串解析markdown"""
        self.logger.debug("Creating temporary file for content parsing")
        # 创建临时文件来使用UnstructuredMarkdownLoader
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            self.logger.debug(f"Temporary file created: {tmp_file_path}")
            
        try:
            loader = UnstructuredMarkdownLoader(tmp_file_path, mode="elements")
            documents = loader.load()
            self.logger.debug(f"Loaded {len(documents)} documents from temporary file")
            processed_docs = self._post_process_documents(documents)
            self.logger.debug(f"Post-processed into {len(processed_docs)} documents")
            return processed_docs
        except Exception as e:
            self.logger.error(f"Failed to parse markdown content: {str(e)}")
            raise
        finally:
            os.unlink(tmp_file_path)
            self.logger.debug("Temporary file cleaned up")

    def _parse_from_bytes(self, content: bytes) -> List[Document]:
        """从字节流解析markdown"""
        self.logger.debug(f"Detecting encoding for {len(content)} bytes")
        # 检测编码
        import chardet
        detected = chardet.detect(content)
        encoding = detected['encoding']
        self.logger.debug(f"Detected encoding: {encoding}")
        
        # 解码为字符串
        try:
            text_content = content.decode(encoding)
            self.logger.debug(f"Successfully decoded {len(text_content)} characters")
            return self._parse_from_content(text_content)
        except Exception as e:
            self.logger.error(f"Failed to decode bytes with encoding {encoding}: {str(e)}")
            raise

    def _post_process_documents(self, documents: List[Document]) -> List[Document]:
        """对解析后的文档进行后处理"""
        self.logger.debug(f"Starting post-processing of {len(documents)} documents")
        self.logger.debug(f"Remove hyperlinks: {self._remove_hyperlinks}, Remove images: {self._remove_images}, Clean HTML: {self._markdown_clean_html}")
        
        original_count = len(documents)
        
        # 清理HTML标签
        if self._markdown_clean_html:
            documents = [Document(page_content=self._clean_html_tags(doc.page_content), metadata=doc.metadata) 
                        for doc in documents]
            self.logger.debug("Cleaned HTML tags from documents")
        
        if self._remove_hyperlinks:
            documents = [Document(page_content=self._remove_links(doc.page_content), metadata=doc.metadata) 
                        for doc in documents]
            self.logger.debug("Removed hyperlinks from documents")
        
        if self._remove_images:
            documents = [Document(page_content=self._remove_imgs(doc.page_content), metadata=doc.metadata) 
                        for doc in documents]
            self.logger.debug("Removed images from documents")
        
        final_count = len(documents)
        self.logger.debug(f"Post-processing complete: {original_count} -> {final_count} documents")
        return documents

    def _remove_links(self, content: str) -> str:
        """移除超链接，但不移除图片链接
        
        正确处理嵌套链接，如：[![image](url)](link) 应该只移除外层链接，保留内层图片
        """
        # 使用更精确的正则表达式匹配嵌套结构
        # 匹配不是以!开头的链接，且内容中不包含图片标记
        
        # 先处理嵌套链接：找到所有嵌套结构并替换
        nested_pattern = r'(\[(!\[.*?\]\(.*?\))\]\(.*?\))'
        
        def replace_nested_link(match):
            # 对于嵌套链接，只移除外层，保留内层图片
            full_match = match.group(1)
            inner_img = match.group(2)  # 内层图片
            return inner_img
        
        # 处理嵌套链接
        content = re.sub(nested_pattern, replace_nested_link, content)
        
        # 处理剩余的普通链接（不包括图片链接）
        link_pattern = r'(?<!\!)\[([^\[\]]*?)\]\(([^()]*?)\)'
        content = re.sub(link_pattern, r'\1', content)
        
        return content

    def _remove_imgs(self, content: str) -> str:
        """移除图片"""
        pattern = r"!\[(.*?)\]\((.*?)\)"
        return re.sub(pattern, "", content)

    def _clean_html_tags(self, content: str, preserve_imgs: bool = None, preserve_tables: bool = None) -> str:
        """清理HTML标签，根据配置保留图片和/或表格
        
        使用BeautifulSoup精确清理HTML内容，根据配置决定是否保留<img>和<table>及其子元素
        保留的HTML元素保持在原始位置，包括嵌套结构
        
        Args:
            content: 包含HTML的文本内容
            
        Returns:
            str: 清理后的文本内容，根据配置保留图片和/或表格在原始位置
        """
        if not self._markdown_clean_html:
            return content
            
        try:
            import re
            from bs4 import BeautifulSoup
            
            # 使用BeautifulSoup解析内容
            soup = BeautifulSoup(content, 'html.parser')
            
            # 定义要保留的标签集合（包括表格的所有子标签）
            preserve_tags = set()
            
            # 根据配置决定是否保留图片和表格
            preserve_imgs = preserve_imgs if preserve_imgs is not None else self._markdown_preserve_html_imgs
            preserve_tables = preserve_tables if preserve_tables is not None else self._markdown_preserve_html_tables
            if preserve_imgs:
                preserve_tags.add('img')
                self.logger.debug("Markdown Parser clean HTML tags preserving <img> elements")
            if preserve_tables:  # 默认保留表格
                preserve_tags.update(['table', 'thead', 'tbody', 'tfoot', 'tr', 'td', 'th', 
                                      'caption', 'col', 'colgroup'])
                self.logger.debug("Markdown Parser clean HTML tags preserving <table> elements")
            
            # 定义要清理的标签（除了保留的标签外，其他都清理）
            def should_remove_tag(tag):
                return tag.name and tag.name.lower() not in preserve_tags
            
            # 找到所有要移除的标签
            tags_to_remove = []
            for tag in soup.find_all():
                if should_remove_tag(tag):
                    tags_to_remove.append(tag)
            
            # 移除不需要的标签，但保留其内容
            for tag in tags_to_remove:
                tag.unwrap()
            
            # 获取清理后的HTML内容，保留指定的标签
            cleaned_html = str(soup.encode(formatter=None), 'utf-8')
            
            # 清理多余的空格和空行
            cleaned_html = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_html)
            cleaned_html = re.sub(r'[ \t]+', ' ', cleaned_html)
            cleaned_html = cleaned_html.strip()
            
            return cleaned_html
                
        except ImportError:
            self.logger.warning("BeautifulSoup not available, skipping HTML cleaning")
            return content
        except Exception as e:
            self.logger.error(f"Error during HTML cleaning: {str(e)}")
            return content

    def load_file(self, filepath: str) -> str:
        """加载文件内容"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def parse_by_sections(self, content: str) -> List[Document]:
        """
        按标题章节解析markdown内容
        
        Args:
            content: markdown内容字符串
            
        Returns:
            List[Document]: 按章节组织的文档列表，每个文档包含章节标题、内容和层级信息
        """
        self.logger.debug("Starting section-based markdown parsing")
        content_length = len(content)
        self.logger.debug(f"Content length: {content_length} characters")
        
        lines = content.split('\n')
        sections = []
        current_section = None
        current_content = []
        
        # 用于跟踪标题层级的栈
        header_stack = []  # 存储 (level, title) 元组
        
        # 检查是否存在标题
        has_headers = bool(re.search(r'^#{1,6}\s+.*', content, flags=re.MULTILINE))
        self.logger.debug(f"Document contains headers: {has_headers}")
        
        # 如果文档存在标题，则进行章节解析
        if has_headers:
            for line_num, line in enumerate(lines):
                # 匹配markdown标题
                header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
                
                if header_match:
                    # 如果遇到新标题，保存上一个章节
                    if current_section is not None and current_content:
                        # 构建完整标题路径
                        full_title_path = ' > '.join([h[1] for h in header_stack])
                        if full_title_path:
                            content_text = f"{full_title_path}\n\n" + '\n'.join(current_content).strip()
                        else:
                            content_text = '\n'.join(current_content).strip()
                            
                        if content_text:
                            # 获取父标题信息
                            parent_title = header_stack[-2][1] if len(header_stack) >= 2 else None
                            parent_level = header_stack[-2][0] if len(header_stack) >= 2 else None
                            
                            doc = Document(
                                page_content=content_text,
                                metadata={
                                    'title': current_section['title'],
                                    'level': current_section['level'],
                                    'header_line': current_section['line_num'],
                                    'type': 'section',
                                    'source': 'markdown_section',
                                    'full_title_path': full_title_path,
                                    'parent_title': parent_title,
                                    'parent_level': str(parent_level),
                                    'title_hierarchy': [h[1] for h in header_stack],
                                    'level_hierarchy': [h[0] for h in header_stack]
                                }
                            )
                            sections.append(doc)
                    
                    # 开始新章节
                    level = len(header_match.group(1))
                    title = header_match.group(2).strip()
                    
                    self.logger.debug(f"Found header: level={level}, title='{title}'")
                    
                    # 更新标题栈：移除所有层级大于等于当前层级的标题
                    while header_stack and header_stack[-1][0] >= level:
                        header_stack.pop()
                    
                    # 添加当前标题到栈中
                    header_stack.append((level, title))
                    
                    current_section = {
                        'title': title,
                        'level': level,
                        'line_num': line_num + 1
                    }
                    current_content = []
                else:
                    # 添加到当前章节内容
                    if current_section is not None:
                        current_content.append(line)
                    elif line.strip():  
                        # 如果没有标题，创建默认章节
                        doc = Document(
                            page_content=line.strip(),
                            metadata={
                                'title': 'Introduction',
                                'level': 0,
                                'header_line': 0,
                                'type': 'section',
                                'source': 'markdown_section',
                                'full_title_path': 'Introduction',
                                'parent_title': None,
                                'parent_level': None,
                                'title_hierarchy': ['Introduction'],
                                'level_hierarchy': [0]
                            }
                        )
                        sections.append(doc)
                        self.logger.debug("Added default Introduction section for content without headers")
        else:
            self.logger.debug("No headers found, treating entire content as single section")
            # 如果没有标题，将整个内容作为一个章节
            if content.strip():
                doc = Document(
                    page_content=content.strip(),
                    metadata={
                        'title': 'Full Document',
                        'level': 0,
                        'header_line': 0,
                        'type': 'section',
                        'source': 'markdown_section',
                        'full_title_path': 'Full Document',
                        'parent_title': None,
                        'parent_level': None,
                        'title_hierarchy': ['Full Document'],
                        'level_hierarchy': [0]
                    }
                )
                sections.append(doc)
        
        # 处理最后一个章节
        if current_section is not None and current_content:
            full_title_path = ' > '.join([h[1] for h in header_stack])
            if full_title_path:
                content_text = f"{full_title_path}\n\n" + '\n'.join(current_content).strip()
            else:
                content_text = '\n'.join(current_content).strip()
                
            if content_text:
                parent_title = header_stack[-2][1] if len(header_stack) >= 2 else None
                parent_level = header_stack[-2][0] if len(header_stack) >= 2 else None
                
                doc = Document(
                    page_content=content_text,
                    metadata={
                        'title': current_section['title'],
                        'level': current_section['level'],
                        'header_line': current_section['line_num'],
                        'type': 'section',
                        'source': 'markdown_section',
                        'full_title_path': full_title_path,
                        'parent_title': parent_title,
                        'parent_level': str(parent_level),
                        'title_hierarchy': [h[1] for h in header_stack],
                        'level_hierarchy': [h[0] for h in header_stack]
                    }
                )
                sections.append(doc)
        
        self.logger.info(f"Section-based parsing complete: {len(sections)} sections extracted")
        
        # 记录每个章节的详细信息
        for i, section in enumerate(sections):
            metadata = section.metadata
            self.logger.debug(
                f"Section {i+1}: title='{metadata['title']}', "
                f"level={metadata['level']}, content_length={len(section.page_content)}, "
                f"title_path='{metadata['full_title_path']}'"
            )
        
        return sections


    def parse_with_sections(self, source: Union[str, bytes], source_type: str = "file") -> List[Document]:
        """
        按标题章节解析markdown内容的高级方法
        
        Args:
            source: 文件路径、文件内容或字节流
            source_type: "file"表示文件路径, "content"表示内容字符串, "bytes"表示字节流
            
        Returns:
            List[Document]: 按章节组织的文档列表
        """
        if source_type == "file":
            content = self.load_file(source)
        elif source_type == "content":
            content = source
        elif source_type == "bytes":
            import chardet
            detected = chardet.detect(source)
            encoding = detected['encoding']
            content = source.decode(encoding)
        else:
            raise ValueError("source_type must be 'file', 'content' or 'bytes'")
        
        # 后处理内容
        if self._markdown_clean_html:
            content = self._clean_html_tags(content)
            self.logger.debug(f"After clean_html content: \n {content}")
        if self._remove_hyperlinks:
            content = self._remove_links(content)
            self.logger.debug(f"After remove_links content: \n {content}")
        if self._remove_images:
            content = self._remove_imgs(content)
            self.logger.debug(f"After remove_imgs content: \n {content}")
        
        return self.parse_by_sections(content)

    def extract_tables(self, content: str) -> tuple[str, List[str]]:
        """提取表格内容"""
        tables = []
        working_text = content
        
        # 处理标准Markdown表格
        if "|" in content:
            # 标准带边框表格
            border_table_pattern = re.compile(
                r'''(?:\n|^)(?:\|.*?\|.*?\|.*?\n)(?:\|(?:\s*[:-]+[-| :]*\s*)\|.*?\n)(?:\|.*?\|.*?\|.*?\n)+''', 
                re.VERBOSE)
            
            # 无边框表格
            no_border_table_pattern = re.compile(
                r'''(?:\n|^)(?:\S.*?\|.*?\n)(?:(?:\s*[:-]+[-| :]*\s*).*?\n)(?:\S.*?\|.*?\n)+''', 
                re.VERBOSE)
                
            # 提取表格
            for pattern in [border_table_pattern, no_border_table_pattern]:
                matches = list(pattern.finditer(working_text))
                for match in reversed(matches):  # 反向处理以避免索引问题
                    table_content = match.group()
                    tables.append(table_content)
                    # 从原文本中移除表格
                    working_text = working_text[:match.start()] + "\n[TABLE]\n" + working_text[match.end():]
        
        # 处理HTML表格
        if "<table>" in working_text.lower():
            html_table_pattern = re.compile(
                r'''(?:\n|^)\s*(?:(?:<html[^>]*>\s*<body[^>]*>\s*<table[^>]*>.*?</table>\s*</body>\s*</html>)|(?:<body[^>]*>\s*<table[^>]*>.*?</table>\s*</body>)|(?:<table[^>]*>.*?</table>))\s*(?=\n|$)''',
                re.VERBOSE | re.DOTALL | re.IGNORECASE)
            
            matches = list(html_table_pattern.finditer(working_text))
            for match in reversed(matches):
                table_content = match.group()
                tables.append(table_content)
                # 从原文本中移除表格
                working_text = working_text[:match.start()] + "\n[HTML_TABLE]\n" + working_text[match.end():]
        
        return working_text, tables