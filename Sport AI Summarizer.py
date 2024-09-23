import streamlit as st
from google.cloud import language_v1
import pdfplumber
from transformers import pipeline
from streamlit_option_menu import option_menu


with open('./style.css') as f:
    css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

with st.sidebar:
    selected = option_menu(
        menu_title="Sports AI",
        options=["Main Menu", "Coach AI", "Sports Article Summarizer"],
        icons=["info-circle", "note", "whistle"],
    )

# Function to extract text from PDF using pdfplumber for better accuracy
def extract_text_from_pdf(file):
    text = ''
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
    return text

#Implement proofreading 

# Function to summarize text using a pre-trained model from Hugging Face
def summarize_text(text):
    # Initialize the summarizer model
    summarizer = pipeline("summarization")
    # Handle larger texts by splitting them (adjust as necessary based on your needs)
    parts = [text[i:i + 1024] for i in range(0, len(text), 1024)]
    summary = ""
    for part in parts:
        summary_part = summarizer(part, max_length=130, min_length=30, do_sample=False)
        summary += summary_part[0]['summary_text'] + " "
    return summary.strip()

def create_download_button(content):
    content_to_download = content.encode()
    st.download_button(label="Download summarized file or text",
                       data=content_to_download,
                       file_name="sportsummary.txt",
                       mime="text/plain")

# Streamlit app
def main():
    st.title("Sports Article Summarizer")
    
    # Input from text area
    user_input_text = st.text_area("Or enter text here to summarize", height=150)
    summarize_button = st.button("Summarize Text")

    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF or text file", type=['pdf', 'txt'])
    file_process_button = st.button("Process Uploaded File")

    text = ""
    if summarize_button and user_input_text:
        text = user_input_text
    elif file_process_button and uploaded_file:
        file_type = uploaded_file.type
        if file_type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
            
        elif file_type == "text/plain":
            text = uploaded_file.read().decode("utf-8")

    if text:
        summary = summarize_text(text)
        st.header("Original Article")
        st.text_area("Original Content", value=text, height=300)
        st.header("Summary")
        st.write(summary)
        create_download_button(summary)
    elif (summarize_button or file_process_button) and not text:
        st.error("Please enter some text or upload a file to summarize.")

if __name__ == "__main__":
    main()
