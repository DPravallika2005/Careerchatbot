import streamlit as st
import pandas as pd
import google.generativeai as genai
from transformers import pipeline
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Inject custom CSS and JavaScript for dynamic background
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
        animation: gradientChange 40s infinite;
        font-family: 'Arial', sans-serif;
        min-height: 100vh;
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
    }
    .bot-msg {
        background: #fff9e6 !important;
        border-radius: 15px !important;
        border: 2px solid #ffd700 !important;
        padding: 10px;
        margin: 5px 0;
    }
    .stChatInput {
        background: #ffffff;
        border-radius: 15px;
        border: 2px solid #2c5f2d;
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
    embedding = np.array(embedder(text, return_tensors="np")[0].mean(axis=1))  # Mean pooling for embeddings
    return embedding

# Function to find the closest matching question using cosine similarity
def find_closest_question(query, df):
    query_embedding = generate_embedding(query)
    embeddings = np.array([generate_embedding(context) for context in df['context']])
    similarities = cosine_similarity(query_embedding, embeddings)
    closest_index = np.argmax(similarities)
    return df.iloc[closest_index]['Answer']

# App Header
st.markdown('<h1 class="chat-font">🤖 Career Chatbot</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="chat-font">Ask me anything about careers, and I\'ll help you out!</h3>', unsafe_allow_html=True)
st.markdown("---")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], 
                        avatar="🙋" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about careers..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Thinking..."):
        try:
            # Find the closest answer
            retrieved_answer = find_closest_question(prompt, df)
            if retrieved_answer:
                # Generate a refined answer using Gemini
                refined_answer = generate_refined_answer(prompt, retrieved_answer)
                response = f"**Career Advisor**:\n{refined_answer}"
            else:
                response = "**Career Advisor**:\nI'm sorry, I cannot answer that question. Please ask something related to careers."
        except Exception as e:
            response = f"An error occurred: {e}"
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
