import os
import re
from PyPDF2 import PdfReader
import argparse

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\f', '', text)
    text = re.sub(r'(\w+)-\s*(\w+)', r'\1\2', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    return text.strip()

def is_title(line):
    return (line.strip() and len(line) < 75 and not line[-1] in '.!?,;:') or line.isupper()

def split_into_paragraphs(text):
    paragraphs = re.split(r'\n{2,}', text)
    return [p.strip() for p in paragraphs if p.strip()]

def format_paragraph(paragraph):
    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
    return ' '.join(sentences)

def pdf_to_markdown(pdf_path, output_dir=None):
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
    
    reader = PdfReader(pdf_path)
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_filename = os.path.basename(pdf_path)
    main_md_file = os.path.join(output_dir, f"{os.path.splitext(pdf_filename)[0]}.md")
    
    with open(main_md_file, 'w', encoding='utf-8') as main_file:
        main_file.write(f"# {os.path.splitext(pdf_filename)[0]}\n\n")
        
        for page in reader.pages:
            text = page.extract_text()
            cleaned_text = clean_text(text)
            paragraphs = split_into_paragraphs(cleaned_text)
            
            for paragraph in paragraphs:
                if is_title(paragraph):
                    main_file.write(f"\n## {paragraph}\n\n")
                else:
                    formatted_paragraph = format_paragraph(paragraph)
                    main_file.write(f"{formatted_paragraph}\n\n")
    
    print(f"Conversion complete. Output file: {main_md_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert PDF to Markdown')
    parser.add_argument('input_file', help='Path to the input PDF file')
    parser.add_argument('output_dir', nargs='?', default=None, 
                       help='Output directory (optional, defaults to input file directory)')
    
    args = parser.parse_args()
    pdf_to_markdown(args.input_file, args.output_dir)

if __name__ == '__main__':
    main()