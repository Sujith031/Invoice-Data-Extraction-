import os
import re
import json
import io
import requests
import streamlit as st
from pdf2image import convert_from_path
from PIL import Image
import google.generativeai as genai

# Configure Google API Key and model settings
GOOGLE_API_KEY = 'AIzaSyDH9iVF3PPlwzSp2k8W0WdAX_vRRFCw4-I'
POPPLER_PATH = r'poppler-24.08.0\Library\bin'

# Initialize the Gemini model with configuration
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}
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

def pdf_to_images(pdf_path):
    return convert_from_path(pdf_path, poppler_path=POPPLER_PATH)

def image_format(image):
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    return [{"mime_type": "image/png", "data": image_bytes.read()}]

def gemini_output(image, system_prompt):
    image_info = image_format(image)
    input_prompt = [system_prompt, image_info[0]]
    response = model.generate_content(input_prompt)
    return response.text

def clean_json_response(response_text):
    try:
        json_string = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_string:
            return json.loads(json_string.group(0))
        raise ValueError("No valid JSON found in response")
    except (json.JSONDecodeError, ValueError) as e:
        return f"JSON Parse Error: {str(e)}"

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

def process_pdf(pdf_path):
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
          "customer_mobile": "",
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
        Ensure that every item in the invoice is included in the "items" array with all relevant fields filled out. The "items" array should contain no duplicates.
        Output must be valid JSON, and fields must not be repeated.
    """
    images = pdf_to_images(pdf_path)
    responses = [gemini_output(img, system_prompt) for img in images]
    return responses

def download_pdfs_from_github(repo_url):
    parts = repo_url.rstrip('/').split('/')
    if len(parts) < 2:
        st.error("Invalid GitHub repository URL.")
        return []
    username = parts[-2]
    repo_name = parts[-1].replace('.git', '')
    repo_api_url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
    response = requests.get(repo_api_url)
    pdf_paths = []
    if response.status_code == 200:
        files = response.json()
        for file in files:
            if file['name'].endswith('.pdf'):
                pdf_paths.append(file['download_url'])
    else:
        st.error(f"Failed to access the repository. Status Code: {response.status_code}")
    return pdf_paths

# Streamlit app

st.title("This System is for extracting data from large volume of Invoices")

repo_link = st.text_input("Enter GitHub Repository Link (with PDFs)")

if repo_link and st.button("Extract"):
    pdf_urls = download_pdfs_from_github(repo_link)
    if not pdf_urls:
        st.warning("No PDF files found in the provided repository.")
    else:
        for idx, pdf_url in enumerate(pdf_urls):
            st.subheader(f"Extracted Data for PDF {idx + 1}")
            st.write(f"Processing {pdf_url}...")
            response = requests.get(pdf_url)
            if response.status_code == 200:
                pdf_path = os.path.join(os.getcwd(), pdf_url.split("/")[-1])
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
                extraction_responses = process_pdf(pdf_path)
                for res in extraction_responses:
                    cleaned_json = clean_json_response(res)
                    if isinstance(cleaned_json, dict):
                        st.json(cleaned_json)
                        # Prepare and display information in tables
                        company_info = {
                            "Company Name": cleaned_json.get("company_name"),
                            "Company GSTIN": cleaned_json.get("company_GSTIN"),
                            "Company Address": cleaned_json.get("company_address"),
                            "Company Email": cleaned_json.get("company_email"),
                            "Company Phone": cleaned_json.get("company_phone"),
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
                        total_info = {
                            "Taxable Amount": cleaned_json.get("taxable_amount"),
                            "Round Off": cleaned_json.get("round_off"),
                            "IGST": cleaned_json.get("igst"),
                            "CGST": cleaned_json.get("cgst"),
                            "SGST": cleaned_json.get("sgst"),
                            "Total": cleaned_json.get("total"),
                            "Total Discount": cleaned_json.get("total_discount"),
                        }
                        
                        st.markdown("### Company Information")
                        st.markdown(generate_html_table(company_info), unsafe_allow_html=True)
                        st.markdown("### Invoice Information")
                        st.markdown(generate_html_table(invoice_info), unsafe_allow_html=True)
                        st.markdown("### Bank Information")
                        st.markdown(generate_html_table(bank_info), unsafe_allow_html=True)
                        st.markdown("### Total Information")
                        st.markdown(generate_html_table(total_info), unsafe_allow_html=True)
                        st.markdown("### Items")
                        items_table = {"Items": cleaned_json.get("items", [])}
                        st.markdown(generate_html_table(items_table), unsafe_allow_html=True)
            else:
                st.error(f"Failed to download PDF: {pdf_url}. Status Code: {response.status_code}")
