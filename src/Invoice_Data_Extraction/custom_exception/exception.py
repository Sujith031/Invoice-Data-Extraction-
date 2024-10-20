import sys
import os
from src.Invoice_Data_Extraction.logging.logging import logger

class CustomException(Exception):
    def __init__(self, message: str, error: Exception):
        super().__init__(message)
        self.error = error
        _, _, exc_tb = sys.exc_info()
        file_path = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        logger.error(f"Error occurred in file: {file_path} at line number: {line_number}")
        logger.error(f"Error message: {message}")
        logger.error(f"Original error: {str(error)}")

    def __str__(self):
        return f"{self.error} : {self.args[0]}"
