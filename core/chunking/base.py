from typing import List, Union
from utils.logger import get_module_logger
from conf.config import RAGConfig

class BaseChunker(object):
    def __init__(self):
        """
        Initialize the chunking base class.
        """
        self.logger = get_module_logger('chunking')
        self.logger.debug("Initializing BaseChunker")
    
    def get_chunks(self, paragraphs: Union[str, List[str]], chunk_size: int = 64):
        raise NotImplementedError