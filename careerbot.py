import streamlit as st
import pandas as pd
import google.generativeai as genai
from transformers import pipeline
import numpy as np
import time
from sklearn.metrics.pairwise import cosine_similarity

# Custom CSS for styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0078d4, #ffffff);
        font-family: 'Arial', sans-serif;
        min-height: 100vh;
    }
    .chat-font {
        font-family: 'Georgia', serif;
        color: #2c5f2d;
    }
    .user-msg {
        background: #ffffff !important;
        border-radius: 15px !important;
        border: 2px solid #2c5f2d !important;
        padding: 10px;
        margin: 5px 0;
    }
    .bot-msg {
        background: #e6f3ff !important;
        border-radius: 15px !important;
        border: 2px solid #0078d4 !important;
        padding: 10px;
        margin: 5px 0;
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
    .footer {
        text-align: center;
        padding: 20px;
        background: #2c5f2d;
        color: white;
        margin-top: 20px;
    }
    .footer a {
        color: white;
        margin: 0 10px;
        text-decoration: none;
    }
    .footer a:hover {
        color: #ffd700;
    }
</style>
""", unsafe_allow_html=True)

# Configure Google Gemini
genai.configure(api_key="AIzaSyDchgKU8oNtY32jw7seTQdxbakzUFy7I7k")  # Replace with your Gemini API key
gemini = genai.GenerativeModel('gemini-pro')  # Use the publicly available model

# Initialize models
embedder = pipeline("feature-extraction", model="distilbert-base-uncased")  # Lightweight embedding model

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('profession_questions_answers.csv')  # Replace with your dataset file name
        if 'Question' not in df.columns or 'Answer' not in df.columns:
            st.error("The CSV file must contain 'Question' and 'Answer' columns.")
            st.stop()
        df['context'] = df.apply(
            lambda row: f"Profession: {row['Profession']}\nQuestion: {row['Question']}\nAnswer: {row['Answer']}", 
            axis=1
        )
        return df
    except Exception as e:
        st.error(f"Failed to load data. Error: {e}")
        st.stop()

# Load dataset
df = load_data()

# Function to generate embeddings
def generate_embedding(text):
    embedding = embedder(text, return_tensors="np")[0].mean(axis=1)  # Mean pooling for embeddings
    return embedding

# Function to find the closest matching question using cosine similarity
def find_closest_question(query, df):
    query_embedding = generate_embedding(query)
    embeddings = np.array([generate_embedding(context) for context in df['context']])
    similarities = cosine_similarity(query_embedding, embeddings)
    closest_index = np.argmax(similarities)
    return df.iloc[closest_index]['Answer']

# App Header with Logo and Tagline
st.markdown("""
<div style="text-align: center;">
    <h1 style="color: #2c5f2d;">🤖 Career Chatbot</h1>
    <p style="color: #1e3d1e;">Your personal career advisor</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Predefined questions for quick interaction
predefined_questions = [
    "What skills are essential for a Data Scientist?",
    "How do I become a successful Graphic Designer?",
    "What are the challenges faced by Architects?",
    "What does a typical day look like for a Software Engineer?"
]

# Display predefined questions in cards
st.markdown("### Quick Questions:")
for question in predefined_questions:
    with st.container():
        st.markdown(f"""
        <div class="card">
            <p>{question}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Ask: {question}"):
            st.session_state.user_input = question

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🙋" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# Handle user input
if "user_input" in st.session_state:
    prompt = st.session_state.user_input
    del st.session_state.user_input  # Clear the input after processing
else:
    prompt = st.chat_input("Ask me anything about careers...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Thinking..."):
        try:
            # Simulate typing effect
            with st.chat_message("assistant", avatar="🤖"):
                response_placeholder = st.empty()
                response_text = ""
                # Find the closest answer
                retrieved_answer = find_closest_question(prompt, df)
                if retrieved_answer:
                    # Generate a refined answer using Gemini
                    refined_answer = generate_refined_answer(prompt, retrieved_answer)
                    for chunk in refined_answer.split():
                        response_text += chunk + " "
                        time.sleep(0.1)  # Simulate typing delay
                        response_placeholder.markdown(f"**Career Advisor**:\n{response_text}")
                else:
                    response_text = "**Career Advisor**:\nI'm sorry, I cannot answer that question. Please ask something related to careers."
                    response_placeholder.markdown(response_text)
        except Exception as e:
            response_text = f"An error occurred: {e}"
            response_placeholder.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()

# Feedback Mechanism
st.markdown("---")
st.markdown("### Rate the Chatbot's Response:")
feedback = st.radio("How would you rate this response?", ("👍 Great!", "👎 Needs Improvement"))
if st.button("Submit Feedback"):
    st.success(f"Thank you for your feedback: {feedback}")

# Footer with Social Media Links
st.markdown("""
<div class="footer">
    <p>Follow us on:</p>
    <a href="https://twitter.com" target="_blank">Twitter</a> | 
    <a href="https://linkedin.com" target="_blank">LinkedIn</a> | 
    <a href="https://github.com" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
