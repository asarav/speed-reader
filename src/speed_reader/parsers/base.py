"""Base parser class and utilities."""
import re
from typing import List


def text_to_words(text: str) -> List[str]:
    """
    Convert text string to a list of words.
    Preserves punctuation and handles whitespace properly.
    """
    # Split on whitespace and keep punctuation attached to words
    words = re.findall(r'\S+', text)
    return words
