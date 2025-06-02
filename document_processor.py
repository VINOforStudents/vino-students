# Standard library imports
import os
import glob
import re
from collections import Counter

# Third-party imports
import PyPDF2

# Local imports
from config import CHUNK_SIZE, CHUNK_OVERLAP,NEW_DOCUMENTS_DIR
from models import ProcessingResult, DocumentMetadata, FileMetadata

from typing import Mapping

from chunking import process_single_file, process_documents

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
                page_text = page.extract_text() or ""
                page_text = page_text.replace('\u0000', '')
                text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text, page_count

def char_word_count(text:str) -> tuple[int, int]:
    """
    Count the number of characters and words in a string.
    
    Args:
        word: The input string
        
    Returns:
        tuple: (number of characters, number of words)
    """
    # Count characters and words
    char_count = len(text)
    word_count = len(text.split()) if text.strip() else 0
    return char_count, word_count

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

def process_document_content(file_path: str, content: str, page_count: int = 0,  source: str = "system_upload"
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
    
    # For supported file types that can use the advanced chunking
    file_extension = os.path.splitext(file_path)[1].lower()
    print(f"Processing file: {file_name} (type: {file_extension})")
    if file_extension in ['.md', '.docx', '.pdf']:
        try:
            # Use the advanced chunking from chunking.py
            all_chunk_data = process_single_file(file_path)
            
            # Calculate rich metadata once for the entire document
            char_count, word_count = char_word_count(content)
            file_size = os.path.getsize(file_path)
            keywords = extract_keywords(content)
            abstract = generate_abstract(content)
            
            file_metadata = FileMetadata(
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
            # Extract chunks and create metadata for each chunk
            for i, all_chunk_data in enumerate(all_chunk_data):
                # Add the chunk text to documents
                result.documents.append(all_chunk_data[i].text)
                # Create DocumentMetadata for each chunk with rich metadata
                result.doc_metadatas.append(all_chunk_data[i].metadata)
                # Add file metadata to file_metadatas
                result.file_metadatas.append(file_metadata)
                # Generate unique ID for each chunk
                result.ids.append(all_chunk_data[i].metadata.doc_id)
            
            print(f"Successfully processed {len(all_chunk_data)} chunks from {file_name}")
            return result
            
        except Exception as e:
            print(f"Error using advanced chunking for {file_name}: {e}")
            print("Falling back to simple processing...")
    # Fallback for unsupported file types or if advanced chunking fails
    # Create basic document-level metadata
    char_count, word_count = char_word_count(content)
    file_size = os.path.getsize(file_path)
    keywords = extract_keywords(content)
    abstract = generate_abstract(content)

    #all_chunk_data, chunk_text = process_single_file(file_path)
    result.documents.append(content)  # Add the full document as a single chunk
    result.ids.append(file_name)  # Use file name as ID for the full document

    file_metadata = FileMetadata(
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
    result.doc_metadatas.append(all_chunk_data)
    result.file_metadatas.append(file_metadata)

    print(f"Processed 1 chunk (full document) from {file_name}")
    return result

def load_documents_from_directory(directory_path, source="system_upload"):
    """
    Read and process all supported documents from a directory.
    
    Args:
        directory_path: Path to the directory containing documents
        source: Source identifier for the documents
        
    Returns:
        tuple: (documents, metadatas, ids)
    """

    all_documents = []
    all_metadatas = []
    all_ids = []

    # Get all .txt and .pdf files in the directory
    txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    md_files = glob.glob(os.path.join(directory_path, "*.md"))
    file_paths = txt_files + pdf_files + md_files

    for file_path in file_paths:
        try:
            page_count = 1
            # Handle different file types
            if file_path.lower().endswith('.pdf'):
                content, page_count = extract_text_from_pdf(file_path)
            else:  # Assume it's a text file
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    page_count = max(1, int(len(content.splitlines())/40))  # Count pages as 40 lines for text files
            result = process_document_content(file_path, content, page_count, source)
            all_documents.extend(result.documents)
            # Convert Pydantic models to dictionaries for ChromaDB
            all_metadatas.extend([metadata.model_dump() for metadata in result.doc_metadatas])
            all_metadatas.extend([metadata.model_dump() for metadata in result.file_metadatas])
            all_ids.extend(result.ids)

            # Log the number of chunks loaded
            file_name = os.path.basename(file_path)
            print(f"Loaded {len(result.documents)} chunks from document: {file_name}")

        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return all_documents, all_metadatas, all_ids

def load_user_document(file_path):
    """
    Load a single document provided by the user.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        tuple: (metadatas, documents, message)
    """
    page_count = 1 # Default to 1 for non-PDF files
    try:
        # Handle different file types
        if file_path.lower().endswith('.pdf'):
            content, page_count = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json')):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                content = content.replace('\u0000', '')
            except UnicodeDecodeError:
                with open(file_path, 'rb') as file:
                    content = file.read().decode('utf-8', errors='replace')
                    content = content.replace('\u0000', '')
        else:
            return None, None, f"Unsupported file type: {file_path}. Supported types are PDF and text files."
        
        result = process_document_content(file_path, content, page_count, source="user_upload")
        
        if not result.documents:
            return None, None, f"No content extracted from {os.path.basename(file_path)}"
            
        return result.metadatas, result.documents, f"Successfully processed {len(result.documents)} chunks from {os.path.basename(file_path)}"
        
    except Exception as e:
        return None, None,  f"Error loading {file_path}: {str(e)}"
