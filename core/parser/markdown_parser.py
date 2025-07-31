import re
from typing import List, Union, Optional, Dict, Tuple
from langchain_core.documents.base import Document
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from core.parser.base import BaseParser

class MarkdownParser(BaseParser):
    def __init__(self, remove_hyperlinks: bool = False, remove_images: bool = False):
        super().__init__()
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images

    def parse(self, source: Union[str, bytes], source_type: str = "file") -> List[Document]:
        """
        解析markdown内容
        
        Args:
            source: 文件路径、文件内容或字节流
            source_type: "file"表示文件路径, "content"表示内容字符串, "bytes"表示字节流
            
        Returns:
            List[Document]: 解析后的文档列表
        """
        if source_type == "file":
            # 从文件路径读取
            documents = self._parse_from_file(source)
        elif source_type == "content":
            # 从内容字符串读取
            documents = self._parse_from_content(source)
        elif source_type == "bytes":
            # 从字节流读取
            documents = self._parse_from_bytes(source)
        else:
            raise ValueError("source_type must be 'file', 'content' or 'bytes'")
            
        return documents

    def _parse_from_file(self, filepath: str) -> List[Document]:
        """从文件路径解析markdown"""
        loader = UnstructuredMarkdownLoader(filepath, mode="elements")
        documents = loader.load()
        return self._post_process_documents(documents)

    def _parse_from_content(self, content: str) -> List[Document]:
        """从内容字符串解析markdown"""
        # 创建临时文件来使用UnstructuredMarkdownLoader
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            
        try:
            loader = UnstructuredMarkdownLoader(tmp_file_path, mode="elements")
            documents = loader.load()
            return self._post_process_documents(documents)
        finally:
            os.unlink(tmp_file_path)

    def _parse_from_bytes(self, content: bytes) -> List[Document]:
        """从字节流解析markdown"""
        # 检测编码
        import chardet
        detected = chardet.detect(content)
        encoding = detected['encoding']
        
        # 解码为字符串
        text_content = content.decode(encoding)
        return self._parse_from_content(text_content)

    def _post_process_documents(self, documents: List[Document]) -> List[Document]:
        """对解析后的文档进行后处理"""
        if self._remove_hyperlinks:
            documents = [Document(page_content=self._remove_links(doc.page_content), metadata=doc.metadata) 
                        for doc in documents]
        
        if self._remove_images:
            documents = [Document(page_content=self._remove_imgs(doc.page_content), metadata=doc.metadata) 
                        for doc in documents]
                        
        return documents

    def _remove_links(self, content: str) -> str:
        """移除超链接"""
        pattern = r"\[(.*?)\]\((.*?)\)"
        return re.sub(pattern, r"\1", content)

    def _remove_imgs(self, content: str) -> str:
        """移除图片"""
        pattern = r"!\[(.*?)\]\((.*?)\)"
        return re.sub(pattern, r"\1", content)

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
        lines = content.split('\n')
        sections = []
        current_section = None
        current_content = []
        
        # 用于跟踪标题层级的栈
        header_stack = []  # 存储 (level, title) 元组
        
        # 如果文档存在标题，则进行章节解析
        if re.search(r'^#{1,6}\s+.*', content, flags=re.MULTILINE):
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
                        # header_stack = [(0, 'Introduction')]
                        # current_section = {
                        #     'title': 'Introduction',
                        #     'level': 0,
                        #     'line_num': line_num + 1
                        # }
                        # current_content = [line]
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
                
        
        # 处理最后一个章节
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
        
        # 如果没有找到任何标题，将整个内容作为一个章节
        if not sections and content.strip():
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
        
        # print(sections)
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
        if self._remove_hyperlinks:
            content = self._remove_links(content)
        if self._remove_images:
            content = self._remove_imgs(content)
        
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