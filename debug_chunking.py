#!/usr/bin/env python3
"""
Debug script for chunking.py - shows file preview and chunk previews with metadata
"""

import tiktoken
from chunking import process_single_file, read_doc, cleanup_plaintext

def truncate_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to max_tokens and add ellipsis if needed"""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens) + "..."

def debug_file(file_path: str):
    """Debug a single file - show original preview and all chunks"""
    print(f"\n{'='*80}")
    print(f"DEBUGGING FILE: {file_path}")
    print(f"{'='*80}")
    
    # Get original content
    toc, text = read_doc(file_path)
    cleaned_text = cleanup_plaintext(text)
    
    # Show original file preview (50 tokens)
    print(f"\nORIGINAL FILE PREVIEW (50 tokens):")
    print(f"{'-'*50}")
    print(truncate_tokens(cleaned_text, 50))
    
    # Process file and show chunks
    chunks = process_single_file(file_path)
    
    print(f"\nCHUNKS ({len(chunks)} total):")
    print(f"{'='*50}")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i}:")
        print(f"  Doc ID: {chunk.metadata.doc_id}")
        print(f"  Section: {chunk.metadata.section}")
        print(f"  Tokens: {chunk.metadata.chunk_length}")
        print(f"  Preview (20 tokens): {truncate_tokens(chunk.text, 20)}")
        print(f"{'-'*30}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python debug_chunking.py <file_path>")
        print("Example: python debug_chunking.py kb/CMD.md")
        sys.exit(1)
    
    file_path = sys.argv[1]
    debug_file(file_path)
