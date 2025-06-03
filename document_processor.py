"""
Document processing module for text extraction, chunking, and metadata generation.

This module provides functionality to:
- Extract text from various document formats (PDF, TXT, MD)
- Generate document metadata (keywords, abstracts, statistics)
- Process documents into chunks for vector storage
- Load and process documents from directories
"""

# Standard library imports
import os
import glob
import re
from collections import Counter
from typing import Tuple, List

# Third-party imports
import PyPDF2

# Local imports
from config import CHUNK_SIZE, CHUNK_OVERLAP, NEW_DOCUMENTS_DIR
from models import ProcessingResult, DocumentMetadata, FileMetadata
from chunking import process_single_file, process_documents

# Configuration constants
DEBUG_MODE = False  # Set to True to enable debug output
DEFAULT_MAX_KEYWORDS = 5
DEFAULT_ABSTRACT_LENGTH = 300
LINES_PER_PAGE = 40  # Estimate for text files
SUPPORTED_EXTENSIONS = ['.md', '.docx', '.pdf']

# Common English stopwords for keyword extraction
STOPWORDS = {
    'and', 'the', 'is', 'in', 'to', 'of', 'for', 'with', 'on', 'at', 'from',
    'by', 'about', 'as', 'it', 'this', 'that', 'be', 'are', 'was', 'were',
    'an', 'or', 'but', 'if', 'then', 'because', 'when', 'where', 'why', 'how'
}
#------------------------------------------------------------------------------
# TEXT EXTRACTION FUNCTIONS
#------------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> Tuple[str, int]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Tuple of (extracted text as string, page count)
    """
    text = ""
    page_count = 0
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)
            
            for page_num in range(page_count):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text() or ""
                # Remove null characters that can cause issues
                page_text = page_text.replace('\u0000', '')
                text += page_text + "\n"
                
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        
    return text, page_count


def extract_text_from_file(file_path: str) -> Tuple[str, int]:
    """
    Extract text content from various file types.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (extracted text, estimated page count)
    """
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    else:
        # Handle text files (txt, md, etc.)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Estimate page count based on line count
                page_count = max(1, len(content.splitlines()) // LINES_PER_PAGE)
                return content, page_count
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return "", 1


#------------------------------------------------------------------------------
# METADATA GENERATION FUNCTIONS
#------------------------------------------------------------------------------

def char_word_count(text: str) -> Tuple[int, int]:
    """
    Count the number of characters and words in a string.
    
    Args:
        text: The input string
        
    Returns:
        Tuple of (character count, word count)
    """
    char_count = len(text)
    word_count = len(text.split()) if text.strip() else 0
    return char_count, word_count


def extract_keywords(text: str, max_keywords: int = DEFAULT_MAX_KEYWORDS) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis.
    
    Args:
        text: Document content
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of top keywords
    """
    # Convert to lowercase and extract words (3+ characters)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter out stopwords
    filtered_words = [word for word in words if word not in STOPWORDS]
    
    # Count word frequencies and get most common
    word_counts = Counter(filtered_words)
    return [word for word, _ in word_counts.most_common(max_keywords)]


def generate_abstract(text: str, max_length: int = DEFAULT_ABSTRACT_LENGTH) -> str:
    """
    Generate a simple abstract by taking the first part of the document.
    
    Args:
        text: Document content
        max_length: Maximum length of abstract
        
    Returns:
        Document abstract
    """
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Take the first part of the document
    abstract = text[:max_length]
    
    # Try to end at a sentence boundary for better readability
    if len(text) > max_length:
        last_period = abstract.rfind('.')
        if last_period > max_length // 2:  # Only trim if we have enough text
            abstract = abstract[:last_period + 1]
    
    return abstract


def create_file_metadata(file_path: str, content: str, page_count: int, 
                        source: str = "system_upload") -> FileMetadata:
    """
    Create file-level metadata for a document.
    
    Args:
        file_path: Path to the source document
        content: Document content
        page_count: Number of pages in the document
        source: Source identifier for the document
        
    Returns:
        FileMetadata object containing document statistics and metadata
    """
    file_name = os.path.basename(file_path)
    char_count, word_count = char_word_count(content)
    file_size = os.path.getsize(file_path)
    keywords = extract_keywords(content)
    abstract = generate_abstract(content)
    
    return FileMetadata(
        source=source,
        filename=file_name,
        file_size=file_size,
        file_type=os.path.splitext(file_path)[1].lstrip('.'),
        page_count=page_count,
        word_count=word_count,
        char_count=char_count,
        keywords=keywords,
        abstract=abstract
    )


#------------------------------------------------------------------------------
# DOCUMENT PROCESSING FUNCTIONS
#------------------------------------------------------------------------------

def process_document_content(file_path: str, content: str, page_count: int = 0, 
                           source: str = "system_upload") -> ProcessingResult:
    """
    Process document content into chunks with metadata and IDs.
    
    Args:
        file_path: Path to the source document
        content: Text content to be chunked
        page_count: Number of pages in the document (for PDFs)
        source: Source identifier for the document
        
    Returns:
        ProcessingResult containing document chunks, metadata, ids and chunk count
    """
    result = ProcessingResult()
    file_name = os.path.basename(file_path)
    
    # Skip if no content was extracted
    if not content.strip():
        print(f"Warning: No content extracted from {file_name}")
        return result
    
    file_extension = os.path.splitext(file_path)[1].lower()
    print(f"Processing file: {file_name} (type: {file_extension})")
    
    # Try advanced chunking for supported file types
    if file_extension in SUPPORTED_EXTENSIONS:
        try:
            return _process_with_advanced_chunking(file_path, content, page_count, source)
        except Exception as e:
            print(f"Error using advanced chunking for {file_name}: {e}")
            print("Falling back to simple processing...")
    
    # Fallback to simple processing
    return _process_with_simple_chunking(file_path, content, page_count, source)


def _process_with_advanced_chunking(file_path: str, content: str, page_count: int, 
                                  source: str) -> ProcessingResult:
    """
    Process document using advanced chunking from chunking.py module.
    
    Args:
        file_path: Path to the source document
        content: Text content of the document
        page_count: Number of pages in the document
        source: Source identifier for the document
        
    Returns:
        ProcessingResult with advanced chunking applied
    """
    result = ProcessingResult()
    file_name = os.path.basename(file_path)
    
    # Use the advanced chunking from chunking.py
    all_chunk_data = process_single_file(file_path)
    
    # Create file metadata once for the entire document
    file_metadata = create_file_metadata(file_path, content, page_count, source)
    
    # Process each chunk
    for chunk_data in all_chunk_data:
        result.documents.append(chunk_data.text)
        result.doc_metadatas.append(chunk_data.metadata)
        result.file_metadatas.append(file_metadata)
        result.ids.append(chunk_data.metadata.doc_id)
    
    print(f"Successfully processed {len(all_chunk_data)} chunks from {file_name}")
    return result


def _process_with_simple_chunking(file_path: str, content: str, page_count: int, 
                                source: str) -> ProcessingResult:
    """
    Process document using simple chunking (entire document as one chunk).
    
    Args:
        file_path: Path to the source document
        content: Text content of the document
        page_count: Number of pages in the document
        source: Source identifier for the document
        
    Returns:
        ProcessingResult with simple chunking applied
    """
    result = ProcessingResult()
    file_name = os.path.basename(file_path)
    
    # Add the full document as a single chunk
    result.documents.append(content)
    result.ids.append(file_name)
    
    # Create metadata
    file_metadata = create_file_metadata(file_path, content, page_count, source)
    doc_metadata = DocumentMetadata(
        doc_id=f"{os.path.splitext(file_name)[0]}_1",
        chunk_number=1,
        chunk_length=len(content),
        section="Full Document"
    )
    
    result.doc_metadatas.append(doc_metadata)
    result.file_metadatas.append(file_metadata)
    
    print(f"Processed 1 chunk (full document) from {file_name}")
    return result


def _print_debug_info(file_name: str, result: ProcessingResult, file_path: str, 
                     page_count: int) -> None:
    """
    Print detailed debug information for processed documents.
    
    Args:
        file_name: Name of the processed file
        result: Processing result containing metadata
        file_path: Path to the source file
        page_count: Number of pages in the document
    """
    print("\n" + "="*60)
    print(f"DOCUMENT PROCESSED: {file_name}")
    print("="*60)
    print(f"Number of chunks: {len(result.documents)}")
    print(f"File size: {os.path.getsize(file_path):,} bytes")
    print(f"Page count: {page_count}")
    
    # Show sample of metadata for first chunk
    if result.file_metadatas:
        file_meta = result.file_metadatas[0]
        print(f"Word count: {file_meta.word_count:,}")
        print(f"Character count: {file_meta.char_count:,}")
        print(f"Keywords: {', '.join(file_meta.keywords)}")
        print(f"Abstract: {file_meta.abstract[:100]}...")
    print("="*60 + "\n")


def _get_supported_files(directory_path: str) -> List[str]:
    """
    Get all supported document files from a directory.
    
    Args:
        directory_path: Path to the directory to scan
        
    Returns:
        List of file paths for supported document types
    """
    file_patterns = ["*.txt", "*.pdf", "*.md"]
    all_files = []
    
    for pattern in file_patterns:
        files = glob.glob(os.path.join(directory_path, pattern))
        all_files.extend(files)
    
    return all_files


#------------------------------------------------------------------------------
# MAIN PROCESSING FUNCTIONS
#------------------------------------------------------------------------------

def load_documents_from_directory(directory_path: str = NEW_DOCUMENTS_DIR, 
                                source: str = "system_upload") -> Tuple[List[str], List[dict], List[str]]:
    """
    Read and process all supported documents from a directory.
    
    Args:
        directory_path: Path to the directory containing documents
        source: Source identifier for the documents
        
    Returns:
        Tuple of (documents, metadatas, ids)
    """
    all_documents = []
    all_metadatas = []
    all_ids = []

    # Get all supported files in the directory
    file_paths = _get_supported_files(directory_path)
    
    if not file_paths:
        print(f"No supported documents found in {directory_path}")
        return all_documents, all_metadatas, all_ids

    print(f"Found {len(file_paths)} documents to process in {directory_path}")

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        try:
            # Extract text content based on file type
            content, page_count = extract_text_from_file(file_path)
            
            # Process the document content
            result = process_document_content(file_path, content, page_count, source)
            
            # Aggregate results
            all_documents.extend(result.documents)
            all_ids.extend(result.ids)
            
            # Convert Pydantic models to dictionaries for ChromaDB
            for doc_meta, file_meta in zip(result.doc_metadatas, result.file_metadatas):
                combined_metadata = {
                    **doc_meta.model_dump(),  # Document-specific metadata
                    **file_meta.model_dump()  # File-level metadata
                }
                all_metadatas.append(combined_metadata)
            
            # Debug output if enabled
            if DEBUG_MODE:
                _print_debug_info(file_name, result, file_path, page_count)
        
            # Log successful processing
            print(f"✓ Successfully loaded {len(result.documents)} chunks from: {file_name}")

        except Exception as e:
            print(f"✗ Error loading {file_name}: {e}")
            continue  # Continue with next file instead of stopping
    
    print(f"\nProcessing complete: {len(all_documents)} total chunks from {len(file_paths)} files")
    return all_documents, all_metadatas, all_ids