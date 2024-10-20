# src/invoice_data_extraction/custom_exception/__init__.py

import logging
from logging import getLogger

# Initialize the logger
logger = getLogger(__name__)

class CustomException(Exception):
    """Custom exception class for handling specific errors."""
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

def handle_exception(exc):
    """Handles exceptions by logging them."""
    logger.error(f"An error occurred: {exc}")
    logger.debug(exc, exc_info=True) 
