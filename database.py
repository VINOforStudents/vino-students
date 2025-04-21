# Standard library imports
import os
from dotenv import load_dotenv

# Local imports
from config import CHROMA_DB_PATH, DOCUMENTS_DIR
from load_documents import load_documents_from_directory

# Third-party imports
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
#------------------------------------------------------------------------------
# DATABASE OPERATIONS
#------------------------------------------------------------------------------

def initialize_vector_db():
    """
    Initialize ChromaDB and load documents if needed.
    
    Returns:
        tuple: (frameworks_collection, user_documents_collection)
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)
    
    try:
        # Create or get the frameworks collection
        collection_fw = client.get_or_create_collection(
            name="frameworks", 
            embedding_function=google_ef
        )
        
        # Create or get the user documents collection
        collection_user = client.get_or_create_collection(
            name="user_documents",
            embedding_function=google_ef
        )
        
        # Process documents only if needed
        if collection_fw.count() == 0:
            print("Frameworks collection is empty. Loading documents...")
            docs, metas, ids = load_documents_from_directory(DOCUMENTS_DIR)
            
            # Add documents to collection if any were loaded
            if docs:
                collection_fw.add(
                    documents=docs,
                    metadatas=metas,
                    ids=ids
                )
                print(f"Added {len(docs)} document chunks to the frameworks collection.")
            else:
                print("No documents were loaded. Please check the directory path.")
        else:
            print(f"Using existing frameworks collection with {collection_fw.count()} document chunks.")
        
        print(f"User documents collection has {collection_user.count()} document chunks.")
        
        return collection_fw, collection_user
        
    except Exception as e:
        print(f"Error initializing ChromaDB collection: {e}")
        raise

# Initialize environment variables
load_dotenv()
    

# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")