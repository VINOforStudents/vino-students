import os
from dotenv import load_dotenv
from supabase import create_client, Client

from config import NEW_DOCUMENTS_DIR, KB_DOCUMENTS_DIR, NEW_USER_UPLOADS_DIR, USER_UPLOADS_DIR

load_dotenv()

url: str = os.environ.get("SUPABASE_URL") or ""
key: str = os.environ.get("SUPABASE_KEY") or ""
supabase: Client = create_client(url, key) 



def upload_move_to_processed(from_dir, to_dir):
    """
    Upload to file storage and move processed files from the new documents directory to the processed documents directory.
    
    Returns:
        str: Success message
    """
    for file in os.listdir(from_dir):
        source = os.path.join(from_dir, file)
        try:
            if from_dir == NEW_DOCUMENTS_DIR:
                # Upload to Supabase storage
                response = supabase.storage.from_('knowledge-base').upload(file, source)
            if from_dir == NEW_USER_UPLOADS_DIR:
                response = supabase.storage.from_('user-uploads').upload(file, source)
            
            # Check if upload was successful or if it's a duplicate
            if hasattr(response, 'get') and response.get('statusCode') == 409:
                print(f"File {file} already exists in storage, skipping upload but moving file...")
            else:
                print(f"Successfully uploaded: {file}")
            
            destination = os.path.join(to_dir, file)
            os.rename(source, destination)
        except Exception as e:
            print(f"Error uploading {file}: {e}")
            # Still move the file even if upload failed
            try:
                destination = os.path.join(to_dir, file)
                os.rename(source, destination)
                print(f"Moved {file} despite upload error")
            except:
                print(f"Failed to move {file}")
            continue
    return 'Files uploaded and moved successfully'

def upload_documents_to_sql(metadata_list, content_list):
    """
    Upload multiple document metadata and content to Supabase.
    
    Args:
        metadata_list: List of combined metadata dictionaries (file + chunk metadata).
        content_list: List of chunk contents.
        
    Returns:
        str: Success message or error information
        
    Raises:
        Exception: If there's an error processing the documents
    """
    try:        # Group chunks by filename to store whole files instead of individual chunks
        files_data = {}
        
        # Group metadata and content by filename
        for i, meta in enumerate(metadata_list):
            if i >= len(content_list):
                print(f"Warning: Content missing for metadata at index {i}")
                continue
            
            # Validate metadata format
            if not isinstance(meta, dict):
                print(f"Warning: Expected dictionary but got {type(meta)} at index {i}")
                continue
                
            filename = meta.get('filename', 'unknown')
            
            if filename not in files_data:
                files_data[filename] = {
                    'file_metadata': meta,  # Use first chunk's metadata for file-level info
                    'chunks': []
                }
            
            # Add chunk content
            files_data[filename]['chunks'].append(content_list[i])
        
        # Process each file
        uploaded_count = 0
        failed_files = []
        
        for filename, file_data in files_data.items():
            try:
                meta = file_data['file_metadata']
                chunks = file_data['chunks']
                
                # Reconstruct full document from chunks
                full_document = '\n\n'.join(chunks)
                
                # Check if document already exists
                existing_doc = (
                    supabase.table("filemetadata")
                    .select("id")
                    .eq("file_name", filename)
                    .execute()
                )
                
                if existing_doc.data:
                    # Document already exists - this is now considered an error for individual processing
                    error_msg = f"Document {filename} already exists in database"
                    print(f"Error uploading {filename}: {{'statusCode': 409, 'error': 'Duplicate', 'message': 'The resource already exists'}}")
                    failed_files.append(filename)
                    continue
                    
                # Insert file metadata into the filemetadata table
                metadata_response = (
                    supabase.table("filemetadata")
                    .insert({
                        "file_name": filename,
                        "file_size": meta.get('file_size', 0),
                        "file_type": meta.get('file_type', 'unknown'),
                        "page_count": meta.get('page_count', 0),
                        "word_count": meta.get('word_count', 0),
                        "char_count": meta.get('char_count', 0),
                        "keywords": meta.get('keywords', []),
                        "source": meta.get('source', 'system_upload'),
                        "abstract": meta.get('abstract', '')
                    })
                    .execute()
                )
                
                # Check if metadata insertion was successful
                if not metadata_response.data:
                    print(f"Failed to insert metadata for {filename}")
                    failed_files.append(filename)
                    continue
                    
                # Get the ID of the newly inserted metadata record
                metadata_id = metadata_response.data[0]['id']
                
                # Insert full document content into the largeobject table
                content_response = (
                    supabase.table("largeobject")
                    .insert({
                        "oid": metadata_id,
                        "plain_text": full_document
                    })
                    .execute()
                )
                
                uploaded_count += 1
                print(f"Uploaded document: {filename} ({len(chunks)} chunks combined)")
                
            except Exception as file_error:
                print(f"Error uploading {filename}: {file_error}")
                failed_files.append(filename)
                continue
        
        # If processing individual files and any failed, raise an exception
        if failed_files and len(files_data) == 1:
            # Single file processing - raise error if it failed
            raise Exception(f"Failed to upload {failed_files[0]}")
        
        if uploaded_count > 0:
            return f"Successfully uploaded {uploaded_count} documents to database"
        else:
            if failed_files:
                raise Exception(f"No documents uploaded - all failed: {', '.join(failed_files)}")
            else:
                return "No new documents were uploaded"
            
    except Exception as e:
        error_message = f"Error uploading documents to Supabase: {str(e)}"
        print(f"Error details: {type(e).__name__}")
        raise e  # Re-raise the exception for individual file processing

def upload_single_file_to_storage(source_path, filename, from_dir):
    """
    Upload a single file to Supabase storage.
    
    Args:
        source_path: Full path to the source file
        filename: Name of the file
        from_dir: Directory the file is coming from
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if from_dir == NEW_DOCUMENTS_DIR:
            # Upload to Supabase storage
            response = supabase.storage.from_('knowledge-base').upload(filename, source_path)
        elif from_dir == NEW_USER_UPLOADS_DIR:
            response = supabase.storage.from_('user-uploads').upload(filename, source_path)
        else:
            print(f"Unknown directory: {from_dir}")
            return False
        
        # Check if upload was successful or if it's a duplicate
        if hasattr(response, 'get') and response.get('statusCode') == 409:
            print(f"File {filename} already exists in storage, skipping upload...")
            return True  # Consider duplicate as success
        else:
            print(f"Successfully uploaded to storage: {filename}")
            return True
            
    except Exception as e:
        print(f"Error uploading {filename} to storage: {e}")
        return False