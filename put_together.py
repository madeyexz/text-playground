import argparse
import logging
import os
from pathlib import Path
from tqdm import tqdm

# This Python script is designed to concatenate all files in a directory into a single markdown file.
# Input: It takes a directory containing multiple markdown files.
# Output: It saves the concatenated content into a single markdown file.

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Concatenate files in a directory into a single markdown file')
    parser.add_argument('directory', type=str, help='Directory containing files to concatenate')
    parser.add_argument('--output', type=str, default='all.md', help='Output file name (default: all.md)')
    args = parser.parse_args()

    # Convert directory path to Path object
    dir_path = Path(args.directory)
    
    # Check if directory exists
    if not dir_path.is_dir():
        logger.error(f"Directory {dir_path} does not exist")
        return

    # Get list of files in directory and sort them
    files = sorted(dir_path.glob('*'))
    
    if not files:
        logger.warning(f"No files found in {dir_path}")
        return

    logger.info(f"Found {len(files)} files in {dir_path}")
    
    # Concatenate files
    with open(args.output, 'w', encoding='utf-8') as outfile:
        for file in tqdm(files, desc="Concatenating files"):
            try:
                with open(file, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                    outfile.write('\n\n')  # Add two newlines between files
            except Exception as e:
                logger.error(f"Error processing file {file}: {str(e)}")
                continue

    logger.info(f"Successfully created {args.output}")

if __name__ == "__main__":
    main()
