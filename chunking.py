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
from models import DocumentChunk, DocumentMetadata


# Load environment variables
load_dotenv()

# Configuration constants
ROOT_DIR = 'kb_new'
ALLOWED_FILETYPES = ['.md', '.docx', '.pdf']
DEBUG_MODE = False  # Set to False to reduce verbose output
MAX_CHUNK_TOKENS = 300  # Maximum tokens per chunk before splitting

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

def process_single_file(file_path: str) -> List[DocumentChunk]:
    """
    Process a single document file and return its chunks with metadata.
    
    Args:
        file_path (str): Path to the file to process
        
    Returns:
        List[DocumentChunk]: List of DocumentChunk objects containing chunk data and metadata
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
        print(f"  Number of chunks before oversized splitting: {len(text_chunks)}")
        if not text_chunks:
            print(f"    No chunks generated for {file_path}")
        else:
            for i, chunk in enumerate(text_chunks, 1):
                print(f"==========    Chunk {i} processed successfully    ==========\n")

    # Apply oversized chunk splitting
    final_chunks = []
    chunk_counter = 1
    for chunk in text_chunks:
        split_chunks = split_oversized_chunk(chunk, MAX_CHUNK_TOKENS)
        if DEBUG_MODE:
            for split_chunk in split_chunks:
                print(f"==========    Chunk {chunk_counter}: \n{split_chunk}\n==========")
                chunk_counter += 1
        final_chunks.extend(split_chunks)
    if DEBUG_MODE:
        print(f"  Number of chunks after oversized splitting: {len(final_chunks)}")
    
    # Initialize TikToken for chunk length calculation
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    # Create list of DocumentChunk objects
    document_chunks = []
    chunk_counter = 1

    for chunk in final_chunks:
        tokens = encoding.encode(chunk)
        section_name = chunk.split("[SEP]")[0].strip() if "[SEP]" in chunk else "No Heading"
        
        # Create DocumentMetadata object
        metadata = DocumentMetadata(
            doc_id=f"{filename}_{chunk_counter}",
            chunk_number=chunk_counter,
            chunk_length=len(tokens),
            section=section_name  # Name of the section this chunk belongs to
        )
        
        # Create DocumentChunk object
        doc_chunk = DocumentChunk(
            metadata=metadata,
            text=chunk
        )
        
        document_chunks.append(doc_chunk)
        chunk_counter += 1
    
    return document_chunks

def split_oversized_chunk(chunk_text: str, max_tokens: int = MAX_CHUNK_TOKENS) -> List[str]:
    """
    Split an oversized chunk into smaller chunks while preserving meaning.
    
    Args:
        chunk_text (str): The chunk text to split (format: "Heading [SEP] Content")
        max_tokens (int): Maximum tokens per chunk
        
    Returns:
        List[str]: List of smaller chunks maintaining context
    """
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    # Check if chunk needs splitting
    if len(encoding.encode(chunk_text)) <= max_tokens:
        return [chunk_text]
    
    # Extract heading and content
    if "[SEP]" in chunk_text:
        heading, content = chunk_text.split("[SEP]", 1)
        heading = heading.strip()
        content = content.strip()
    else:
        heading = ""
        content = chunk_text.strip()
    
    # Split content by natural breaks (in order of preference)
    split_chunks = []
    
    # First try splitting by bullet points or numbered lists
    if re.search(r'\n- |\n\d+\.', content):
        # Split on bullet points or numbered items, keeping the delimiter
        parts = re.split(r'(\n- |\n\d+\.)', content)
        current_chunk = ""
        
        for i in range(0, len(parts)):
            if i == 0:
                current_chunk = parts[i]
            else:
                test_chunk = current_chunk + parts[i]
                test_text = f"{heading} [SEP] {test_chunk}".strip() if heading else test_chunk
                
                if len(encoding.encode(test_text)) > max_tokens and current_chunk.strip():
                    # Save current chunk and start new one
                    final_text = f"{heading} [SEP] {current_chunk}".strip() if heading else current_chunk.strip()
                    split_chunks.append(final_text)
                    current_chunk = parts[i] if i + 1 < len(parts) else ""
                else:
                    current_chunk = test_chunk
        
        # Add remaining content
        if current_chunk.strip():
            final_text = f"{heading} [SEP] {current_chunk}".strip() if heading else current_chunk.strip()
            split_chunks.append(final_text)
    
    # If no bullet points, try splitting by sentences
    elif '.' in content:
        sentences = re.split(r'(?<=[.!?])\s+', content)
        current_chunk = ""
        
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            test_text = f"{heading} [SEP] {test_chunk}".strip() if heading else test_chunk
            
            if len(encoding.encode(test_text)) > max_tokens and current_chunk.strip():
                # Save current chunk and start new one
                final_text = f"{heading} [SEP] {current_chunk}".strip() if heading else current_chunk.strip()
                split_chunks.append(final_text)
                current_chunk = sentence
            else:
                current_chunk = test_chunk
        
        # Add remaining content
        if current_chunk.strip():
            final_text = f"{heading} [SEP] {current_chunk}".strip() if heading else current_chunk.strip()
            split_chunks.append(final_text)
    
    # Last resort: split by approximate token count
    else:
        words = content.split()
        # Rough estimate: 1 token ≈ 0.75 words
        words_per_chunk = int(max_tokens * 0.75)
        
        for i in range(0, len(words), words_per_chunk):
            chunk_words = words[i:i + words_per_chunk]
            chunk_content = " ".join(chunk_words)
            final_text = f"{heading} [SEP] {chunk_content}".strip() if heading else chunk_content.strip()
            split_chunks.append(final_text)
    
    # If we still have oversized chunks, recursively split them
    final_chunks = []
    for chunk in split_chunks:
        if len(encoding.encode(chunk)) > max_tokens:
            final_chunks.extend(split_oversized_chunk(chunk, max_tokens))
        else:
            final_chunks.append(chunk)
    
    return final_chunks if final_chunks else [chunk_text]

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
    print(f"Total chunks created: {len(all_chunk_data)}")
    # Create DataFrame from all chunk data
    #df = pd.DataFrame(all_chunk_data)
    #df.reset_index(drop=True, inplace=True)
    for i in all_chunk_data:
        print(f"{i}\n=======\n")
    for i, chunk in enumerate(all_chunk_data, 1):
        print(f"\n{'='*60}")
        print(f"CHUNK {i}")
        print(f"{'='*60}")
        print(f"Doc ID: {chunk.metadata.doc_id}")
        print(f"Section: {chunk.metadata.section}")
        print(f"Chunk Number: {chunk.metadata.chunk_number}")
        print(f"Token Length: {chunk.metadata.chunk_length}")
        print(f"{'-'*60}")
        print("TEXT:")
        print(f"{'-'*60}")
        print(chunk.text)
        print(f"{'='*60}\n")
    return "success"

def main():
    """
    Main function to process documents and display results.
    """
    try:
        result = process_documents()
        print("\n" + "="*50)
        print("PROCESSING COMPLETE")
        print("="*50)
        print(result)
        
    except Exception as e:
        print(f"Error in main processing: {e}")


if __name__ == "__main__":
    main()