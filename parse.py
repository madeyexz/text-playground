import re

def parse_nexus_md(input_file, output_dir):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split content into chapters
    chapters = re.split(r'^## ', content, flags=re.MULTILINE)[1:]  # Skip the first empty split

    for chapter in chapters:
        lines = chapter.strip().split('\n')
        chapter_title = lines[0].strip()
        chapter_content = '\n'.join(lines[1:]).strip()

        # Create a valid filename
        filename = re.sub(r'[^\w\s-]', '', chapter_title.lower())
        filename = re.sub(r'[-\s]+', '_', filename)
        
        # Write chapter content to a new file
        with open(f"{output_dir}/{filename}.md", 'w', encoding='utf-8') as f:
            f.write(f"# {chapter_title}\n\n{chapter_content}")

    print(f"Chapters have been parsed and saved in the '{output_dir}' directory.")

if __name__ == "__main__":
    NAME = "harry"
    input_file = f"./md/{NAME}.md"
    output_dir = f"./{NAME}_chapters"
    import os
    os.makedirs(output_dir, exist_ok=True)
    parse_nexus_md(input_file, output_dir)