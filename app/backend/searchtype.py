from enum import Enum

class SearchType(str, Enum):
    keyword = "keyword"
    semantic = "semantic"
    hybrid = "hybrid"