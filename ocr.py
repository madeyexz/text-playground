from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_image(image):
    """Process a single image with OCR"""
    custom_config = r'--oem 1 --psm 3 -c tessedit_do_invert=0'
    return pytesseract.image_to_string(image, lang='chi_sim', config=custom_config)

def pdf_to_text(pdf_path, output_path=None):
    """
    Convert a scanned PDF to text using OCR
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str, optional): Path to save the output text file
    
    Returns:
        str: Extracted text from the PDF
    """
    try:
        # Convert PDF to images
        print("Converting PDF to images...")
        images = convert_from_path(pdf_path)
        
        # Extract text from each page in parallel
        print("Performing OCR on pages...")
        full_text = [None] * len(images)  # Pre-allocate list
        
        # Use number of CPU cores for parallel processing
        max_workers = multiprocessing.cpu_count()
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks and map them to their original page numbers
            future_to_index = {executor.submit(process_image, image): idx 
                             for idx, image in enumerate(images)}
            
            # Process results as they complete
            for future in tqdm(as_completed(future_to_index), total=len(images), desc="Processing pages"):
                idx = future_to_index[future]
                full_text[idx] = future.result()
        
        # Combine text from all pages
        complete_text = '\n\n'.join(full_text)
        
        # Save to file if output path is provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(complete_text)
        
        return complete_text
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    pdf_file = "/Users/ianhsiao/Developer/Covert_Epub_and_PDF_to_Markdown/pdf/eur.pdf"
    output_file = "eur.txt"
    
    extracted_text = pdf_to_text(pdf_file, output_file)
    if extracted_text:
        print("Text extraction completed successfully!")
        print("\nFirst 500 characters of extracted text:")
        print(extracted_text[:500])
