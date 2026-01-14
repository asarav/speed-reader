"""PDF file parser."""
from typing import Optional
import PyPDF2
from ..models.document import DocumentMetadata
from .base import text_to_words


class PDFParser:
    """Parser for PDF files."""
    
    @staticmethod
    def parse(file_path: str) -> Optional[DocumentMetadata]:
        """Extract text from PDF file with page tracking."""
        words = []
        word_to_page = {}
        word_index = 0
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text()
                    if text:
                        page_words = text_to_words(text)
                        words.extend(page_words)
                        # Map all words from this page to the page number
                        for _ in page_words:
                            word_to_page[word_index] = page_num
                            word_index += 1
                
                return DocumentMetadata(
                    words=words,
                    word_to_page=word_to_page,
                    word_to_chapter={},
                    page_count=total_pages,
                    chapter_names=[],
                    file_type='pdf'
                )
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return None
