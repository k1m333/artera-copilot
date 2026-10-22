import streamlit as st
import asyncio
from main import agent, Runner
from agents.exceptions import InputGuardrailTripwireTriggered
import nest_asyncio

nest_asyncio.apply()

st.title("Artera Healthcare Copilot")
st.caption("Senior Staff AI Builder Interview Project")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about appointments or clinic policies..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Run the agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # 1. Format the history into a single string for the agent
                history_string = ""
                for msg in st.session_state.messages[:-1]: # Exclude the current prompt we just added
                    history_string += f"{msg['role'].capitalize()}: {msg['content']}\n"
                
                # 2. Combine history with the new prompt
                full_prompt = f"{history_string}\nUser: {prompt}\nAssistant:"
                
                # 3. Run the agent with the contextualized prompt
                result = asyncio.run(Runner.run(agent, full_prompt))
                response = result.final_output
                
            except InputGuardrailTripwireTriggered:
                response = "I'm sorry, I cannot provide medical advice. Please consult a doctor."
            except Exception as e:
                response = f"An error occurred: {e}"
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})