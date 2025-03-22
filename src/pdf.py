import pdfplumber
import pandas as pd
import cohere

# Initialize the Cohere client with your API key
client = cohere.Client("0mdbUsC2CfoWbampSNAjgqqFynSBjciFFBJ5xNX3")

def analyze_table_with_cohere(table_text):
    # Custom prompt asking for an analysis of the table
    prompt = f"Analyze the following table data extracted from a PDF. Provide insights, summaries, or any relevant details based on the table content:\n\n{table_text}\n\nFocus on key information, patterns, or notable observations."

    # Make the API call to Cohere
    response = client.generate(
        model='command-r-plus-08-2024',
        prompt=prompt,
        temperature=0.7,
        max_tokens=1500
    )

    # Extract the generated text from the response
    analysis_result = response.generations[0].text.strip()

    return analysis_result

# Path to your PDF file
pdf_path = "/home/faycal/Desktop/projects/plan/data/2.pdf"

# Open the PDF file
with pdfplumber.open(pdf_path) as pdf:
    # Assuming there is only 1 page
    page = pdf.pages[0]

    # Extract table from the page (adjusting for better accuracy)
    table = page.extract_table(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})

    if table:
        # Convert the table to a pandas DataFrame
        df = pd.DataFrame(table[1:], columns=table[0])

        # Replace None values with " " for better analysis
        df = df.fillna("")



        # Convert the DataFrame to a string for analysis
        table_text = df.to_string()

        # Analyze the table using Cohere
        analysis_result = analyze_table_with_cohere(table_text)

        # Display the analysis result
        print("\nAnalysis Result:")
        print(analysis_result)

        # Save the DataFrame to a CSV file
    else:
        print("No table found on the page.")

print("Extraction and analysis complete!")