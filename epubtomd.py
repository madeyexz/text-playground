import os
import ebooklib
from ebooklib import epub
from html2text import html2text
import re

def clean_markdown(content):
    # 移除多餘的空行，但保留段落之間的一個空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    # 移除圖片引用
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    # 移除行尾的空格
    content = re.sub(r' +\n', '\n', content)
    
    lines = content.split('\n')
    cleaned_lines = []
    in_list_or_code = False
    for i, line in enumerate(lines):
        if line.strip().startswith(('- ', '* ', '+ ', '    ', '```')):
            in_list_or_code = True
        elif line.strip() == '' and in_list_or_code:
            in_list_or_code = False
        
        if in_list_or_code:
            cleaned_lines.append(line)
        elif i > 0 and line.strip() and not line.startswith('#'):
            if lines[i-1].strip() and not lines[i-1].endswith(('.', '!', '?', ':', ';')):
                cleaned_lines[-1] += ' ' + line.strip()
            else:
                if cleaned_lines and cleaned_lines[-1].strip() != '':
                    cleaned_lines.append('')
                cleaned_lines.append(line)
        else:
            if cleaned_lines and cleaned_lines[-1].strip() != '':
                cleaned_lines.append('')
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def epub_to_markdown(epub_path, output_dir):
    book = epub.read_epub(epub_path)
    
    os.makedirs(output_dir, exist_ok=True)
    
    book_title = book.get_metadata('DC', 'title')[0][0]
    main_md_file = os.path.join(output_dir, f"{book_title}.md")
    
    with open(main_md_file, 'w', encoding='utf-8') as main_file:
        main_file.write(f"# {book_title}\n\n")
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                html_content = item.get_content().decode('utf-8')
                
                markdown_content = html2text(html_content)
                
                markdown_content = clean_markdown(markdown_content)
                
                chapter_title = re.search(r'# (.*)', markdown_content)
                if chapter_title:
                    chapter_title = chapter_title.group(1)
                else:
                    chapter_title = f"Chapter {item.id}"
                
                main_file.write(f"## {chapter_title}\n\n")
                main_file.write(markdown_content)
                main_file.write("\n\n")
    
    print(f"Conversion complete. Output file: {main_md_file}")

# epub_file = "./epub/IntelligenceAnalysis.epub"
epub_file = "/Users/ianhsiao/Developer/Covert_Epub_and_PDF_to_Markdown/epub/improv.epub"
output_directory = "/Users/ianhsiao/Developer/Covert_Epub_and_PDF_to_Markdown/"
epub_to_markdown(epub_file, output_directory)
