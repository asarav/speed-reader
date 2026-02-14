"""
Part-of-speech tagging for color coding in the speed reader.
Uses NLTK Penn Treebank tags; maps pronouns, nouns, and verbs to colors and optional styling.
"""
import os
import sys
from typing import List, Optional, Tuple


def _ensure_nltk_data_path() -> None:
    """Ensure NLTK looks in the Windows AppData Roaming folder where the downloader puts data."""
    try:
        import nltk
        # Where the downloader puts data on Windows when you run: python -m nltk.downloader ...
        roaming = os.environ.get("APPDATA")
        if roaming:
            nltk_data_roaming = os.path.join(roaming, "nltk_data")
            if os.path.isdir(nltk_data_roaming) and nltk_data_roaming not in nltk.data.path:
                nltk.data.path.insert(0, nltk_data_roaming)
    except Exception:
        pass


# Penn Treebank tags we care about
PRONOUN_TAGS = frozenset({"PRP", "PRP$", "WP", "WP$"})  # I, my, who, whose
NOUN_TAGS = frozenset({"NN", "NNS", "NNP", "NNPS"})  # noun, nouns, proper noun, ...
VERB_TAGS = frozenset({"VB", "VBD", "VBG", "VBN", "VBP", "VBZ"})  # base, past, gerund, ...

# Styling: (color_hex, bold, italic) – vivid colors that pop on dark backgrounds
STYLE_PRONOUN = ("#f4a261", False, True)   # Warm orange, italic (matches tests)
STYLE_NOUN = ("#7fc8f8", True, False)      # Soft cyan, bold (matches tests)
STYLE_VERB = ("#7ae582", False, True)      # Soft green, italic (matches tests)
STYLE_DEFAULT = ("#ffffff", False, False)  # White, normal (main/fullscreen default)


def ensure_nltk_pos_data(quiet: bool = True) -> bool:
    """
    Ensure NLTK POS tagger data is available, downloading if necessary.
    NLTK 3.9+ uses averaged_perceptron_tagger_eng; older versions use averaged_perceptron_tagger.
    """
    try:
        import nltk
        _ensure_nltk_data_path()
        # NLTK 3.9+ looks for taggers/averaged_perceptron_tagger_eng (language-specific)
        for resource in ("averaged_perceptron_tagger_eng", "averaged_perceptron_tagger"):
            try:
                nltk.data.find(f"taggers/{resource}")
            except LookupError:
                try:
                    nltk.data.find(resource)
                except LookupError:
                    if not quiet:
                        print(f"Downloading NLTK POS tagger data ({resource})...")
                    nltk.download(resource, quiet=quiet)
        return True
    except Exception:
        return False


def tag_words(words: List[str], ensure_download: bool = False) -> Optional[List[str]]:
    """
    Tag a list of words with Penn Treebank part-of-speech tags.
    Returns a list of tag strings (one per word), or None if tagging is unavailable.
    If ensure_download is True, calls ensure_nltk_pos_data(quiet=False) before tagging
    so the user sees the download in the console if data is missing.
    """
    if ensure_download:
        ensure_nltk_pos_data(quiet=False)
    try:
        import nltk
        _ensure_nltk_data_path()
        # Ensure both resources exist (NLTK 3.9+ needs _eng)
        for resource in ("averaged_perceptron_tagger_eng", "averaged_perceptron_tagger"):
            try:
                nltk.data.find(f"taggers/{resource}")
            except LookupError:
                try:
                    nltk.data.find(resource)
                except LookupError:
                    nltk.download(resource, quiet=not ensure_download)
        from nltk import pos_tag
        tags = pos_tag(words)
        return [t[1] for t in tags]
    except Exception as e:
        # So you can see why tagging failed when running from terminal (e.g. python run.py)
        print("[POS tagger] Part-of-speech tagging failed:", e, file=sys.stderr)
        if ensure_download:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return None


def get_style_for_tag(tag: str) -> Tuple[str, bool, bool]:
    """
    Return (color_hex, bold, italic) for a Penn Treebank tag.
    Used for both main reading display and fullscreen.
    """
    if tag in PRONOUN_TAGS:
        return STYLE_PRONOUN
    if tag in NOUN_TAGS:
        return STYLE_NOUN
    if tag in VERB_TAGS:
        return STYLE_VERB
    return STYLE_DEFAULT


