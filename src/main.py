# src/main.py

from Invoice_Data_Extraction.logging import setup_logging
from Invoice_Data_Extraction.custom_exception import CustomException, handle_exception

def main():
    setup_logging()

    try:
        # Your application logic here
        raise ValueError("This is a sample error!")  # Sample error to demonstrate
    except Exception as e:
        handle_exception(CustomException("An error occurred in the application.", e))

if __name__ == "__main__":
    main()
