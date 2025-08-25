from abc import ABC, abstractmethod
from typing import List, Dict
from core.talent import Talent

class SourcePlugin(ABC):
    """Base class for all data source plugins"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.name = self.__class__.__name__.replace('Plugin', '')
    
    @abstractmethod
    def search(self, query_params: Dict) -> List[Talent]:
        """Search and return normalized Talent objects"""
        pass
    
    @abstractmethod
    def is_au_connected(self, raw_data: Dict) -> float:
        """Return AU connection strength (0-1)"""
        pass
    
    def get_platform_score(self, talent: Talent) -> float:
        """Platform-specific scoring logic"""
        return 0.0