"""Setup script for Exceli-Mermaid package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="excelimermaid",
    version="0.1.0",
    description="Offline Python engine to render Mermaid flowcharts with Excalidraw-style hand-drawn aesthetics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/excelimermaid",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "excelimermaid": [
            "fonts/*.ttf",
            "fonts/*.woff",
            "fonts/*.woff2",
        ],
    },
    include_package_data=True,
    install_requires=[
        "pyparsing>=3.1.0",
        "networkx>=3.2",
        "svgwrite>=1.4.3",
        "cairosvg>=2.7.1",
        "Pillow>=10.1.0",
        "numpy>=1.24.0",
        "fonttools>=4.47.0",
        "grandalf>=0.8",
        "click>=8.1.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "mypy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "excelimermaid=excelimermaid.cli:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
    ],
    keywords="mermaid, flowchart, diagram, excalidraw, hand-drawn, visualization",
)
