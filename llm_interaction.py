# Standard library imports
import os
from typing import List, Dict, Any

# Third-party imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import prompts

# Local imports
from config import USER_UPLOADS_DIR


#------------------------------------------------------------------------------
# QUERY AND RESPONSE
#------------------------------------------------------------------------------

def convert_history_data(history_data: List[Dict[str, Any]]) -> List[BaseMessage]:
    """Converts the history format from the API request to LangChain messages."""
    messages = []
    for item in history_data:
        if item.get("role") == "user":
            messages.append(HumanMessage(content=item.get("content", "")))
        elif item.get("role") == "assistant":
            messages.append(AIMessage(content=item.get("content", "")))
    return messages

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
            source = results['metadatas'][0][i]['file_name'] if 'metadatas' in results and results['metadatas'][0] else "Unknown source"
            context += f"\n--- From {source} ---\n{doc}\n"
        return context, True
    return context, False

def query_and_respond(query_text: str, history_data: List[Dict[str, Any]], current_step: int, collection_fw=None, collection_user=None):
    """
    Queries vector databases, constructs a prompt using history and step,
    and gets a response from the LLM.
    """
    global chain # Assuming chain is a global variable initialized elsewhere

    # Use the passed collections instead of trying to access global variables
    if collection_fw is None or collection_user is None:
         # Handle error: Collections not provided
         print("Error: Vector database collections not provided to query_and_respond.")
         return "Error: Internal server configuration issue."

    # Query frameworks collection
    fw_results = collection_fw.query(
        query_texts=[query_text],
        n_results=3
    )

    # Query user collection
    user_results = collection_user.query(
        query_texts=[query_text],
        n_results=3
    )

    # Convert history data from API format to LangChain message objects
    langchain_history = convert_history_data(history_data)

    # Combine all retrieved document chunks into a comprehensive context
    combined_context = ""

    # Add both collections' results
    combined_context, has_fw_results = add_results_to_context(fw_results, "From Framework Documents", combined_context)
    combined_context, has_user_results = add_results_to_context(user_results, "From Your Documents", combined_context)

    # Correctly call get_universal_matrix_prompt with required arguments
    prompt_template = prompts.get_universal_matrix_prompt(
        current_step=current_step,  # Use the passed current_step
        history=langchain_history, # Pass the converted history object
        question=query_text,
        step_context="", # No specific step context retrieved here (can be enhanced later)
        general_context=combined_context, # Pass combined results as general context
    )
    if prompt_template is None: # Handle the case where the step might be invalid
            print(f"Error: Could not generate prompt for step {current_step}.")
            return "Error generating prompt for the query."

    # Prepare the input dictionary for the prompt template
    input_data = {
        "history": langchain_history, # Pass history again for the template formatting
        "question": query_text,
        "step_context": "",
        "general_context": combined_context,
        "current_step": current_step # Use passed step
    }

    try:
        # Format the prompt template using the input data
        formatted_prompt = prompt_template.invoke(input_data)

        # Pass the formatted prompt (PromptValue or list of BaseMessages) to the model
        response = model.invoke(formatted_prompt)

        return response.content

    except Exception as e:
        print(f"Error during chain invocation: {e}")
        return "Error: Failed to get response from language model."

    
#------------------------------------------------------------------------------
# INITIALIZATION
#------------------------------------------------------------------------------
 
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