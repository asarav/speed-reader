"""Document metadata model."""
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class DocumentMetadata:
    """Metadata about the parsed document."""
    words: List[str]
    word_to_page: Dict[int, int]  # word_index -> page_number
    word_to_chapter: Dict[int, str]  # word_index -> chapter_name
    page_count: int
    chapter_names: List[str]
    file_type: str  # 'pdf', 'epub', 'docx', 'txt', 'text'
