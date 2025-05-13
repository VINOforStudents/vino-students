# Standard library imports
import os
import glob

# Third-party imports
import PyPDF2

# Local imports
from config import CHUNK_SIZE, CHUNK_OVERLAP
from models import KBMetadata, ProcessingResult

from typing import Mapping
#------------------------------------------------------------------------------
# DOCUMENT PROCESSING
#------------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Extracted text as a string
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text

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


def process_document_content(file_path: str, content: str, 
                            ) -> ProcessingResult:
    """
    Process document content into chunks with metadata and IDs.
    
    Args:
        file_path: Path to the source document
        content: Text content to be chunked
        chunk_size: Size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        
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
    #.chunk_count = chunk_number - 1
    file_size = os.path.getsize(file_path)
    metadata = KBMetadata(file_name=file_name,
                        file_size=file_size,
                        file_type=file_name.split('.')[-1],
                        page_count=0,  # Placeholder for page count
                        word_count=word_count,
                        char_count=char_count,
                        keywords=[],  # Placeholder for keywords
                        source="system_upload",
                        abstract="", # Placeholder for abstract
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

    #all_metadatas = []

    # Get all .txt and .pdf files in the directory
    txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    file_paths = txt_files + pdf_files

    for file_path in file_paths:
        try:
            # Handle different file types
            if file_path.lower().endswith('.pdf'):
                content = extract_text_from_pdf(file_path)
            else:  # Assume it's a text file
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

            # Process the document content
            result = process_document_content(file_path, content)
            

            #file_name = os.path.basename(file_path)
            #print(f"Loaded {result.chunk_count} chunks from document: {file_name}")

        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return result.metadatas, content

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
            content = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json')):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            return None, None, None, f"Unsupported file type: {file_path}. Supported types are PDF and text files."

        # Process the document content
        result = process_document_content(file_path, content)
        
        if not result.documents:
            return None, None, None, f"No content extracted from {os.path.basename(file_path)}"
            
        return result.documents, result.metadatas, result.ids, f"Successfully processed {os.path.basename(file_path)} into {result.chunk_count} chunks"
    
    except Exception as e:
        return None, None, None, f"Error loading {file_path}: {str(e)}"
