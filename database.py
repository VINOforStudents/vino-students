"""
ChromaDB Vector Database Operations Module

This module provides a clean interface for managing ChromaDB vector databases,
including initialization, document management, and collection operations.
"""

# Standard library imports
import os
import logging
from typing import Dict, List, Optional, Tuple, Any

# Third-party imports
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv

# Local imports
from config import CHROMA_DB_PATH, KB_DOCUMENTS_DIR, NEW_DOCUMENTS_DIR
from document_processor import load_documents_from_directory

# Initialize environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
FRAMEWORKS_COLLECTION = "frameworks"
USER_DOCUMENTS_COLLECTION = "user_documents"


class DatabaseManager:
    """
    A manager class for ChromaDB operations providing a clean interface
    for vector database management.
    """
    
    def __init__(self):
        """Initialize the DatabaseManager with API key validation."""
        self.api_key = self._get_api_key()
        self.client = None
        self.embedding_function = None
    
    def _get_api_key(self) -> str:
        """
        Get and validate the Google API key from environment variables.
        
        Returns:
            str: The API key
            
        Raises:
            ValueError: If API key is not found
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "API key not found. Please set the GOOGLE_API_KEY environment variable."
            )
        return api_key
    
    def _get_client(self) -> chromadb.PersistentClient:
        """
        Get or create a ChromaDB client instance.
        
        Returns:
            chromadb.PersistentClient: The ChromaDB client
        """
        if self.client is None:
            self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        return self.client
    
    def _get_embedding_function(self) -> embedding_functions.GoogleGenerativeAiEmbeddingFunction:
        """
        Get or create the embedding function.
        
        Returns:
            GoogleGenerativeAiEmbeddingFunction: The embedding function
        """
        if self.embedding_function is None:
            self.embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                api_key=self.api_key
            )
        return self.embedding_function
    
    def _prepare_metadata(self, metadatas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare metadata for storage by converting list keywords to strings.
        
        Args:
            metadatas: List of metadata dictionaries
            
        Returns:
            List[Dict[str, Any]]: Processed metadata
        """
        for metadata in metadatas:
            if metadata and 'keywords' in metadata and isinstance(metadata['keywords'], list):
                metadata['keywords'] = ', '.join(metadata['keywords'])
        return metadatas
    
    def initialize_vector_db(self) -> Tuple[Any, Any]:
        """
        Initialize ChromaDB and load documents if needed.
        
        Returns:
            tuple: (frameworks_collection, user_documents_collection)
            
        Raises:
            Exception: If initialization fails
        """
        try:
            client = self._get_client()
            embedding_function = self._get_embedding_function()
            
            # Create or get collections
            collection_fw = client.get_or_create_collection(
                name=FRAMEWORKS_COLLECTION,
                embedding_function=embedding_function
            )
            
            collection_user = client.get_or_create_collection(
                name=USER_DOCUMENTS_COLLECTION,
                embedding_function=embedding_function
            )
            
            # Load documents if frameworks collection is empty
            if collection_fw.count() == 0:
                self._load_initial_documents(collection_fw)
            else:
                logger.info(
                    f"Using existing frameworks collection with {collection_fw.count()} document chunks."
                )
            
            logger.info(
                f"User documents collection has {collection_user.count()} document chunks."
            )
            
            return collection_fw, collection_user
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB collection: {e}")
            raise
    
    def _load_initial_documents(self, collection: Any) -> None:
        """
        Load initial documents into the frameworks collection.
        
        Args:
            collection: The ChromaDB collection to load documents into
        """
        logger.info("Frameworks collection is empty. Loading documents...")
        
        try:
            documents, metadatas, ids = load_documents_from_directory(NEW_DOCUMENTS_DIR)
            
            if not documents:
                logger.warning("No documents were loaded. Please check the directory path.")
                return
            
            # Prepare metadata
            prepared_metadatas = self._prepare_metadata(metadatas)
            
            # Add documents to collection
            collection.add(
                documents=documents,
                metadatas=prepared_metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} document chunks to the frameworks collection.")
            
        except Exception as e:
            logger.error(f"Error loading initial documents: {e}")
            raise

    
    def list_documents_in_collection(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        List all documents in a specific collection or in all collections.
        
        Args:
            collection_name: The name of the collection to query. 
                           If None, lists documents from all collections.
        
        Returns:
            Dict[str, Any]: Information about the queried collection(s)
        """
        try:
            client = self._get_client()
            
            if collection_name:
                collections = [client.get_collection(name=collection_name)]
            else:
                collections = [
                    client.get_collection(name=FRAMEWORKS_COLLECTION),
                    client.get_collection(name=USER_DOCUMENTS_COLLECTION)
                ]
            
            results = {}
            
            for collection in collections:
                collection_info = self._process_collection_documents(collection)
                results[collection.name] = collection_info
                
                logger.info(f"Collection '{collection.name}' has {collection.count()} documents total.")
            
            return results
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise
    
    def _process_collection_documents(self, collection: Any) -> Dict[str, Any]:
        """
        Process documents from a collection and format them for display.
        
        Args:
            collection: The ChromaDB collection
            
        Returns:
            Dict[str, Any]: Formatted collection data
        """
        documents = collection.get()
        
        collection_data = {
            "count": collection.count(),
            "documents": []
        }
        
        for i, doc_id in enumerate(documents["ids"]):
            metadata = documents["metadatas"][i] if documents["metadatas"] else None
            document_text = documents["documents"][i] if documents["documents"] else None
            
            # Log document information
            self._log_document_info(i + 1, doc_id, metadata, document_text)
            
            # Store document info
            doc_info = {
                "id": doc_id,
                "metadata": metadata,
                "text_preview": document_text[:100] + "..." if document_text else None
            }
            collection_data["documents"].append(doc_info)
        
        return collection_data
    
    def _log_document_info(self, doc_num: int, doc_id: str, metadata: Optional[Dict], 
                          document_text: Optional[str]) -> None:
        """
        Log detailed information about a document.
        
        Args:
            doc_num: Document number for display
            doc_id: Document ID
            metadata: Document metadata
            document_text: Document text content
        """
        logger.info(f"\n--- Document {doc_num} ---")
        logger.info(f"ID: {doc_id}")
        
        if metadata:
            # Document-level metadata
            logger.info(f"Doc ID: {metadata.get('doc_id')}")
            logger.info(f"Chunk Number: {metadata.get('chunk_number')}")
            logger.info(f"Chunk Length: {metadata.get('chunk_length')}")
            logger.info(f"Section: {metadata.get('section')}")
            
            # File-level metadata
            logger.info(f"Source: {metadata.get('source')}")
            logger.info(f"Filename: {metadata.get('filename')}")
            logger.info(f"File Size: {metadata.get('file_size')} bytes")
            logger.info(f"File Type: {metadata.get('file_type')}")
            logger.info(f"Page Count: {metadata.get('page_count')}")
            logger.info(f"Word Count: {metadata.get('word_count')}")
            logger.info(f"Character Count: {metadata.get('char_count')}")
            logger.info(f"Keywords: {metadata.get('keywords')}")
            
            abstract = metadata.get('abstract', '')
            if abstract:
                logger.info(f"Abstract: {abstract[:100]}...")
        else:
            logger.info("No metadata available")
        
        # Show text preview
        if document_text:
            logger.info(f"Text Preview: {document_text[:150]}...")
        
        logger.info("-" * 50)
    
    def delete_all_documents(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete all documents from a specific collection or from all collections.
        
        Args:
            collection_name: The name of the collection to clear.
                           If None, clears all collections.
        
        Returns:
            Dict[str, Any]: Information about the deletion operation
        """
        try:
            client = self._get_client()
            
            if collection_name:
                collections = [client.get_collection(name=collection_name)]
            else:
                collections = [
                    client.get_collection(name=FRAMEWORKS_COLLECTION),
                    client.get_collection(name=USER_DOCUMENTS_COLLECTION)
                ]
            
            results = {}
            
            for collection in collections:
                deletion_result = self._delete_collection_documents(collection)
                results[collection.name] = deletion_result
            
            return results
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    def _delete_collection_documents(self, collection: Any) -> Dict[str, Any]:
        """
        Delete all documents from a specific collection.
        
        Args:
            collection: The ChromaDB collection
            
        Returns:
            Dict[str, Any]: Deletion operation result
        """
        documents = collection.get()
        doc_ids = documents["ids"]
        
        if doc_ids:
            collection.delete(ids=doc_ids)
            result = {
                "deleted_count": len(doc_ids),
                "status": "success"
            }
            logger.info(f"Deleted {len(doc_ids)} documents from collection '{collection.name}'.")
        else:
            result = {
                "deleted_count": 0,
                "status": "no documents found"
            }
            logger.info(f"No documents to delete in collection '{collection.name}'.")
        
        return result


# Convenience functions for backward compatibility
def initialize_vector_db() -> Tuple[Any, Any]:
    """
    Initialize ChromaDB and load documents if needed.
    
    Returns:
        tuple: (frameworks_collection, user_documents_collection)
    """
    db_manager = DatabaseManager()
    return db_manager.initialize_vector_db()


def list_documents_in_collection(collection_name: Optional[str] = None) -> Dict[str, Any]:
    """
    List all documents in a specific collection or in all collections.
    
    Args:
        collection_name: The name of the collection to query. 
                        If None, lists documents from all collections.
    
    Returns:
        Dict[str, Any]: Information about the queried collection(s)
    """
    db_manager = DatabaseManager()
    return db_manager.list_documents_in_collection(collection_name)


def delete_all_documents(collection_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete all documents from a specific collection or from all collections.
    
    Args:
        collection_name: The name of the collection to clear.
                        If None, clears all collections.
    
    Returns:
        Dict[str, Any]: Information about the deletion operation
    """
    db_manager = DatabaseManager()
    return db_manager.delete_all_documents(collection_name)


def main():
    """
    Main function for testing and debugging database operations.
    This should only be called when running this module directly.
    """
    logger.info("Starting database operations testing...")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Test operations - comment out any you don't want to run
        
        # DESTRUCTIVE OPERATION - Uncomment only if you want to delete all documents
        # logger.info("Deleting all documents from frameworks collection...")
        # delete_result = db_manager.delete_all_documents("frameworks")
        # logger.info(f"Delete result: {delete_result}")
        
        logger.info("Initializing vector database...")
        fw_collection, user_collection = db_manager.initialize_vector_db()
        
        # VERBOSE OPERATION - Uncomment only if you want to see all document details
        # logger.info("Listing documents in frameworks collection...")
        # list_result = db_manager.list_documents_in_collection("frameworks")
        
        logger.info("Database operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during database operations: {e}")
        raise


def test_database_operations(
    delete_documents: bool = False,
    initialize_db: bool = True,
    list_documents: bool = False,
    collection_name: Optional[str] = None
):
    """
    Flexible function for testing specific database operations.
    
    Args:
        delete_documents: Whether to delete documents (DESTRUCTIVE!)
        initialize_db: Whether to initialize the database
        list_documents: Whether to list documents (can be verbose)
        collection_name: Specific collection to operate on, or None for all
    """
    logger.info("Starting selective database operations testing...")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Conditional operations based on parameters
        if delete_documents:
            logger.warning("DESTRUCTIVE OPERATION: Deleting documents...")
            delete_result = db_manager.delete_all_documents(collection_name)
            logger.info(f"Delete result: {delete_result}")
        
        if initialize_db:
            logger.info("Initializing vector database...")
            fw_collection, user_collection = db_manager.initialize_vector_db()
        
        if list_documents:
            logger.info("Listing documents...")
            list_result = db_manager.list_documents_in_collection(collection_name)
        
        logger.info("Selected database operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during database operations: {e}")
        raise


if __name__ == "__main__":
    # Uncomment the line below to run tests when executing this file directly
    # main()
    
    # Alternative: Run only specific operations
    # test_database_operations(
    #     delete_documents=False,    # Set to True only if you want to delete documents
    #     initialize_db=False,        # Usually safe to run
    #     list_documents=True,      # Set to True if you want to see document details
    #     collection_name="frameworks"  # Or None for all collections
    # )
    
    print("Database module loaded. No tests executed. Use main() or test_database_operations() to run tests.")
