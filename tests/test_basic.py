"""
Basic tests for Speed Reader application.
Run with: python tests/test_basic.py
"""
import sys
import os
import unittest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from speed_reader.utils.file_history import FileHistory
from speed_reader.models.document import DocumentMetadata
from speed_reader.parsers.file_parser import FileParser


class TestSpeedReader(unittest.TestCase):
    
    def test_file_history_initialization(self):
        """Test that FileHistory initializes correctly."""
        history = FileHistory()
        self.assertEqual(history.max_items, 10)
        self.assertGreaterEqual(len(history.get_history()), 0)

    def test_speed_persistence(self):
        """Test that speed preferences are saved and loaded."""
        history = FileHistory()

        # Save a speed
        test_speed = 350
        history.save_speed(test_speed)

        # Load the speed
        loaded_speed = history.get_speed()
        self.assertEqual(loaded_speed, test_speed)

    def test_document_creation(self):
        """Test that DocumentMetadata can be created."""
        words = ["Hello", "world", "this", "is", "a", "test"]
        word_to_page = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1}
        word_to_chapter = {0: "Chapter 1", 1: "Chapter 1", 2: "Chapter 1", 3: "Chapter 1", 4: "Chapter 1", 5: "Chapter 1"}
        chapter_names = ["Chapter 1"]

        metadata = DocumentMetadata(
            words=words,
            word_to_page=word_to_page,
            word_to_chapter=word_to_chapter,
            page_count=1,
            chapter_names=chapter_names,
            file_type="txt"
        )

        self.assertEqual(len(metadata.words), 6)
        self.assertEqual(metadata.words[0], "Hello")
        self.assertEqual(metadata.words[-1], "test")
        self.assertEqual(metadata.page_count, 1)
        self.assertEqual(metadata.file_type, "txt")

    def test_file_parser_text(self):
        """Test parsing a simple text file."""
        # Create a temporary text file
        test_content = "This is a test file.\nWith multiple lines.\nAnd some words."
        temp_file = "test_temp.txt"
        with open(temp_file, 'w') as f:
            f.write(test_content)
        
        try:
            parser = FileParser()
            metadata = parser.parse_file(temp_file)
            
            self.assertIsNotNone(metadata)
            self.assertGreater(len(metadata.words), 0)
            self.assertEqual(metadata.file_type, "txt")
            self.assertEqual(metadata.page_count, 1)  # Text files have 1 page
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_file_history_recent_files(self):
        """Test adding and retrieving recent files."""
        history = FileHistory()
        initial_count = len(history.get_history())
        
        # Create temporary files
        temp_file1 = "test_temp1.txt"
        temp_file2 = "test_temp2.txt"
        with open(temp_file1, 'w') as f:
            f.write("test")
        with open(temp_file2, 'w') as f:
            f.write("test")
        
        try:
            # Add some files
            history.add_file(temp_file1)
            history.add_file(temp_file2)
            history.add_file(temp_file1)  # Duplicate
            
            recent = history.get_history()
            self.assertLessEqual(len(recent), 10)  # Max items
            self.assertGreaterEqual(len(recent), initial_count + 1)  # At least one added
            # Check that our files are in the list
            self.assertIn(temp_file1, recent)
            self.assertIn(temp_file2, recent)
        finally:
            # Clean up
            if os.path.exists(temp_file1):
                os.remove(temp_file1)
            if os.path.exists(temp_file2):
                os.remove(temp_file2)

    def test_document_metadata_validation(self):
        """Test DocumentMetadata validation."""
        # Test with empty words
        try:
            metadata = DocumentMetadata(
                words=[],
                word_to_page={},
                word_to_chapter={},
                page_count=0,
                chapter_names=[],
                file_type="txt"
            )
            self.assertEqual(len(metadata.words), 0)
        except Exception:
            pass  # Expected for empty words
        
        # Test with valid data
        words = ["test"]
        metadata = DocumentMetadata(
            words=words,
            word_to_page={0: 1},
            word_to_chapter={0: "Chapter 1"},
            page_count=1,
            chapter_names=["Chapter 1"],
            file_type="txt"
        )
        self.assertEqual(metadata.words, words)


if __name__ == "__main__":
    print("Running basic tests...")
    unittest.main()