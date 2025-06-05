from importnb import Notebook
with Notebook(): 
    import supervisor_test as notebook
# import supervisor_test as notebook
import streamlit as st

#parsing method
import json
import re
def parse_llm_output(text):
    """
    Parse LLM output to extract and validate JSON content.
    
    Args:
        text (str): Raw text output from LLM
        
    Returns:
        dict: Parsed JSON object or None if no valid JSON found
    """
    # Find content between triple backticks
    json_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', text)
    
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            print("Found JSON-like content but failed to parse")
            return None
    
    # Try to find raw JSON without backticks
    try:
        # Look for content that starts with { and ends with }
        json_match = re.search(r'({[\s\S]*})', text)
        if json_match:
            return json.loads(json_match.group(1))
    except json.JSONDecodeError:
        print("No valid JSON found in the text")
        return None
    
    return None

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_message(role, content, structured_data=None):
    with st.chat_message(role):
        st.write(content)
        if structured_data:
            with st.expander("Question Details"):
                if 'question' in structured_data:
                    st.write("**Question:**", structured_data['question'])
                if 'options' in structured_data:
                    st.write("**Options:**")
                    for option in structured_data['options']:
                        st.write(f"- {option['option']}: {option['text']}")
                
                col1, col2 = st.columns(2)
                if 'correct_option' in structured_data:
                    with col1:
                        st.write("**Correct Answer:**", structured_data['correct_option'])
                if 'explanation' in structured_data or 'comment' in structured_data:
                    with col2:
                        if st.button("Show Explanation", key=f"explain_{len(st.session_state.messages)}"):
                            st.write("**Explanation:**", structured_data['explanation'])
                            st.write("**Comment:**", structured_data['comment'])

def main():
    st.title("Educational AI Assistant")
    st.write("""
    Welcome to your interactive learning session! 
    Ask any question, and I'll guide you through the concept step by step.
    """)
    
    init_session_state()
    
    # Display chat history
    for message in st.session_state.messages:
        display_message(
            message["role"],
            message["content"],
            message.get("structured_data")
        )
    
    # Chat input
    if prompt := st.chat_input("What would you like to learn about?"):
        # Display user message
        display_message("user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get AI response
        response = notebook.get_response(prompt)
        

        # Access different types of messages
        for supervisor_msg in response['supervisor_messages']:
            print("Supervisor:", supervisor_msg)
            
        # Parse the response if it's a string
        if isinstance(response['supervisor_messages'][-1], str):
            parsed_response = parse_llm_output(response['supervisor_messages'][-1])
            if parsed_response:
                response['supervisor_messages'][-1] = parsed_response

        for react_msg in response['react_messages']:
            print("React Agent:", react_msg)

        # Access structured response if available
        if response['structured_response']:
            print("Structured Response:", response['structured_response'])

        # Access memory
        print("Conversation History:", response['memory'])
        
        print("\n\n --------------------- \n\n", response['supervisor_messages'], "\n\n --------------------- \n\n")
        # Display AI response
        display_message(
            "assistant",
            response['supervisor_messages'][-1]['conversation_message'] if response['supervisor_messages'] else "",
            # response['structured_response'],
            response['supervisor_messages'][-1]['question_data']
        )
        
        # Save to session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": response['supervisor_messages'][-1] if response['supervisor_messages'] else "",
        })

if __name__ == "__main__":
    main()