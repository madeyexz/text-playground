import argparse
import os
from pathlib import Path
from tqdm import tqdm
import asyncio
from openai import AsyncOpenAI
from asyncio import Semaphore
from dotenv import load_dotenv
from typing import Tuple

model_name = "o3-mini"

def read_markdown_file(file_path: Path) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

async def generate_summary(content: str, semaphore: Semaphore, client: AsyncOpenAI) -> str:
    async with semaphore:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                # {"role": "user", "content": f"請幫我完整總結這個逐字稿的內容。在總結的方式上，請用階層式的列點架構，讓我知道這裡探討了哪些主題、每個主題有哪些觀點、洞見，每個觀點或洞見都有哪些重要的例子、論證或論據。\n\n{content}"},
                {"role": "user", "content": f"\n\n{content}"},
            ]
        )
        return response.choices[0].message.content

async def process_file(file_path: Path, semaphore: Semaphore, client: AsyncOpenAI) -> Tuple[Path, str]:
    content = read_markdown_file(file_path)
    try:
        summary = await generate_summary(content, semaphore, client)
        return file_path, summary
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return file_path, f"Error: {str(e)}"

def save_summary(file_path: Path, summary: str):
    output_path = file_path.parent / f"sum_{model_name}_{file_path.name}"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)

async def main():
    parser = argparse.ArgumentParser(
        description='Generate AI-powered summaries for markdown files using OpenAI models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process a single file
    python summarize_o1.py path/to/file.md

    # Process all markdown files in a directory
    python summarize_o1.py path/to/directory

Notes:
    - Requires OPENAI_API_KEY in environment variables or .env file
    - Summaries are saved as 'sum_filename.md' in the same directory
    - Processes up to 20 files concurrently
    - Supports recursive directory scanning
    """
    )
    parser.add_argument(
        'path', 
        type=str, 
        help='Path to a markdown file or directory containing markdown files'
    )
    args = parser.parse_args()

    load_dotenv()
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    input_path = Path(args.path)
    
    # Handle single file
    if input_path.is_file():
        markdown_files = [input_path]
    # Handle directory
    elif input_path.is_dir():
        markdown_files = [f for f in input_path.glob('**/*.md') if not f.name.startswith('sum_')]
    else:
        print(f"Error: '{input_path}' is neither a valid file nor directory.")
        return

    if not markdown_files:
        print("No markdown files found to process.")
        return

    # Create semaphore to limit concurrent requests
    semaphore = Semaphore(20)
    
    # Process files concurrently with progress bar
    tasks = [process_file(file_path, semaphore, client) for file_path in markdown_files]
    
    for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Generating summaries using {model_name}"):
        file_path, summary = await task
        save_summary(file_path, summary)

if __name__ == "__main__":
    asyncio.run(main())