# from src.Invoice_Data_Extraction.logging.logging import logger
# from src.Invoice_Data_Extraction.custom_exception.exception import CustomException

# def process_invoice(file_path):
#     try:
#         logger.info(f"Processing file: {file_path}")
#         # Simulate an error
#         raise ValueError("Simulated processing error")
#     except Exception as e:
#         raise CustomException("Failed to process invoice", e)

# if __name__ == "__main__":
#     try:
#         process_invoice("sample_invoice.pdf")
#     except CustomException as e:
#         logger.error(f"Application error: {str(e)}")

from Invoice_Data_Extraction.logging.logging import logger
from Invoice_Data_Extraction.custom_exception.exception import CustomException

# Test function for logging
def test_logging():
    logger.info("Testing the logger functionality!")
    logger.warning("This is a warning log.")
    logger.error("This is an error log.")

# Test function to simulate an error and trigger the custom exception handling
def test_exception_handling():
    try:
        logger.info("Attempting to process invoice and simulate an error.")
        # Simulate an error
        raise ValueError("Simulated processing error.")
    except Exception as e:
        raise CustomException("An error occurred during invoice processing.", e)

if __name__ == "__main__":
    # Test the logging functionality
    test_logging()

    # Test the exception handling
    try:
        test_exception_handling()
    except CustomException as e:
        logger.error(f"Custom Exception caught: {str(e)}")
