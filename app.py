import pdfplumber
import pandas as pd
import cohere
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
# Initialize the Cohere client with your API key
# Get the API key from the environment variable
COHERE_API_KEY = os.getenv('COHERE_API_KEY')

# Initialize the Cohere client with the hidden API key
client = cohere.Client(COHERE_API_KEY)
def analyze_table_with_cohere(table_text):
    prompt = f"Analyze the following table data extracted from a PDF \n and response should be in frensh:\n\n{table_text}"
    response = client.generate(
        model='command-r-plus-08-2024',
        prompt=prompt,
        temperature=0.7,
        max_tokens=1500
    )
    return response.generations[0].text.strip()

# Streamlit UI
import streamlit as st

st.title("PDF Table Extractor & Analyzer")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        page = pdf.pages[0]
        table = page.extract_table(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})
        
        if table:
            df = pd.DataFrame(table[1:], columns=table[0])


            df.fillna("")


            table_text = df.to_string()
            analysis_result = analyze_table_with_cohere(table_text)

            # Affichage du résultat
            st.subheader("Table Analysis")
            st.write(analysis_result)
        else:
            st.error("No table found in the uploaded PDF.")
