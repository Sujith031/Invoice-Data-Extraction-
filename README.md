<div align="center">
    <h3 style="text-align: center;">Hi 👋 Sujith Here</h3>
    <h1 style="text-align: center;">Invoice-Data-Extraction</h1>
</div>
<div align="center">
    <img src="research/1" alt="Alt Text" width="500" height="300"/>
</div>



## Description
The Invoice Data Extraction project is designed to automate the extraction of essential information from PDF invoices using Python. It utilizes the `pdf2image` library for PDF-to-image conversion, `google.generativeai` for language-based extraction, and the `Levenshtein` library for string similarity matching, ensuring accurate data retrieval even with slight variations in invoice formats. The extracted data can be organized into structured formats for easy further processing.

## Table of Contents
- [Installation Instructions](#installation-instructions)
- [Usage Instructions](#usage-instructions)
- [Features](#features)
- [Contributing Guidelines](#contributing-guidelines)
- [License](#license)
- [Contact Information](#contact-information)
- [Acknowledgements](#acknowledgements)

## Installation Instructions

### Prerequisites
Ensure that Python 3.x is installed on your system. You will also need to install the following libraries:

- **pdf2image**: For converting PDF pages into images.
- **google.generativeai**: For using Google's generative AI models for text extraction.
- **Levenshtein**: For string comparison and matching.

### Steps
1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/invoice-data-extraction.git
   cd invoice-data-extraction
## Installation Instructions

### Install the Required Dependencies
    ```bash
    pip install -r requirements.txt 



## Usage Instructions

This project provides modules for extracting data from PDF invoices, supporting both single and multiple file extraction. Below are instructions on how to utilize the main components of the project.

- **Single PDF Extraction**


https://github.com/user-attachments/assets/e9bf0dd2-29a3-43c5-8aeb-0baf033e8724


- **Multiple PDF Invoices Extraction** - Extraction of large volumes of invoices from PDFs hosted on GitHub.


https://github.com/user-attachments/assets/ef281288-dc20-4181-9c3a-34dcdd61dd74

- **Accuracy and Trust Assessment** - The process involves taking invoice PDFs and manually created PDFs, calculating the accuracy score using the Levenshtein distance metric, and determining the trust score through a weighted average approach.


https://github.com/user-attachments/assets/31ecdfc0-e557-4d07-9695-f2bb4799ebf1


## Features

- **PDF to Image Conversion**: Uses `pdf2image` to convert invoice pages into images for easier data extraction.
- **Generative AI Integration**: Utilizes Google's Generative AI for accurate extraction of text from invoice images.
- **Levenshtein String Matching**: Ensures accurate extraction by matching similar text entries using Levenshtein distance.
- **Trust Score Calculation**: Computes trust scores using a weighted average approach to assess data reliability.
- **Single and Multiple PDF Handling**: Supports data extraction from both single invoices and batches of invoices.
