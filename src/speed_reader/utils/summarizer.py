"""
Summarization of session text: optional abstractive (OpenAI API) or extractive (sumy/NLTK).
Returns (summary_text, is_abstractive) so the UI can label appropriately.
"""
import os
import re
import json
import urllib.request
import urllib.error
from typing import Optional, Tuple

# Minimum characters needed to attempt a summary (~10–15 words)
MIN_CHARS_FOR_SUMMARY = 50

# Truncate text sent to API to stay within token limits (~4 chars per token, 8k context)
MAX_CHARS_FOR_API = 12000


def summarize_text(text: str, max_sentences: int = 8, use_api: bool = False) -> Optional[Tuple[str, bool]]:
    """
    Produce a short summary (1–2 paragraphs).
    Returns (summary_text, is_abstractive) or None if text too short / all methods fail.
    is_abstractive True = condensed summary from API; False = key excerpts from the text.
    """
    text = (text or "").strip()
    if len(text) < MIN_CHARS_FOR_SUMMARY:
        return None
    # Abstractive summary (API) only used when explicitly allowed via `use_api` or
    # when the environment variable `SUMMARIZER_USE_API` is set (for backward compatibility).
    # This avoids sending text to external LLMs by default.
    if not use_api:
        use_api = bool(os.environ.get("SUMMARIZER_USE_API"))
    if use_api:
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            result = _abstractive_summary(text, api_key)
            if result:
                return (result, True)
    # Extractive: try sumy LSA (picks important sentences), then NLTK spread.
    result = _sumy_summary(text, max_sentences)
    if result:
        return (result, False)
    result = _fallback_summary(text, max_sentences)
    if result:
        return (result, False)
    # Sentence-ranker (regex-based) - scores sentences by term frequency
    result = _sentence_rank_summary(text, max_sentences)
    if result:
        return (result, False)
    result = _last_resort_summary(text, max_sentences)
    return (result, False) if result else None


def _abstractive_summary(text: str, api_key: str) -> Optional[str]:
    """Call OpenAI API for a condensed 1–2 paragraph summary (abstractive)."""
    if len(text) > MAX_CHARS_FOR_API:
        text = text[:MAX_CHARS_FOR_API] + "..."
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes text in 1–2 short paragraphs. "
                "Capture the main points, plot points if it's a story, and key ideas. Be concise."
            },
            {
                "role": "user",
                "content": "Summarize the following text in 1–2 paragraphs:\n\n" + text
            }
        ],
        "max_tokens": 400,
    }
    try:
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        choice = data.get("choices")
        if choice and len(choice) > 0:
            content = choice[0].get("message", {}).get("content", "").strip()
            if content:
                return content
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, KeyError, OSError):
        pass
    return None


def _sumy_summary(text: str, max_sentences: int) -> Optional[str]:
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer
        from sumy.nlp.stemmers import Stemmer
        from sumy.utils import get_stop_words
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        if not parser.document.sentences:
            return None
        stemmer = Stemmer("english")
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words("english")
        count = min(max_sentences, len(parser.document.sentences))
        sentences = summarizer(parser.document, count)
        if not sentences:
            return None
        summary_sentences = [str(s) for s in sentences]
        return _sentences_to_paragraphs(summary_sentences)
    except Exception:
        return None


def _fallback_summary(text: str, max_sentences: int) -> Optional[str]:
    """Fallback: pick first, last, and spread sentences using NLTK."""
    try:
        import nltk
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt", quiet=True)
        from nltk import sent_tokenize
        sentences = sent_tokenize(text)
        if not sentences:
            return None
        # Allow a single sentence (was: required 2, so long text with no periods returned None)
        n = min(max_sentences, len(sentences))
        if n <= 3:
            selected = sentences[:n]
        else:
            seen = {0}
            selected = [sentences[0]]
            step = (len(sentences) - 1) / (n - 1) if n > 1 else 0
            for i in range(1, n - 1):
                idx = min(int(round(i * step)), len(sentences) - 1)
                if idx not in seen:
                    seen.add(idx)
                    selected.append(sentences[idx])
            if len(sentences) - 1 not in seen:
                selected.append(sentences[-1])
        return _sentences_to_paragraphs(selected[:max_sentences])
    except Exception:
        return None


def _last_resort_summary(text: str, max_sentences: int) -> str:
    """When sumy and NLTK fail, split on .?! and take first few fragments (or first N chars)."""
    fragments = re.split(r'(?<=[.!?])\s+', text)
    fragments = [f.strip() for f in fragments if f.strip()]
    if fragments:
        selected = fragments[:max_sentences]
        return _sentences_to_paragraphs(selected)
    # No sentence endings: use first ~400 chars as a single paragraph
    return text[:400].strip() + ("..." if len(text) > 400 else "")


def _sentences_to_paragraphs(sentences: list) -> str:
    """Format a list of sentences into 1–2 paragraphs."""
    if not sentences:
        return ""
    mid = (len(sentences) + 1) // 2
    p1 = " ".join(sentences[:mid])
    p2 = " ".join(sentences[mid:]) if mid < len(sentences) else ""
    if p2:
        return p1 + "\n\n" + p2
    return p1


def _chunked_extractive_summary(text: str, max_sentences: int) -> Optional[str]:
    """Chunk text into fixed-size word windows and pick top-scoring chunks by word frequency.

    This works well when the input has no sentence punctuation (e.g., session word lists).
    """
    try:
        # Normalize whitespace and tokenize words
        norm = re.sub(r"\s+", " ", (text or "").strip())
        words = re.findall(r"[A-Za-z0-9']+", norm)
        if not words:
            return None
        # Try to get stopwords from NLTK, otherwise use a small fallback set
        stopwords = None
        try:
            from nltk.corpus import stopwords as _sw
            stopwords = set(w.lower() for w in _sw.words('english'))
        except Exception:
            stopwords = {
                'the', 'and', 'is', 'in', 'it', 'of', 'to', 'a', 'that', 'i', 'you', 'for', 'on', 'with', 'as', 'was',
                'are', 'this', 'be', 'or', 'by', 'an', 'at', 'from', 'not', 'have', 'has'
            }
        # Build frequency map (simple term frequency)
        freqs = {}
        for w in words:
            wl = w.lower()
            if wl in stopwords:
                continue
            freqs[wl] = freqs.get(wl, 0) + 1

        # Define chunk size (words per chunk)
        chunk_size = max(20, int(len(words) / max(1, max_sentences)))
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i : i + chunk_size]
            if not chunk_words:
                continue
            # Score chunk by sum of term frequencies
            score = sum(freqs.get(w.lower(), 0) for w in chunk_words)
            chunks.append((i, score, chunk_words))
        if not chunks:
            return None
        # Pick top N chunks by score
        n = min(max_sentences, len(chunks))
        chunks_sorted = sorted(chunks, key=lambda t: t[1], reverse=True)[:n]
        # Restore original order for readability
        chunks_sorted.sort(key=lambda t: t[0])
        selected_texts = []
        # For each selected chunk, take a short, readable snippet (centered, limited length)
        for start_idx, score, chunk_words in chunks_sorted:
            max_snippet_words = min(40, len(chunk_words))
            # pick centered window within chunk for better context
            mid = len(chunk_words) // 2
            half = max_snippet_words // 2
            s = max(0, mid - half)
            e = min(len(chunk_words), s + max_snippet_words)
            snippet_words = chunk_words[s:e]
            snippet = " ".join(snippet_words).strip()
            if not snippet:
                continue
            # Ensure snippet ends with terminal punctuation for readability
            if not re.search(r"[\.\!\?]$", snippet):
                snippet = snippet.rstrip() + "..."
            selected_texts.append(snippet)
        if not selected_texts:
            return None
        return _sentences_to_paragraphs(selected_texts)
    except Exception:
        return None


def _sentence_rank_summary(text: str, max_sentences: int) -> Optional[str]:
    """Split text into sentences with a regex, score them by TF (ignoring stopwords),
    and return the top-ranked sentences in original order.
    This is a lightweight extractive method that doesn't rely on NLTK or sumy.
    """
    try:
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s and s.strip()]
        if not sentences:
            return None

        # Tokenize words and build term frequencies (ignore short tokens)
        words = re.findall(r"[A-Za-z0-9']+", text)
        if not words:
            return None

        stopwords = None
        try:
            from nltk.corpus import stopwords as _sw
            stopwords = set(w.lower() for w in _sw.words('english'))
        except Exception:
            stopwords = {
                'the', 'and', 'is', 'in', 'it', 'of', 'to', 'a', 'that', 'i', 'you', 'for', 'on', 'with', 'as', 'was',
                'are', 'this', 'be', 'or', 'by', 'an', 'at', 'from', 'not', 'have', 'has'
            }

        freqs = {}
        for w in words:
            wl = w.lower()
            if wl in stopwords:
                continue
            freqs[wl] = freqs.get(wl, 0) + 1

        # Score each sentence by sum of term frequencies of its words
        scored = []
        for idx, s in enumerate(sentences):
            toks = re.findall(r"[A-Za-z0-9']+", s)
            score = 0
            for t in toks:
                tl = t.lower()
                score += freqs.get(tl, 0)
            scored.append((idx, score, s))

        # Pick top N by score, then sort by original position
        n = min(max_sentences, len(scored))
        top = sorted(scored, key=lambda t: t[1], reverse=True)[:n]
        top.sort(key=lambda t: t[0])
        selected = [t[2].rstrip() for t in top]
        return _sentences_to_paragraphs(selected)
    except Exception:
        return None
