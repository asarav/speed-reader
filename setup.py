"""Setup script for Speed Reader."""
from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements with fallback for isolated build environments
requirements = [
    "PyQt6>=6.6.0",
    "PyPDF2>=3.0.0",
    "ebooklib>=0.18",
    "python-docx>=1.1.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=4.9.0",
    "pyttsx3>=2.90",
    "nltk>=3.8.0",
    "sumy>=0.11.0",
]

# Try to read from requirements.txt if it exists (for development builds)
if os.path.exists("requirements.txt"):
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except (IOError, OSError):
        pass  # Use the fallback list if reading fails

setup(
    name="speed-reader",
    version="1.0.0",
    author="Speed Reader Team",
    description="A cross-platform speed reading application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/speed-reader",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "speed-reader=speed_reader.main:main",
        ],
    },
)
