import os
import tempfile
from pathlib import Path
import re
import zipfile
from bs4 import BeautifulSoup
import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from langdetect import detect
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def preprocess_image(image):
    """
    Preprocess image to improve OCR accuracy
    
    Args:
        image: The input image
        
    Returns:
        The preprocessed image
    """
    # Convert to numpy array if needed
    if not isinstance(image, np.ndarray):
        img = np.array(image)
    else:
        img = image.copy()
    
    # Convert to grayscale if it's not already
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    # Apply adaptive thresholding to handle different lighting conditions
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Apply dilation to make text more visible
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    
    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(dilated, None, 10, 7, 21)
    
    return denoised

def detect_language(text_sample):
    """
    Detect the language of the text sample
    
    Args:
        text_sample: A sample of text
        
    Returns:
        ISO language code
    """
    try:
        # Skip detection for very short text
        if len(text_sample.strip()) < 20:
            return 'eng'  # Default to English
        
        lang = detect(text_sample)
        
        # Map language codes to Tesseract language packs
        lang_map = {
            'zh': 'chi_sim',  # Chinese simplified
            'ja': 'jpn',      # Japanese
            'ko': 'kor',      # Korean
            'ru': 'rus',      # Russian
            'ar': 'ara',      # Arabic
            'hi': 'hin',      # Hindi
            'fa': 'fas',      # Persian
        }
        
        return lang_map.get(lang, lang)
    except Exception as e:
        logger.warning(f"Language detection failed: {str(e)}. Defaulting to English.")
        return 'eng'

def process_image(args):
    """Process a single image with OCR"""
    image, lang, preprocess = args
    
    if preprocess:
        processed_img = preprocess_image(image)
    else:
        processed_img = np.array(image)
    
    # Determine OCR config based on detected language
    custom_config = r'--oem 1 --psm 3'
    
    # Detect text
    return pytesseract.image_to_string(processed_img, lang=lang, config=custom_config)

def extract_text_from_epub(epub_path):
    """
    Extract text from an EPUB file
    
    Args:
        epub_path (str): Path to the EPUB file
        
    Returns:
        list: Extracted text from each chapter
    """
    chapters = []
    
    try:
        # Open the EPUB file as a zip
        with zipfile.ZipFile(epub_path, 'r') as epub_zip:
            # Find content files (HTML/XHTML)
            content_files = [f for f in epub_zip.namelist() if 
                             f.endswith('.html') or f.endswith('.xhtml') or f.endswith('.htm')]
            
            # Extract text from each content file
            for content_file in sorted(content_files):
                with epub_zip.open(content_file) as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    
                    # Remove script and style elements
                    for script_or_style in soup(['script', 'style']):
                        script_or_style.decompose()
                    
                    # Extract text
                    text = soup.get_text()
                    
                    # Clean text (remove excessive whitespace)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if text:
                        chapters.append(text)
        
        return chapters
    
    except Exception as e:
        logger.error(f"Error extracting text from EPUB: {str(e)}")
        return []

def document_to_text(file_path, output_path=None, dpi=300, preprocess=True, language=None, pages=None):
    """
    Convert a scanned PDF or EPUB to text
    
    Args:
        file_path (str): Path to the PDF or EPUB file
        output_path (str, optional): Path to save the output text file
        dpi (int): DPI for PDF to image conversion
        preprocess (bool): Whether to preprocess images
        language (str, optional): Language code for OCR
        pages (tuple, optional): Range of pages to process (start, end)
        
    Returns:
        str: Extracted text
    """
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.epub':
            logger.info(f"Processing EPUB file: {file_path}")
            chapters = extract_text_from_epub(file_path)
            complete_text = '\n\n'.join(chapters)
            
        elif file_ext == '.pdf':
            logger.info(f"Processing PDF file: {file_path}")
            
            # Convert PDF to images with proper DPI
            logger.info(f"Converting PDF to images with DPI={dpi}...")
            
            # Handle page range if specified
            if pages:
                start_page, end_page = pages
                images = convert_from_path(file_path, dpi=dpi, first_page=start_page, last_page=end_page)
            else:
                images = convert_from_path(file_path, dpi=dpi)
            
            logger.info(f"Converted {len(images)} pages")
            
            # Detect language from first page if not specified
            if not language and images:
                # Process the first page without preprocessing for better language detection
                first_page_text = pytesseract.image_to_string(images[0], config='--psm 3')
                language = detect_language(first_page_text)
                logger.info(f"Detected language: {language}")
            
            # Default to English if language detection failed
            if not language:
                language = 'eng'
            
            # Extract text from each page in parallel
            logger.info("Performing OCR on pages...")
            full_text = [None] * len(images)  # Pre-allocate list
            
            # Use number of CPU cores for parallel processing
            max_workers = max(1, multiprocessing.cpu_count() - 1)  # Leave one core free
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks and map them to their original page numbers
                future_to_index = {
                    executor.submit(process_image, (image, language, preprocess)): idx 
                    for idx, image in enumerate(images)
                }
                
                # Process results as they complete
                for future in tqdm(as_completed(future_to_index), total=len(images), desc="Processing pages"):
                    idx = future_to_index[future]
                    try:
                        full_text[idx] = future.result()
                    except Exception as e:
                        logger.error(f"Error processing page {idx+1}: {str(e)}")
                        full_text[idx] = f"[ERROR ON PAGE {idx+1}]"
            
            # Combine text from all pages
            complete_text = '\n\n'.join(filter(None, full_text))
        
        else:
            logger.error(f"Unsupported file format: {file_ext}")
            return None
        
        # Save to file if output path is provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(complete_text)
            logger.info(f"Text saved to {output_path}")
        
        return complete_text
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Convert scanned PDF or EPUB to text using OCR')
    parser.add_argument('file_path', help='Path to the PDF or EPUB file')
    parser.add_argument('-o', '--output', help='Path to save the output text file')
    parser.add_argument('-d', '--dpi', type=int, default=300, help='DPI for PDF to image conversion')
    parser.add_argument('-l', '--language', help='Language code for OCR (auto-detect if not specified)')
    parser.add_argument('-p', '--pages', nargs=2, type=int, metavar=('START', 'END'), 
                        help='Range of pages to process (only for PDF)')
    parser.add_argument('--no-preprocess', action='store_true', help='Disable image preprocessing')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        logger.error(f"File not found: {args.file_path}")
        return
    
    # Set default output path if not specified
    if not args.output:
        file_base = os.path.splitext(os.path.basename(args.file_path))[0]
        args.output = f"{file_base}.txt"
    
    extracted_text = document_to_text(
        args.file_path, 
        args.output,
        dpi=args.dpi,
        preprocess=not args.no_preprocess,
        language=args.language,
        pages=args.pages
    )
    
    if extracted_text:
        logger.info("Text extraction completed successfully!")
        print("\nFirst 300 characters of extracted text:")
        print(extracted_text[:300] + "...")

if __name__ == "__main__":
    main()
