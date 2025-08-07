"""
使用pymupdf进行简单pdf解析
"""
import re
import os
from io import BytesIO
from typing import List, Union
import fitz
from tqdm import tqdm

from langchain_core.documents.base import Document
from core.parser.base import BaseParser


class PdfSimpleParser(BaseParser):
    """
    PdfSimpleParser is a parser class for extracting text from PDF files using PyMuPDF library.
    Inherits from BaseParser to provide standardized PDF parsing functionality.
    """

    supported_extensions = [".pdf"]

    def __init__(self, max_chunk_size: int = 1000, **kwargs):
        """
        Initializes the PdfSimpleParser object.
        
        Args:
            max_chunk_size: Maximum size for text chunks (default: 1000)
            **kwargs: Additional keyword arguments
        """
        super().__init__(max_chunk_size=max_chunk_size, **kwargs)
        self.max_chunk_size = max_chunk_size
        self.logger.info(f"Initialized PdfSimpleParser with max_chunk_size: {max_chunk_size}")

    def parse(self, source: Union[str, bytes], source_type: str = "file") -> List[Document]:
        """
        Parses PDF content and returns it as Document objects.
        
        Args:
            source: File path, file content, or bytes
            source_type: "file" for file path, "content" for content string, "bytes" for bytes
            
        Returns:
            List[Document]: List of parsed documents
        """
        self.logger.debug(f"Starting PDF parsing with source_type: {source_type}")
        
        try:
            if source_type == "file":
                documents = self._parse_pdf_file(source)
            elif source_type == "content":
                documents = self._parse_pdf_content(source)
            elif source_type == "bytes":
                documents = self._parse_pdf_bytes(source)
            else:
                raise ValueError(f"Unsupported source_type: {source_type}")
            
            self.logger.info(f"Successfully parsed PDF into {len(documents)} documents")
            return documents
            
        except Exception as e:
            self.logger.error(f"Failed to parse PDF: {str(e)}")
            raise

    def _parse_pdf_file(self, file_path: str) -> List[Document]:
        """Parse PDF from file path."""
        self.logger.debug(f"Parsing PDF from file: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
            
        doc = fitz.open(file_path)
        return self._extract_content_from_doc(doc, {"source": file_path})

    def _parse_pdf_content(self, content: str) -> List[Document]:
        """Parse PDF from content string."""
        self.logger.debug("Parsing PDF from content string")
        
        # Convert string to bytes for fitz
        content_bytes = content.encode('utf-8') if isinstance(content, str) else content
        doc = fitz.open(stream=BytesIO(content_bytes), filetype="pdf")
        return self._extract_content_from_doc(doc, {"source": "content_string"})

    def _parse_pdf_bytes(self, content: bytes) -> List[Document]:
        """Parse PDF from bytes."""
        self.logger.debug(f"Parsing PDF from bytes (size: {len(content)} bytes)")
        
        doc = fitz.open(stream=BytesIO(content), filetype="pdf")
        return self._extract_content_from_doc(doc, {"source": "bytes"})

    def _extract_content_from_doc(self, doc: fitz.Document, metadata: dict) -> List[Document]:
        """Extract text and tables from fitz document."""
        documents = []
        final_texts = []
        final_tables = []
        
        self.logger.debug(f"Processing {len(doc)} pages")
        
        for page_num, page in enumerate(tqdm(doc, total=len(doc), desc="Processing PDF pages")):
            # Extract tables
            tables = page.find_tables()
            tables = list(tables)
            
            for table_idx, tab in enumerate(tables):
                try:
                    tab_data = tab.extract()
                    tab_data = list(map(lambda x: [str(t) for t in x], tab_data))
                    tab_data = list(map("||".join, tab_data))
                    tab_text = "\n".join(tab_data)
                    final_tables.append(tab_text)
                    
                    # Create document for each table
                    table_metadata = metadata.copy()
                    table_metadata.update({
                        "page": page_num + 1,
                        "type": "table",
                        "table_index": table_idx
                    })
                    documents.append(Document(page_content=tab_text, metadata=table_metadata))
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract table {table_idx} from page {page_num + 1}: {str(e)}")
            
            # Extract text
            try:
                text = page.get_text()
                text = re.sub(r"\n+", " ", text).strip()
                
                if text.strip():
                    final_texts.append(text)
                    
                    # Create document for page text
                    text_metadata = metadata.copy()
                    text_metadata.update({
                        "page": page_num + 1,
                        "type": "text"
                    })
                    documents.append(Document(page_content=text, metadata=text_metadata))
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
        
        # Create combined document if no individual documents were created
        if not documents:
            combined_content = "\n\n".join(final_texts + final_tables)
            if combined_content.strip():
                combined_metadata = metadata.copy()
                combined_metadata.update({"type": "combined"})
                documents.append(Document(page_content=combined_content, metadata=combined_metadata))
                self.logger.debug("Created combined document from all content")
        
        doc.close()
        return documents