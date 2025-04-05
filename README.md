# text-playground

A playground for text processing tools including OCR text extraction, PDF/EPUB to Markdown conversion, and AI-powered (openai) file-based summarization. These utilities support multiple languages and can be used individually or combined into workflows for document conversion and content processing.


Created for my personal use, but PRs are welcomed!

## Core Files

### convert.py
**Purpose**: Main conversion script that orchestrates the entire PDF/EPUB to Markdown conversion process.  
**Input**: PDF or EPUB file, optional parameters for DPI, language, page range, etc.  
**Output**: Markdown file with formatted content from the original document.

**Example Usage**:
```bash
# Basic conversion of a PDF to Markdown
python convert.py my_document.pdf

# Conversion with custom parameters
python convert.py my_document.pdf --output output.md --dpi 500 --language eng
```

### ocr.py
**Purpose**: Extracts text from scanned PDFs and EPUBs using OCR technology.  
**Input**: PDF or EPUB file path, output path, DPI settings, language preferences.  
**Output**: Raw text extracted from the document.

**Example Usage**:
```bash
# Extract text from a PDF with default settings
python ocr.py my_document.pdf

# Extract text with custom parameters
python ocr.py my_document.pdf --output extracted_text.txt --dpi 400 --language chi_sim
```

### markdown_converter.py
**Purpose**: Converts raw text to properly formatted Markdown with headers, paragraphs, etc.  
**Input**: Raw text file, optional document title and author.  
**Output**: Formatted Markdown file.

**Example Usage**:
```bash
# Convert text file to Markdown
python markdown_converter.py extracted_text.txt

# Convert with document metadata
python markdown_converter.py extracted_text.txt --output formatted.md --title "Document Title" --author "Author Name"
```

### epubtomd.py
**Purpose**: Specialized script for converting EPUB files directly to Markdown.  
**Input**: EPUB file path, output directory.  
**Output**: Markdown file with content extracted from the EPUB.

**Example Usage**:
```bash
# Change the file paths in the script and run
# First modify these lines in the script:
# epub_file = "/path/to/your/book.epub"
# output_directory = "/path/to/output/directory"
python epubtomd.py
```

### pdftomd.py
**Purpose**: Specialized script for converting PDF files directly to Markdown.  
**Input**: PDF file path, optional output directory.  
**Output**: Markdown file with content extracted from the PDF.

**Example Usage**:
```bash
# Basic conversion
python pdftomd.py my_document.pdf

# Specify output directory
python pdftomd.py my_document.pdf output_directory
```

## Utility Files

### put_together.py
**Purpose**: Concatenates multiple files in a directory into a single Markdown file.  
**Input**: Directory containing Markdown files.  
**Output**: Single Markdown file containing content from all source files.

**Example Usage**:
```bash
# Concatenate all files in a directory
python put_together.py my_chapters_directory

# Specify output file name
python put_together.py my_chapters_directory --output complete_book.md
```

### parse.py
**Purpose**: Splits a single Markdown file into multiple chapter files based on header markers.  
**Input**: Markdown file with multiple chapters, output directory.  
**Output**: Multiple Markdown files, one per chapter.

**Example Usage**:
```bash
# Split a markdown file into chapters
python parse.py complete_book.md

# Specify output directory
python parse.py complete_book.md --output_dir chapter_files
```

### summarize_each_section.py
**Purpose**: Generates AI-powered summaries for Markdown files using OpenAI models.  
**Input**: Markdown file or directory containing Markdown files.  
**Output**: Summary files (prefixed with "sum_") for each input Markdown file.

**Example Usage**:
```bash
# Summarize a single markdown file
python summarize_each_section.py chapter.md

# Summarize all markdown files in a directory
python summarize_each_section.py chapters_directory
```

## Requirements

The necessary dependencies for running these scripts are listed in `requirements.txt`. You can install them using:

```
pip install -r requirements.txt
```

For OCR functionality, you will need to have Tesseract OCR installed on your system. The scripts are configured to work with multiple languages, with a default focus on Simplified Chinese and English. 