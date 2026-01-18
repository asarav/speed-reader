"""
File parser module for extracting text from various file formats.
Supports: PDF, EPUB, Word documents (.docx), and plain text files.
Enhanced with page numbers, chapters, and metadata tracking.
"""
import os
from typing import List, Optional
from ..models.document import DocumentMetadata
from .pdf_parser import PDFParser
from .epub_parser import EPUBParser
from .docx_parser import DOCXParser
from .text_parser import TextParser


class FileParser:
    """Parser for extracting text from various file formats with metadata."""
    
    @staticmethod
    def parse_file(file_path: str) -> Optional[DocumentMetadata]:
        """
        Parse a file and return words with metadata.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            DocumentMetadata object with words and metadata, or None if parsing fails
        """
        if not os.path.exists(file_path):
            return None
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return PDFParser.parse(file_path)
        elif file_ext == '.epub':
            return EPUBParser.parse(file_path)
        elif file_ext in ['.docx', '.doc']:
            return DOCXParser.parse(file_path)
        elif file_ext == '.txt':
            return TextParser.parse_file(file_path)
        else:
            return None
    
    @staticmethod
    def parse_text(text: str) -> Optional[DocumentMetadata]:
        """
        Parse plain text string into words with metadata.
        Useful for pasted text.
        """
        return TextParser.parse_text(text)
