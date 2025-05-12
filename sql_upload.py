# Standard library imports
import os

# Database imports
import psycopg2

# Local imports
from document_processor import load_documents_from_directory, extract_text_from_pdf, process_document_content
from config import NEW_DOCUMENTS_DIR, DOCUMENTS_DIR



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




metadata = load_documents_from_directory(NEW_DOCUMENTS_DIR)
print(metadata)
#cur.close()
#conn.close()

