"""EPUB file parser."""
from typing import Optional, List
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from ..models.document import DocumentMetadata
from .base import text_to_words


class EPUBParser:
    """Parser for EPUB files."""
    
    @staticmethod
    def parse(file_path: str) -> Optional[DocumentMetadata]:
        """Extract text from EPUB file with chapter tracking."""
        words = []
        word_to_chapter = {}
        word_to_page = {}
        chapter_names = []
        word_index = 0
        current_chapter = "Chapter 1"
        page_num = 1
        
        try:
            # Try different options for reading EPUB
            try:
                book = epub.read_epub(file_path, options={'ignore_ncx': True})
            except Exception:
                # Fallback: try without options
                book = epub.read_epub(file_path)
            
            # Get all items from the book
            all_items = list(book.get_items())
            
            if not all_items:
                print("Warning: No items found in EPUB file")
                return None
            
            # Collect items to process
            items_to_process = []
            
            # First, try spine items (reading order)
            if book.spine:
                for item_id, _ in book.spine:
                    item = book.get_item_with_id(item_id)
                    if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
                        items_to_process.append(item)
            
            # If no spine items, get all document items
            if not items_to_process:
                items_to_process = [
                    item for item in all_items 
                    if item.get_type() == ebooklib.ITEM_DOCUMENT
                ]
            
            # If still nothing, try all items
            if not items_to_process:
                items_to_process = all_items
            
            if not items_to_process:
                print("Warning: No document items found to process")
                return None
            
            chapter_num = 1
            processed_count = 0
            
            for item in items_to_process:
                # Skip non-document items
                if item.get_type() != ebooklib.ITEM_DOCUMENT:
                    continue
                
                try:
                    # Get content
                    content = item.get_content()
                    if not content:
                        continue
                    
                    # Try to decode content
                    text_content = None
                    
                    # Try different decoding methods
                    for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                        try:
                            text_content = content.decode(encoding, errors='ignore')
                            break
                        except (UnicodeDecodeError, AttributeError):
                            continue
                    
                    if not text_content:
                        # If content is already a string
                        if isinstance(content, str):
                            text_content = content
                        else:
                            # Last resort: try utf-8 with errors='ignore'
                            try:
                                text_content = content.decode('utf-8', errors='ignore')
                            except Exception:
                                continue
                    
                    if not text_content or not text_content.strip():
                        continue
                    
                    # Try to parse as HTML/XML
                    soup = None
                    try:
                        soup = BeautifulSoup(text_content, 'html.parser')
                    except Exception:
                        try:
                            soup = BeautifulSoup(text_content, 'lxml')
                        except Exception:
                            # If HTML parsing fails, try to extract text using regex
                            # Remove HTML tags
                            text_only = re.sub(r'<[^>]+>', '', text_content)
                            # Clean up whitespace
                            text_only = re.sub(r'\s+', ' ', text_only).strip()
                            
                            if text_only:
                                page_words = text_to_words(text_only)
                                if page_words:
                                    words.extend(page_words)
                                    for _ in page_words:
                                        word_to_chapter[word_index] = current_chapter
                                        word_to_page[word_index] = page_num
                                        word_index += 1
                                        if word_index % 250 == 0:
                                            page_num += 1
                                    processed_count += 1
                            continue
                    
                    if soup is None:
                        continue
                    
                    # Try to extract chapter title from headings
                    chapter_title = None
                    for tag in ['h1', 'h2', 'h3', 'h4', 'title']:
                        heading = soup.find(tag)
                        if heading:
                            heading_text = heading.get_text().strip()
                            if heading_text and len(heading_text) > 0:
                                chapter_title = heading_text
                                # Limit chapter title length
                                if len(chapter_title) > 100:
                                    chapter_title = chapter_title[:100] + "..."
                                break
                    
                    # If no chapter title found, use default
                    if not chapter_title:
                        chapter_title = f"Chapter {chapter_num}"
                    
                    # Add to chapter names if new
                    if chapter_title not in chapter_names:
                        chapter_names.append(chapter_title)
                    current_chapter = chapter_title
                    
                    # Extract all text from the soup
                    text = soup.get_text(separator=' ', strip=True)
                    
                    # Also try to get text from body tag specifically
                    if not text or len(text.strip()) < 10:
                        body = soup.find('body')
                        if body:
                            text = body.get_text(separator=' ', strip=True)
                    
                    # Clean up the text
                    if text:
                        # Remove excessive whitespace
                        text = re.sub(r'\s+', ' ', text).strip()
                        
                        if text and len(text) > 0:
                            page_words = text_to_words(text)
                            
                            if page_words:
                                words.extend(page_words)
                                
                                # Map words to chapter and page
                                for _ in page_words:
                                    word_to_chapter[word_index] = current_chapter
                                    word_to_page[word_index] = page_num
                                    word_index += 1
                                    # Increment page every ~250 words
                                    if word_index % 250 == 0:
                                        page_num += 1
                                
                                processed_count += 1
                                chapter_num += 1
                
                except Exception as e:
                    # Continue processing other items even if one fails
                    print(f"Warning: Error processing EPUB item {item.get_id()}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Check if we extracted any words
            if not words:
                print(f"Warning: No words extracted from EPUB. Processed {processed_count} items.")
                return None
            
            return DocumentMetadata(
                words=words,
                word_to_page=word_to_page,
                word_to_chapter=word_to_chapter,
                page_count=max(page_num, 1),
                chapter_names=chapter_names if chapter_names else ["Chapter 1"],
                file_type='epub'
            )
            
        except Exception as e:
            print(f"Error parsing EPUB: {e}")
            import traceback
            traceback.print_exc()
            return None
