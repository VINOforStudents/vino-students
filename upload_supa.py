""" Program to upload a files to Supabase storage."""
import os

from supa import upload_move_to_processed, upload_documents_to_sql, upload_single_file_to_storage
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
    Each file is processed individually - successful files are moved even if others fail.
    
    Args:
        from_dir: Path to the directory to process.
        to_dir: Path to move processed files.
        source: Source identifier for the documents.
        
    Returns:
        bool: True if any documents were processed successfully, False otherwise.
    """
    if check_not_empty(from_dir):
        documents, metadatas, ids, message = load_documents_from_directory(from_dir, source)
        
        if not documents:
            print(f"No documents to upload from {from_dir}")
            return False
            
        # Group documents by filename for individual processing
        files_data = {}
        for i, meta in enumerate(metadatas):
            if i >= len(documents):
                continue
                
            filename = meta.get('filename', 'unknown')
            if filename not in files_data:
                files_data[filename] = {
                    'documents': [],
                    'metadatas': [],
                    'ids': []
                }
            
            files_data[filename]['documents'].append(documents[i])
            files_data[filename]['metadatas'].append(meta)
            files_data[filename]['ids'].append(ids[i])
        
        processed_any = False
          # Process each file individually
        for filename, file_data in files_data.items():
            try:
                # Try to upload this specific file's data
                upload_documents_to_sql(file_data['metadatas'], file_data['documents'])
                
                # If successful, move the file
                source_path = os.path.join(from_dir, filename)
                destination_path = os.path.join(to_dir, filename)
                
                if os.path.exists(source_path):
                    try:
                        # Upload to storage first
                        storage_success = upload_single_file_to_storage(source_path, filename, from_dir)
                        if storage_success:
                            # Then move the file
                            os.rename(source_path, destination_path)
                            print(f"✓ Successfully processed and moved: {filename}")
                            processed_any = True
                        else:
                            print(f"⚠ Storage upload failed for {filename}, not moving file")
                    except Exception as move_error:
                        print(f"⚠ Failed to move {filename}: {move_error}")
                        # File was uploaded to SQL successfully but couldn't be moved
                        # This is still considered a partial success
                        processed_any = True
                else:
                    print(f"⚠ Warning: Source file not found: {filename}")
                    # Still consider this processed since the data was uploaded to SQL
                    
            except Exception as e:
                print(f"✗ Error processing {filename}: {e}")
                print(f"Failed to move {filename}")
                # Don't move this file - continue with next file
                continue
        
        if processed_any:
            print(f"Successfully processed some documents from {from_dir}")
            return True
        else:
            print(f"No documents were successfully processed from {from_dir}")
            return False
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