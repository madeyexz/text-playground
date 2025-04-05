import re
import argparse
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def detect_headers(line, min_length=3):
    """
    Detect if a line is likely a header based on length and formatting
    
    Args:
        line: The line of text
        min_length: Minimum length to consider as header
        
    Returns:
        tuple: (is_header, header_level)
    """
    stripped = line.strip()
    
    # Too short
    if len(stripped) < min_length:
        return False, 0
        
    # Check if entire line is uppercase
    if stripped.isupper() and len(stripped) > 5:
        return True, 1
    
    # Check for chapter indicators
    chapter_patterns = [
        r'^chapter\s+\d+',
        r'^section\s+\d+',
        r'^\d+\.\s+[A-Z]',
        r'^\d+\.\d+\s+[A-Z]',
    ]
    
    for pattern in chapter_patterns:
        if re.match(pattern, stripped, re.IGNORECASE):
            return True, 2
            
    # Check for numeric prefixes (like 1. Title)
    if re.match(r'^\d+\.\s+\w+', stripped):
        return True, 3
        
    return False, 0

def format_paragraphs(text):
    """
    Format the text into proper paragraphs
    
    Args:
        text: The input text
        
    Returns:
        str: Formatted text with paragraphs
    """
    # Split by double newlines (paragraph breaks)
    paragraphs = re.split(r'\n\s*\n', text)
    
    # Clean each paragraph
    formatted_paragraphs = []
    for para in paragraphs:
        # Replace single newlines with spaces (join broken lines)
        para = re.sub(r'\n', ' ', para)
        
        # Clean up multiple spaces
        para = re.sub(r'\s+', ' ', para).strip()
        
        if para:
            formatted_paragraphs.append(para)
    
    return formatted_paragraphs

def identify_special_sections(paragraphs):
    """
    Identify special sections like TOC, index, etc.
    
    Args:
        paragraphs: List of paragraphs
        
    Returns:
        dict: Information about special sections
    """
    toc_start = -1
    toc_end = -1
    
    # Look for table of contents indicators
    toc_patterns = [
        r'^\s*table\s+of\s+contents\s*$',
        r'^\s*contents\s*$',
        r'^\s*toc\s*$'
    ]
    
    # Find TOC start
    for i, para in enumerate(paragraphs):
        if any(re.match(pattern, para, re.IGNORECASE) for pattern in toc_patterns):
            toc_start = i
            break
    
    # If TOC found, try to find its end (usually when numbering pattern stops)
    if toc_start >= 0:
        toc_pattern = r'.*\.{2,}.*\d+' # matches "Chapter title...... 42" patterns
        
        # Count consecutive TOC-like entries
        consecutive_toc = 0
        for i in range(toc_start + 1, min(toc_start + 50, len(paragraphs))):
            if re.match(toc_pattern, paragraphs[i]):
                consecutive_toc += 1
            elif consecutive_toc >= 3:  # We found at least 3 TOC entries and now a non-TOC paragraph
                toc_end = i - 1
                break
            else:
                consecutive_toc = 0
    
    return {
        'toc': (toc_start, toc_end)
    }

def convert_text_to_markdown(text, title=None, author=None):
    """
    Convert extracted text to properly formatted markdown
    
    Args:
        text: The input text from OCR
        title: Document title (optional)
        author: Document author (optional)
        
    Returns:
        str: Converted markdown text
    """
    # Format the text into paragraphs
    paragraphs = format_paragraphs(text)
    
    # Identify special sections
    sections = identify_special_sections(paragraphs)
    
    # Start building markdown
    markdown = []
    
    # Add title and metadata if provided
    if title:
        markdown.append(f"# {title}\n")
    if author:
        markdown.append(f"*By {author}*\n")
    
    markdown.append("")  # Empty line after metadata
    
    # Process each paragraph
    current_section = None
    for i, para in enumerate(paragraphs):
        # Skip paragraphs in the TOC section
        toc_start, toc_end = sections['toc']
        if toc_start >= 0 and toc_end >= 0 and toc_start <= i <= toc_end:
            if i == toc_start:
                markdown.append("## Table of Contents\n")
                markdown.append("*[TOC content omitted in conversion]*\n")
            continue
            
        # Check if it's a header
        is_header, header_level = detect_headers(para)
        
        if is_header:
            # Map the detected header level to markdown heading level
            md_level = min(header_level + 1, 6)  # maximum heading level is 6
            markdown.append(f"{'#' * md_level} {para.strip()}\n")
        else:
            # Regular paragraph
            markdown.append(f"{para}\n")
            
        markdown.append("")  # Empty line after each paragraph or header
    
    return "\n".join(markdown)

def process_file(input_path, output_path=None, title=None, author=None):
    """
    Process a text file and convert it to markdown
    
    Args:
        input_path: Path to the input text file
        output_path: Path to save the markdown file (optional)
        title: Document title (optional)
        author: Document author (optional)
        
    Returns:
        str: Path to the output file
    """
    try:
        # Read the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Convert to markdown
        markdown = convert_text_to_markdown(text, title, author)
        
        # Set default output path if not provided
        if not output_path:
            output_path = str(Path(input_path).with_suffix('.md'))
        
        # Write the markdown to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
            
        logger.info(f"Markdown conversion completed: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error converting to markdown: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Convert OCR text to formatted markdown')
    parser.add_argument('input_file', help='Path to the input text file')
    parser.add_argument('-o', '--output', help='Path to save the markdown file')
    parser.add_argument('-t', '--title', help='Document title')
    parser.add_argument('-a', '--author', help='Document author')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        logger.error(f"Input file not found: {args.input_file}")
        return
    
    output_file = process_file(args.input_file, args.output, args.title, args.author)
    
    if output_file:
        logger.info("Conversion complete!")

if __name__ == "__main__":
    main() 