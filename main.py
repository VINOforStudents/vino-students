import os
import glob

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import PyPDF2
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Constants and Configuration
CHROMA_DB_PATH = "D:\\chromadb"
DOCUMENTS_DIR = "D:\\programs\\exploration\\chatbot_env\\documents"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text

# Function to read text files and PDFs from a directory
def load_documents_from_directory(directory_path):
    documents = []
    metadatas = []
    ids = []

    # Get all .txt and .pdf files in the directory
    txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    file_paths = txt_files + pdf_files

    for i, file_path in enumerate(file_paths):
        try:
            file_name = os.path.basename(file_path)
            doc_id_base = os.path.splitext(file_name)[0]

            # Handle different file types
            if file_path.lower().endswith('.pdf'):
                content = extract_text_from_pdf(file_path)
            else:  # Assume it's a text file
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

            # Skip if no content was extracted
            if not content.strip():
                print(f"Warning: No content extracted from {file_name}")
                continue

            # Implement fixed-size chunking
            start_index = 0
            chunk_number = 1
            while start_index < len(content):
                end_index = min(start_index + CHUNK_SIZE, len(content))
                chunk = content[start_index:end_index]

                documents.append(chunk)
                metadatas.append({"source": file_path, "filename": file_name, "chunk": chunk_number})
                ids.append(f"{doc_id_base}_chunk_{chunk_number}")

                print(f"Loaded chunk {chunk_number} from document: {file_name}")

                start_index += CHUNK_SIZE - CHUNK_OVERLAP
                chunk_number += 1

        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return documents, metadatas, ids

def query_and_respond(query_text, conversation_history):
    query_results = collection_fw.query(
        query_texts=[query_text],
        n_results=3
    )

    # Build conversation context from history
    conversation_context = ""
    if conversation_history:
        for entry in conversation_history:
            role = entry["role"]
            content = entry["content"]
            conversation_context += f"{role.capitalize()}: {content}\n"

    if query_results['documents'] and query_results['documents'][0]:
        context = query_results['documents'][0][0]

        # Use the template variables directly
        response = chain.invoke({
            "context": context,
            "history": conversation_context,
            "question": query_text
        })

        return response.content
    else:
        return "No relevant information found. Please try a different question."

def run_chat_interface():

    print("Chat with Gemini 1.5 Pro (type 'exit' to quit)")
    print("-" * 50)

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Get document context and response
        answer = query_and_respond(user_input, conversation_history)

        # Add this exchange to history
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": answer})

        print(f"Gemini: {answer}")
        print("-" * 50)

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

# System prompt
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

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)


collection_fw = client.get_collection(name="frameworks", embedding_function=google_ef)

# Specify  directory containing .txt  and .pdf files
documents_dir = DOCUMENTS_DIR

# Load documents from the directory
docs, metas, ids = load_documents_from_directory(documents_dir)

# Add documents to collection
if docs:
    collection_fw.add(
        documents=docs,
        metadatas=metas,
        ids=ids
    )
else:
    print("No documents were loaded. Please check the directory path.")

conversation_history = []

chain = prompt | model

if __name__ == "__main__":
    run_chat_interface()