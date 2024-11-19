import os
import re
from PyPDF2 import PdfReader

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

def pdf_to_markdown(pdf_path, output_dir):
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

pdf_file = "/Users/ianhsiao/Developer/Covert_Epub_and_PDF_to_Markdown/pdf/eur.pdf"
output_directory = "./md"
pdf_to_markdown(pdf_file, output_directory)