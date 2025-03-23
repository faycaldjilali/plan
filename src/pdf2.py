import os
import PyPDF2
import json
from dotenv import load_dotenv
import cohere

# Load environment variables
load_dotenv()

# Initialize Cohere client
client = cohere.Client(os.getenv('COHERE_API_KEY'))

def extract_text_from_pdf(pdf_path):
    """Improved PDF text extraction with error handling"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return '\n'.join([page.extract_text() for page in reader.pages])
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {str(e)}")

def generate_analysis_prompt(text):
    """Create structured prompt with proper escaping"""
    base_prompt = r'''
    **Analyze these architectural plans and generate comprehensive JSON output following this exact structure:**

    {structure_placeholder}
    
    **Requirements:**
    1. Preserve original French technical terms and metric units
    2. Convert all abbreviations using plan legends
    3. Separate botanical names from common names
    4. Handle multiple document types in single output
    5. Distinguish between conserved and new elements
    
    **Plans to Analyze:**
    {text}
    '''
    
    structure = r'''{
    "project_metadata": {
        "name": "Reconversion et extension de la nouvelle mairie",
        "location": "18 Rue de la Lombardie, 78930 Guerville",
        "documents": [
            {
                "file_name": "string",
                "type": "vegetation|elevation|floorplan|section|axonometry",
                "scale": "string",
                "revision_date": "DD/MM/YYYY"
            }
        ]
    },
    "zones": [
        {
            "zone_id": "string",
            "area_m2": float,
            "features": {
                "structural": ["list"],
                "vegetation": {
                    "trees": ["scientific names"],
                    "shrubs": ["scientific names"]
                }
            }
        }
    ]
    }'''

    return base_prompt.replace('{structure_placeholder}', structure).replace('{text}', text[:3000])

def extract_project_details_cr_pdf(text):
    """Improved Cohere integration with JSON validation"""
    try:
        response = client.generate(
            model='command-r-plus',
            prompt=generate_analysis_prompt(text),
            temperature=0.3,
            max_tokens=4000,
            return_cohere_sdk_response=False
        )
        
        # Extract JSON from response
        json_str = response.generations[0].text
        json_str = json_str[json_str.find('{'):json_str.rfind('}')+1]
        
        return json.loads(json_str)
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"API request failed: {str(e)}")

def process_pdf(pdf_path):
    """End-to-end processing pipeline"""
    try:
        text = extract_text_from_pdf(pdf_path)
        data = extract_project_details_cr_pdf(text)
        save_json(data, pdf_path)
        return data
    except Exception as e:
        return {"error": str(e)}

def save_json(data, pdf_path):
    """Improved file saving with unique filenames"""
    base_name = os.path.basename(pdf_path)
    json_name = f"{os.path.splitext(base_name)[0]}_analysis.json"
    
    with open(json_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


result = process_pdf("/home/faycal/Desktop/Untitled Folder 3/Untitled Folder/Untitled Folder/plan/data/3.5_PRO_Coupes.pdf")
print(json.dumps(result, indent=2))