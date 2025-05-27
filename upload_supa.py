""" Program to upload a files to Supabase storage."""
import os

from supa import upload_move_to_processed, upload_documents_to_sql
from document_processor import load_documents_from_directory

from config import NEW_DOCUMENTS_DIR, NEW_USER_UPLOADS_DIR, KB_DOCUMENTS_DIR, USER_UPLOADS_DIR

def check_not_empty(directory):
    """
    Check if the directory is not empty.
    
    Args:
        directory: Path to the directory to check.
        
    Returns:
        bool: True if the directory is empty, False otherwise.
    """
    return  any(os.scandir(directory))

def process_directory(from_dir, to_dir, source="system_upload"):
    """
    Process documents from a specific directory and upload to Supabase.
    
    Args:
        from_dir: Path to the directory to process.
        to_dir: Path to move processed files.
        source: Source identifier for the documents.
        
    Returns:
        bool: True if documents were processed, False otherwise.
    """
    if check_not_empty(from_dir):
        metadata, content = load_documents_from_directory(from_dir, source)
        try:
            upload_documents_to_sql(metadata, content)
            upload_move_to_processed(from_dir, to_dir)
            print(f"Successfully processed documents from {from_dir}")
            return True
        except Exception as e:
            error_message = f"Error uploading documents from {from_dir} to Supabase: {str(e)}"
            print(error_message)
    else:
        print(f"No documents to upload from {from_dir}")
    return False

def upload_documents():
    """
    Upload documents from all configured directories to Supabase.
    
    Returns:
        str: Success message or error information
    """
    processed_docs = False
    
    # Process NEW_DOCUMENTS_DIR
    if process_directory(NEW_DOCUMENTS_DIR, KB_DOCUMENTS_DIR):
        processed_docs = True
        
    # Process NEW_USER_UPLOADS_DIR with source "user_uploads"
    if process_directory(NEW_USER_UPLOADS_DIR, USER_UPLOADS_DIR, source="user_uploads"):
        processed_docs = True
        
    if not processed_docs:
        return "No documents were processed from any directory."
    
    return "Document processing complete."

if __name__ == "__main__":
    result = upload_documents()
    print(result)