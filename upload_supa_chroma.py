"""Supabase and ChromaDB Integration Module

This module provides functionality to upload documents to Supabase and ChromaDB,
as well as to ChromaDB.
"""

import database
from typing import Dict, List, Optional, Tuple, Any

FRAMEWORKS_COLLECTION = "frameworks"
USER_DOCUMENTS_COLLECTION = "user_documents"

def upload_documents_to_supabase() -> None:
    """
    Uploads a document to Supabase.
    """
    database.initialize_vector_db()

def upload_documents_to_chromadb() -> None:
    """
    Uploads a document to ChromaDB.
    """
    database.upload_document()

