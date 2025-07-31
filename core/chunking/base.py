from typing import List, Union

class BaseChunker(object):
    def __init__(self):
        pass
    def get_chunks(self, paragraphs: Union[str, List[str]], chunk_size: int = 64):
        raise NotImplementedError