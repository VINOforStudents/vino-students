import os
#------------------------------------------------------------------------------
# CONSTANTS AND CONFIGURATION
#------------------------------------------------------------------------------

CHROMA_DB_PATH = os.path.join(os.getcwd(), "chromadb")
DOCUMENTS_DIR = os.path.join(os.getcwd(), "documents")
NEW_DOCUMENTS_DIR = os.path.join(os.getcwd(), "kb_new")
KB_DOCUMENTS_DIR = os.path.join(os.getcwd(), "kb")
USER_UPLOADS_DIR = os.path.join(os.getcwd(), "user_uploads")
NEW_USER_UPLOADS_DIR = os.path.join(os.getcwd(), "new_user_uploads")
CHUNK_SIZE = 2000  # Increased from 500 to 2000 characters for better context
CHUNK_OVERLAP = 200  # Proportional increase in overlap