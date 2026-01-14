"""Plain text parser."""
from typing import Optional
from ..models.document import DocumentMetadata
from .base import text_to_words


class TextParser:
    """Parser for plain text files."""
    
    @staticmethod
    def parse_file(file_path: str) -> Optional[DocumentMetadata]:
        """Extract text from plain text file."""
        words = []
        word_to_page = {}
        word_index = 0
        page_num = 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                words = text_to_words(content)
                
                # Approximate pages: ~250 words per page
                words_per_page = 250
                for i in range(len(words)):
                    word_to_page[i] = page_num
                    if (i + 1) % words_per_page == 0:
                        page_num += 1
            
            return DocumentMetadata(
                words=words,
                word_to_page=word_to_page,
                word_to_chapter={},
                page_count=page_num,
                chapter_names=[],
                file_type='txt'
            )
        except Exception as e:
            print(f"Error parsing TXT: {e}")
            return None
    
    @staticmethod
    def parse_text(text: str) -> Optional[DocumentMetadata]:
        """
        Parse plain text string into words with metadata.
        Useful for pasted text.
        """
        words = text_to_words(text)
        word_to_page = {}
        page_num = 1
        words_per_page = 250
        
        for i in range(len(words)):
            word_to_page[i] = page_num
            if (i + 1) % words_per_page == 0:
                page_num += 1
        
        return DocumentMetadata(
            words=words,
            word_to_page=word_to_page,
            word_to_chapter={},
            page_count=page_num,
            chapter_names=[],
            file_type='text'
        )
