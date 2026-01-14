"""
Debug script to test EPUB parsing and see what's happening.
Run this with: python debug_epub.py <path_to_epub_file>
"""
import sys
import os

if len(sys.argv) < 2:
    print("Usage: python debug_epub.py <path_to_epub_file>")
    sys.exit(1)

epub_path = sys.argv[1]

if not os.path.exists(epub_path):
    print(f"Error: File not found: {epub_path}")
    sys.exit(1)

print(f"Testing EPUB file: {epub_path}")
print("=" * 60)

try:
    from src.speed_reader.parsers.file_parser import FileParser
    
    print("\n1. Attempting to parse EPUB...")
    metadata = FileParser.parse_file(epub_path)
    
    if metadata:
        print(f"✓ Successfully parsed EPUB!")
        print(f"  - Total words: {len(metadata.words)}")
        print(f"  - Pages: {metadata.page_count}")
        print(f"  - Chapters: {len(metadata.chapter_names)}")
        print(f"  - File type: {metadata.file_type}")
        
        if metadata.chapter_names:
            print("\n  Chapters found:")
            for i, chapter in enumerate(metadata.chapter_names[:10], 1):
                print(f"    {i}. {chapter}")
            if len(metadata.chapter_names) > 10:
                print(f"    ... and {len(metadata.chapter_names) - 10} more")
        
        if metadata.words:
            print(f"\n  First 20 words: {' '.join(metadata.words[:20])}")
            print(f"  Last 20 words: {' '.join(metadata.words[-20:])}")
    else:
        print("✗ Failed to parse EPUB - returned None")
        print("\n2. Trying to inspect EPUB structure...")
        
        try:
            import ebooklib
            from ebooklib import epub
            
            book = epub.read_epub(epub_path)
            all_items = list(book.get_items())
            
            print(f"  - Total items in EPUB: {len(all_items)}")
            
            document_items = [item for item in all_items if item.get_type() == ebooklib.ITEM_DOCUMENT]
            print(f"  - Document items: {len(document_items)}")
            
            if book.spine:
                print(f"  - Spine items: {len(list(book.spine))}")
                for i, (item_id, _) in enumerate(list(book.spine)[:5], 1):
                    print(f"    {i}. {item_id}")
            
            if document_items:
                print("\n  Sample document items:")
                for i, item in enumerate(document_items[:5], 1):
                    print(f"    {i}. ID: {item.get_id()}, Type: {item.get_type()}")
                    try:
                        content = item.get_content()
                        if content:
                            print(f"       Content length: {len(content)} bytes")
                            # Try to decode
                            try:
                                text = content.decode('utf-8', errors='ignore')[:100]
                                print(f"       Preview: {text}...")
                            except:
                                print(f"       (Could not decode as UTF-8)")
                    except Exception as e:
                        print(f"       Error getting content: {e}")
        except Exception as e:
            print(f"  Error inspecting EPUB: {e}")
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
