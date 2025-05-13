# Standard library imports
import os
import glob
import re
from collections import Counter

# Third-party imports
import PyPDF2

# Local imports
from config import CHUNK_SIZE, CHUNK_OVERLAP
from models import KBMetadata, ProcessingResult

from typing import Mapping
#------------------------------------------------------------------------------
# DOCUMENT PROCESSING
#------------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> tuple[str, int]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        tuple: (extracted text as string, page count)
    """
    text = ""
    page_count = 0
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)
            for page_num in range(page_count):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text, page_count

def char_word_count(text:str) -> int:
    """
    Count the number of characters and words in a string.
    
    Args:
        word: The input string
        
    Returns:
        tuple: (number of characters, number of words)
    """
    # Count characters and words
    charCount = 0
    wordCount = 0
    for i in text:
        charCount += 1
        if i == ' ':
            wordCount += 2
    return charCount, wordCount

def extract_keywords(text, max_keywords=5):
    """
    Extract keywords from text using simple frequency analysis.
    
    Args:
        text: Document content
        max_keywords: Maximum number of keywords to return
        
    Returns:
        list: Top keywords
    """
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Common English stopwords to filter out
    stopwords = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'on', 'at', 'from', 
                'by', 'about', 'as', 'it', 'this', 'that', 'be', 'are', 'was', 'were'}
    
    # Filter out stopwords
    filtered_words = [word for word in words if word not in stopwords]
    
    # Count word frequencies
    word_counts = Counter(filtered_words)
    
    # Get the most common words
    return [word for word, _ in word_counts.most_common(max_keywords)]

def generate_abstract(text, max_length=300):
    """
    Generate a simple abstract by taking the first part of the document.
    
    Args:
        text: Document content
        max_length: Maximum length of abstract
        
    Returns:
        str: Document abstract
    """
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Take the first part of the document
    abstract = text[:max_length]
    
    # Try to end at a sentence boundary
    if len(text) > max_length:
        last_period = abstract.rfind('.')
        if last_period > max_length // 2:  # Only trim if we have a decent amount of text
            abstract = abstract[:last_period + 1]
    
    return abstract

def process_document_content(file_path: str, content: str, page_count: int = 0
                            ) -> ProcessingResult:
    """
    Process document content into chunks with metadata and IDs.
    
    Args:
        file_path: Path to the source document
        content: Text content to be chunked
        page_count: Number of pages in the document (for PDFs)
        
    Returns:
        ProcessingResult containing document chunks, metadata, ids and chunk count
    """
    result = ProcessingResult()
    file_name = os.path.basename(file_path)
    
    # Skip if no content was extracted
    if not content.strip():
        print(f"Warning: No content extracted from {file_name}")
        return result

    char_count, word_count = char_word_count(content)
    file_size = os.path.getsize(file_path)
    keywords = extract_keywords(content)
    abstract = generate_abstract(content)
    metadata = KBMetadata(file_name=file_name,
                        file_size=file_size,
                        file_type=file_name.split('.')[-1],
                        page_count=page_count,
                        word_count=word_count,
                        char_count=char_count,
                        keywords=keywords,
                        source="system_upload",
                        abstract=abstract,
                        ).model_dump() 
    result.metadatas.append(metadata)
    return result

def load_documents_from_directory(directory_path):
    """
    Read and process all supported documents from a directory.
    
    Args:
        directory_path: Path to the directory containing documents
        
    Returns:
        tuple: (documents, metadatas, ids)
    """

    all_metadatas = []
    all_contents = []
    # Get all .txt and .pdf files in the directory
    txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    file_paths = txt_files + pdf_files

    for file_path in file_paths:
        try:
            page_count = 0
            # Handle different file types
            if file_path.lower().endswith('.pdf'):
                content, page_count = extract_text_from_pdf(file_path)
            else:  # Assume it's a text file
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

            # Process the document content
            result = process_document_content(file_path, content, page_count)
            all_metadatas.extend(result.metadatas)
            all_contents.append(content)

            #file_name = os.path.basename(file_path)
            #print(f"Loaded {result.chunk_count} chunks from document: {file_name}")

        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return all_metadatas, all_contents

def load_user_document(file_path):
    """
    Load a single document provided by the user.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        tuple: (documents, metadatas, ids, message)
    """
    try:
        # Handle different file types
        if file_path.lower().endswith('.pdf'):
            content, page_count = extract_text_from_pdf(file_path)
            result = process_document_content(file_path, content, page_count)
        elif file_path.lower().endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json')):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            result = process_document_content(file_path, content)
        else:
            return None, None, None, f"Unsupported file type: {file_path}. Supported types are PDF and text files."

        if not result.documents:
            return None, None, None, f"No content extracted from {os.path.basename(file_path)}"
            
        return result.documents, result.metadatas, result.ids, f"Successfully processed {os.path.basename(file_path)} into {result.chunk_count} chunks"
    
    except Exception as e:
        return None, None, None, f"Error loading {file_path}: {str(e)}"
