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
