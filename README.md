# Artera Support Copilot 🏥🤖

An agentic AI copilot designed to handle healthcare support workflows, featuring intent-based guardrails, Retrieval-Augmented Generation (RAG), and resilient tool calling.

*Built as an interview project for the Senior Staff AI Builder role at Artera.*

## 🏗️ Architecture & Features

1. **Agentic Tool Calling (Function Calling)**: The LLM dynamically routes queries to backend functions (e.g., `check_patient_appointment`) based on the user's intent, rather than hardcoded logic.
2. **RAG (Retrieval-Augmented Generation)**: Integrates **ChromaDB** as a local vector database to retrieve clinic policies from `faq.txt`, preventing hallucinations on operational questions (e.g., late-arrival policies).
3. **Semantic Input Guardrails**: A secondary, lightweight "Guardrail Agent" intercepts unsafe inputs before they reach the main agent.
4. **Interactive UI**: A **Streamlit** frontend for real-time chatting and guardrail testing.

## 🧠 Key Engineering Decisions (The "Why")

* **LLM Guardrail vs. Keyword Matching**: 
  Instead of hardcoding `if "prescribe" in input`, the system uses a separate LLM agent to evaluate intent. During testing, it successfully intercepted a real-world edge case: *"I have a bump on my lip, what medication should I get?"*—a prompt that lacks the word "prescribe" but clearly violates medical advice policies.
* **Context Isolation**: 
  The guardrail runs in a separate context window. This ensures the main agent never processes the unsafe prompt, keeping its context clean and eliminating the risk of generating harmful medical advice.
* **RAG over Fine-Tuning**: 
  Clinic hours and booking policies change frequently. Retrieval from a Vector DB is faster, cheaper, and easier to update than fine-tuning an LLM.

## 🛠️ Tech Stack
* **Orchestration**: OpenAI Agents SDK
* **Vector Database**: ChromaDB
* **UI**: Streamlit
* **Language**: Python

## 🚀 How to Run Locally

1. Clone the repository and navigate to the project directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate

## Challenges
LLM guardrails had a high false-positive rate if the system prompt isn't constrained properly. Had to tune guardrail to ignore status questions while catching diagnosis requests. Also, fixed integrating async agent loops with nest_asyncio to prevent loop from closing between messages.