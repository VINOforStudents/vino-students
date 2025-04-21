"""
Document processing and retrieval system using ChromaDB and LLM.
This module provides functions for document handling, vector database operations,
and LLM-based question answering to be used by API endpoints.
"""

# Standard library imports
import os

# Third-party imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Local imports
from config import USER_UPLOADS_DIR




#------------------------------------------------------------------------------
# QUERY AND RESPONSE
#------------------------------------------------------------------------------

def add_results_to_context(results, section_title, context=""):
    """
    Add search results to the context string with proper formatting.
    
    Args:
        results: Search results from ChromaDB
        section_title: Title for this section of results
        context: Existing context to append to
        
    Returns:
        tuple: (updated_context, has_results)
    """
    if results['documents'] and results['documents'][0]:
        context += f"\n--- {section_title} ---\n"
        for i, doc in enumerate(results['documents'][0]):
            source = results['metadatas'][0][i]['filename'] if 'metadatas' in results and results['metadatas'][0] else "Unknown source"
            context += f"\n--- From {source} ---\n{doc}\n"
        return context, True
    return context, False

def query_and_respond(query_text, conversation_history, collection_fw=None, collection_user=None):
    """
    Query collections and generate a response.
    
    Args:
        query_text: User's question
        conversation_history: List of previous conversation entries
        collection_fw: Frameworks collection
        collection_user: User documents collection
        
    Returns:
        str: Generated response
    """
    # Use the passed collections instead of trying to access global variables
    if collection_fw is None or collection_user is None:
        raise ValueError("Both collection_fw and collection_user must be provided")
    
    # Query frameworks collection
    fw_results = collection_fw.query(
        query_texts=[query_text],
        n_results=3  # Get top 3 from frameworks
    )
    
    # Query user collection
    user_results = collection_user.query(
        query_texts=[query_text],
        n_results=3  # Get top 3 from user docs
    )

    # Build conversation context from history
    conversation_context = ""
    if conversation_history:
        for entry in conversation_history:
            role = entry["role"]
            content = entry["content"]
            conversation_context += f"{role.capitalize()}: {content}\n"

    # Combine all retrieved document chunks into a comprehensive context
    combined_context = ""
    
    # Add both collections' results
    combined_context, has_fw_results = add_results_to_context(fw_results, "From Framework Documents", combined_context)
    combined_context, has_user_results = add_results_to_context(user_results, "From Your Documents", combined_context)
    
    # If we have context, generate a response
    if has_fw_results or has_user_results:
        response = chain.invoke({
            "context": combined_context,
            "history": conversation_context,
            "question": query_text
        })
        return response.content
    else:
        return "No relevant information found. Please try a different question."

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

#------------------------------------------------------------------------------
# INITIALIZATION
#------------------------------------------------------------------------------

# Setup prompt template for the LLM
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant that answers questions based on document context."
    ),
    (
        "human",
        """I have the following context:
        {context}

        Conversation history:
        {history}

        Answer my question: {question}"""
    )
])

 
# Ensure upload directory exists
os.makedirs(USER_UPLOADS_DIR, exist_ok=True)

# Initialize LLM model
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

# Create the LLM chain
chain = prompt | model
