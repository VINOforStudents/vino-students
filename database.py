# Standard library imports
import os
from dotenv import load_dotenv

# Local imports
from config import CHROMA_DB_PATH, DOCUMENTS_DIR
from document_processor import load_documents_from_directory

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

def list_documents_in_collection(collection_name=None):
    """
    List all documents in a specific collection or in all collections.
    
    Args:
        collection_name (str, optional): The name of the collection to query. 
                                         If None, lists documents from all collections.
    
    Returns:
        dict: Information about the queried collection(s)
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    if collection_name:
        collections = [client.get_collection(name=collection_name)]
    else:
        collections = [
            client.get_collection(name="frameworks"),
            client.get_collection(name="user_documents")
        ]
    
    results = {}
    
    for collection in collections:
        # Get all documents from the collection
        documents = collection.get()
        
        # Format the results
        collection_data = {
            "count": collection.count(),
            "documents": []
        }
        
        # Add document details
        for i in range(len(documents["ids"])):
            doc_info = {
                "id": documents["ids"][i],
                "metadata": documents["metadatas"][i] if documents["metadatas"] else None,
                "text_preview": documents["documents"][i][:100] + "..." if documents["documents"][i] else None
            }
            collection_data["documents"].append(doc_info)
        
        results[collection.name] = collection_data
        print(f"Collection '{collection.name}' has {collection.count()} documents.")
    return results


# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")