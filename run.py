"""
Convenience script to run Speed Reader from the project root.
Run from a terminal with the same Python where you installed dependencies:
  python run.py
"""
import sys
import os

# Add project root so "src" package is importable
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

if __name__ == "__main__":
    # Use the same Python that has nltk (e.g. python run.py in terminal).
    # If you see "NLTK not found" below, run:  python -m pip install nltk
    # using this Python:  {sys.executable}
    try:
        import nltk
    except ImportError:
        print("NLTK is not installed for this Python.", file=sys.stderr)
        print(f"This run is using: {sys.executable}", file=sys.stderr)
        print("Install NLTK with:  python -m pip install nltk", file=sys.stderr)
        print("Then:  python -m nltk.downloader averaged_perceptron_tagger", file=sys.stderr)
        sys.exit(1)

    from src.speed_reader.utils.pos_tagger import ensure_nltk_pos_data
    ensure_nltk_pos_data(quiet=False)
    from src.speed_reader.main import main
    main()
