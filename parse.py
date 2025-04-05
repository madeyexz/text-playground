import re
import os
import argparse

# This Python script is designed to split a single Markdown file into multiple chapter files.
# Input: It takes a Markdown file (like ./md/harry.md) that contains multiple chapters marked with certain markdown headers.
# Output: It saves each chapter into a separate file in the specified output directory.

def parse_md_into_chapters(input_file, output_dir, num=1):
    # Add input validation
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' does not exist")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            raise ValueError("Input file is empty")

        # Split content into chapters
        chapters = re.split(rf'^{'#'* num} ', content, flags=re.MULTILINE)[1:]  # Skip the first empty split
        
        if not chapters:
            raise ValueError("No chapters found. Make sure chapters are marked with '## '")

        for chapter in chapters:
            lines = chapter.strip().split('\n')
            chapter_title = lines[0].strip()
            
            # Validate chapter title
            if not chapter_title:
                continue  # Skip chapters with empty titles
                
            chapter_content = '\n'.join(lines[1:]).strip()

            # Create a valid filename with additional safety
            filename = re.sub(r'[^\w\s-]', '', chapter_title.lower())
            filename = re.sub(r'[-\s]+', '_', filename)
            if not filename:
                filename = f"chapter_{chapters.index(chapter) + 1}"
            
            # Use os.path.join for proper path handling
            output_path = os.path.join(output_dir, f"{filename}.md")
            
            # Write chapter content with error handling
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {chapter_title}\n\n{chapter_content}")
            except IOError as e:
                print(f"Error writing chapter '{chapter_title}': {e}")

        print(f"Chapters have been parsed and saved in the '{output_dir}' directory.")
        
    except Exception as e:
        raise Exception(f"Error processing markdown file: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split a markdown file into chapter files')
    parser.add_argument('input_file', help='Path to input markdown file')
    parser.add_argument('--output_dir', help='Directory to save chapter files (optional)')
    
    args = parser.parse_args()
    
    # Create output directory based on input filename if not specified
    if not args.output_dir:
        input_basename = os.path.splitext(os.path.basename(args.input_file))[0]
        args.output_dir = f"{input_basename}_chapters"
    
    os.makedirs(args.output_dir, exist_ok=True)
    parse_md_into_chapters(args.input_file, args.output_dir, num=1)