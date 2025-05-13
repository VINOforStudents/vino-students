# Standard library imports
import os

# Database imports
import psycopg2

# Local imports
from document_processor import load_documents_from_directory, extract_text_from_pdf, process_document_content
from config import NEW_DOCUMENTS_DIR, KB_DOCUMENTS_DIR



# Get db info from environment variable
db_info = os.getenv("DB_INFO")
if not db_info:
    raise ValueError("Database not found. Please set the DB_INFO environment variable.")

#------------------------------------------------------------------------------
# DATABASE OPERATIONS
#------------------------------------------------------------------------------


def db_connection():
    """
    Establish a connection to the PostgreSQL database.
    
    Returns:
        conn: A connection object to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(db_info)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise

def create_cursor(conn):
    """
    Create a cursor object for the database connection.
    
    Args:
        conn: A connection object to the PostgreSQL database.
        
    Returns:
        cur: A cursor object for executing SQL commands.
    """
    try:
        cur = conn.cursor()
        return cur
    except Exception as e:
        print(f"Error creating cursor: {e}")
        raise

metadata, content = load_documents_from_directory(NEW_DOCUMENTS_DIR)

def move_files_to_processed():
    """
    Move processed files from the new documents directory to the processed documents directory.
    
    Returns:
        None
    """
    for file_name in os.listdir(NEW_DOCUMENTS_DIR):
        source_path = os.path.join(NEW_DOCUMENTS_DIR, file_name)
        dest_path = os.path.join(KB_DOCUMENTS_DIR, file_name)
        try:
            os.rename(source_path, dest_path)
            print(f"Moved {file_name} to processed documents.")
        except Exception as e:
            print(f"Error moving {file_name}: {e}")

def upload_documents_to_db(metadata_list, content_list):
    """
    Upload multiple document metadata and content to the PostgreSQL database.
    
    Args:
        metadata_list: List of metadata dictionaries for documents.
        content_list: List of document contents.
        
    Returns:
        None
    """
    conn = db_connection()
    cur = create_cursor(conn)

    try:
        # Process all documents
        for i, meta in enumerate(metadata_list):
            # Insert metadata into the database
            cur.execute("""
                INSERT INTO filemetadata (file_name, file_size, file_type, page_count, word_count, char_count, keywords, source, abstract)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (meta['file_name'], meta['file_size'], meta['file_type'],
                  meta['page_count'], meta['word_count'],
                  meta['char_count'], meta['keywords'],
                  meta['source'], meta['abstract']))
            
            # Get the corresponding content
            if isinstance(content_list, list) and i < len(content_list):
                doc = content_list[i]
            else:
                print(f"Warning: Content missing for document {meta['file_name']}")
                continue
                
            # Insert content into the database
            cur.execute("""
                INSERT INTO largeobject (plain_text)
                VALUES (%s)
            """, (doc,))
            
            print(f"Uploaded document: {meta['file_name']}")
        
        conn.commit()
    except Exception as e:
        print(f"Error uploading documents to the database: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


try:
    upload_documents_to_db(metadata, content)
    move_files_to_processed()
except Exception as e:
    print(f"Error in the main process: {e}")