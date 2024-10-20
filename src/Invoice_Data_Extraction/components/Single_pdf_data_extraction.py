

import streamlit as st
from pdf2image import convert_from_path
from PIL import Image
import google.generativeai as genai
import io
import json
import re

# Constants
GOOGLE_API_KEY = 'GOOGLE_API_KEY'
POPPLER_PATH = r'poppler-24.08.0\Library\bin'

# Configure Google API
genai.configure(api_key=GOOGLE_API_KEY)

# Model Configuration
MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.95,  # Adjusted for more focused sampling
    "top_k": 50,    # Increased to allow for more diverse responses
    "max_output_tokens": 4096,
}

# Initialize the Gemini Model
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

# Function to convert PDF pages to images
def pdf_to_images(pdf_path):
    return convert_from_path(pdf_path, poppler_path=POPPLER_PATH)

# Function to format the image for processing with Gemini
def image_format(image):
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    
    return [{"mime_type": "image/png", "data": image_bytes.read()}]

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
        raise ValueError("No valid JSON found in response")
    except json.JSONDecodeError as e:
        return f"JSON Parse Error: {str(e)}"
    except Exception as e:
        return f"Error cleaning JSON: {str(e)}"

# Function to generate an HTML table for invoice sections
def generate_html_table(data):
    table_html = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
    </style>
    <table>
    """
    for key, value in data.items():
        if isinstance(value, str):
            value = value.replace("\n", "<br>")
        if isinstance(value, list):
            table_html += f"<tr><th colspan='2'>{key}</th></tr>"
            table_html += "<tr><th>Description</th><th>Rate</th><th>Quantity</th><th>Taxable Value</th><th>Tax Amount</th><th>Total Amount</th></tr>"
            for item in value:
                table_html += "<tr>"
                table_html += f"<td>{item.get('description', '')}</td>"
                table_html += f"<td>{item.get('rate', '')}</td>"
                table_html += f"<td>{item.get('quantity', '')}</td>"
                table_html += f"<td>{item.get('taxable_value', '')}</td>"
                table_html += f"<td>{item.get('tax_amount', '')}</td>"
                table_html += f"<td>{item.get('total_amount', '')}</td>"
                table_html += "</tr>"
        else:
            table_html += f"<tr><td>{key}</td><td>{value}</td></tr>"

    table_html += "</table>"
    return table_html

# Function to process the PDF and extract invoice data
def process_pdf(pdf_path, user_prompt):
    system_prompt = system_prompt = """
    Extract the following invoice details in a valid JSON format. Ensure to capture all information accurately, 
    including the rate for each item and the GSTIN number.

    {
      "company_name": "",
      "company_GSTIN": "",  # Ensure this is captured
      "company_address": "",
      "company_email": "",
      "company_phone": "",
      "invoice_number": "",
      "invoice_date": "",
      "due_date": "",
      "customer_name": "",
      "customer_mobile": "",
      "place_of_supply": "",

      "bank": "",
      "account_number": "",
      "ifsc_code": "",
      "branch": "",

      "items": [
        {
          "description": "",
          "rate": "",  # Ensure this is captured accurately
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

    Please ensure that the values for the items' fields are filled out correctly without additional keywords.
"""

    images = pdf_to_images(pdf_path)
    responses = []

    for img in images:
        response = gemini_output(img, system_prompt, user_prompt)
        responses.append(response)

    return responses

def clean_json_response(response_text):
    try:
        json_string = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_string:
            clean_json = json_string.group(0)
            return json.loads(clean_json)
        raise ValueError("No valid JSON found in response")
    except json.JSONDecodeError as e:
        return f"JSON Parse Error: {str(e)}"
    except Exception as e:
        return f"Error cleaning JSON: {str(e)}"



# Streamlit app


st.header("This System is for extracting data from single scanned PDFs as well as regular PDFs.")
st.subheader("Invoice Data Extractor using Google Gemini AI")


# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

# Extract button
if uploaded_file:
    st.write("Click 'Extract' to extract invoice details from the PDF.")
    
    if st.button("Extract"):
        with open("uploaded_file.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.write("Extracting data from PDF...")
        extracted_data = process_pdf("uploaded_file.pdf", "")

        for i, json_response in enumerate(extracted_data):
            st.subheader(f"Page {i+1} - JSON Response:")
            if json_response.strip():
                cleaned_json = clean_json_response(json_response)
                if isinstance(cleaned_json, dict):
                    st.json(cleaned_json)

                    company_info = {
                        "Company Name": cleaned_json.get("company_name"),
                        "GSTIN": cleaned_json.get("company_GSTIN"),
                        "Address": cleaned_json.get("company_address"),
                        "Email": cleaned_json.get("company_email"),
                        "Phone": cleaned_json.get("company_phone"),
                    }

                    invoice_info = {
                        "Invoice Number": cleaned_json.get("invoice_number"),
                        "Invoice Date": cleaned_json.get("invoice_date"),
                        "Due Date": cleaned_json.get("due_date"),
                        "Customer Name": cleaned_json.get("customer_name"),
                        "Customer Mobile": cleaned_json.get("customer_mobile"),
                        "Place of Supply": cleaned_json.get("place_of_supply"),
                    }

                    bank_info = {
                        "Bank": cleaned_json.get("bank"),
                        "Account Number": cleaned_json.get("account_number"),
                        "IFSC Code": cleaned_json.get("ifsc_code"),
                        "Branch": cleaned_json.get("branch"),
                    }

                    items_info = cleaned_json.get("items", [])
                    total_info = {
                        "Taxable Amount": cleaned_json.get("taxable_amount"),
                        "Round Off": cleaned_json.get("round_off"),
                        "IGST": cleaned_json.get("igst"),
                        "CGST": cleaned_json.get("cgst"),
                        "SGST": cleaned_json.get("sgst"),
                        "Total": cleaned_json.get("total"),
                        "Total Discount": cleaned_json.get("total_discount"),
                    }

                    st.subheader(f"Page {i+1} - Company Info:")
                    st.markdown(generate_html_table(company_info), unsafe_allow_html=True)

                    st.subheader(f"Page {i+1} - Invoice Info:")
                    st.markdown(generate_html_table(invoice_info), unsafe_allow_html=True)

                    st.subheader(f"Page {i+1} - Bank Info:")
                    st.markdown(generate_html_table(bank_info), unsafe_allow_html=True)

                    st.subheader(f"Page {i+1} - Items Info:")
                    st.markdown(generate_html_table({"Items": items_info}), unsafe_allow_html=True)

                    st.subheader(f"Page {i+1} - Total Info:")
                    st.markdown(generate_html_table(total_info), unsafe_allow_html=True)

                else:
                    st.warning(f"Page {i+1} - Error: {cleaned_json}")
            else:
                st.warning(f"Page {i+1} returned an empty response. Check the content or try another file.")
