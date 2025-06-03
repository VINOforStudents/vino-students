"""Supabase and ChromaDB Integration Module

This module provides functionality to upload documents to Supabase and ChromaDB,
as well as to ChromaDB.
"""


from database import *
#from upload_supa import *
from typing import Dict, List, Optional, Tuple, Any

from config import *
FRAMEWORKS_COLLECTION = "frameworks"
USER_DOCUMENTS_COLLECTION = "user_documents"

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

#def upload_to_supa(source: str) -> None:
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
        documents, metadatas, ids = load_documents_from_directory(directory)
        
        if not documents:
            return f"No documents found in {directory}."
        
        # Process keywords in metadata
        for metadata in metadatas:
            if metadata and 'keywords' in metadata and isinstance(metadata['keywords'], list):
                metadata['keywords'] = ', '.join(metadata['keywords'])
            # Ensure source is set correctly in metadata
            if metadata:
                metadata['source'] = source
        
        # Add documents to the appropriate collection
        uploaded_count = 0
        for doc, metadata, doc_id in zip(documents, metadatas, ids):
            try:
                target_collection.add(documents=[doc], metadatas=[metadata], ids=[doc_id])
                uploaded_count += 1
            except Exception as e:
                print(f"Warning: Failed to upload document {doc_id}: {e}")
        
        if uploaded_count > 0:
            return f"Successfully uploaded {uploaded_count} document chunks to {collection_name} collection."
        else:
            return f"No documents were successfully uploaded to {collection_name} collection."
            
    except Exception as e:
        print(f"❌ Error uploading documents to ChromaDB: {e}")
        return f"Error uploading documents to ChromaDB: {e}"

#def upload_documents(source: str) -> None:
    """
    Uploads documents to both Supabase and ChromaDB based on source type.
    
    Args:
        source (str): Either "user_upload" or "system_upload"
    """
    print(f"Starting upload process for source: {source}")
    
    

    # Upload to ChromaDB
    chroma_result = upload_documents_to_chromadb(source)
    print(chroma_result)

    # Upload to Supabase
    supa_result = upload_to_supa(source)
    print(supa_result)
    
    print(f"Upload process completed for source: {source}")

result = upload_documents_to_chromadb("system_upload")  # or "user_upload"
print(result)