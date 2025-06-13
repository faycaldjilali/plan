import PyPDF2
import pandas as pd
import io
from openai import OpenAI

def extract_text_from_pdf(uploaded_file, page_limit=1):
    """Extract text from the first page(s) of a PDF"""
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    
    for page in reader.pages[:page_limit]:
        text += page.extract_text()
    
    if not text:
        raise ValueError("No text found in PDF")
        
    # Clean extracted text
    table_lines = [line.strip() for line in text.split('\n') if line.strip()]
    return "\n".join(table_lines)

def analyze_table_with_openai(table_text, client):
    """Analyze table text using OpenAI"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """Vous êtes un assistant qui analyse des tableaux extraits de plans d'architecture. 
             Renvoyez les résultats dans un format structuré en français comme suit :
             
             | Catégorie | Description | Quantité | Unité | Remarques |
             |-----------|-------------|----------|-------|-----------|
             ... (remplissez les lignes avec les données pertinentes)"""},
             
            {"role": "user", "content": f"Analysez ces données de tableau architectural :\n{table_text}"}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content

def process_analysis_result(analysis_result):
    """Convert OpenAI analysis result to DataFrame"""
    lines = analysis_result.split('\n')
    table_data = []
    
    for line in lines:
        if line.startswith('|') and '---' not in line:
            clean_line = line.strip('|').replace('||', '|')
            parts = [p.strip() for p in clean_line.split('|')]
            
            if len(parts) == 5:
                table_data.append(parts)
    
    if not table_data:
        raise ValueError("No structured table found in the response")
        
    df = pd.DataFrame(
        table_data[1:],  # Skip header row
        columns=table_data[0]  # Use first row as headers
    )
    
    return df

def create_excel_file(df):
    """Create Excel file in memory from DataFrame"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
    return output