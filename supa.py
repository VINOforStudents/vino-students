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
            print(f"Successfully uploaded: {file}")
            destination = os.path.join(to_dir, file)
            os.rename(source, destination)
        except Exception as e:
            print(f"Error uploading {file}: {e}")
            continue
    return 'Files uploaded and moved successfully'

def upload_documents_to_sql(metadata_list, content_list):
    """
    Upload multiple document metadata and content to Supabase.
    
    Args:
        metadata_list: List of metadata dictionaries for documents.
        content_list: List of document contents.
        
    Returns:
        str: Success message or error information
    """
    try:
        # Process all documents
        for i, meta in enumerate(metadata_list):
            # Get the corresponding content
            if isinstance(content_list, list) and i < len(content_list):
                doc_content = content_list[i]
            else:
                print(f"Warning: Content missing for document {meta['file_name']}")
                continue
                
            # Insert metadata into the filemetadata table
            metadata_response = (
                supabase.table("filemetadata")
                .insert({
                    "file_name": meta['file_name'],
                    "file_size": meta['file_size'],
                    "file_type": meta['file_type'],
                    "page_count": meta['page_count'],
                    "word_count": meta['word_count'],
                    "char_count": meta['char_count'],
                    "keywords": meta['keywords'],
                    "source": meta['source'],
                    "abstract": meta['abstract']
                })
                .execute()
            )
            
            # Get the ID of the newly inserted metadata record
            metadata_id = metadata_response.data[0]['id']
            
            # Insert content into the largeobject table with reference to metadata
            content_response = (
                supabase.table("largeobject")
                .insert({
                    "oid": metadata_id,
                    "plain_text": doc_content
                })
                .execute()
            )
            
            print(f"Uploaded document: {meta['file_name']}")
        
        return "All documents uploaded successfully"
    except Exception as e:
        error_message = f"Error uploading documents to Supabase: {str(e)}"
        print(error_message)
        return error_message