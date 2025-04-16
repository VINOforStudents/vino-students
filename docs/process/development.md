# Context Management

currently there's an issue with the prompting, and it does not get past step 1 because of the lack of confirmation or command.
in a sequence diagram i want you to describe the possible scenarios that happen for chat navigation and steps navigation (1-6)

the user needs to be able to navigate to context of step 1, and if it's good enough, we do /next to go to the next step.

to go to any step that exists, do /step <n>
to go to previous step do /previous


wondering how this is going to interact with our stack in the context of a SQ

```mermaid
sequenceDiagram
    actor User
    participant ReflexFrontend as Reflex Frontend (GUI + State)
    participant FastAPIBackend as FastAPI Backend (APIendpoint.py)
    participant LLMLogic as Langchain/LLM Logic (main.py + Prompts)
    participant VectorDB as ChromaDB

    %% Scenario 1: Normal Chat within a Step %%
    User->>ReflexFrontend: Enters chat message "Tell me more about X"
    ReflexFrontend->>ReflexFrontend: Get current_step (e.g., 1)
    ReflexFrontend->>FastAPIBackend: POST /chat (question="...", current_step=1)
    FastAPIBackend->>LLMLogic: query_and_respond(question="...", step=1, history=...)
    LLMLogic->>LLMLogic: get_universal_matrix_prompt(step=1, ...)
    LLMLogic->>VectorDB: Query context relevant to Step 1 + question
    VectorDB-->>LLMLogic: Return relevant documents
    LLMLogic->>LLMLogic: Call LLM with Step 1 prompt + context + history
    LLMLogic-->>FastAPIBackend: Return LLM response for Step 1
    FastAPIBackend-->>ReflexFrontend: Return JSON {answer: "..."}
    ReflexFrontend->>User: Display LLM response for Step 1

    %% Scenario 2: User wants to proceed - /next %%
    User->>ReflexFrontend: Enters command "/next"
    ReflexFrontend->>ReflexFrontend: Parse command, identify "/next"
    ReflexFrontend->>ReflexFrontend: Get current_step (e.g., 1)
    ReflexFrontend->>ReflexFrontend: Increment current_step (to 2)
    ReflexFrontend->>FastAPIBackend: POST /chat (question="Proceed to next step.", current_step=2) # Send a placeholder question or guiding prompt
    FastAPIBackend->>LLMLogic: query_and_respond(question="Proceed to next step.", step=2, history=...)
    LLMLogic->>LLMLogic: get_universal_matrix_prompt(step=2, ...)
    LLMLogic->>VectorDB: Query context relevant to Step 2
    VectorDB-->>LLMLogic: Return relevant documents
    LLMLogic->>LLMLogic: Call LLM with Step 2 prompt + context + history (maybe prompt asks "Okay, let's start Step 2...")
    LLMLogic-->>FastAPIBackend: Return LLM response for Step 2
    FastAPIBackend-->>ReflexFrontend: Return JSON {answer: "Okay, let's start Step 2..."}
    ReflexFrontend->>User: Display LLM response initiating Step 2

    %% Scenario 3: User wants to go back - /previous %%
    User->>ReflexFrontend: Enters command "/previous"
    ReflexFrontend->>ReflexFrontend: Parse command, identify "/previous"
    ReflexFrontend->>ReflexFrontend: Get current_step (e.g., 3)
    ReflexFrontend->>ReflexFrontend: Decrement current_step (to 2, ensure >= 1)
    ReflexFrontend->>FastAPIBackend: POST /chat (question="Go back to previous step.", current_step=2)
    FastAPIBackend->>LLMLogic: query_and_respond(question="Go back to previous step.", step=2, history=...)
    LLMLogic->>LLMLogic: get_universal_matrix_prompt(step=2, ...)
    LLMLogic->>VectorDB: Query context relevant to Step 2
    VectorDB-->>LLMLogic: Return relevant documents
    LLMLogic->>LLMLogic: Call LLM with Step 2 prompt + context + history (maybe prompt asks "Okay, we are back at Step 2...")
    LLMLogic-->>FastAPIBackend: Return LLM response for Step 2
    FastAPIBackend-->>ReflexFrontend: Return JSON {answer: "Okay, we are back at Step 2..."}
    ReflexFrontend->>User: Display LLM response confirming return to Step 2

    %% Scenario 4: User jumps to a specific step - /step <n> %%
    User->>ReflexFrontend: Enters command "/step 4"
    ReflexFrontend->>ReflexFrontend: Parse command, identify "/step", extract n=4
    ReflexFrontend->>ReflexFrontend: Validate n (1 <= n <= 6)
    ReflexFrontend->>ReflexFrontend: Set current_step = 4
    ReflexFrontend->>FastAPIBackend: POST /chat (question="Jump to step 4.", current_step=4)
    FastAPIBackend->>LLMLogic: query_and_respond(question="Jump to step 4.", step=4, history=...)
    LLMLogic->>LLMLogic: get_universal_matrix_prompt(step=4, ...)
    LLMLogic->>VectorDB: Query context relevant to Step 4
    VectorDB-->>LLMLogic: Return relevant documents
    LLMLogic->>LLMLogic: Call LLM with Step 4 prompt + context + history (maybe prompt asks "Okay, moving to Step 4...")
    LLMLogic-->>FastAPIBackend: Return LLM response for Step 4
    FastAPIBackend-->>ReflexFrontend: Return JSON {answer: "Okay, moving to Step 4..."}
    ReflexFrontend->>User: Display LLM response initiating Step 4

    