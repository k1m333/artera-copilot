import streamlit as st
from main import agent, Runner
from agents.exceptions import InputGuardrailTripwireTriggered
import asyncio
from concurrent.futures import ThreadPoolExecutor

st.title("Artera Healthcare Copilot")
st.caption("Senior Staff AI Builder Interview Project")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Helper function to run the agent in a separate thread
def run_agent_in_thread(full_prompt):
    # Create a fresh event loop for this specific thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def _run():
        return await Runner.run(agent, full_prompt)
    
    try:
        # Run the async function to completion
        result = loop.run_until_complete(_run())
        return result.final_output
    finally:
        loop.close()

# React to user input
if prompt := st.chat_input("Ask about appointments or clinic policies..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Run the agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # 1. Format history
                history_string = ""
                for msg in st.session_state.messages[:-1]:
                    history_string += f"{msg['role'].capitalize()}: {msg['content']}\n"
                
                full_prompt = f"{history_string}\nUser: {prompt}\nAssistant:"
                
                # 2. Run agent safely in a separate thread
                with ThreadPoolExecutor(max_workers=1) as executor:
                    response = executor.submit(run_agent_in_thread, full_prompt).result()
                
            except InputGuardrailTripwireTriggered:
                response = "I'm sorry, I cannot provide medical advice. Please consult a doctor."
            except Exception as e:
                response = f"An error occurred: {e}"
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})