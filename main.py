import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
import chromadb
from agents import input_guardrail, GuardrailFunctionOutput

# Load API key from .env
load_dotenv()

# 1. Create the "checker" agent
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="""Check if the user is asking for a medical diagnosis, symptoms, or prescription medications. 
    DO NOT flag appointment status questions, booking requests, or clinic policy questions.""",
    output_type=bool
)

# 2. Define the guardrail function
@input_guardrail
async def medical_guardrail(ctx, agent, input) -> GuardrailFunctionOutput:
    # Run the checker agent on the user's input
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    
    # If the checker returns True (it is medical advice), trip the guardrail
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output
    )

# 1. Initialize ChromaDB and load the FAQ
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="faq")

with open("faq.txt", "r") as f:
    faq_text = f.read()

# Add the whole file as one document for simplicity
collection.add(
    documents=[faq_text],
    ids=["faq_1"]
)

# 2. Create the search tool
@function_tool
def search_faq(query: str) -> str:
    """Searches the clinic FAQ for policies regarding appointments, billing, and hours."""
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    # Return the text of the most relevant document
    return results['documents'][0][0]

# --- Define your tool here ---
@function_tool
def check_patient_appointment(patient_id: str) -> str:
    """
    Looks up a patient's appointment status and time. 
    Use this tool when the user asks where a patient is, what time their appointment is, or their status.
    """
    if patient_id == "999":
        raise Exception("Database connection timeout")

    if patient_id == "123":
        return "Patient 123 has a confirmed appointment with Dr. Smith on Monday at 2 PM."
    return f"No appointment found for patient {patient_id}."

# --- Initialize the agent ---
agent = Agent(
    name="Artera Copilot",
    instructions="""You are a helpful healthcare support copilot. 
    If a user asks for the status of an appointment (e.g., 'Where is patient 123?'), 
    you MUST use the check_patient_appointment tool to look up their status. 
    Do not refuse the request; assume 'where' means 'what is the status of'.
    If a tool fails, do not make up an answer. Apologize and tell the user the system is currently down.""",
    tools=[check_patient_appointment, search_faq],
    input_guardrails=[medical_guardrail]
)

if __name__ == "__main__":
    # Test the agent
    result = Runner.run_sync(agent, "Can you prescribe me some antibiotics?")
    print(result.final_output)