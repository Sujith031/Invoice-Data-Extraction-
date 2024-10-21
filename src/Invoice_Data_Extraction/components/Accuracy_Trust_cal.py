
import streamlit as st
from pdf2image import convert_from_bytes
import google.generativeai as genai
import io
import json
import re
from Levenshtein import distance as levenshtein_distance


GOOGLE_API_KEY = 'GOOGLE_API_KEY' 
genai.configure(api_key=GOOGLE_API_KEY)
POPPLER_PATH = r'poppler-24.08.0\Library\bin'



# Model Configuration
MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}



# Initializing the Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=MODEL_CONFIG,
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ]
)



# Function to convert PDF pages to images from bytes
def pdf_to_images(pdf_bytes):
    return convert_from_bytes(pdf_bytes, poppler_path=POPPLER_PATH)




# Function to format the image for processing with Gemini
def image_format(image):
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return [
        {
            "mime_type": "image/png",
            "data": image_bytes.read()
        }
    ]
    
    
    
    

# Function to generate output using the Gemini model
def gemini_output(image, system_prompt, user_prompt):
    image_info = image_format(image)
    input_prompt = [system_prompt, image_info[0], user_prompt]

    response = model.generate_content(input_prompt)
    return response.text




# Function to clean up and extract JSON from a response
def clean_json_response(response_text):
    try:
        json_string = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_string:
            clean_json = json_string.group(0)
            return json.loads(clean_json)
        else:
            raise ValueError("No valid JSON found in response")
    except json.JSONDecodeError as e:
        return f"JSON Parse Error: {str(e)}"
    except Exception as e:
        return f"Error cleaning JSON: {str(e)}"
    
    
    
    

# Function to process the PDF and extract invoice data
def process_pdf(pdf_bytes, user_prompt):
    system_prompt = """
        Output the invoice data in the following JSON format only:
        {
          "company_name": "",
          "company_GSTIN": "",
          "company_address": "",
          "company_email": "",
          "company_phone": "",
          "invoice_number": "",
          "invoice_date": "",
          "due_date": "",
          "customer_name": "",
          "place_of_supply": "",
          "bank": "",
          "account_number": "",
          "ifsc_code": "",
          "branch": "",
          "items": [
            {
              "description": "",
              "rate": "",
              "quantity": "",
              "taxable_value": "",
              "tax_amount": "",
              "total_amount": ""
            }
          ],
          "taxable_amount": "",
          "round_off": "",
          "igst": "",
          "cgst": "",
          "sgst": "",
          "total": "",
          "total_discount": ""
        }
        Ensure that every item in the invoice is included in the "items" array with all relevant fields filled out.
    """

    images = pdf_to_images(pdf_bytes)  
    responses = []

    for img in images:
        response = gemini_output(img, system_prompt, user_prompt)
        responses.append(response)

    return responses




# Enhanced function to calculate similarity using Levenshtein distance
def calculate_similarity(ref_value, user_value):
    
    if isinstance(ref_value, list):
        ref_value = " ".join(str(v) for v in ref_value).strip()
    else:
        ref_value = ref_value.strip() if ref_value else ""

    if isinstance(user_value, list):
        user_value = " ".join(str(v) for v in user_value).strip()
    else:
        user_value = user_value.strip() if user_value else ""

    
    if (ref_value.lower() in ["none", "null"] and user_value.lower() in ["none", "null"]):
        return 100.0  

    if not ref_value and not user_value:
        return 100.0  

    if not ref_value or not user_value:
        return 0.0  
    
    
    

    # Calculate similarity using Levenshtein distance
    max_len = max(len(ref_value), len(user_value))
    if max_len == 0:
        return 100.0

    # Calculate Levenshtein distance
    lev_distance = levenshtein_distance(ref_value, user_value)

    # Calculate similarity percentage
    similarity = (1 - lev_distance / max_len) * 100
    return similarity



# Function to compare two sets of data field by field
def compare_fields(ref_data, user_data):
    comparison_results = {}
    overall_similarity = 0.0
    field_count = 0
    
    for key in ref_data.keys():
        if key in user_data:
            field_count += 1
            similarity = calculate_similarity(ref_data[key], user_data[key])
            comparison_results[key] = {
                "reference": ref_data[key],
                "user": user_data[key],
                "similarity": similarity
            }
            overall_similarity += similarity
        else:
            comparison_results[key] = {
                "reference": ref_data[key],
                "user": None,
                "similarity": 0.0  # Key not present in user data
            }
    
    # Handle items separately for detailed comparison
    if "items" in ref_data and "items" in user_data:
        item_comparisons = []
        for item_ref, item_user in zip(ref_data["items"], user_data["items"]):
            item_comparison = {}
            for key in item_ref.keys():
                item_similarity = calculate_similarity(item_ref[key], item_user.get(key, ""))
                item_comparison[key] = {
                    "reference": item_ref[key],
                    "user": item_user.get(key, ""),
                    "similarity": item_similarity
                }
            item_comparisons.append(item_comparison)
        comparison_results["items"] = item_comparisons

    # Calculate overall accuracy percentage
    if field_count > 0:
        overall_accuracy = overall_similarity / field_count
    else:
        overall_accuracy = 0.0
    
    comparison_results["overall_accuracy"] = overall_accuracy
    return comparison_results

# Function to determine trust level based on the overall accuracy
def determine_trust_level(overall_accuracy, completeness, consistency):
    # Define weights for each factor
    weights = {
        "accuracy": 0.6,
        "completeness": 0.2,
        "consistency": 0.2,
    }

    # Calculate weighted trust score
    trust_score = (
        (weights["accuracy"] * overall_accuracy) +
        (weights["completeness"] * completeness) +
        (weights["consistency"] * consistency) 
    )

    return trust_score

# Function to calculate completeness based on character match
def calculate_completeness(ref_data, user_data):
    total_fields = len(ref_data)
    total_completeness_percentage = 0.0

    for key in ref_data.keys():
        ref_value = ref_data[key] or ""
        user_value = user_data.get(key, "") or ""

    
        ref_value = str(ref_value)
        user_value = str(user_value)

        if ref_value:  
            lev_distance = levenshtein_distance(ref_value, user_value)

           
            max_length = max(len(ref_value), len(user_value))
            if max_length > 0:
                completeness_percentage = (1 - lev_distance / max_length) * 100
                total_completeness_percentage += completeness_percentage

    return total_completeness_percentage / total_fields if total_fields > 0 else 0.0

# Function to calculate consistency
def calculate_consistency(ref_data, user_data):
   
    matching_fields = 0
    total_fields = len(ref_data)

    for key in ref_data.keys():
        if ref_data[key] == user_data.get(key, None):
            matching_fields += 1

    return (matching_fields / total_fields) * 100 if total_fields > 0 else 0.0



def highlight_comparisons(comparison_results, ref_data, user_data):
    highlighted = ""
    overall_accuracy = comparison_results.pop("overall_accuracy", 0.0)

    completeness = calculate_completeness(ref_data, user_data)
    consistency = calculate_consistency(ref_data, user_data)
    

    
    trust_score = determine_trust_level(overall_accuracy, completeness, consistency)

    
    results = {
        "comparison": comparison_results,
        "trust_score": trust_score,
        "overall_accuracy": overall_accuracy,
    }

    
    for key, values in comparison_results.items():
        if key != "items":
            highlighted += f"<p><strong>{key}:</strong><br>"
            highlighted += f"<span style='color: red'>Reference: {values['reference']}</span><br>"
            highlighted += f"<span style='color: green'>User: {values['user']}</span><br>"
            highlighted += f"Similarity: {values['similarity']:.2f}%</p>"
    
    
    if "items" in comparison_results:
        highlighted += "<h3>Item Comparisons</h3>"
        for idx, item_comparison in enumerate(comparison_results["items"], 1):
            highlighted += f"<h4>Item {idx}</h4>"
            for key, values in item_comparison.items():
                highlighted += f"<p><strong>{key}:</strong><br>"
                highlighted += f"<span style='color: red'>Reference: {values['reference']}</span><br>"
                highlighted += f"<span style='color: green'>User: {values['user']}</span><br>"
                highlighted += f"Similarity: {values['similarity']:.2f}%</p>"

    return highlighted, results  

def main():
    st.title("Invoice Comparison ")

    
    ref_pdf_file = st.file_uploader("Upload Reference Invoice PDF", type=["pdf"])
    user_pdf_file = st.file_uploader("Upload User Invoice PDF", type=["pdf"])

    if ref_pdf_file and user_pdf_file:
        
        ref_pdf_bytes = ref_pdf_file.read()
        user_pdf_bytes = user_pdf_file.read()

        
        user_prompt = "Extract the invoice data from this PDF."
        ref_response = process_pdf(ref_pdf_bytes, user_prompt)
        user_response = process_pdf(user_pdf_bytes, user_prompt)

        
        ref_data = clean_json_response(ref_response[0])
        user_data = clean_json_response(user_response[0])

        
        comparison_results = compare_fields(ref_data, user_data)
        highlighted_comparisons, results = highlight_comparisons(comparison_results, ref_data, user_data)
        
        
        st.write(f"**Trust Score:** {results['trust_score']:.2f}")
        st.write(f"**Overall Accuracy:** {results['overall_accuracy']:.2f}%")

        st.markdown(highlighted_comparisons, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
