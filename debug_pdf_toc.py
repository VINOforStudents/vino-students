#!/usr/bin/env python3

from document_processor import extract_text_from_pdf
from chunking import identify_doc_type
import re

def debug_pdf_toc():
    pdf_path = 'kb_new/SCRUMv2.pdf'
    
    # Extract text
    text, page_count = extract_text_from_pdf(pdf_path)
    
    print(f"Page count: {page_count}")
    print(f"Text length: {len(text)}")
    print("\n" + "="*50)
    print("FIRST 1500 CHARACTERS:")
    print("="*50)
    print(repr(text[:1500]))
    
    print("\n" + "="*50)
    print("LOOKING FOR TOC PATTERNS:")
    print("="*50)
    
    # Test current TOC pattern
    TOC_PATTERN = re.compile(r'- .*\r?\n\r?\n[A-Z]')
    matches = TOC_PATTERN.findall(text[:2000])
    print(f"Current TOC pattern matches: {matches}")
    
    # Look for table of contents manually
    lines = text.split('\n')
    print(f"\nFirst 30 lines:")
    for i, line in enumerate(lines[:30]):
        print(f"{i:2d}: {repr(line)}")
    
    # Test doc type identification
    doc_type = identify_doc_type(text)
    print(f"\nDocument type identified: {doc_type}")
    
    # Look for different TOC patterns
    print("\nTesting alternative TOC patterns:")
    
    # Pattern 1: Lines with dots (table of contents with dots)
    dot_pattern = re.compile(r'\.{3,}')
    dot_matches = dot_pattern.findall(text[:2000])
    print(f"Dot pattern matches: {len(dot_matches)}")
    
    # Pattern 2: Page numbers at end of lines
    page_num_pattern = re.compile(r'\d+\s*$', re.MULTILINE)
    page_matches = page_num_pattern.findall(text[:2000])
    print(f"Page number pattern matches: {page_matches}")
    
    # Pattern 3: Common TOC structure
    toc_lines = []
    for line in lines[:50]:
        if '...' in line or (len(line.strip()) > 0 and line.strip()[-1].isdigit()):
            toc_lines.append(line.strip())
    
    print(f"Potential TOC lines: {toc_lines}")

if __name__ == "__main__":
    debug_pdf_toc()
