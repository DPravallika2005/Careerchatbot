import streamlit as st
import time
import openai

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Chat interface
st.title("Interactive Chatbot")

# Display chat history
for message in st.session_state['chat_history']:
    if message['role'] == 'user':
        st.markdown(f'<div style="background: #f0f0f0; padding: 10px; border-radius: 10px; margin: 5px 0;">User: {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background: #e0f7fa; padding: 10px; border-radius: 10px; margin: 5px 0;">Bot: {message["content"]}</div>', unsafe_allow_html=True)

# Function to generate bot response using OpenAI GPT
def generate_bot_response(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ],
    )
    return response['choices'][0]['message']['content']

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat history
    st.session_state['chat_history'].append({'role': 'user', 'content': user_input})

    # Simulate typing effect
    with st.spinner("Bot is typing..."):
        time.sleep(1)  # Simulate delay for typing effect

        # Generate bot response using OpenAI GPT
        bot_response = generate_bot_response(user_input)

        # Add bot response to chat history
        st.session_state['chat_history'].append({'role': 'bot', 'content': bot_response})

    # Rerun to update the chat interface
    st.experimental_rerun()
