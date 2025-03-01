import streamlit as st
import time
import openai

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Inject custom CSS for dynamic background and animations
st.markdown("""
<style>
    @keyframes gradientChange {
        0% { background: linear-gradient(135deg, #0078d4, #ffffff); }
        25% { background: linear-gradient(135deg, #ff7eb9, #ffffff); }
        50% { background: linear-gradient(135deg, #6a11cb, #ffffff); }
        75% { background: linear-gradient(135deg, #ff9a9e, #ffffff); }
        100% { background: linear-gradient(135deg, #0078d4, #ffffff); }
    }
    .stApp {
        animation: gradientChange 10s infinite; /* 10s for smooth gradient transition */
        font-family: 'Arial', sans-serif;
        min-height: 100vh;
        background-size: cover; /* Ensure gradient covers the entire page */
    }
    .chat-font {
        font-family: 'Times New Roman', serif;
        color: #2c5f2d;
    }
    .user-msg {
        background: #ffffff !important;
        border-radius: 15px !important;
        border: 2px solid #2c5f2d !important;
        padding: 10px;
        margin: 5px 0;
        animation: slideIn 0.5s ease;
    }
    .bot-msg {
        background: #fff9e6 !important;
        border-radius: 15px !important;
        border: 2px solid #ffd700 !important;
        padding: 10px;
        margin: 5px 0;
        animation: slideIn 0.5s ease;
    }
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    .stChatInput {
        background: #ffffff;
        border-radius: 15px;
        border: 2px solid #2c5f2d;
    }
    .stButton button {
        background: linear-gradient(45deg, #2c5f2d, #1e3d1e);
        color: white;
        border-radius: 15px;
        padding: 10px 20px;
        border: none;
        transition: background 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(45deg, #1e3d1e, #2c5f2d);
    }
    .card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
    }
    .typing-effect {
        display: inline-block;
        overflow: hidden;
        white-space: nowrap;
        margin: 0;
        letter-spacing: 2px;
        animation: typing 1.5s steps(30, end);
    }
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    .dark-mode {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .dark-mode .stChatInput {
        background: #2d2d2d;
        border-color: #444;
    }
    .dark-mode .stButton button {
        background: linear-gradient(45deg, #444, #333);
    }
    .dark-mode .stButton button:hover {
        background: linear-gradient(45deg, #333, #444);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history and user preferences
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False
if 'points' not in st.session_state:
    st.session_state['points'] = 0

# Function to toggle dark mode
def toggle_dark_mode():
    st.session_state['dark_mode'] = not st.session_state['dark_mode']

# Dark mode toggle button
st.sidebar.button("Toggle Dark Mode", on_click=toggle_dark_mode)

# Apply dark mode if enabled
if st.session_state['dark_mode']:
    st.markdown('<div class="dark-mode">', unsafe_allow_html=True)

# Custom avatars
user_avatar = "https://via.placeholder.com/40"
bot_avatar = "https://via.placeholder.com/40"

# Chat interface
st.title("Interactive Chatbot")
st.markdown('<div class="chat-font">', unsafe_allow_html=True)

# Display chat history
for message in st.session_state['chat_history']:
    if message['role'] == 'user':
        st.markdown(f'<div class="user-msg"><img src="{user_avatar}" class="avatar">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg"><img src="{bot_avatar}" class="avatar"><span class="typing-effect">{message["content"]}</span></div>', unsafe_allow_html=True)

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

# Feedback mechanism
st.sidebar.title("Feedback")
feedback = st.sidebar.radio("Rate the bot's response:", ("👍", "👎"))
if feedback:
    st.sidebar.write(f"Thank you for your feedback: {feedback}")

# Multimedia support
st.sidebar.title("Multimedia Support")
uploaded_file = st.sidebar.file_uploader("Upload an image or video", type=["jpg", "png", "mp4"])
if uploaded_file:
    st.sidebar.write("File uploaded successfully!")
    if uploaded_file.type.startswith('image'):
        st.sidebar.image(uploaded_file)
    elif uploaded_file.type.startswith('video'):
        st.sidebar.video(uploaded_file)

# Personalization
user_name = st.sidebar.text_input("Enter your name for personalization:")
if user_name:
    st.sidebar.write(f"Hello, {user_name}! How can I assist you today?")

# Gamification
st.sidebar.title("Gamification")
st.sidebar.write(f"Your current points: {st.session_state['points']}")
if st.sidebar.button("Earn Points"):
    st.session_state['points'] += 10
    st.sidebar.write(f"Congratulations! You earned 10 points. Total points: {st.session_state['points']}")

# Error handling
try:
    # Example of a potential error
    result = 10 / 0
except Exception as e:
    st.sidebar.error(f"An error occurred: {e}")

# Close dark mode div if enabled
if st.session_state['dark_mode']:
    st.markdown('</div>', unsafe_allow_html=True)
