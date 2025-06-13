import os
from dotenv import load_dotenv
import streamlit as st
from src.pdfplan import (
    extract_text_from_pdf as extract_plan_text,
    analyze_table_with_openai as analyze_plan,
    process_analysis_result as process_plan_result,
    create_excel_file as create_plan_excel
)
from src.cctp import (
    extract_text_from_pdf as extract_cctp_text,
    analyze_cctp_with_openai as analyze_cctp,
    process_analysis_result as process_cctp_result,
    create_excel_file as create_cctp_excel
)
from openai import OpenAI

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def main():
    st.title("Analyse de documents de construction")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Document type selection
    doc_type = st.radio(
        "Type de document à analyser",
        ("Plan architectural", "Cahier des Clauses Techniques Particulières (CCTP)"),
        horizontal=True
    )
    
    uploaded_file = st.file_uploader("Téléverser un PDF", type=["pdf"])
    
    if uploaded_file:
        try:
            if doc_type == "Plan architectural":
                # Process as architectural plan
                table_text = extract_plan_text(uploaded_file)
                
                st.subheader("Texte extrait du plan")
                st.text(table_text)
                
                analysis_result = analyze_plan(table_text, client)
                
                st.subheader("Analyse structurée")
                st.write(analysis_result)
                
                df = process_plan_result(analysis_result)
                excel_file = create_plan_excel(df)
                file_name = "analyse_plan.xlsx"
                
            else:  # CCTP
                # Process as CCTP
                cctp_text = extract_cctp_text(uploaded_file)
                
                st.subheader("Texte extrait du CCTP")
                st.text(cctp_text)
                
                analysis_result = analyze_cctp(cctp_text, client)
                
                st.subheader("Analyse structurée")
                st.write(analysis_result)
                
                df = process_cctp_result(analysis_result)
                excel_file = create_cctp_excel(df)
                file_name = "analyse_cctp.xlsx"
            
            # Create download button
            st.download_button(
                label="📥 Télécharger le fichier Excel",
                data=excel_file.getvalue(),
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Une erreur inattendue s'est produite : {str(e)}")
            if 'analysis_result' in locals():
                st.text("Réponse brute pour débogage:")
                st.text(analysis_result)

if __name__ == "__main__":
    main()