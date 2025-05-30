"""
Document Chunking Module

This module provides functionality to process documents (markdown, docx, pdf) 
and split them into chunks based on their table of contents structure.
"""

import os
import re
import pandas as pd
from typing import List, Tuple
from dotenv import load_dotenv
import pypandoc
import tiktoken
# Optional imports for semantic chunking (currently unused)
# from langchain_experimental.text_splitter import SemanticChunker
# import chromadb.utils.embedding_functions as embedding_functions
# from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()

# Configuration constants
ROOT_DIR = 'kb_new'
ALLOWED_FILETYPES = ['.md', '.docx', '.pdf']
DEBUG_MODE = True  # Set to False to reduce verbose output

def identify_doc_type(doc: str) -> str:
    """
    Categorizes a plaintext document based on the format of the table of contents.
    
    Args:
        doc (str): The document content as a string
        
    Returns:
        str: Document type classification
    """
    # Look for TOC pattern: lines starting with "- " followed by double newline and then content
    if re.search(r'- .*\r?\n\r?\n[A-Z]', doc):
        return "TOC_WITHOUT_TITLE"
    else:
        return "NO_TOC_TITLE"


def read_doc(path: str) -> Tuple[str, str]:
    """
    Reads a document file and extracts the table of contents and full text.
    
    Args:
        path (str): File path to the document
        
    Returns:
        Tuple[str, str]: A tuple containing (table_of_contents, full_text)
        
    Raises:
        Exception: If the file cannot be processed by pypandoc
    """
    try:
        doc = str(pypandoc.convert_file(
            path, 'plain', format='md', 
            extra_args=["--toc", "--standalone"]
        ))
        doc_type = identify_doc_type(doc)

        if doc_type == "TOC_WITH_TITLE":
            doc = re.sub('.*\n\n\n-', '-', doc)
            toc, text = doc.split('\n\n', 1)
        elif doc_type == "TOC_WITHOUT_TITLE":
            # Split on double newline/carriage return to separate TOC from content
            parts = re.split(r'\r?\n\r?\n', doc, 1)
            if len(parts) >= 2:
                toc, text = parts[0], parts[1]
            else:
                toc, text = "", doc
        else:
            toc, text = "", doc

        return toc, text
    
    except Exception as e:
        if DEBUG_MODE:
            print(f"Error processing file {path}: {e}")
        return "", ""

def cleanup_plaintext(text: str) -> str:
    """
    Cleans up the full text of a document by normalizing whitespace and removing artifacts.
    
    Args:
        text (str): Raw text content from the document
        
    Returns:
        str: Cleaned text with normalized formatting
    """
    # Remove image artifacts
    text = text.replace("[image]", "")
    text = text.replace("[]", "")

    # Normalize line endings - convert \r\n to \n
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')

    # Replace single \n with space EXCEPT when:
    # - followed by another \n (paragraph break)
    # - followed by "- " (bullet point)
    # - preceded by a bullet point and followed by "- " (between bullet points)
    text = re.sub('(?<!\n)\n(?!(\n|- ))', ' ', text)

    # Replace any sequence of two or more newlines with \n\n
    text = re.sub('\n{2,}', '\n\n', text)

    # Replace multiple spaces with single space
    text = re.sub('(?<!\n) +', ' ', text)
    
    return text

def split_text(toc: str, text: str) -> List[str]:
    """
    Splits text into chunks based on headings from the table of contents.
    
    Args:
        toc (str): Table of contents with headings
        text (str): Cleaned document text
        
    Returns:
        List[str]: List of text chunks in format "Heading [SEP] Content"
    """
    # Handle empty TOC case
    if not toc.strip():
        headings = []
    else:
        # Split TOC by newlines and extract headings, handling carriage returns
        toc_lines = re.split(r'\r?\n', toc)
        headings = []
        for line in toc_lines:
            # Strip bullets and whitespace, handle indented items
            cleaned_line = line.strip('- \n\r').strip()
            if cleaned_line:
                headings.append(cleaned_line)
    
    paragraphs = text.split("\n\n")
    current_heading = ""
    current_content = []
    text_chunks = []
    
    for para in paragraphs:
        # Skip empty paragraphs
        if not para.strip():
            continue

        # Check if this paragraph is a heading
        if len(headings) > 0 and para.strip() in headings:
            # Save the previous heading and its content as a chunk
            if current_heading and current_content:
                combined_content = " ".join(current_content)
                text_chunks.append(f"{current_heading} [SEP] {combined_content}".strip())
            
            # Start new heading
            current_heading = para.strip()
            headings.remove(para.strip())
            current_content = []
            continue

        # Accumulate content under the current heading
        current_content.append(para.strip())

    # Add the last heading and its content
    if current_heading and current_content:
        combined_content = " ".join(current_content)
        text_chunks.append(f"{current_heading} [SEP] {combined_content}".strip())
    elif current_content and not current_heading:
        # Handle content without headings
        combined_content = " ".join(current_content)
        text_chunks.append(combined_content.strip())

    return text_chunks

def process_single_file(file_path: str) -> List[dict]:
    """
    Process a single document file and return its chunks with metadata.
    
    Args:
        file_path (str): Path to the file to process
        
    Returns:
        List[dict]: List of dictionaries containing chunk data and metadata
    """
    directory, filename_with_ext = os.path.split(file_path)
    filename, filetype = os.path.splitext(filename_with_ext)
    
    if DEBUG_MODE:
        print(f"Processing file: {file_path}")
    
    # Extract TOC and text
    toc, text = read_doc(file_path)
    if DEBUG_MODE:
        print(f"  TOC length: {len(toc)}, Text length: {len(text)}")
    
    # Clean the text
    text_cleaned = cleanup_plaintext(text)
    if DEBUG_MODE:
        print(f"  Cleaned text length: {len(text_cleaned)}")
    
    # Split into chunks
    text_chunks = split_text(toc, text_cleaned)
    if DEBUG_MODE:
        print(f"  Number of chunks: {len(text_chunks)}")
        if not text_chunks:
            print(f"    No chunks generated for {file_path}")
        else:
            for i, chunk in enumerate(text_chunks, 1):
                print(f"==========    Chunk {i}: \n{chunk}\n==========")
    
    # Initialize TikToken for chunk length calculation
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    # Create list of dictionaries with chunk data and metadata
    chunk_data = []
    for chunk in text_chunks:
        tokens = encoding.encode(chunk)
        chunk_data.append({
            'text': chunk,
            'directory': directory,
            'filename': filename,
            'filetype': filetype,
            'chunk_length': len(tokens),
        })
    
    return chunk_data


def process_documents(root_dir: str = ROOT_DIR, 
                     allowed_filetypes: List[str] = ALLOWED_FILETYPES) -> pd.DataFrame:
    """
    Process all documents in a directory and return a DataFrame of chunks.
    
    Args:
        root_dir (str): Root directory to search for documents
        allowed_filetypes (List[str]): List of allowed file extensions
        
    Returns:
        pd.DataFrame: DataFrame containing all chunks with metadata
    """
    if DEBUG_MODE:
        print(f"Walking directory: {os.path.abspath(root_dir)}")
    
    all_chunk_data = []
    
    for directory, subdirectories, files in os.walk(root_dir):
        if DEBUG_MODE:
            print(f"In directory: {directory}")
        
        for file in files:
            filename, filetype = os.path.splitext(file)
            if filetype in allowed_filetypes:
                full_path = os.path.join(directory, file)
                chunk_data = process_single_file(full_path)
                all_chunk_data.extend(chunk_data)
            elif DEBUG_MODE:
                print(f"Skipping file (wrong type): {os.path.join(directory, file)}")
    
    # Create DataFrame from all chunk data
    df = pd.DataFrame(all_chunk_data)
    df.reset_index(drop=True, inplace=True)
    
    return df


def main():
    """
    Main function to process documents and display results.
    """
    try:
        df = process_documents()
        print("\n" + "="*50)
        print("PROCESSING COMPLETE")
        print("="*50)
        print(f"Total chunks created: {len(df)}")
        print("\nFirst 100 rows of results:")
        print(df.head(100))
        
        # Optionally save to CSV
        # df.to_csv('document_chunks.csv', index=False)
        # print("\nResults saved to 'document_chunks.csv'")
        
    except Exception as e:
        print(f"Error in main processing: {e}")


if __name__ == "__main__":
    main()