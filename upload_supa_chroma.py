"""Supabase and ChromaDB Integration Module

This module provides functionality to upload documents to Supabase and ChromaDB,
as well as to ChromaDB.
"""

import os

from database import initialize_vector_db
from upload_supa import *
from document_processor import load_documents_from_directory
from typing import Dict, List, Optional, Tuple, Any

from config import *
FRAMEWORKS_COLLECTION = "frameworks"
USER_DOCUMENTS_COLLECTION = "user_documents"

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

def upload_to_supa(source: str) -> None:
    """
    Uploads documents to Supabase.
    """
    if source == "user_upload":
        success = process_directory(NEW_USER_UPLOADS_DIR, USER_UPLOADS_DIR, source=source)
        if success:
            print("User documents uploaded to Supabase successfully.")
        else:
            print("Error uploading user documents to Supabase.")
    elif source == "system_upload":
        success = process_directory(NEW_DOCUMENTS_DIR, KB_DOCUMENTS_DIR, source=source)
        if success:
            print("KB documents uploaded to Supabase successfully.")
        else:
            print("Error uploading KB documents to Supabase.")
    else:
        print(f"Unknown source: {source}. No documents uploaded.")

def upload_documents_to_chromadb(source: str = "system_upload") -> str:
    """
    Uploads documents to ChromaDB based on the source type.
    Files are processed individually - successful files don't depend on failed ones.
    
    Args:
        source (str): Either "user_upload" or "system_upload"
    
    Returns:
        str: Success or error message
    """
    try:
        # Initialize the collections
        collection_fw, collection_user = initialize_vector_db()
        
        # Determine which directory and collection to use based on source
        if source == "user_upload":
            directory = NEW_USER_UPLOADS_DIR
            target_collection = collection_user
            collection_name = "user_documents"
        elif source == "system_upload":
            directory = NEW_DOCUMENTS_DIR
            target_collection = collection_fw
            collection_name = "frameworks"
        else:
            return f"Unknown source: {source}. No documents uploaded."
        
        # Load documents from the appropriate directory
        documents, metadatas, ids, message = load_documents_from_directory(directory)
        
        if not documents:
            return f"No documents found in {directory}."
        
        # Group documents by filename for individual processing
        files_data = {}
        for i, metadata in enumerate(metadatas):
            if i >= len(documents):
                continue
                
            filename = metadata.get('filename', 'unknown')
            if filename not in files_data:
                files_data[filename] = {
                    'documents': [],
                    'metadatas': [],
                    'ids': []
                }
            
            files_data[filename]['documents'].append(documents[i])
            files_data[filename]['metadatas'].append(metadata)
            files_data[filename]['ids'].append(ids[i])
        
        # Process each file individually
        uploaded_count = 0
        failed_files = []
        
        for filename, file_data in files_data.items():
            try:
                # Process keywords in metadata for this file
                for metadata in file_data['metadatas']:
                    if metadata and 'keywords' in metadata and isinstance(metadata['keywords'], list):
                        metadata['keywords'] = ', '.join(metadata['keywords'])
                    # Ensure source is set correctly in metadata
                    if metadata:
                        metadata['source'] = source
                
                # Add documents to the appropriate collection for this file
                file_uploaded_count = 0
                for doc, metadata, doc_id in zip(file_data['documents'], file_data['metadatas'], file_data['ids']):
                    try:
                        target_collection.add(documents=[doc], metadatas=[metadata], ids=[doc_id])
                        file_uploaded_count += 1
                    except Exception as e:
                        print(f"Warning: Failed to upload chunk {doc_id} from {filename}: {e}")
                
                if file_uploaded_count > 0:
                    uploaded_count += file_uploaded_count
                    print(f"✓ Successfully uploaded {file_uploaded_count} chunks from {filename} to ChromaDB")
                else:
                    failed_files.append(filename)
                    print(f"✗ Failed to upload any chunks from {filename} to ChromaDB")
                    
            except Exception as e:
                failed_files.append(filename)
                print(f"✗ Error processing {filename} for ChromaDB: {e}")
                continue
        
        if uploaded_count > 0:
            success_msg = f"Successfully uploaded {uploaded_count} document chunks to {collection_name} collection."
            if failed_files:
                success_msg += f" (Failed files: {', '.join(failed_files)})"
            return success_msg
        else:
            return f"No documents were successfully uploaded to {collection_name} collection."
            
    except Exception as e:
        print(f"❌ Error uploading documents to ChromaDB: {e}")
        return f"Error uploading documents to ChromaDB: {e}"
    
def upload_documents(source: str) -> None:
    """
    Uploads documents to both Supabase and ChromaDB based on source type.
    Files are processed individually to ensure successful files are moved even if others fail.
    
    Args:
        source (str): Either "user_upload" or "system_upload"
    """
    print(f"Starting upload process for source: {source}")
    
    # Upload to ChromaDB (this handles files individually now)
    chroma_result = upload_documents_to_chromadb(source)
    print(chroma_result)

    # Upload to Supabase (this also handles files individually now)
    supa_result = upload_to_supa(source)
    if supa_result:
        print("Supabase upload process completed.")
    else:
        print("No files were processed in Supabase upload.")

    print(f"Upload process completed for source: {source}")
    return "Success"

result = upload_documents("system_upload")  # Change to "system_upload" or "user_upload" as needed
print(result)