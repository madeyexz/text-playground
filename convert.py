#!/usr/bin/env python3
import argparse
import logging
import os
from pathlib import Path
import tempfile

# Import our modules
from ocr import document_to_text
from markdown_converter import process_file

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_document(input_path, output_path=None, dpi=300, preprocess=True, 
                     language=None, pages=None, title=None, author=None, 
                     skip_ocr=False, skip_markdown=False):
    """
    Convert a document (PDF or EPUB) to markdown in one step
    
    Args:
        input_path: Path to the input file
        output_path: Path to save the output markdown file (optional)
        dpi: DPI for PDF to image conversion
        preprocess: Whether to preprocess images
        language: Language code for OCR
        pages: Range of pages to process (start, end)
        title: Document title
        author: Document author
        skip_ocr: Skip OCR and use an existing text file
        skip_markdown: Skip markdown conversion and only output OCR text
        
    Returns:
        str: Path to the output file
    """
    try:
        file_base = os.path.splitext(os.path.basename(input_path))[0]
        
        # Set default output path if not provided
        if not output_path:
            output_path = f"{file_base}.md"
        
        # Skip OCR if requested (use an existing text file)
        if skip_ocr:
            if not input_path.lower().endswith('.txt'):
                logger.error("Input file must be a .txt file when using --skip-ocr")
                return None
            
            text_file = input_path
        else:
            # OCR - Convert document to plain text
            logger.info(f"Processing document: {input_path}")
            
            # Use a temporary file for text output if we're continuing to markdown
            if skip_markdown:
                text_file = output_path
            else:
                # Create a temporary file for the OCR output
                text_file = tempfile.mktemp(suffix='.txt')
            
            # Run OCR
            extracted_text = document_to_text(
                input_path,
                output_path=text_file,
                dpi=dpi,
                preprocess=preprocess,
                language=language,
                pages=pages
            )
            
            if not extracted_text:
                logger.error("OCR processing failed")
                return None
        
        # Skip markdown conversion if requested
        if skip_markdown:
            logger.info(f"Text file saved to: {text_file}")
            return text_file
        
        # Convert text to markdown
        logger.info("Converting to markdown...")
        md_file = process_file(
            text_file,
            output_path=output_path,
            title=title,
            author=author
        )
        
        # Clean up temporary file
        if not skip_ocr and not skip_markdown:
            try:
                os.remove(text_file)
            except:
                pass
        
        return md_file
        
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Convert PDF or EPUB to Markdown in one step')
    parser.add_argument('input_file', help='Path to the PDF or EPUB file')
    parser.add_argument('-o', '--output', help='Path to save the output markdown file')
    parser.add_argument('-d', '--dpi', type=int, default=300, help='DPI for PDF to image conversion')
    parser.add_argument('-l', '--language', help='Language code for OCR (auto-detect if not specified)')
    parser.add_argument('-p', '--pages', nargs=2, type=int, metavar=('START', 'END'), 
                        help='Range of pages to process (only for PDF)')
    parser.add_argument('--no-preprocess', action='store_true', help='Disable image preprocessing')
    parser.add_argument('-t', '--title', help='Document title for markdown')
    parser.add_argument('-a', '--author', help='Document author for markdown')
    parser.add_argument('--skip-ocr', action='store_true', 
                        help='Skip OCR and convert an existing text file to markdown')
    parser.add_argument('--skip-markdown', action='store_true', 
                        help='Skip markdown conversion and output only OCR text')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        logger.error(f"Input file not found: {args.input_file}")
        return
    
    output_file = convert_document(
        args.input_file,
        output_path=args.output,
        dpi=args.dpi,
        preprocess=not args.no_preprocess,
        language=args.language,
        pages=args.pages,
        title=args.title,
        author=args.author,
        skip_ocr=args.skip_ocr,
        skip_markdown=args.skip_markdown
    )
    
    if output_file:
        logger.info(f"Conversion completed successfully: {output_file}")
    else:
        logger.error("Conversion failed")

if __name__ == "__main__":
    main() 