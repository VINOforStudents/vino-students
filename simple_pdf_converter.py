#!/usr/bin/env python3
"""
Simple PDF to Markdown Converter with Better Formatting

This script fixes the main formatting issues from the original PDF conversion.
"""

import os
import re
import fitz  # PyMuPDF
from typing import List

def simple_improved_pdf_to_markdown(pdf_path: str) -> str:
    """
    Convert PDF to markdown with simple but effective formatting improvements.
    """
    print(f"🔍 Converting PDF to markdown: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File {pdf_path} does not exist!")
        return ""
    
    try:
        doc = fitz.open(pdf_path)
        all_text = ""
        
        # Extract all text
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            all_text += text + "\n"
        
        doc.close()
        
        # Process the text
        return clean_and_format_markdown(all_text)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return ""

def clean_and_format_markdown(text: str) -> str:
    """
    Clean and format the extracted text into proper markdown.
    """
    lines = text.split('\n')
    result = []
    skip_until_content = True
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            if not skip_until_content:
                result.append("")
            continue
        
        # Skip table of contents entries (lines with dots and numbers)
        if re.match(r'^[^.\n]+\.{3,}.*\d+\s*$', line):
            continue
        
        # Skip TOC header
        if 'table of contents' in line.lower():
            continue
        
        # Start processing content after we see actual content
        if skip_until_content:
            # Look for the first real content line (not TOC)
            if not re.match(r'^[^.\n]+\.{3,}.*\d+\s*$', line) and 'table of contents' not in line.lower():
                skip_until_content = False
            else:
                continue
        
        # Now format the content
        formatted_line = format_line(line, lines, i)
        if formatted_line:
            result.append(formatted_line)
    
    # Join and clean up
    markdown = '\n'.join(result)
    return post_process_clean(markdown)

def format_line(line: str, lines: List[str], index: int) -> str:
    """
    Format a single line based on its content and context.
    """
    # Section headers - these are typically standalone and followed by content
    section_keywords = [
        'summary', 'full description', 'core principles', 'roles', 'events', 
        'artifacts', 'application area', 'application examples', 
        'step-by-step guide', 'considerations', 'resource link'
    ]
    
    if any(keyword in line.lower() for keyword in section_keywords):
        # Only make it a header if it's a short line (likely a section title)
        if len(line) < 100:
            return f"\n# {line}\n"
    
    # Handle bullet points
    if line.startswith('•'):
        content = line[1:].strip()
        if content:
            # Check if this looks like a definition (contains a colon)
            if ':' in content:
                parts = content.split(':', 1)
                term = parts[0].strip()
                definition = parts[1].strip() if len(parts) > 1 else ""
                return f"- **{term}**: {definition}"
            else:
                return f"- {content}"
        else:
            # Standalone bullet, might need to combine with next line
            return None
    
    # Handle standalone bullets followed by content on next line
    if line == '•' and index + 1 < len(lines):
        next_line = lines[index + 1].strip()
        if next_line and not next_line.startswith('•'):
            return f"- {next_line}"
    
    # Regular content
    return line

def post_process_clean(markdown: str) -> str:
    """
    Final cleanup of the markdown text.
    """
    # Fix multiple consecutive empty lines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    
    # Fix bullet points that got separated
    # Look for pattern: "•\nContent" and fix it to "- Content"
    markdown = re.sub(r'•\s*\n([^•\n-]+)', r'- \1', markdown)
    
    # Clean up any remaining standalone bullets
    markdown = re.sub(r'\n•\s*\n', '\n', markdown)
    
    # Fix headers that might have extra spacing
    markdown = re.sub(r'\n+#\s+(.+?)\s*\n+', r'\n\n# \1\n\n', markdown)
    
    # Bold important terms in definitions
    important_terms = [
        'Product Owner', 'Scrum Master', 'Development Team', 'Developers',
        'Sprint', 'Sprint Planning', 'Daily Scrum', 'Sprint Review', 
        'Sprint Retrospective', 'Product Backlog', 'Sprint Backlog', 'Increment',
        'Transparency', 'Inspection', 'Adaptation'
    ]
    
    for term in important_terms:
        # Bold the term when it appears at the start of a definition
        pattern = rf'- ({term})\s*([:\(])'
        replacement = rf'- **\1**\2'
        markdown = re.sub(pattern, replacement, markdown)
    
    return markdown.strip()

def main():
    """
    Main function to test the converter.
    """
    pdf_path = "kb_new/SCRUMv2.pdf"
    
    print("🚀 Simple Improved PDF to Markdown Converter")
    print("=" * 60)
    
    # Convert
    markdown_content = simple_improved_pdf_to_markdown(pdf_path)
    
    if not markdown_content:
        print("❌ Conversion failed!")
        return
    
    # Save output
    output_file = "simple_improved_scrum.md"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# SCRUM Methodology\n\n")
            f.write(markdown_content)
        
        print(f"✅ Output saved to: {output_file}")
        print(f"📊 Content length: {len(markdown_content)} characters")
        
        # Show preview
        preview = markdown_content[:500]
        print(f"\n📖 Preview:\n{preview}...")
        
    except Exception as e:
        print(f"❌ Error saving: {e}")

if __name__ == "__main__":
    main()
