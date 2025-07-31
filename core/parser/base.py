
from utils.logger import get_module_logger

class BaseParser:
    def __init__(self):
        self.logger = get_module_logger("parser")