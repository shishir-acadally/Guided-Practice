import streamlit as st
from importnb import Notebook
import json
# Import only get_response from your notebook
with Notebook():
    import react_agent_langraph as notebook

def parse_response(response):
    """Parse the response from the agent."""
    if isinstance(response, dict):
        return response
    else:
        first_bracket = response.find('{')
        end_bracket = response.rfind('}')
        if first_bracket != -1 and end_bracket != -1:
            response = response[first_bracket:end_bracket + 1]
        else:
            response = "{}"
        
        return json.loads(response)

# Streamlit app setup
st.set_page_config(page_title="AcadGenie Chat", page_icon="🧠", layout="centered")
st.title("🤖 AcadGenie")
st.markdown("Your AI learning companion. Ask anything!")

# Initialize chat history in session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input from user
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.chat_history.append(("You", user_input))
    with st.spinner("AcadGenie is thinking..."):
        try:
            # Call get_response from the notebook
            result = notebook.get_response(user_input)

            # Extract messages from result
            human_msg = result.get("human_message", user_input)
            assistance_msg = result.get("acadgenie", "I'm not sure what to respond!")
            ai_msg = parse_response(assistance_msg)

            # Format the AI message for display
            formatted_msg = ""
            if isinstance(ai_msg, dict):
                if "conversation_message" in ai_msg:
                    # Handle normal conversation
                    formatted_msg = ai_msg.get("conversation_message", "No message available")
                    # Handle question format
                    question_data = ai_msg.get("question_data", {})
                    if question_data:
                        # Format the question and options
                        formatted_msg += f"\n\n**Question:** {question_data.get('question', 'No question available')}\n\n"
                        if question_data.get('type') == 'MCQ':
                            formatted_msg += "**Options:**\n"
                            for option in question_data.get('options', []):
                                option_letter = option.get('option', '')
                                option_text = option.get('text', 'No text available')
                                formatted_msg += f"- {option_letter}: {option_text}\n"
                        
                        formatted_msg += f"\n**Correct Answer:** {question_data.get('correct_answer', 'Not specified')}\n"
                        formatted_msg += f"\n**Explanation:** {question_data.get('explanation', 'No explanation available')}\n"
                        formatted_msg += f"\n**Comment:** {question_data.get('comment', 'No comment available')}"
            else:
                formatted_msg = str(ai_msg)

            # Save chat history with formatted message
            st.session_state.chat_history.append(("AcadGenie", formatted_msg))

        except Exception as e:
            st.error(f"Error calling agent: {e}")

# Display chat history
for sender, message in st.session_state.chat_history:
    with st.chat_message("user" if sender == "You" else "assistant"):
        st.markdown(message)
