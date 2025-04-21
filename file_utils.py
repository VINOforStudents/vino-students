"""
Document processing and retrieval system using ChromaDB and LLM.
This module provides functions for document handling, vector database operations,
and LLM-based question answering to be used by API endpoints.
"""

# Standard library imports
import os

# Local imports
from config import USER_UPLOADS_DIR
from document_processor import load_user_document
from database import collection_user


#------------------------------------------------------------------------------
# FILE MANAGEMENT
#------------------------------------------------------------------------------

def process_command(command):
    """
    Process special commands.
    
    Args:
        command: Command string from the user
        
    Returns:
        str or None: Command result message or None if not a recognized command
    """
    if command.startswith("/upload") or command.startswith("/add"):
        # Extract file path from command if provided
        parts = command.split(" ", 1)
        if len(parts) > 1 and parts[1].strip():
            file_path = parts[1].strip()
            return upload_file(file_path)
        else:
            # Prompt for file path
            file_path = input("Enter the path to the file you want to upload: ")
            return upload_file(file_path)
    elif command.startswith("/list"):
        return list_uploaded_files()
    elif command.startswith("/process"):
        return process_uploaded_files()
    
    return None  # Not a command

def list_uploaded_files():
    """
    List all files that have been uploaded by the user.
    
    Returns:
        str: Formatted list of files
    """
    if not os.path.exists(USER_UPLOADS_DIR) or not os.listdir(USER_UPLOADS_DIR):
        return "No files have been uploaded yet."
    
    files = os.listdir(USER_UPLOADS_DIR)
    
    # Get the details from the collection
    user_docs = {}
    try:
        all_ids = collection_user.get(include=["metadatas"])
        if all_ids and "metadatas" in all_ids:
            for metadata in all_ids["metadatas"]:
                if metadata and "filename" in metadata:
                    filename = metadata["filename"]
                    if filename not in user_docs:
                        user_docs[filename] = 0
                    user_docs[filename] += 1
    except Exception as e:
        return f"Error retrieving document information: {str(e)}"
    
    # Format the output
    result = "Uploaded files:\n"
    for file in files:
        chunks = user_docs.get(file, "Unknown")
        result += f"  - {file} ({chunks} chunks in database)\n"
    
    return result

def process_uploaded_files():
    """
    Process all files in the user_uploads directory that haven't been processed yet.
    
    Returns:
        str: Processing results summary
    """
    if not os.path.exists(USER_UPLOADS_DIR) or not os.listdir(USER_UPLOADS_DIR):
        return "No files found in the uploads directory."
    
    # Get all files in the user_uploads directory
    files = os.listdir(USER_UPLOADS_DIR)
    processed_count = 0
    error_count = 0
    results = []
    
    # Process each file
    for file_name in files:
        file_path = os.path.join(USER_UPLOADS_DIR, file_name)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
            
        # Process the file
        docs, metas, ids, message = load_user_document(file_path)
        
        if docs is None:
            results.append(f"Error: {message}")
            error_count += 1
        else:
            # Add to user collection
            try:
                collection_user.add(
                    documents=docs,
                    metadatas=metas,
                    ids=ids
                )
                results.append(f"Success: {message}")
                processed_count += 1
            except Exception as e:
                results.append(f"Error adding {file_name} to collection: {str(e)}")
                error_count += 1
    
    # Prepare result message
    if processed_count == 0 and error_count == 0:
        return "No compatible files found to process."
    
    summary = f"Processed {processed_count} files with {error_count} errors.\n"
    return summary + "\n".join(results)

def upload_file(file_path):
    """
    Upload a file to the user collection.
    
    Args:
        file_path: Path to the file to upload
        
    Returns:
        str: Upload result message
    """
    # Handle relative paths - convert to absolute
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    # Create a copy in the user_uploads directory
    os.makedirs(USER_UPLOADS_DIR, exist_ok=True)
    file_name = os.path.basename(file_path)
    destination_path = os.path.join(USER_UPLOADS_DIR, file_name)
    
    try:
        # Copy the file to our uploads directory
        with open(file_path, 'rb') as src_file:
            with open(destination_path, 'wb') as dest_file:
                dest_file.write(src_file.read())
        print(f"Copied file to {destination_path}")
    except Exception as e:
        return f"Error copying file to uploads directory: {str(e)}"
    
    # Process the file
    docs, metas, ids, message = load_user_document(destination_path)
    
    if docs is None:
        return message
    
    # Add to user collection
    try:
        collection_user.add(
            documents=docs,
            metadatas=metas,
            ids=ids
        )
        return f"{message}. Added to your documents collection."
    except Exception as e:
        return f"Error adding document to collection: {str(e)}"

