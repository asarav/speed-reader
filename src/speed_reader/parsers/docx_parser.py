"""Word document parser."""
from typing import Optional
from docx import Document
from ..models.document import DocumentMetadata
from .base import text_to_words


class DOCXParser:
    """Parser for Word documents."""
    
    @staticmethod
    def parse(file_path: str) -> Optional[DocumentMetadata]:
        """Extract text from Word document."""
        words = []
        word_to_page = {}
        word_index = 0
        page_num = 1
        
        try:
            doc = Document(file_path)
            # Approximate pages: ~250 words per page
            words_per_page = 250
            
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    para_words = text_to_words(paragraph.text)
                    words.extend(para_words)
                    for _ in para_words:
                        word_to_page[word_index] = page_num
                        word_index += 1
                        if word_index % words_per_page == 0:
                            page_num += 1
            
            return DocumentMetadata(
                words=words,
                word_to_page=word_to_page,
                word_to_chapter={},
                page_count=page_num,
                chapter_names=[],
                file_type='docx'
            )
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return None
